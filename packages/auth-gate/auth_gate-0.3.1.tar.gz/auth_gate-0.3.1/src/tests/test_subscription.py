"""Tests for subscription tier functionality."""

from auth_gate import (
    SubscriptionStatus,
    SubscriptionTier,
    compare_tiers,
    get_tier_level,
    get_tiers_at_or_above,
    get_tiers_below,
    is_paid_tier,
    meets_minimum_tier,
    parse_subscription_status,
    parse_subscription_tier,
)


class TestSubscriptionTier:
    """Test subscription tier utilities."""

    def test_meets_minimum_tier_equal(self):
        """Test tier comparison when equal."""
        assert (
            meets_minimum_tier(SubscriptionTier.PROFESSIONAL, SubscriptionTier.PROFESSIONAL) is True
        )

    def test_meets_minimum_tier_above(self):
        """Test tier comparison when above required."""
        assert meets_minimum_tier(SubscriptionTier.ENTERPRISE, SubscriptionTier.BASIC) is True

    def test_meets_minimum_tier_below(self):
        """Test tier comparison when below required."""
        assert meets_minimum_tier(SubscriptionTier.FREE, SubscriptionTier.PROFESSIONAL) is False

    def test_meets_minimum_tier_free_requires_free(self):
        """Test free tier meets free requirement."""
        assert meets_minimum_tier(SubscriptionTier.FREE, SubscriptionTier.FREE) is True

    def test_compare_tiers_greater(self):
        """Test tier comparison when first is greater."""
        assert compare_tiers(SubscriptionTier.ENTERPRISE, SubscriptionTier.FREE) > 0

    def test_compare_tiers_less(self):
        """Test tier comparison when first is less."""
        assert compare_tiers(SubscriptionTier.FREE, SubscriptionTier.ENTERPRISE) < 0

    def test_compare_tiers_equal(self):
        """Test tier comparison when equal."""
        assert compare_tiers(SubscriptionTier.BASIC, SubscriptionTier.BASIC) == 0

    def test_is_paid_tier_free(self):
        """Test free tier is not paid."""
        assert is_paid_tier(SubscriptionTier.FREE) is False

    def test_is_paid_tier_basic(self):
        """Test basic tier is paid."""
        assert is_paid_tier(SubscriptionTier.BASIC) is True

    def test_is_paid_tier_professional(self):
        """Test professional tier is paid."""
        assert is_paid_tier(SubscriptionTier.PROFESSIONAL) is True

    def test_is_paid_tier_enterprise(self):
        """Test enterprise tier is paid."""
        assert is_paid_tier(SubscriptionTier.ENTERPRISE) is True

    def test_parse_subscription_tier_valid_lowercase(self):
        """Test parsing valid tier string lowercase."""
        assert parse_subscription_tier("professional") == SubscriptionTier.PROFESSIONAL

    def test_parse_subscription_tier_valid_uppercase(self):
        """Test parsing valid tier string uppercase."""
        assert parse_subscription_tier("ENTERPRISE") == SubscriptionTier.ENTERPRISE

    def test_parse_subscription_tier_valid_mixed_case(self):
        """Test parsing valid tier string mixed case."""
        assert parse_subscription_tier("Basic") == SubscriptionTier.BASIC

    def test_parse_subscription_tier_invalid(self):
        """Test parsing invalid tier string returns default."""
        assert parse_subscription_tier("invalid") == SubscriptionTier.FREE

    def test_parse_subscription_tier_none(self):
        """Test parsing None returns default."""
        assert parse_subscription_tier(None) == SubscriptionTier.FREE

    def test_parse_subscription_tier_empty(self):
        """Test parsing empty string returns default."""
        assert parse_subscription_tier("") == SubscriptionTier.FREE

    def test_parse_subscription_tier_custom_default(self):
        """Test parsing with custom default."""
        assert (
            parse_subscription_tier("invalid", default=SubscriptionTier.BASIC)
            == SubscriptionTier.BASIC
        )

    def test_get_tiers_at_or_above_professional(self):
        """Test getting tiers at or above professional."""
        tiers = get_tiers_at_or_above(SubscriptionTier.PROFESSIONAL)
        assert SubscriptionTier.PROFESSIONAL in tiers
        assert SubscriptionTier.ENTERPRISE in tiers
        assert SubscriptionTier.BASIC not in tiers
        assert SubscriptionTier.FREE not in tiers

    def test_get_tiers_at_or_above_free(self):
        """Test getting tiers at or above free returns all."""
        tiers = get_tiers_at_or_above(SubscriptionTier.FREE)
        assert len(tiers) == 4
        assert SubscriptionTier.FREE in tiers
        assert SubscriptionTier.ENTERPRISE in tiers

    def test_get_tiers_at_or_above_enterprise(self):
        """Test getting tiers at or above enterprise returns only enterprise."""
        tiers = get_tiers_at_or_above(SubscriptionTier.ENTERPRISE)
        assert len(tiers) == 1
        assert SubscriptionTier.ENTERPRISE in tiers

    def test_get_tiers_below_professional(self):
        """Test getting tiers below professional."""
        tiers = get_tiers_below(SubscriptionTier.PROFESSIONAL)
        assert SubscriptionTier.FREE in tiers
        assert SubscriptionTier.BASIC in tiers
        assert SubscriptionTier.PROFESSIONAL not in tiers
        assert SubscriptionTier.ENTERPRISE not in tiers

    def test_get_tiers_below_free(self):
        """Test getting tiers below free returns empty."""
        tiers = get_tiers_below(SubscriptionTier.FREE)
        assert len(tiers) == 0

    def test_get_tier_level_ordering(self):
        """Test tier levels are in correct order."""
        assert get_tier_level(SubscriptionTier.FREE) == 0
        assert get_tier_level(SubscriptionTier.BASIC) == 1
        assert get_tier_level(SubscriptionTier.PROFESSIONAL) == 2
        assert get_tier_level(SubscriptionTier.ENTERPRISE) == 3


