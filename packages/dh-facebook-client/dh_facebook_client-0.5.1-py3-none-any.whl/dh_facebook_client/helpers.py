import json
from typing import Any, Final, Iterable, Optional

import requests
from typing_extensions import NotRequired, TypedDict

# TODO: Recursive type hints not yet available in mypy,
#  should change sub_fields hint to Optional[List[FieldConfig]] when possible:
#  https://github.com/python/mypy/issues/731
FieldConfig = TypedDict(
    'FieldConfig',
    {
        'field_name': str,
        'limit': NotRequired[int],
        'after': NotRequired[str],
        'username': NotRequired[str],
        'date_preset': NotRequired[str],
        'sub_fields': NotRequired[list[Any]],
    },
)


class NameValuePair(TypedDict):
    name: str
    value: str


ACCEPTED_SUB_PARAM_NAMES: Final = (
    'limit',
    'after',
    'date_preset',
    'breakdowns',
    'metric',
    'username',
)


def build_field_config_list(field_literals: Iterable[str]) -> list[FieldConfig]:
    """
    Helper function to convert iterables containing field literals into FieldConfig objects
        for use with format_fields_str
    :param field_literals: An iterable containing a Graph API field literal (i.e. ['foo']).
    :return: A list containing respective FieldConfig objects (i.e. [{'field_name': 'foo'}]).
    """
    return [{'field_name': f} for f in field_literals]


def format_fields_str(fields_config: list[FieldConfig]) -> str:
    """
    Helper function to support field expansion / limiting functionality:
    https://developers.facebook.com/docs/graph-api/field-expansion
    :param fields_config: The field configurations you want contained in string format
    :return: A formatted fields string
    """
    fields_str = ''
    for config in fields_config:
        # Prep the base sub string for a field w/ params (i.e. foo.limit(5).after(BAR))
        fields_str += f'{config["field_name"]}'
        for param_name in ACCEPTED_SUB_PARAM_NAMES:
            fields_str += _format_sub_parameter_str(config, param_name)
        # If sub-fields exist, prep the nested sub-field(s) strings
        sub_fields = config.get('sub_fields')
        if sub_fields:
            fields_str += f'{{{format_fields_str(sub_fields)}}}'

        # If not the last item in a config list, add a comma separator
        if config != fields_config[-1]:
            fields_str += ','
    return fields_str


def _format_sub_parameter_str(config: FieldConfig, param_name: str) -> str:
    """
    Used to help format sub-param strings for a specific field:
    Ex: https://developers.facebook.com/docs/graph-api/field-expansion#limiting-results
    :param config: An instance of FieldConfig
    :param param_name: The parameter name to pluck from config (i.e. limit or after)
    :return: A formatted paging sub string (i.e. .limit(5))
    """
    if not (param := config.get(param_name)):
        return ''
    if isinstance(param, (list, set)):
        param = ','.join(param)
    return f'.{param_name}({param})'


def deserialize_json_header(res: requests.Response, header_name: str) -> dict:
    header_val = res.headers.get(header_name)
    return _safe_deserialize(header_val)


def deserialize_list(value_list: Iterable[NameValuePair], name: str) -> dict:
    value = next((r['value'] for r in value_list if r['name'].lower() == name.lower()), None)
    return _safe_deserialize(value)


def _safe_deserialize(value: Optional[str]) -> dict:
    return json.loads(value) if value else {}
