from __future__ import annotations

import json
import logging
import urllib.parse
from collections.abc import Iterable
from contextlib import contextmanager
from copy import copy
from dataclasses import astuple
from http import HTTPStatus
from types import TracebackType
from typing import Any, Final, Generator, Optional, Type, TypeVar

import backoff
from requests import Response, Session
from requests.exceptions import JSONDecodeError

from .constants import GRAPH_API_URL, GRAPH_API_VERSIONS
from .dataclasses import (
    AppUsageDetails,
    BusinessUseCaseUsageDetails,
    GraphAPIRequestParams,
    GraphAPIResponse,
    MarketingAPIThrottleInsights,
)
from .error_code import GraphAPICommonErrorCode
from .exceptions import (
    GraphAPIApplicationError,
    GraphAPIBatchRequestLimitReached,
    GraphAPIBatchRequestTimeoutError,
    GraphAPIError,
    GraphAPIGatewayError,
    GraphAPIServiceError,
    GraphAPITokenError,
    GraphAPIUsageError,
    InvalidAccessToken,
    InvalidGraphAPIVersion,
)
from .typings import (
    ErrorCodeExceptionMap,
    GraphAPIErrorClassType,
    GraphAPIQueryResult,
    JSONTypeSimple,
)

logger = logging.getLogger(__name__)

BATCH_API_REQUESTS_LIMIT: Final = 50

Self = TypeVar('Self', bound='GraphAPIClient')


