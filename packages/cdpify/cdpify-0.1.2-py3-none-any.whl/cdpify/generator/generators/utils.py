import re

from cdpify.generator.models import Parameter


def map_cdp_type(param: Parameter) -> str:
    base_type = _get_base_type(param)

    if param.enum:
        base_type = _create_enum_literal(param.enum)

    if param.optional:
        return _make_optional(base_type)

    return base_type


_CAMEL_PATTERN_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_PATTERN_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake_case(name: str) -> str:
    """
    Convert camelCase/PascalCase to snake_case with proper acronym handling.

    Examples:
        setSPCTransactionMode → set_spc_transaction_mode
        getDOMNode → get_dom_node
        parseHTML → parse_html
        AXTree → ax_tree
        getSSLCertificate → get_ssl_certificate
    """
    s1 = _CAMEL_PATTERN_1.sub(r"\1_\2", name)
    s2 = _CAMEL_PATTERN_2.sub(r"\1_\2", s1)
    return s2.lower()


def to_pascal_case(name: str) -> str:
    if not name:
        return name

    return name[0].upper() + name[1:]


def format_docstring(text: str, indent: int = 4) -> str:
    if not text:
        return ""

    indent_str = " " * indent
    max_length = 88 - indent

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1
        if current_length + word_length > max_length and current_line:
            lines.append(indent_str + " ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += word_length

    if current_line:
        lines.append(indent_str + " ".join(current_line))

    result = [f'{indent_str}"""']
    result.extend(lines)
    result.append(f'{indent_str}"""')

    return "\n".join(result)


def _get_base_type(param: Parameter) -> str:
    if param.ref:
        return param.ref

    if param.type in _BASIC_TYPE_MAPPING:
        return _BASIC_TYPE_MAPPING[param.type]

    if param.type == "array":
        return _create_array_type(param.items)

    return "Any"


def _create_enum_literal(enum_values: list[str]) -> str:
    quoted_values = ", ".join(f'"{value}"' for value in enum_values)
    return f"Literal[{quoted_values}]"


def _make_optional(type_annotation: str) -> str:
    return f"{type_annotation} | None"


def _create_array_type(items: dict | None) -> str:
    if not items:
        return "list[Any]"

    item_type = _get_array_item_type(items)
    return f"list[{item_type}]"


def _get_array_item_type(item_spec: dict) -> str:
    if "$ref" in item_spec:
        ref = item_spec["$ref"]
        if "." in ref:
            parts = ref.split(".")
            return f"{parts[0].lower()}.{parts[1]}"
        return ref

    if "type" in item_spec:
        return _BASIC_TYPE_MAPPING.get(item_spec["type"], "Any")

    return "Any"


_BASIC_TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "object": "dict[str, Any]",
    "any": "Any",
}
