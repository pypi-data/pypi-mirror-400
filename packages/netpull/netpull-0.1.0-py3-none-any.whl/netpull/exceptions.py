"""NetPull exception hierarchy"""


class NetPullError(Exception):
    """Base exception for all netpull errors"""
    pass


class BrowserLaunchError(NetPullError):
    """Raised when browser fails to launch"""
    pass


class NavigationError(NetPullError):
    """Raised when page navigation fails"""
    pass


class ExtractionError(NetPullError):
    """Raised when content extraction fails"""
    pass


class ConfigurationError(NetPullError):
    """Raised when configuration is invalid"""
    pass