class GraphAPIClient:
    """
    A small client built to interact with the Facebook social graph:
    https://developers.facebook.com/docs/graph-api/overview

    This is currently built minimally for distribution in Dash Hudson
    services where JSON-based requests need to be handled.

    The following functionality is currently unsupported when
    comparing to the official facebook-sdk:
        - HMAC authentication
        - batch request handling
        - file uploading
        - generating oauth redirect urls

    For now API access is provisioned through access tokens,
    if you are unfamiliar with how this works see the following:
    https://developers.facebook.com/docs/facebook-login
    """

    DEFAULT_CODE_EXCEPTION_MAP: Final[ErrorCodeExceptionMap] = {
        (GraphAPICommonErrorCode.API_UNKNOWN.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_METHOD.value, None): GraphAPIServiceError,
        (GraphAPICommonErrorCode.API_PERMISSION_DENIED.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.APPLICATION_BLOCKED_TEMP.value, None): GraphAPIApplicationError,
        (GraphAPICommonErrorCode.API_SESSION.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.ACCESS_TOKEN_EXPIRED.value, None): GraphAPITokenError,
        (GraphAPICommonErrorCode.APPLICATION_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.API_TOO_MANY_CALLS.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.PAGE_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
        (GraphAPICommonErrorCode.CUSTOM_RATE_LIMIT_REACHED.value, None): GraphAPIUsageError,
    }

    def __init__(
        self,
        access_token: str,
        version: str,
        global_timeout: Optional[int] = None,
        params_to_mask: Optional[list[str]] = None,
        retry_params: Optional[dict] = None,
        disable_logger: Optional[bool] = False,
        code_exception_map: Optional[ErrorCodeExceptionMap] = None,
        loose_match_errors: Optional[bool] = False,
    ) -> None:
        """
        Initialize the API client
        :param access_token: An access token provisioned through Facebook login
        :param version: The Graph API version to use (ex: 12.0)
        :param global_timeout: A global request timeout to set
        :param params_to_mask: A list of query parameter names to mask when formatting
            exception messages
        :param disable_logger Disables exception logging if truthy
        :param retry_config Params for https://github.com/litl/backoff#backoffon_exception
        :param code_exception_map: A an error code -> exception map / configuration
        """
        if not access_token or not isinstance(access_token, str):
            raise InvalidAccessToken
        version = (
            version[1:] if isinstance(version, str) and version.lower().startswith('v') else version
        )
        if version not in GRAPH_API_VERSIONS:
            raise InvalidGraphAPIVersion(version)

        self.version = f'v{version}'
        self.global_timeout = global_timeout
        self.params_to_mask = params_to_mask
        self.disable_logger = disable_logger
        # Defaulting to max_tries=0 disables retrying by default
        self.retry_params = retry_params or {'exception': tuple(), 'max_tries': 0}

        self.code_exception_map = self.DEFAULT_CODE_EXCEPTION_MAP
        if code_exception_map:
            self.code_exception_map = {
                **self.DEFAULT_CODE_EXCEPTION_MAP,
                **code_exception_map,
            }

        self._access_token = access_token
        self._session = Session()
        self._session.params = {'access_token': self._access_token}

        self._loose_match_errors = loose_match_errors

        self._batch_mode: bool = False
        self._batch_auto_execute: bool = False
        self._batch_kwargs: dict[str, Any] = {}
        self._future_responses: list[GraphAPIResponse] = []

    def get(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse:
        """
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations)
        Performs a GET request to the Graph API
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='GET',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def get_all_pages(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> Generator[GraphAPIResponse, None, None]:
        """
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations)
        Performs a GET request to the Graph API
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An iterator containing paginated instances of GraphAPIResponse
        """
        params = copy(params) if params else {}
        params['after'] = None
        while True:
            res = self.get(path, params, timeout, retry_params, **kwargs)
            yield res
            if not res.after_cursor or not res.next_page_url:
                break
            params['after'] = res.after_cursor

    def get_all_pages_from_next_url(
        self,
        next_url: str,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> Generator[GraphAPIResponse, None, None]:
        _next_url = next_url
        while True:
            res = self._do_request(
                method='GET',
                full_url=_next_url,
                timeout=timeout,
                retry_params=retry_params,
                **kwargs,
            )
            yield res
            if not res.next_page_url:
                break
            _next_url = res.next_page_url

    def post(
        self,
        path: str,
        data: Any,
        params: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse:
        """
        Performs a POST request to the Graph API
        :param path: A path pointing to an edge or node
            (ex: /<page_id>/conversations | /<page_id>)
        :param data: The request body to be included
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='POST',
            path=path,
            params=params,
            data=data,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def delete(
        self,
        path: str,
        params: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse:
        """
        Performs a DELETE request to the Graph API
        :param path: A path pointing to a node
            (ex: /<video_id>)
        :param params: Query parameters to be included with the request
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """
        return self._do_request(
            method='DELETE',
            path=path,
            params=params,
            timeout=timeout,
            retry_params=retry_params,
            **kwargs,
        )

    def _do_request(
        self,
        method: str,
        path: str = '',
        full_url: str = '',
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        future_responses: Iterable[GraphAPIResponse] = (),
        **kwargs: Any,
    ) -> GraphAPIResponse:
        """
        Handle Graph API requests. Raise if error body detected and lets ambiguous network
        errors propagate.
        :param method: The HTTP request method
        :param path: A path pointing to an edge or node (ex: /<page_id>/conversations)
        :param params: Query parameters to be included with the request
        :param data: The request body to be included
        :param timeout: A custom timeout for the request (seconds)
        :param retry_params: Retry params override
        :return: An instance of GraphAPIResponse
        """

        if not future_responses and self._batch_mode:
            return self._register_batch_request(
                method, path, full_url, params, data, timeout, retry_params, **kwargs
            )

        @backoff.on_exception(backoff.expo, **(retry_params or self.retry_params))
        def _retry_parameterizer() -> GraphAPIResponse:
            if not path and not full_url:
                raise ValueError('either path or full_url must be specified')

            response = self._session.request(
                method=method,
                url=f'{GRAPH_API_URL}/{self.version}/{path}' if path else full_url,
                params=params,
                data=data,
                timeout=timeout or self.global_timeout,
            )
            result, paging = self._parse_response_body_or_raise(
                response, future_responses=future_responses
            )
            return GraphAPIResponse(
                request_params=GraphAPIRequestParams(method, path, params, data),
                app_usage_details=AppUsageDetails.from_header(response),
                business_use_case_usage_details=BusinessUseCaseUsageDetails.from_header(response),
                marketing_api_throttle_insights=MarketingAPIThrottleInsights.from_header(response),
                raw_data=result,
                paging=paging,
            )

        return _retry_parameterizer()

    def _register_batch_request(
        self,
        method: str,
        path: str = '',
        full_url: str = '',
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        retry_params: Optional[dict] = None,
        **kwargs: Any,
    ) -> GraphAPIResponse:
        if full_url:
            raise ValueError('Batch requests are not supported for full_url requests')
        if timeout is not None:
            raise ValueError('Batch requests do not support custom timeouts')
        if retry_params is not None:
            raise ValueError('Batch requests do not support retry_params')
        if kwargs:
            raise ValueError('Batch requests do not support additional kwargs')
        if self.queued_requests_count >= BATCH_API_REQUESTS_LIMIT:
            raise GraphAPIBatchRequestLimitReached
        future_response = GraphAPIResponse(GraphAPIRequestParams(method, path, params, data))
        self._future_responses.append(future_response)
        if self._batch_auto_execute and self.queued_requests_count == BATCH_API_REQUESTS_LIMIT:
            self.execute_batch(**self._batch_kwargs)
        return future_response

    @property
    def queued_requests_count(self) -> int:
        return len(self._future_responses)

    def _parse_response_body_or_raise(
        self, response: Response, *, future_responses: Iterable[GraphAPIResponse] = ()
    ) -> tuple[GraphAPIQueryResult | list[GraphAPIResponse], Optional[JSONTypeSimple]]:
        """
        Parse Graph API response body and raise if error details present
        :param response: A response from the Graph API
        :return: Parsed request body and optional paging params
        """
        try:
            if response.status_code in [HTTPStatus.BAD_GATEWAY, HTTPStatus.GATEWAY_TIMEOUT]:
                logger.exception('Meta API returned Bad Gateway error')
                raise GraphAPIGatewayError(
                    response, {'message': 'Meta API returned Bad Gateway error'}
                )
            response_body = response.json()
        except JSONDecodeError:
            logger.exception(f'Failed to parse response body: {response.text}')
            raise GraphAPIError(response, {'message': 'Failed to parse response body'})

        if future_responses and isinstance(response_body, list):
            return self._parse_batch_response_body(response, response_body, future_responses)

        if error_details := response_body.get('error'):
            exc = self._get_exc(error_details, response)
            if not self.disable_logger:
                logger.error(str(exc))
            raise exc

        return self._get_results_and_paging(response_body)

    def _get_results_and_paging(
        self, response_body: dict
    ) -> tuple[JSONTypeSimple, None] | tuple[list[JSONTypeSimple], JSONTypeSimple]:
        # If 'data' is present, it means the result is a list of graph nodes and may have
        # paging params as well
        if 'data' in response_body:
            return response_body['data'], response_body.get('paging')
        # If not, the response body is a single graph node without paging params
        return response_body, None

    def _parse_batch_response_body(
        self,
        response: Response,
        response_body: list[dict | None],
        future_responses: Iterable[GraphAPIResponse],
    ) -> tuple[list[GraphAPIResponse], None]:
        for item, future_response in zip(response_body, future_responses):
            if item is None:
                future_response.set_exception(
                    GraphAPIBatchRequestTimeoutError(response, {'message': 'Batch request timeout'})
                )
                continue

            if headers := item.get('headers'):
                future_response.set_usage_details(headers)

            try:
                parsed_body = json.loads(item['body'])
            except JSONDecodeError:
                logger.exception(f'Failed to parse batch response body: {item["body"]}')
                error_details: dict = {
                    'message': 'Failed to parse batch response body',
                    "code": item["code"],
                }
                future_response.set_exception(GraphAPIError(response, error_details))
                continue

            if error_details := parsed_body.get('error'):
                future_response.set_exception(
                    self._get_exc(error_details, response, future_response.request_params)
                )
            else:
                result, paging = self._get_results_and_paging(parsed_body)
                future_response.set_result(data=result, paging=paging)

        return list(future_responses), None

    def _get_exc(
        self,
        error_details: dict[str, Any],
        response: Response,
        request_params: Optional[GraphAPIRequestParams] = None,
    ) -> GraphAPIError:
        # Raise a specific exception if a code mapping is set, custom exceptions take priority
        exc_type = self._get_exc_type(error_details)
        # Log & raise default GraphAPIError if no mapping was found
        return exc_type(
            response=response,
            error_details=error_details,
            params_to_mask=self.params_to_mask,
            request_params=request_params,
        )

    def _get_exc_type(self, error_details: dict[str, Any]) -> GraphAPIErrorClassType:
        code_key: tuple[Any, Any] = (error_details.get('code'), error_details.get('error_subcode'))
        # Raise a specific exception if a code mapping is set, custom exceptions take priority
        if exc_type := self.code_exception_map.get(code_key):
            return exc_type
        # If no mapping was found, try to match loosely
        if self._loose_match_errors and code_key[1]:
            exc_type = self.code_exception_map.get((code_key[0], None))
        return exc_type or GraphAPIError

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._session.close()

    def reset_batch(self) -> None:
        """
        Resets the batch requests
        """

        self._future_responses = []

    @contextmanager
    def batch(
        self: Self, *, auto_execute: bool = True, **kwargs: Any
    ) -> Generator[Self, None, None]:
        old_batch_mode = self._batch_mode
        try:
            self._batch_mode = True
            self._batch_auto_execute = auto_execute
            self._batch_kwargs = kwargs
            yield self
        finally:
            self._batch_mode = old_batch_mode

        if self.queued_requests_count > 0 and auto_execute:
            self.execute_batch(**kwargs)

    def execute_batch(self, **kwargs: Any) -> GraphAPIResponse:
        """
        Executes a batch request using registered requests

        docs: https://developers.facebook.com/docs/graph-api/batch-requests/
        """
        if not self.queued_requests_count:
            raise ValueError('execute_batch called without any batch requests')

        batch: list[dict] = []
        for future_response in self._future_responses:
            method, path, params, data = astuple(future_response.request_params)
            params_string = urllib.parse.urlencode(params) if params else ''
            relative_url = f'{path}?{params_string}' if params_string else path
            req_data = {'method': method, 'relative_url': relative_url}
            if data and method in ('POST', 'PUT'):
                req_data['body'] = urllib.parse.urlencode(data)
            batch.append(req_data)

        future_responses: list[GraphAPIResponse] = self._future_responses
        self.reset_batch()

        return self._do_request(
            method='POST',
            path='.',
            data={'batch': json.dumps(batch)},
            future_responses=future_responses,
            **kwargs,
        )
