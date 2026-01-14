from enum import Enum


class GraphAPICommonErrorCode(Enum):
    """
    Taken from:
    https://developers.facebook.com/docs/graph-api/guides/error-handling#errorcodes
    """

    API_SESSION = 102
    API_UNKNOWN = 1
    API_SERVICE = 2
    API_METHOD = 3
    API_TOO_MANY_CALLS = 4
    API_PERMISSION_DENIED = 10
    API_USER_TOO_MANY_CALLS = 17
    PAGE_RATE_LIMIT_REACHED = 32
    ACCESS_TOKEN_EXPIRED = 190
    APPLICATION_LIMIT_REACHED = 341
    APPLICATION_BLOCKED_TEMP = 368
    CUSTOM_RATE_LIMIT_REACHED = 613
