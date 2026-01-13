# Auth Gate

Enterprise-grade authentication for microservices with Kong and Keycloak integration, supporting user authentication, service-to-service authentication, and subscription tier enforcement.

## Features

-   **Dual authentication types**: Support for both user authentication and service-to-service authentication
-   **Unified authentication flow**: Single middleware handles both user and service tokens seamlessly
-   **Subscription tier enforcement**: Built-in support for FREE, BASIC, PROFESSIONAL, and ENTERPRISE tiers
-   **Flexible endpoint protection**: Configure endpoints as user-only, service-only, or accessible by both
-   **Dual-mode authentication**: Support for both Kong header-based auth (production) and direct Keycloak validation (development)
-   **Service-to-service authentication**: Built-in client credentials flow for secure inter-service communication
-   **Automatic token detection**: Intelligently detects whether tokens are from users or services
-   **Circuit breaker pattern**: Resilient handling of Keycloak failures with automatic recovery
-   **FastAPI integration**: Ready-to-use dependencies for protecting endpoints
-   **Role-based access control**: Fine-grained permission management with role and scope validation for both users and services
-   **Middleware support**: Automatic request authentication with configurable exclusions
-   **Organization context**: Multi-tenant support with organization ID tracking

## Installation

```bash
pip install auth-gate
```

### For Development

```bash
pip install auth-gate[dev]
```

## Quick Start

### Basic User Authentication

```python
from fastapi import FastAPI, Depends
from auth_gate import (
    AuthMiddleware,
    UserContext,
    get_current_user,
    require_admin,
)

# Initialize FastAPI app
app = FastAPI()

# Add authentication middleware
app.add_middleware(
    AuthMiddleware,
    excluded_paths={"/health", "/metrics"},
    excluded_prefixes={"/docs", "/openapi.json"}
)

# Protected endpoint - requires user authentication
@app.get("/api/profile")
async def get_profile(user: UserContext = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "username": user.username,
        "roles": user.roles
    }

# Admin-only endpoint (users only)
@app.get("/api/admin/users")
async def list_users(admin: UserContext = Depends(require_admin)):
    return {"message": "Admin access granted"}
```

### Service Authentication

```python
from auth_gate import ServiceContext, get_current_service

# Service-only endpoint
@app.post("/api/internal/sync")
async def sync_data(service: ServiceContext = Depends(get_current_service)):
    return {
        "status": "syncing",
        "service": service.service_name
    }
```

### Endpoints Accessible by Both Users and Services

```python
from auth_gate import AuthContext, get_current_auth

@app.get("/api/data")
async def get_data(auth: AuthContext = Depends(get_current_auth)):
    # Check what type of authentication this is
    if isinstance(auth, UserContext):
        # User authentication - return filtered data
        return {"data": "filtered", "user_id": auth.user_id}
    else:
        # Service authentication - return full data
        return {"data": "full", "service": auth.service_name}
```

### Subscription Tier Enforcement

```python
from auth_gate import (
    require_tier,
    require_tier_and_active,
    require_basic,
    require_professional,
    require_enterprise,
    require_paid_subscription,
    SubscriptionTier,
)

# Require minimum tier (PROFESSIONAL or higher)
@app.get("/api/analytics/advanced")
async def get_advanced_analytics(
    auth: AuthContext = Depends(require_tier(SubscriptionTier.PROFESSIONAL))
):
    return {"data": "advanced analytics"}

# Convenience dependency for common tiers
@app.get("/api/reports/enterprise")
async def get_enterprise_reports(auth: AuthContext = Depends(require_enterprise)):
    return {"reports": [...]}

# Require both minimum tier AND active subscription
@app.get("/api/premium/dashboard")
async def get_premium_dashboard(
    auth: AuthContext = Depends(require_tier_and_active(SubscriptionTier.BASIC))
):
    return {"dashboard": "premium data"}

# Require any paid subscription (non-free)
@app.get("/api/paid-feature")
async def get_paid_feature(auth: AuthContext = Depends(require_paid_subscription)):
    return {"feature": "paid-only data"}
```

### Role-Based Access Control