class TestSubscriptionStatus:
    """Test subscription status parsing."""

    def test_parse_subscription_status_active(self):
        """Test parsing active status."""
        assert parse_subscription_status("active") == SubscriptionStatus.ACTIVE

    def test_parse_subscription_status_suspended(self):
        """Test parsing suspended status."""
        assert parse_subscription_status("suspended") == SubscriptionStatus.SUSPENDED

    def test_parse_subscription_status_cancelled(self):
        """Test parsing cancelled status."""
        assert parse_subscription_status("cancelled") == SubscriptionStatus.CANCELLED

    def test_parse_subscription_status_past_due(self):
        """Test parsing past_due status."""
        assert parse_subscription_status("past_due") == SubscriptionStatus.PAST_DUE

    def test_parse_subscription_status_uppercase(self):
        """Test parsing uppercase status."""
        assert parse_subscription_status("ACTIVE") == SubscriptionStatus.ACTIVE

    def test_parse_subscription_status_invalid(self):
        """Test parsing invalid status returns default."""
        assert parse_subscription_status("invalid") == SubscriptionStatus.ACTIVE

    def test_parse_subscription_status_none(self):
        """Test parsing None returns default."""
        assert parse_subscription_status(None) == SubscriptionStatus.ACTIVE

    def test_parse_subscription_status_empty(self):
        """Test parsing empty string returns default."""
        assert parse_subscription_status("") == SubscriptionStatus.ACTIVE


class TestUserContextSubscription:
    """Test UserContext subscription methods."""

    def test_has_minimum_tier_meets(self, user_context_professional):
        """Test has_minimum_tier when tier is sufficient."""
        assert user_context_professional.has_minimum_tier(SubscriptionTier.BASIC) is True

    def test_has_minimum_tier_not_meets(self, user_context_professional):
        """Test has_minimum_tier when tier is insufficient."""
        assert user_context_professional.has_minimum_tier(SubscriptionTier.ENTERPRISE) is False

    def test_has_minimum_tier_equal(self, user_context_professional):
        """Test has_minimum_tier when tier is equal."""
        assert user_context_professional.has_minimum_tier(SubscriptionTier.PROFESSIONAL) is True

    def test_is_subscription_active_true(self, user_context_professional):
        """Test is_subscription_active when active."""
        assert user_context_professional.is_subscription_active is True

    def test_is_subscription_active_false(self, user_context_suspended):
        """Test is_subscription_active when suspended."""
        assert user_context_suspended.is_subscription_active is False

    def test_is_paid_subscriber_true(self, user_context_professional):
        """Test is_paid_subscriber when paid tier."""
        assert user_context_professional.is_paid_subscriber is True

    def test_is_paid_subscriber_false(self, user_context_free):
        """Test is_paid_subscriber when free tier."""
        assert user_context_free.is_paid_subscriber is False

    def test_can_access_feature_active_and_sufficient(self, user_context_professional):
        """Test can_access_feature when active and tier sufficient."""
        assert user_context_professional.can_access_feature(SubscriptionTier.PROFESSIONAL) is True

    def test_can_access_feature_active_but_insufficient(self, user_context_professional):
        """Test can_access_feature when active but tier insufficient."""
        assert user_context_professional.can_access_feature(SubscriptionTier.ENTERPRISE) is False

    def test_can_access_feature_suspended(self, user_context_suspended):
        """Test can_access_feature when subscription suspended."""
        # Even though tier is sufficient, status is not active
        assert user_context_suspended.can_access_feature(SubscriptionTier.BASIC) is False


class TestServiceContextSubscription:
    """Test ServiceContext subscription defaults."""

    def test_service_default_tier(self, service_context):
        """Test service has default free tier."""
        assert service_context.subscription_tier == SubscriptionTier.FREE

    def test_service_default_status(self, service_context):
        """Test service has default active status."""
        assert service_context.subscription_status == SubscriptionStatus.ACTIVE

    def test_service_is_subscription_active(self, service_context):
        """Test service is_subscription_active returns True by default."""
        assert service_context.is_subscription_active is True

    def test_service_is_paid_subscriber(self, service_context):
        """Test service is_paid_subscriber returns False by default."""
        assert service_context.is_paid_subscriber is False
