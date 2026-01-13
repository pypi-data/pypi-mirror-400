"""
FastAPI middleware for authentication (with service-to-service support)
"""

import logging
import re
import time
from typing import Dict, List, Optional, Pattern, Set, Tuple, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import get_settings
from .user_auth import get_user_validator

logger = logging.getLogger(__name__)

# UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
# where y is 8, 9, a, or b (variant bits)
TYPE_PATTERNS = {
    "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication in Kong/Keycloak environment.

    Features:
    - Automatic authentication based on configured mode
    - Support for both user and service authentication
    - Configurable path exclusions
    - Optional authentication paths
    - Request enrichment with user/service context
    - Security headers injection
    """

    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: Optional[Union[Set[str], Dict[str, Optional[Set[str]]]]] = None,
        excluded_prefixes: Optional[Union[Set[str], Dict[str, Optional[Set[str]]]]] = None,
        optional_auth_paths: Optional[Union[Set[str], Dict[str, Optional[Set[str]]]]] = None,
    ):
        """
        Initialize authentication middleware.

        Args:
            app: ASGI application
            excluded_paths: Exact paths that don't require authentication. Can be a set of paths (all methods) or a dict of path to methods (None for all methods).
            excluded_prefixes: Path prefixes that don't require authentication. Similar format as excluded_paths.
            optional_auth_paths: Paths where authentication is optional. Similar format as excluded_paths.
        """
        super().__init__(app)

        # Paths that don't require authentication
        self.excluded_paths_dict = self._normalize_paths(
            excluded_paths
            or {
                "/health",
                "/metrics",
                "/openapi.json",
                "/favicon.ico",
            }
        )

        # Path prefixes that don't require authentication
        self.excluded_prefixes_dict = self._normalize_paths(
            excluded_prefixes
            or {
                "/api/docs",
                "/api/redoc",
                "/static",
                "/_health",
            }
        )

        # Paths where authentication is optional
        self.optional_auth_dict = self._normalize_paths(optional_auth_paths or set())

        # Compile parameterized patterns
        self._excluded_patterns = self._compile_patterns(self.excluded_paths_dict)
        self._excluded_prefix_patterns = self._compile_patterns(
            self.excluded_prefixes_dict, is_prefix=True
        )
        self._optional_patterns = self._compile_patterns(self.optional_auth_dict)

        # Remove parameterized paths from literal dicts (they're now in pattern lists)
        self._remove_parameterized_from_dicts()

        self.validator = get_user_validator()
        self.settings = get_settings()

    def _normalize_paths(
        self, paths: Union[Set[str], Dict[str, Optional[Set[str]]]]
    ) -> Dict[str, Optional[Set[str]]]:
        """Normalize paths to dict format for backward compatibility"""
        if isinstance(paths, set):
            return {p: None for p in paths}
        if isinstance(paths, dict):
            normalized: Dict[str, Optional[Set[str]]] = {}
            for p, m in paths.items():
                if m is None:
                    normalized[p] = None
                else:
                    if not isinstance(m, set):
                        raise ValueError("Methods must be a set or None")
                    normalized[p] = {meth.upper() for meth in m}
            return normalized
        raise ValueError("Invalid type for paths: must be set or dict")

    @staticmethod
    def _has_parameters(path: str) -> bool:
        """Check if path contains parameter placeholders like {param:type}"""
        return "{" in path and "}" in path

    def _compile_path_pattern(self, path: str, is_prefix: bool = False) -> Pattern:
        """
        Compile a parameterized path pattern to regex.

        Supports syntax: /path/{param:type}/more

        Types:
            - uuid: UUID v4 format (case-insensitive)

        Args:
            path: Path pattern with {param:type} placeholders
            is_prefix: If True, don't anchor end of pattern (for prefix matching)

        Returns:
            Compiled regex pattern

        Raises:
            ValueError: If syntax is invalid or type is unsupported

        Examples:
            >>> _compile_path_pattern('/api/{id:uuid}')
            re.compile(r'^/api/[0-9a-f]{8}-...$', re.IGNORECASE)

            >>> _compile_path_pattern('/api/{version:uuid}', is_prefix=True)
            re.compile(r'^/api/[0-9a-f]{8}-...', re.IGNORECASE)
        """
        # Pattern to find parameter placeholders: {param:type}
        param_pattern = r"\{([^}:]+)(?::([^}]+))?\}"

        def replace_param(match: re.Match) -> str:
            param_name = match.group(1).strip()
            param_type = match.group(2).strip() if match.group(2) else None

            if param_type is None:
                raise ValueError(
                    f"Parameter '{{{param_name}}}' missing type annotation. "
                    f"Use {{param:type}} syntax (e.g., {{id:uuid}})"
                )

            if param_type not in TYPE_PATTERNS:
                supported = ", ".join(TYPE_PATTERNS.keys())
                raise ValueError(
                    f"Unsupported type '{param_type}' for parameter '{{{param_name}}}'. "
                    f"Supported types: {supported}"
                )

            return f"({TYPE_PATTERNS[param_type]})"

        # Escape special regex characters in path
        escaped_path = re.escape(path)

        # Unescape { and } for parameter replacement
        escaped_path = escaped_path.replace(r"\{", "{").replace(r"\}", "}")

        # Replace parameters with regex patterns
        regex_pattern = re.sub(param_pattern, replace_param, escaped_path)

        # Anchor pattern
        if is_prefix:
            regex_pattern = f"^{regex_pattern}"
        else:
            regex_pattern = f"^{regex_pattern}$"

        # Compile with case-insensitive flag for UUIDs
        try:
            return re.compile(regex_pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Failed to compile pattern for path '{path}': {e}")

    def _compile_patterns(
        self, paths_dict: Dict[str, Optional[Set[str]]], is_prefix: bool = False
    ) -> List[Tuple[Pattern, Optional[Set[str]]]]:
        """
        Extract parameterized paths and compile them to regex patterns.

        Args:
            paths_dict: Dictionary of paths with optional method restrictions
            is_prefix: If True, compile as prefix patterns (don't anchor end)

        Returns:
            List of (compiled_pattern, methods) tuples

        Raises:
            ValueError: If pattern syntax is invalid or type is unsupported
        """
        patterns = []

        for path, methods in paths_dict.items():
            if self._has_parameters(path):
                try:
                    compiled_pattern = self._compile_path_pattern(path, is_prefix)
                    patterns.append((compiled_pattern, methods))
                except ValueError as e:
                    raise ValueError(f"Invalid pattern in path '{path}': {e}")

        return patterns

    def _remove_parameterized_from_dicts(self):
        """
        Remove parameterized paths from literal path dictionaries.
        They are now stored in pattern lists.
        """
        for path_dict in [
            self.excluded_paths_dict,
            self.excluded_prefixes_dict,
            self.optional_auth_dict,
        ]:
            parameterized_keys = [key for key in path_dict.keys() if self._has_parameters(key)]
            for key in parameterized_keys:
                del path_dict[key]

    def is_excluded(self, path: str, method: str) -> bool:
        """
        Check if path is excluded from authentication for the given method.

        Matching order (highest to lowest priority):
        1. Exact literal match in excluded_paths
        2. Parameterized pattern match in excluded_paths
        3. Prefix literal match in excluded_prefixes
        4. Prefix pattern match in excluded_prefixes

        Args:
            path: Request path (e.g., '/api/v1/categories/7b5bcc8f-...')
            method: HTTP method (e.g., 'GET', 'POST')

        Returns:
            True if path is excluded from authentication for this method
        """
        # 1. Exact literal match (O(1) dict lookup)
        for p, methods in self.excluded_paths_dict.items():
            if path == p and (methods is None or method in methods):
                logger.debug(f"Exact match excluded: {path} [{method}]")
                return True

        # 2. Parameterized pattern match (O(n) pattern checks)
        for pattern, methods in self._excluded_patterns:
            if pattern.match(path) and (methods is None or method in methods):
                logger.debug(f"Pattern match excluded: {path} [{method}] via {pattern.pattern}")
                return True

        # 3. Prefix literal match (O(n) prefix checks)
        for p, methods in self.excluded_prefixes_dict.items():
            if path.startswith(p) and (methods is None or method in methods):
                logger.debug(f"Prefix match excluded: {path} [{method}]")
                return True

        # 4. Prefix pattern match (O(n) pattern checks)
        for pattern, methods in self._excluded_prefix_patterns:
            # For prefix patterns, check if path starts with pattern match
            match = pattern.match(path)
            if match and (methods is None or method in methods):
                logger.debug(
                    f"Prefix pattern match excluded: {path} [{method}] via {pattern.pattern}"
                )
                return True

        return False

    def is_optional_auth(self, path: str, method: str) -> bool:
        """
        Check if path has optional authentication for the given method.

        Checks both literal paths and parameterized patterns.

        Args:
            path: Request path
            method: HTTP method

        Returns:
            True if authentication is optional for this path and method
        """
        # Exact literal match
        for p, methods in self.optional_auth_dict.items():
            if (path == p) and (methods is None or method in methods):
                return True

        # Parameterized pattern match
        for pattern, methods in self._optional_patterns:
            if pattern.match(path) and (methods is None or method in methods):
                logger.debug(
                    f"Pattern match optional auth: {path} [{method}] via {pattern.pattern}"
                )
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication"""
        start_time = time.time()

        # Add request ID for tracing
        request_id = request.headers.get("X-Request-ID", str(time.time()))

        # Skip authentication for excluded paths
        method = request.method.upper()
        if self.is_excluded(request.url.path, method):
            response = await call_next(request)
            self._add_security_headers(response, request_id, start_time)
            return response

        try:
            # Extract authentication headers
            auth_headers = self._extract_auth_headers(request)

            # Check if we have any authentication
            has_auth = self._has_authentication(auth_headers)

            if not has_auth:
                # No authentication present
                if self.is_optional_auth(request.url.path, method):
                    request.state.user = None
                else:
                    logger.warning(f"Missing authentication for {request.url.path}")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={
                            "error": "unauthorized",
                            "message": "Authentication required",
                            "request_id": request_id,
                        },
                    )
            else:
                # Validate authentication
                auth_context = await self.validator.get_current_user(request, **auth_headers)
                request.state.user = auth_context

                # Log authentication details
                self._log_authentication(auth_context, request)

            # Process request
            response = await call_next(request)

            # Add security headers
            self._add_security_headers(response, request_id, start_time)

            return response

        except HTTPException as e:
            # Handle authentication exceptions
            logger.warning(f"Auth failed: {e.detail}, path={request.url.path}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "authentication_failed",
                    "message": e.detail,
                    "request_id": request_id,
                },
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_error",
                    "message": "An internal error occurred",
                    "request_id": request_id,
                },
            )

    def _extract_auth_headers(self, request: Request) -> dict:
        """Extract all authentication-related headers (user, service, and subscription)"""
        return {
            "authorization": request.headers.get("Authorization"),
            # Common headers
            "x_token_verified": request.headers.get("X-Token-Verified"),
            "x_auth_source": request.headers.get("X-Auth-Source"),
            # User headers
            "x_user_id": request.headers.get("X-User-ID"),
            "x_username": request.headers.get("X-Username"),
            "x_user_email": request.headers.get("X-User-Email"),
            "x_user_roles": request.headers.get("X-User-Roles"),
            "x_user_scopes": request.headers.get("X-User-Scopes"),
            # Service headers
            "x_service_name": request.headers.get("X-Service-Name"),
            "x_service_authenticated": request.headers.get("X-Service-Authenticated"),
            "x_service_roles": request.headers.get("X-Service-Roles"),
            # Common session/client headers
            "x_session_id": request.headers.get("X-Session-ID"),
            "x_client_id": request.headers.get("X-Client-ID"),
            # Organization header
            "x_organization_id": request.headers.get("X-Organization-ID"),
            # Subscription headers
            "x_subscription_tier": request.headers.get("X-Subscription-Tier"),
            "x_subscription_status": request.headers.get("X-Subscription-Status"),
        }

    def _has_authentication(self, auth_headers: dict) -> bool:
        """Check if request has any authentication (user or service)"""
        if self.settings.is_production:
            # Kong mode - check for verified token header
            return auth_headers.get("x_token_verified") == "true"
        elif self.settings.is_development:
            # Direct Keycloak mode - check for Bearer token
            auth: str = auth_headers.get("authorization", "")
            return auth.startswith("Bearer ")
        elif self.settings.is_testing:
            # Bypass mode - always authenticated
            return True
        return False

    def _log_authentication(self, auth_context, request: Request):
        """Log authentication details for user or service"""
        from .schemas import ServiceContext, UserContext

        if isinstance(auth_context, UserContext):
            logger.info(
                f"Authenticated user request: user_id={auth_context.user_id}, "
                f"username={auth_context.username}, roles={auth_context.roles}, "
                f"path={request.url.path}, method={request.method}, "
                f"source={auth_context.auth_source}"
            )
        elif isinstance(auth_context, ServiceContext):
            logger.info(
                f"Authenticated service request: service={auth_context.service_name}, "
                f"roles={auth_context.roles}, path={request.url.path}, "
                f"method={request.method}, source={auth_context.auth_source}"
            )
        else:
            logger.info(
                f"Authenticated request: path={request.url.path}, "
                f"method={request.method}, source={getattr(auth_context, 'auth_source', 'unknown')}"
            )

    def _add_security_headers(self, response, request_id: str, start_time: float):
        """Add security and performance headers to response"""
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Add performance metrics
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