```python
from auth_gate import require_roles, require_user_roles, require_service_roles

# Endpoint accessible by users OR services with the role
require_supplier_or_admin = require_roles("supplier", "admin")

@app.get("/api/products")
async def list_products(auth: AuthContext = Depends(require_supplier_or_admin)):
    # Both users and services with supplier or admin role can access
    return {"products": []}

# User-only role requirement
require_user_supplier = require_user_roles("supplier")

@app.post("/api/user/products")
async def create_product(user: UserContext = Depends(require_user_supplier)):
    # Only users with supplier role can access
    return {"created": True}

# Service-only role requirement
require_data_processor = require_service_roles("data-processor")

@app.post("/api/internal/process")
async def process_data(service: ServiceContext = Depends(require_data_processor)):
    # Only services with data-processor role can access
    return {"processed": True}
```

### Optional Authentication

```python
from auth_gate import get_optional_user, get_optional_auth

# Optional user authentication (services are ignored)
@app.get("/api/recommendations")
async def get_recommendations(user: UserContext = Depends(get_optional_user)):
    if user:
        # Return personalized recommendations
        return {"recommendations": [...], "personalized": True}
    # Return general recommendations
    return {"recommendations": [...], "personalized": False}

# Optional authentication for both users and services
@app.get("/api/content")
async def get_content(auth: AuthContext = Depends(get_optional_auth)):
    if auth is None:
        return {"content": "public"}

    if isinstance(auth, UserContext):
        return {"content": "personalized", "user": auth.user_id}

    return {"content": "full", "service": auth.service_name}
```

## Configuration

Configure via environment variables:

```bash
# Authentication mode
AUTH_MODE=kong_headers  # or "direct_keycloak", "bypass" (testing only)

# Keycloak settings
KEYCLOAK_REALM_URL=https://keycloak.example.com/realms/tradelink
KEYCLOAK_CLIENT_ID=my-service
KEYCLOAK_CLIENT_SECRET=secret

# Service account (for S2S auth)
SERVICE_CLIENT_ID=my-service-account
SERVICE_CLIENT_SECRET=secret

# Optional settings
VERIFY_HMAC=false
INTERNAL_HMAC_KEY=your-hmac-key
```

### Kong Headers for Subscription

When using Kong, configure the Token Introspector plugin to inject these subscription headers:

| Header                  | Description                    | Example Values                          |
| ----------------------- | ------------------------------ | --------------------------------------- |
| `X-Subscription-Tier`   | User's subscription tier       | `free`, `basic`, `professional`, `enterprise` |
| `X-Subscription-Status` | Subscription status            | `active`, `suspended`, `cancelled`, `past_due` |
| `X-Organization-ID`     | Organization identifier        | `org-12345`                             |

## Service-to-Service Authentication

### Making Service Calls

```python
from auth_gate import ServiceAuthClient
import httpx

# Get service auth client
auth_client = ServiceAuthClient()

# Make authenticated service call
async def call_other_service():
    # Get service token (automatically cached and refreshed)
    auth_header = await auth_client.get_service_token()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://other-service/api/data",
            headers={"Authorization": auth_header}
        )
        return response.json()
```

### Kong Configuration for Services

When using Kong, configure the Token Introspector plugin with service authentication enabled:

```yaml
plugins:
    - name: token-introspector
      config:
          token_introspection_url: "https://keycloak.example.com/realms/production/protocol/openid-connect/token/introspect"
          client_id: "kong-gateway"
          client_secret: "your-secret"
          enable_service_auth: true
          service_role_identifier: "service" # Default role that identifies service tokens
```

### Service Token Detection

The system automatically detects service tokens based on:

1. Presence of "service" or "service-account" roles
2. Explicit `typ` or `token_type` claim set to "service"
3. Token has `client_id` but lacks user-specific claims (username, email, etc.)

## Advanced Features

### Custom Excluded Paths

```python
app.add_middleware(
    AuthMiddleware,
    excluded_paths={"/health", "/metrics", "/public"},
    excluded_prefixes={"/static", "/docs"},
    optional_auth_paths={"/api/products"}  # Auth optional for these paths
)
```

### Method-Specific Path Exclusions

```python
# Exclude specific HTTP methods from authentication
app.add_middleware(
    AuthMiddleware,
    excluded_paths={
        "/api/webhooks": {"POST"},  # Only POST is excluded
        "/health": None,  # All methods excluded
    },
    excluded_prefixes={
        "/api/docs": {"GET", "HEAD"},  # Only GET and HEAD excluded
    }
)
```

