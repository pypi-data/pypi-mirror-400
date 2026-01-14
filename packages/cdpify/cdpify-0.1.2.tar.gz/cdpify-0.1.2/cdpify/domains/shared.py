import re
from dataclasses import asdict, dataclass, fields
from cdpify.generator.generators.utils import to_snake_case
from typing import Any, Self


_ACRONYMS = frozenset(
    {
        "api",
        "css",
        "dom",
        "html",
        "id",
        "json",
        "pdf",
        "spc",
        "ssl",
        "url",
        "uuid",
        "xml",
        "xhr",
        "ax",
        "cpu",
        "gpu",
        "io",
        "js",
        "os",
        "ui",
        "uri",
        "usb",
        "wasm",
        "http",
        "https",
    }
)


def _to_camel(s: str) -> str:
    parts = s.split("_")

    if not parts:
        return s

    result = [parts[0].lower()]

    for part in parts[1:]:
        lower = part.lower()
        result.append(part.upper() if lower in _ACRONYMS else part.capitalize())

    return "".join(result)


def _to_snake(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


@dataclass
class CDPModel:
    def to_cdp_params(self) -> dict[str, Any]:
        return {_to_camel(k): v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_cdp(cls, data: dict) -> Self:
        snake_data = {_to_snake(k): v for k, v in data.items()}
        valid_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in snake_data.items() if k in valid_fields})
