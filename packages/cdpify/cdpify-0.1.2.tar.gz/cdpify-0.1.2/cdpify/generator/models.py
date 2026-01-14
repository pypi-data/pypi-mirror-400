from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProtocolVersion(BaseModel):
    major: str
    minor: str


class Parameter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    type: str | None = None
    ref: str | None = Field(None, alias="$ref")
    optional: bool = False
    description: str | None = None
    enum: list[str] | None = None
    items: dict[str, Any] | None = None


class Command(BaseModel):
    name: str
    description: str | None = None
    parameters: list[Parameter] = []
    returns: list[Parameter] = []
    experimental: bool = False
    deprecated: bool = False


class Event(BaseModel):
    name: str
    description: str | None = None
    parameters: list[Parameter] = []
    experimental: bool = False
    deprecated: bool = False


class TypeDefinition(BaseModel):
    id: str
    type: str
    description: str | None = None
    enum: list[str] | None = None
    properties: list[Parameter] = []
    items: dict[str, Any] | None = None


class Domain(BaseModel):
    domain: str
    description: str | None = None
    experimental: bool = False
    deprecated: bool = False
    dependencies: list[str] = []
    types: list[TypeDefinition] = []
    commands: list[Command] = []
    events: list[Event] = []


class ProtocolSpec(BaseModel):
    version: ProtocolVersion
    domains: list[Domain]


class CDPSpecs(BaseModel):
    browser: ProtocolSpec
    js: ProtocolSpec

    @property
    def all_domains(self) -> list[Domain]:
        return self.browser.domains + self.js.domains

    @property
    def version_string(self) -> str:
        return f"{self.browser.version.major}.{self.browser.version.minor}"

    def get_domain(self, name: str) -> Domain | None:
        for domain in self.all_domains:
            if domain.domain == name:
                return domain
        return None