### Parameterized Paths with UUID Matching

You can exclude or make paths optional using UUID v4 parameters:

```python
app.add_middleware(
    AuthMiddleware,
    excluded_paths={
        "/api/v1/categories/{category_id:uuid}": {"GET"},  # Public read
        "/api/v1/products/{product_id:uuid}": {"GET"},
    },
    excluded_prefixes={
        "/api/{version:uuid}": {"GET"},  # Version-specific docs
    },
    optional_auth_paths={
        "/api/v1/recommendations/{user_id:uuid}": {"GET"},  # Personalized if authenticated
    }
)
```

**Pattern Syntax:**
- `{param:uuid}` - Matches valid UUID v4 format (case-insensitive)
- Works with exact paths, prefixes, and optional auth paths
- Supports method-specific exclusions
- Exact matches take precedence over patterns

**Example Behavior:**
```python
# Matches: /api/v1/categories/7b5bcc8f-2c99-43c0-9c7d-e27c10881bd2
# Does not match: /api/v1/categories/invalid-id
# Does not match: /api/v1/categories/all
```

**UUID v4 Validation:**
- Must have version digit "4" in the correct position
- Must have variant bits (8, 9, a, or b) in the correct position
- Accepts uppercase, lowercase, or mixed case

### Direct Validator Usage

```python
from auth_gate import UserValidator, AuthMode

validator = UserValidator(mode=AuthMode.DIRECT_KEYCLOAK)

# Validate a token and get user or service context
auth_context = await validator.validate_keycloak_token(token)

# Check what type it is
if isinstance(auth_context, UserContext):
    print(f"User: {auth_context.user_id}")
else:
    print(f"Service: {auth_context.service_name}")
```

### Type Checking

```python
from auth_gate import UserContext, ServiceContext, AuthContext

# Using isinstance
if isinstance(auth, UserContext):
    # Handle user
    print(f"User ID: {auth.user_id}")
elif isinstance(auth, ServiceContext):
    # Handle service
    print(f"Service: {auth.service_name}")

# Using the is_service property
if auth.is_service:
    print(f"Service: {auth.service_name}")
else:
    print(f"User: {auth.user_id}")
```

### Circuit Breaker Configuration

The S2S auth client includes automatic circuit breaker protection:

-   Opens after 5 consecutive failures
-   Attempts recovery after 60 seconds
-   Provides fail-fast behavior when Keycloak is unavailable

## Authentication Context

### UserContext

```python
class UserContext:
    user_id: str                        # Unique user identifier
    username: str | None                # Username
    email: str | None                   # Email address
    roles: List[str]                    # User roles
    scopes: List[str]                   # OAuth scopes
    session_id: str | None              # Session identifier
    client_id: str | None               # OAuth client ID
    auth_source: str                    # Authentication source
    organization_id: str | None         # Organization identifier
    subscription_tier: SubscriptionTier # Subscription tier (FREE, BASIC, PROFESSIONAL, ENTERPRISE)
    subscription_status: SubscriptionStatus  # Status (ACTIVE, SUSPENDED, CANCELLED, PAST_DUE)

    # Properties
    is_service: bool          # Always False for users
    is_admin: bool            # True if has admin role
    is_supplier: bool         # True if has supplier role (legacy)
    is_customer: bool         # True if has customer role
    is_moderator: bool        # True if has moderator role
    is_buyer: bool            # True if has buyer or customer role (legacy)
    is_subscription_active: bool  # True if subscription status is ACTIVE
    is_paid_subscriber: bool  # True if tier is not FREE

    # Platform Role Properties (Keycloak realm roles)
    is_platform_user: bool    # True if has 'user' role
    is_buyer_capable: bool    # True if has buyer_capable role
    is_supplier_capable: bool # True if has supplier_capable role
    is_verified_supplier: bool # True if has verified_supplier role
    is_platform_admin: bool   # True if has platform_admin role

    # Methods
    has_role(role: str) -> bool
    has_any_role(roles: List[str]) -> bool
    has_all_roles(roles: List[str]) -> bool
    has_scope(scope: str) -> bool
    has_any_scope(scopes: List[str]) -> bool
    has_minimum_tier(required_tier: SubscriptionTier) -> bool
    can_access_feature(required_tier: SubscriptionTier) -> bool
```

