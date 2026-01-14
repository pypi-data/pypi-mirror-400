from cdpify.generator.generators.base import TypeAwareGenerator
from cdpify.generator.generators.utils import (
    format_docstring,
    map_cdp_type,
    to_pascal_case,
    to_snake_case,
)
from cdpify.generator.models import Command, Domain, Parameter


class ClientGenerator(TypeAwareGenerator):
    def generate(self, domain: Domain) -> str:
        self._reset_tracking()
        self._scan_commands(domain)

        sections = [
            self._header(),
            self._imports(domain),
            self._client_class(domain),
        ]

        return "\n\n".join(sections)

    def _scan_commands(self, domain: Domain) -> None:
        for command in domain.commands:
            if not command.returns:
                self._uses_any = True

            if not command.parameters:
                continue

            for param in command.parameters:
                self._scan_parameter(param)
                self._track_type_usage(map_cdp_type(param))

    def _imports(self, domain: Domain) -> str:
        if self._cross_domain_refs:
            self._build_cross_domain_imports(use_type_checking=True)

        lines = [
            "from __future__ import annotations",
            "",
        ]

        # Build typing imports dynamically
        typing_imports = ["TYPE_CHECKING"]
        if self._uses_any:
            typing_imports.append("Any")
        if self._uses_literal:
            typing_imports.append("Literal")

        lines.append(f"from typing import {', '.join(typing_imports)}")
        lines.append("")
        lines.append("if TYPE_CHECKING:")
        lines.append("    from cdpify.client import CDPClient")
        lines.append("")

        # Add deprecated decorator import if needed
        if self._has_deprecated_commands(domain):
            lines.append("from cdpify.shared.decorators import deprecated")
            lines.append("")

        if domain.commands:
            lines.extend(self._build_command_imports(domain))

            type_imports = self._build_type_imports()
            if type_imports:
                lines.append(type_imports)
                lines.append("")

            if self._cross_domain_refs:
                lines.append(self._cross_domain_imports())

        return "\n".join(lines)

    def _has_deprecated_commands(self, domain: Domain) -> bool:
        """Check if domain has any deprecated commands."""
        return any(getattr(cmd, "deprecated", False) for cmd in domain.commands)

    def _build_command_imports(self, domain: Domain) -> list[str]:
        param_classes = {
            f"{to_pascal_case(cmd.name)}Params"
            for cmd in domain.commands
            if cmd.parameters
        }
        return_classes = {
            f"{to_pascal_case(cmd.name)}Result"
            for cmd in domain.commands
            if cmd.returns
        }

        all_classes = sorted(param_classes | return_classes)

        command_enum = f"{domain.domain}Command"
        all_classes.insert(0, command_enum)

        lines = ["from .commands import ("]
        for cls in all_classes:
            lines.append(f"    {cls},")
        lines.append(")")
        lines.append("")

        return lines

    def _cross_domain_imports(self) -> str:
        return self._build_cross_domain_imports(use_type_checking=True)

    def _client_class(self, domain: Domain) -> str:
        class_name = f"{domain.domain}Client"

        lines = [f"class {class_name}:"]
        lines.append("    def __init__(self, client: CDPClient) -> None:")
        lines.append("        self._client = client")

        for command in domain.commands:
            lines.append("")
            lines.append(self._generate_method(command, domain.domain))

        return "\n".join(lines)

    def _generate_method(self, command: Command, domain_name: str) -> str:
        method_name = to_snake_case(command.name)

        params = self._build_params(command)
        return_type = self._get_return_type(command)
        method_body = self._build_method_body(command, domain_name)

        lines = []

        # Add deprecated decorator if command is deprecated
        if getattr(command, "deprecated", False):
            lines.append(self._build_deprecated_decorator(command))

        lines.append(f"    async def {method_name}(")

        for param in params:
            lines.append(f"        {param},")

        lines.append(f"    ) -> {return_type}:")

        if command.description:
            doc = format_docstring(command.description, indent=8)
            lines.extend(doc.rstrip().splitlines())

        lines.extend(f"        {line}" for line in method_body)

        return "\n".join(lines)

    def _build_deprecated_decorator(self, command: Command) -> str:
        return "    @deprecated()"

    def _build_params(self, command: Command) -> list[str]:
        params = ["self"]

        if not command.parameters:
            params.append("session_id: str | None = None")
            return params

        params.append("*")

        for param in command.parameters:
            param_signature = self._build_param_signature(command, param)
            params.append(param_signature)

        params.append("session_id: str | None = None")
        return params

    def _build_param_signature(self, command: Command, param: Parameter) -> str:
        param_name = self._resolve_param_name(command, param)
        base_type = self._resolve_base_param_type(param)

        if param.optional:
            return f"{param_name}: {base_type} | None = None"
        return f"{param_name}: {base_type}"

    def _resolve_param_name(self, command: Command, param: Parameter) -> str:
        param_name = to_snake_case(param.name)

        if param_name == "session_id":
            return f"{to_snake_case(command.name)}_session_id"

        return param_name

    def _resolve_base_param_type(self, param: Parameter) -> str:
        # Resolve type with proper cross-domain formatting (lowercase domain)
        if param.ref and "." in param.ref:
            parts = param.ref.split(".")
            domain_lower = parts[0].lower()
            type_name = parts[1]
            param_type = f"{domain_lower}.{type_name}"
        else:
            param_type = map_cdp_type(param)

        self._track_type_usage(param_type)
        return param_type.removesuffix(" | None")

    def _build_method_body(self, command: Command, domain_name: str) -> list[str]:
        lines = []

        if command.parameters:
            lines.extend(self._build_params_construction(command))
            lines.append("")
            lines.extend(self._build_send_with_params(command, domain_name))
        else:
            lines.extend(self._build_send_without_params(command, domain_name))

        lines.extend(self._build_return_statement(command))
        return lines

    def _build_params_construction(self, command: Command) -> list[str]:
        param_class = f"{to_pascal_case(command.name)}Params"

        constructor_args = ", ".join(
            f"{to_snake_case(param.name)}={self._resolve_param_name(command, param)}"
            for param in command.parameters
        )

        return [f"params = {param_class}({constructor_args})"]

    def _to_enum_name(self, name: str) -> str:
        snake = to_snake_case(name)
        return snake.upper()

    def _build_send_with_params(self, command: Command, domain_name: str) -> list[str]:
        enum_ref = f"{domain_name}Command.{self._to_enum_name(command.name)}"
        return [
            "result = await self._client.send_raw(",
            f"    method={enum_ref},",
            "    params=params.to_cdp_params(),",
            "    session_id=session_id,",
            ")",
        ]

    def _build_send_without_params(
        self, command: Command, domain_name: str
    ) -> list[str]:
        enum_ref = f"{domain_name}Command.{self._to_enum_name(command.name)}"
        return [
            "result = await self._client.send_raw(",
            f"    method={enum_ref},",
            "    params=None,",
            "    session_id=session_id,",
            ")",
        ]

    def _build_return_statement(self, command: Command) -> list[str]:
        if command.returns:
            result_class = f"{to_pascal_case(command.name)}Result"
            return [f"return {result_class}.from_cdp(result)"]
        return ["return result"]

    def _get_return_type(self, command: Command) -> str:
        if command.returns:
            return f"{to_pascal_case(command.name)}Result"

        self._uses_any = True
        return "dict[str, Any]"
