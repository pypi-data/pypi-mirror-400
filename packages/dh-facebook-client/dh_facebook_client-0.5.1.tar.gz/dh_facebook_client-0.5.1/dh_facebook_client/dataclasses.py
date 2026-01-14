from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, TypeVar

from requests import Response

from dh_facebook_client.exceptions import GraphAPIError, GraphAPIResponseNotReady

from .helpers import NameValuePair, deserialize_json_header, deserialize_list
from .typings import GraphAPIQueryResult, JSONTypeSimple

T = TypeVar('T', bound='GraphAPIResponse')


@dataclass(frozen=True)
class BaseUsageDetails:
    call_count: int
    total_time: int
    total_cputime: int


@dataclass(frozen=True)
class AppUsageDetails(BaseUsageDetails):
    """
    Encapsulates stats from X-App-Usage header:
    https://developers.facebook.com/docs/graph-api/overview/rate-limiting#headers
    """

    _HEADER_NAME: ClassVar[str] = 'X-App-Usage'

    @classmethod
    def from_list(cls, headers: Iterable[NameValuePair]) -> AppUsageDetails:
        app_usage_dict = deserialize_list(headers, cls._HEADER_NAME)
        return cls.from_usage_dict(app_usage_dict)

    @classmethod
    def from_header(cls, res: Response) -> AppUsageDetails:
        app_usage_dict = deserialize_json_header(res, cls._HEADER_NAME)
        return cls.from_usage_dict(app_usage_dict)

    @classmethod
    def from_usage_dict(cls, usage_dict: dict) -> AppUsageDetails:
        return cls(
            call_count=usage_dict.get('call_count', 0),
            total_time=usage_dict.get('total_time', 0),
            total_cputime=usage_dict.get('total_cputime', 0),
        )


@dataclass(frozen=True)
class BusinessUseCaseUsageDetails(BaseUsageDetails):
    """
    Encapsulates stats from X-Business-Use-Case-Usage header:
    https://developers.facebook.com/docs/graph-api/overview/rate-limiting#headers-2
    """

    _HEADER_NAME: ClassVar[str] = 'X-Business-Use-Case-Usage'

    type: str | None
    estimated_time_to_regain_access: int

    @classmethod
    def from_list(cls, headers: Iterable[NameValuePair]) -> dict[str, BusinessUseCaseUsageDetails]:
        buc_usage_dict = deserialize_list(headers, cls._HEADER_NAME)
        return cls.from_usage_dict(buc_usage_dict)

    @classmethod
    def from_header(cls, res: Response) -> dict[str, BusinessUseCaseUsageDetails]:
        buc_usage_dict = deserialize_json_header(res, cls._HEADER_NAME)
        return cls.from_usage_dict(buc_usage_dict)

    @classmethod
    def from_usage_dict(cls, buc_usage_dict: dict) -> dict[str, BusinessUseCaseUsageDetails]:
        return_dict = {}
        for id_, usage_dicts in buc_usage_dict.items():
            if not (usage_dict := next(iter(usage_dicts), None)):
                continue
            time_to_regain_access = usage_dict.get('estimated_time_to_regain_access') or 0
            return_dict[id_] = cls(
                type=usage_dict.get('type'),
                estimated_time_to_regain_access=time_to_regain_access,
                call_count=usage_dict.get('call_count', 0),
                total_time=usage_dict.get('total_time', 0),
                total_cputime=usage_dict.get('total_cputime', 0),
            )
        return return_dict


@dataclass(frozen=True)
class MarketingAPIThrottleInsights:
    """
    Encapsulates stats from X-Fb-Ads-Insights-Throttle header:
    https://developers.facebook.com/docs/marketing-api/insights/best-practices/#insightscallload
    """

    _HEADER_NAME: ClassVar[str] = 'X-Fb-Ads-Insights-Throttle'

    app_id_util_pct: float
    acc_id_util_pct: float
    ads_api_access_tier: str

    @classmethod
    def from_list(cls, headers: Iterable[NameValuePair]) -> MarketingAPIThrottleInsights:
        throttle_insights_dict = deserialize_list(headers, cls._HEADER_NAME)
        return cls.from_usage_dict(throttle_insights_dict)

    @classmethod
    def from_header(cls, res: Response) -> MarketingAPIThrottleInsights:
        throttle_insights_dict = deserialize_json_header(res, cls._HEADER_NAME)
        return cls.from_usage_dict(throttle_insights_dict)

    @classmethod
    def from_usage_dict(cls, throttle_insights_dict: dict) -> MarketingAPIThrottleInsights:
        return cls(
            app_id_util_pct=throttle_insights_dict.get('app_id_util_pct', 0.0),
            acc_id_util_pct=throttle_insights_dict.get('acc_id_util_pct', 0.0),
            ads_api_access_tier=throttle_insights_dict.get('ads_api_access_tier', ''),
        )


@dataclass(frozen=True)
class GraphAPIRequestParams:
    """
    Encapsulates Graph API request params
    """

    method: str
    path: str
    params: Optional[dict] = None
    data: Optional[Any] = None


@dataclass
class GraphAPIResponse:
    """
    Encapsulates a Graph API response payload with parsed app usage headers
    """

    request_params: GraphAPIRequestParams

    app_usage_details: AppUsageDetails | None = None
    business_use_case_usage_details: dict[str, BusinessUseCaseUsageDetails] | None = None
    marketing_api_throttle_insights: MarketingAPIThrottleInsights | None = None

    raw_data: GraphAPIQueryResult | list[GraphAPIResponse] | None = None
    paging: Optional[JSONTypeSimple] = None

    error: Optional[GraphAPIError] = None

    def set_usage_details(self, headers: Iterable[NameValuePair]) -> None:
        self.app_usage_details = AppUsageDetails.from_list(headers)
        self.business_use_case_usage_details = BusinessUseCaseUsageDetails.from_list(headers)
        self.marketing_api_throttle_insights = MarketingAPIThrottleInsights.from_list(headers)

    def set_result(
        self,
        data: GraphAPIQueryResult | list[GraphAPIResponse],
        paging: Optional[JSONTypeSimple] = None,
    ) -> None:
        self.raw_data = data
        self.paging = paging

    def set_exception(self, error: GraphAPIError) -> None:
        self.error = error

    @property
    def is_ready(self) -> bool:
        return self.raw_data is not None or self.error is not None

    @property
    def data(self) -> GraphAPIQueryResult | list[GraphAPIResponse]:
        if self.error:
            raise self.error
        if self.raw_data is None:
            raise GraphAPIResponseNotReady('data is not set yet')
        return self.raw_data

    @property
    def is_empty(self) -> bool:
        return not self.data

    @property
    def is_list(self) -> bool:
        return isinstance(self.data, list)

    @property
    def is_dict(self) -> bool:
        return isinstance(self.data, dict)

    @property
    def before_cursor(self) -> Optional[str]:
        return self.cursors.get('before')

    @property
    def after_cursor(self) -> Optional[str]:
        return self.cursors.get('after')

    @property
    def next_page_url(self) -> Optional[str]:
        return self.paging.get('next') if self.paging else None

    @property
    def cursors(self) -> JSONTypeSimple:
        return self.paging.get('cursors', {}) if self.paging else {}

    @property
    def is_batch(self) -> bool:
        if not isinstance(self.data, list) or not self.data:
            return False
        return isinstance(self.data[0], GraphAPIResponse)