### ServiceContext

```python
class ServiceContext:
    service_name: str                   # Service identifier (client_id)
    service_id: str | None              # Service sub claim
    roles: List[str]                    # Service roles
    session_id: str | None              # Session identifier
    client_id: str | None               # OAuth client ID
    auth_source: str                    # Authentication source
    organization_id: str | None         # Organization identifier
    subscription_tier: SubscriptionTier # Defaults to FREE (services bypass tier checks)
    subscription_status: SubscriptionStatus  # Defaults to ACTIVE

    # Properties
    is_service: bool          # Always True for services
    is_admin: bool            # True if has admin role

    # Methods
    has_role(role: str) -> bool
    has_any_role(roles: List[str]) -> bool
    has_all_roles(roles: List[str]) -> bool
```

**Note:** Services bypass subscription tier checks by default when using `require_tier()` and related dependencies.

## Available Dependencies

### Authentication Dependencies

| Dependency              | Returns               | Description                                  |
| ----------------------- | --------------------- | -------------------------------------------- |
| `get_current_auth()`    | `AuthContext`         | Returns either UserContext or ServiceContext |
| `get_current_user()`    | `UserContext`         | Returns user, rejects services with 403      |
| `get_current_service()` | `ServiceContext`      | Returns service, rejects users with 403      |
| `get_optional_auth()`   | `AuthContext \| None` | Optional for both types                      |
| `get_optional_user()`   | `UserContext \| None` | Optional user, returns None for services     |

### Role Dependencies (Both Users and Services)

| Dependency                  | Required Role     |
| --------------------------- | ----------------- |
| `require_admin`             | admin             |
| `require_supplier`          | supplier          |
| `require_customer`          | customer          |
| `require_moderator`         | moderator         |
| `require_supplier_or_admin` | supplier or admin |

### Platform Role Dependencies (User-Only)

| Dependency                        | Required Role                         |
| --------------------------------- | ------------------------------------- |
| `require_user_role`               | user (base authenticated)             |
| `require_buyer`                   | buyer_capable                         |
| `require_buyer_or_admin`          | buyer_capable or platform_admin       |
| `require_supplier_capable`        | supplier_capable                      |
| `require_supplier_capable_or_admin` | supplier_capable or platform_admin  |
| `require_verified_supplier`       | verified_supplier                     |
| `require_platform_admin`          | platform_admin                        |

### Platform Role Constants

```python
from auth_gate import PlatformRole

# Available platform roles
PlatformRole.USER              # Base authenticated user role
PlatformRole.BUYER_CAPABLE     # Can create purchase orders
PlatformRole.SUPPLIER_CAPABLE  # Can list products and fulfill orders
PlatformRole.VERIFIED_SUPPLIER # Completed supplier verification
PlatformRole.PLATFORM_ADMIN    # Full platform access (composite role)
```

### Role Factories

```python
# Works with both users and services
require_roles("role1", "role2", ...)

# User-only
require_user_roles("role1", "role2", ...)

# Service-only
require_service_roles("role1", "role2", ...)

# Scope checking (user-only, as services don't have scopes)
require_scopes("scope1", "scope2", ...)
```

### Subscription Dependencies

| Dependency                    | Description                                         |
| ----------------------------- | --------------------------------------------------- |
| `require_tier(tier)`          | Factory requiring minimum subscription tier         |
| `require_active_subscription()` | Factory requiring active subscription status      |
| `require_tier_and_active(tier)` | Factory requiring both tier and active status     |
| `require_basic`               | Requires BASIC tier or higher                       |
| `require_professional`        | Requires PROFESSIONAL tier or higher                |
| `require_enterprise`          | Requires ENTERPRISE tier                            |
| `require_paid_subscription`   | Requires any paid tier (non-FREE)                   |
| `get_subscription_tier`       | Extract tier from header                            |
| `get_organization_id`         | Extract organization ID from header                 |

### Subscription Types

```python
from auth_gate import SubscriptionTier, SubscriptionStatus

# Tier hierarchy (lowest to highest)
SubscriptionTier.FREE
SubscriptionTier.BASIC
SubscriptionTier.PROFESSIONAL
SubscriptionTier.ENTERPRISE

# Subscription statuses
SubscriptionStatus.ACTIVE
SubscriptionStatus.SUSPENDED
SubscriptionStatus.CANCELLED
SubscriptionStatus.PAST_DUE
```

