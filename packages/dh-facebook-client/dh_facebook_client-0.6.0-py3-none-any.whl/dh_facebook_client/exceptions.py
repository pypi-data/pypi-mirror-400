from typing import TYPE_CHECKING, Any, Final, Optional, Set, Union
from urllib.parse import parse_qs, urlencode, urlsplit

from requests import Response

from .constants import GRAPH_API_VERSIONS

if TYPE_CHECKING:
    from .dataclasses import GraphAPIRequestParams


class InvalidAccessToken(Exception):
    """
    Raised if invalid access token supplied to Client
    """

    def __init__(self) -> None:
        self.message = 'Invalid access token: must be of type str'

    def __str__(self) -> str:  # pragma: no cover
        return self.message


class InvalidGraphAPIVersion(Exception):
    """
    Raised if invalid version supplied to Client
    """

    def __init__(self, version: Any) -> None:
        self.message = (
            f'Invalid Graph API version: {version}. '
            f'Available versions: {", ".join(GRAPH_API_VERSIONS)}'
        )

    def __str__(self) -> str:  # pragma: no cover
        return self.message


class GraphAPIBatchRequestLimitReached(ValueError):
    """
    Raised if batch request limit reached
    """

    def __init__(self) -> None:
        self.message = 'Batch request limit reached'

    def __str__(self) -> str:  # pragma: no cover
        return self.message


class GraphAPIResponseNotReady(ValueError):
    pass


class GraphAPIError(Exception):
    """
    Encapsulate Graph API & HTTP error data. Raised when error response
    detected from Graph API
    """

    SENSITIVE_FIELD_MASK: Final = '*****'
    DEFAULT_PARAMS_TO_MASK: Final = ['access_token']
    DETAIL_NOT_FOUND_PLACEHOLDER: Final = '<not_found>'

    def __init__(
        self,
        response: Response,
        error_details: dict[str, Union[str, int]],
        params_to_mask: Optional[list[str]] = None,
        request_params: Optional['GraphAPIRequestParams'] = None,
    ) -> None:
        """
        Scrapes Graph API error body and HTTP response
        :param response: An instance of requests.Response encapsulating the graph API call
        :param error_details: Parsed error details / body from Graph API,
            this is done ahead of time in Client
        :param params_to_mask: A list of additional query params to mask in error messages
        :param request_params: Optional sub-request params for batch requests, used to
            override path/query params extracted from the batch response URL
        """
        super().__init__(response, error_details, params_to_mask)
        self.status_code = response.status_code
        self.reason = response.reason
        self.fb_error_msg = error_details.get('message', GraphAPIError.DETAIL_NOT_FOUND_PLACEHOLDER)
        self.type = error_details.get('type', GraphAPIError.DETAIL_NOT_FOUND_PLACEHOLDER)
        self.code = error_details.get('code', GraphAPIError.DETAIL_NOT_FOUND_PLACEHOLDER)
        self.subcode = error_details.get(
            'error_subcode', GraphAPIError.DETAIL_NOT_FOUND_PLACEHOLDER
        )
        self.fbtrace_id = error_details.get(
            'fbtrace_id', GraphAPIError.DETAIL_NOT_FOUND_PLACEHOLDER
        )

        if request_params:
            self.path = request_params.path
            query = urlencode(request_params.params) if request_params.params else ''
        else:
            split_url = urlsplit(response.url)
            self.path = split_url.path
            query = split_url.query

        # Ensure default param masks are always set
        self.sanitized_query_params = GraphAPIError._sanitize_query_params(
            query,
            set(GraphAPIError.DEFAULT_PARAMS_TO_MASK + (params_to_mask or [])),
        )

        self.message = (
            f'{self.fb_error_msg}\n'
            '[Debug Info]\n'
            f'Type: {self.type}\n'
            f'Code: {self.code}\n'
            f'Subcode: {self.subcode}\n'
            f'Trace ID: {self.fbtrace_id}\n'
            '[HTTP Info]\n'
            f'Status Code: {self.status_code} | {self.reason}\n'
            f'Path: {self.path}\n'
            f'Query Params: {self.sanitized_query_params}'
        )

    def __str__(self) -> str:  # pragma: no cover
        return self.message

    @staticmethod
    def _sanitize_query_params(query: str, params_to_mask: Set[str]) -> dict[str, list[str]]:
        """
        Process query params present on request that was sent and mask sensitive fields
        :param response: Response to pull query params from
        :param params_to_mask: The parameters that should have their values masked
        :return: Transformed query params dict where sensitive params are masked
        """
        parsed_params = parse_qs(query)
        for param in params_to_mask:
            if param in parsed_params:
                parsed_params[param] = [
                    GraphAPIError.SENSITIVE_FIELD_MASK for _ in parsed_params[param]
                ]
        return parsed_params


class GraphAPITokenError(GraphAPIError):
    """
    Raised if a token issue occurs
    """

    pass


class GraphAPIServiceError(GraphAPIError):
    """
    Raised if an unknown API error occurs
    """

    pass


class GraphAPIApplicationError(GraphAPIError):
    """
    Raised if there's an issue with the developer application associated with a token
    """

    pass


class GraphAPIUsageError(GraphAPIError):
    """
    Raised if the developer application is rate limited or throttled
    """

    pass


class GraphAPIUserError(GraphAPIError):
    """
    Raised if there's an issue with the user account associated with a token
    """

    pass


class GraphAPIBatchRequestTimeoutError(GraphAPIError):
    """
    Raised if there's an timeout of one of the batch requests
    """

    pass


class GraphAPIGatewayError(GraphAPIError):
    """
    Raised if there's an issue with the gateway
    """

    pass
