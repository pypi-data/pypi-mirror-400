class RobloxAPIError(Exception):
    """Base exception for Roblox API errors."""
    pass


class UserNotFound(RobloxAPIError):
    """Raised when a Roblox user cannot be found."""
    pass
