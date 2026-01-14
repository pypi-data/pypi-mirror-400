from cdpify.generator.generators.base import TypeAwareGenerator
from cdpify.generator.generators.utils import (
    format_docstring,
    map_cdp_type,
    to_pascal_case,
    to_snake_case,
)
from cdpify.generator.models import Command, Domain, Parameter


class CommandsGenerator(TypeAwareGenerator):
    def generate(self, domain: Domain) -> str:
        self._reset_tracking()
        self._uses_type_checking = False

        self._scan_commands(domain)

        command_enum = self._generate_command_enum(domain)
        command_models = self._generate_command_models(domain)

        sections = [
            self._header(),
            self._imports(bool(command_models)),
        ]

        if self._cross_domain_refs:
            sections.append(self._cross_domain_imports())

        if command_enum:
            sections.append(command_enum)

        sections.append(command_models if command_models else "# No commands defined")

        return "\n\n".join(sections)

    def _scan_commands(self, domain: Domain) -> None:
        for command in domain.commands:
            self._scan_command_parameters(command)
            self._scan_command_returns(command)

    def _scan_command_parameters(self, command: Command) -> None:
        if not command.parameters:
            return

        for param in command.parameters:
            self._scan_parameter(param)

    def _scan_command_returns(self, command: Command) -> None:
        if not command.returns:
            return

        for param in command.returns:
            self._scan_parameter(param)

    def _imports(self, has_models: bool) -> str:
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
        return self._build_cross_domain_imports(use_type_checking=False)

    def _generate_command_enum(self, domain: Domain) -> str:
        if not domain.commands:
            return ""

        class_name = f"{domain.domain}Command"
        lines = [f"class {class_name}(StrEnum):"]

        for command in domain.commands:
            enum_name = self._to_enum_name(command.name)
            command_value = f"{domain.domain}.{command.name}"
            lines.append(f'    {enum_name} = "{command_value}"')

        return "\n".join(lines)

    def _to_enum_name(self, name: str) -> str:
        snake = to_snake_case(name)
        return snake.upper()

    def _generate_command_models(self, domain: Domain) -> str:
        if not domain.commands:
            return ""

        models = []
        for command in domain.commands:
            if command.parameters:
                models.append(self._create_params_model(command))
            if command.returns:
                models.append(self._create_returns_model(command))

        return "\n\n".join(models)

    def _create_params_model(self, command: Command) -> str:
        class_name = f"{to_pascal_case(command.name)}Params"

        lines = ["@dataclass(kw_only=True)"]
        lines.append(f"class {class_name}(CDPModel):")

        if command.description:
            doc = format_docstring(command.description, indent=4)
            lines.extend(doc.rstrip().splitlines())

        for param in command.parameters:
            lines.append(f"    {self._create_field(param)}")

        return "\n".join(lines)

    def _create_returns_model(self, command: Command) -> str:
        class_name = f"{to_pascal_case(command.name)}Result"

        lines = ["@dataclass(kw_only=True)"]
        lines.append(f"class {class_name}(CDPModel):")

        for param in command.returns:
            lines.append(f"    {self._create_field(param)}")

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