### Subscription Utilities

```python
from auth_gate import (
    meets_minimum_tier,
    compare_tiers,
    is_paid_tier,
    get_tier_level,
)

# Check if user tier meets requirement
meets_minimum_tier(SubscriptionTier.PROFESSIONAL, SubscriptionTier.BASIC)  # True

# Compare tiers (-1, 0, 1)
compare_tiers(SubscriptionTier.ENTERPRISE, SubscriptionTier.FREE)  # > 0

# Check if tier is paid
is_paid_tier(SubscriptionTier.BASIC)  # True
is_paid_tier(SubscriptionTier.FREE)   # False
```

## Migration Guide

### Updating Existing Applications

Your existing application will continue to work without changes. To add service support:

1. **Keep user-only endpoints as-is:**

```python
# No changes needed - already user-only
@app.get("/api/profile")
async def get_profile(user: UserContext = Depends(get_current_user)):
    return {"user_id": user.user_id}
```

2. **Add service-only endpoints:**

```python
# New service-only endpoint
@app.post("/api/internal/sync")
async def sync_data(service: ServiceContext = Depends(get_current_service)):
    return {"service": service.service_name}
```

3. **Update shared endpoints:**

```python
# Before - only users
@app.get("/api/data")
async def get_data(user: UserContext = Depends(get_current_user)):
    return {"data": [...]}

# After - both users and services
@app.get("/api/data")
async def get_data(auth: AuthContext = Depends(get_current_auth)):
    if isinstance(auth, UserContext):
        return {"data": "filtered"}
    return {"data": "full"}
```

## Development

### Running Tests

```bash
pytest tests/ --cov=auth_gate
```

### Code Quality

```bash
black src/
ruff check src/
mypy src/
```

## Examples

### Complete Example Application

```python
from fastapi import FastAPI, Depends
from auth_gate import (
    AuthMiddleware,
    AuthContext,
    UserContext,
    ServiceContext,
    SubscriptionTier,
    get_current_auth,
    get_current_user,
    get_current_service,
    require_roles,
    require_user_roles,
    require_tier,
    require_tier_and_active,
    require_professional,
)

app = FastAPI()

app.add_middleware(
    AuthMiddleware,
    excluded_paths={"/health"},
    optional_auth_paths={"/api/public"}
)

# Public endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# User-only endpoint
@app.get("/api/user/profile")
async def get_profile(user: UserContext = Depends(get_current_user)):
    return {
        "user": user.user_id,
        "tier": user.subscription_tier.value,
        "organization": user.organization_id
    }

# Service-only endpoint
@app.post("/api/internal/batch")
async def batch_process(service: ServiceContext = Depends(get_current_service)):
    return {"processed_by": service.service_name}

# Shared endpoint with role requirement
require_admin = require_roles("admin")

@app.delete("/api/data/{id}")
async def delete_data(id: str, auth: AuthContext = Depends(require_admin)):
    # Both admin users and admin services can delete
    return {"deleted": id}

# User-only with role requirement
require_user_editor = require_user_roles("editor")

@app.post("/api/articles")
async def create_article(user: UserContext = Depends(require_user_editor)):
    return {"author": user.user_id}

# Tier-protected endpoint (PROFESSIONAL or higher)
@app.get("/api/analytics")
async def get_analytics(auth: AuthContext = Depends(require_professional)):
    return {"analytics": "professional data"}

# Tier and active subscription required
@app.get("/api/premium/reports")
async def get_premium_reports(
    auth: AuthContext = Depends(require_tier_and_active(SubscriptionTier.BASIC))
):
    return {"reports": "premium data"}

# Custom tier check within endpoint
@app.get("/api/features")
async def get_features(user: UserContext = Depends(get_current_user)):
    features = ["basic_dashboard"]

    if user.has_minimum_tier(SubscriptionTier.PROFESSIONAL):
        features.append("advanced_analytics")

    if user.has_minimum_tier(SubscriptionTier.ENTERPRISE):
        features.append("custom_integrations")

    return {"features": features, "tier": user.subscription_tier.value}
```

## License

For use within tradelink suite of services - See LICENSE file for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/tradelink-org/auth-gate/issues).
