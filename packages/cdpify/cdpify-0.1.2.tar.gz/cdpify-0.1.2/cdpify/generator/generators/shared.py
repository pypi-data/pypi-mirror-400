import re
from dataclasses import asdict, dataclass, fields
from typing import Any, Self


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def to_snake(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


@dataclass
class CDPModel:
    def to_cdp_params(self) -> dict[str, Any]:
        return {to_camel(k): v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_cdp(cls, data: dict) -> Self:
        snake_data = {to_snake(k): v for k, v in data.items()}
        valid_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in snake_data.items() if k in valid_fields})
