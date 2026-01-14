# Just here to save some boiler, recursive JSON structure is difficult in mypy:
# https://github.com/python/typing/issues/182
from typing import Any, Optional, Type, Union

from .exceptions import GraphAPIError

JSONTypeSimple = dict[str, Any]
GraphAPIErrorClassType = Type[GraphAPIError]
ErrorCodeExceptionMap = dict[tuple[int, Optional[int]], GraphAPIErrorClassType]
GraphAPIQueryResult = Union[JSONTypeSimple, list[JSONTypeSimple]]
