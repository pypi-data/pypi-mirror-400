from enum import Enum

class DomainEvent(Enum):
    AUTH_ACCESS_RIGHT_ADDED = "auth_access_right_added"
    AUTH_ACCESS_RIGHT_REMOVED = "auth_access_right_removed"
    AUTH_USER_ADDED_TO_GROUP = "auth_user_added_to_group"
    AUTH_USER_REMOVED_FROM_GROUP = "auth_user_removed_from_group"
    AUTH_USER_ADDED_TO_SPONSOR_AND_SUMMIT = "auth_user_added_to_sponsor_and_summit"
    AUTH_USER_REMOVED_FROM_SPONSOR_AND_SUMMIT = "auth_user_removed_from_sponsor_and_summit"
    AUTH_USER_REMOVED_FROM_SUMMIT = "auth_user_removed_from_summit"

class InboundDomainEvent(Enum):
    # Summit events
    SUMMIT_CREATED = "summit_created"
    SUMMIT_UPDATED = "summit_updated"
    SUMMIT_DELETED = "summit_deleted"

    # Sponsor events
    SPONSOR_CREATED = "sponsor_created"
    SPONSOR_UPDATED = "sponsor_updated"
    SPONSOR_DELETED = "sponsor_deleted"

    # Sponsorship events
    SPONSORSHIP_CREATED = "sponsorship_created"
    SPONSORSHIP_UPDATED = "sponsorship_updated"
    SPONSORSHIP_REMOVED = "sponsorship_removed"

    # Sponsorship addon events
    SPONSORSHIP_ADDON_CREATED = "sponsorship_addon_created"
    SPONSORSHIP_ADDON_UPDATED = "sponsorship_addon_updated"
    SPONSORSHIP_ADDON_REMOVED = "sponsorship_addon_removed"