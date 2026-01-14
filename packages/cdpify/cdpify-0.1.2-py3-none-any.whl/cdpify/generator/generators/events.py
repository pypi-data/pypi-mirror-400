from cdpify.generator.generators.base import TypeAwareGenerator
from cdpify.generator.generators.utils import (
    format_docstring,
    map_cdp_type,
    to_pascal_case,
    to_snake_case,
)
from cdpify.generator.models import Domain, Event, Parameter


class EventsGenerator(TypeAwareGenerator):
    def generate(self, domain: Domain) -> str:
        self._reset_tracking()
        self._scan_events(domain)

        event_enum = self._generate_event_enum(domain)
        event_models = self._generate_event_models(domain)

        sections = [self._header()]

        if event_models:
            sections.append(self._imports())

        if self._cross_domain_refs:
            sections.append(self._cross_domain_imports())

        if event_enum:
            sections.append(event_enum)

        sections.append(event_models if event_models else "# No events defined")

        return "\n\n".join(sections)

    def _scan_events(self, domain: Domain) -> None:
        for event in domain.events:
            self._scan_event_parameters(event)

    def _scan_event_parameters(self, event: Event) -> None:
        if not event.parameters:
            return

        for param in event.parameters:
            self._scan_parameter(param)

    def _imports(self) -> str:
        # Pre-build cross-domain imports to set TYPE_CHECKING flag
        if self._cross_domain_refs:
            self._build_cross_domain_imports(use_type_checking=True)

        lines = []

        typing_imports = self._build_typing_imports()
        if typing_imports:
            lines.append(typing_imports)

        lines.append("from dataclasses import dataclass")
        lines.append("from enum import StrEnum")
        lines.append("from cdpify.domains.shared import CDPModel")

        type_imports = self._build_type_imports()
        if type_imports:
            lines.append("")
            lines.append(type_imports)

        return "\n".join(lines)

    def _cross_domain_imports(self) -> str:
        return self._build_cross_domain_imports(use_type_checking=True)

    def _generate_event_enum(self, domain: Domain) -> str:
        if not domain.events:
            return ""

        class_name = f"{domain.domain}Event"
        lines = [f"class {class_name}(StrEnum):"]

        for event in domain.events:
            enum_name = self._to_enum_name(event.name)
            event_value = f"{domain.domain}.{event.name}"
            lines.append(f'    {enum_name} = "{event_value}"')

        return "\n".join(lines)

    def _to_enum_name(self, name: str) -> str:
        snake = to_snake_case(name)
        return snake.upper()

    def _generate_event_models(self, domain: Domain) -> str:
        if not domain.events:
            return ""

        return "\n\n".join(self._create_event_model(event) for event in domain.events)

    def _create_event_model(self, event: Event) -> str:
        class_name = f"{to_pascal_case(event.name)}Event"

        lines = ["@dataclass(kw_only=True)"]
        lines.append(f"class {class_name}(CDPModel):")

        if event.description:
            doc = format_docstring(event.description, indent=4)
            lines.extend(doc.rstrip().splitlines())

        if event.parameters:
            for param in event.parameters:
                lines.append(f"    {self._create_field(param)}")
        else:
            lines.append("    pass")

        return "\n".join(lines)

    def _create_field(self, param: Parameter) -> str:
        field_name = to_snake_case(param.name)
        py_type = self._resolve_type(param)

        self._track_type_usage(py_type)

        if param.optional:
            return f"{field_name}: {py_type} | None = None"
        return f"{field_name}: {py_type}"

    def _resolve_type(self, param: Parameter) -> str:
        if param.ref and "." in param.ref:
            parts = param.ref.split(".")
            domain_lower = parts[0].lower()
            type_name = parts[1]
            return f"{domain_lower}.{type_name}"

        return map_cdp_type(param)
