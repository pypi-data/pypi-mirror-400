from cdpify.generator.generators.base import BaseGenerator
from cdpify.generator.generators.utils import to_pascal_case
from cdpify.generator.models import Domain


class InitGenerator(BaseGenerator):
    def generate(self, domain: Domain) -> str:
        sections = [
            self._header(),
            self._module_docstring(domain),
            self._type_imports(domain),
            self._command_imports(domain),
            self._event_imports(domain),
            self._client_import(domain),
            self._all_exports(domain),
        ]

        return "\n\n".join(filter(None, sections))

    def _module_docstring(self, domain: Domain) -> str:
        return f'"""CDP {domain.domain} Domain."""'

    def _type_imports(self, domain: Domain) -> str | None:
        if not domain.types:
            return None

        type_names = [t.id for t in domain.types]
        return self._build_import_block("types", type_names)

    def _command_imports(self, domain: Domain) -> str | None:
        if not domain.commands:
            return None

        names = [f"{domain.domain}Command"]

        for cmd in domain.commands:
            pascal = to_pascal_case(cmd.name)
            if cmd.parameters:
                names.append(f"{pascal}Params")
            if cmd.returns:
                names.append(f"{pascal}Result")

        return self._build_import_block("commands", sorted(names))

    def _event_imports(self, domain: Domain) -> str | None:
        if not domain.events:
            return None

        names = [f"{domain.domain}Event"]

        for event in domain.events:
            pascal = to_pascal_case(event.name)
            names.append(f"{pascal}Event")

        return self._build_import_block("events", sorted(names))

    def _client_import(self, domain: Domain) -> str:
        client_name = f"{domain.domain}Client"
        return f"from .client import {client_name}"

    def _build_import_block(self, module: str, names: list[str]) -> str:
        if len(names) <= 3:
            return f"from .{module} import {', '.join(names)}"

        lines = [f"from .{module} import ("]
        for name in names:
            lines.append(f"    {name},")
        lines.append(")")

        return "\n".join(lines)

    def _all_exports(self, domain: Domain) -> str:
        exports = self._collect_all_exports(domain)

        lines = ["__all__ = ["]
        for name in exports:
            lines.append(f'    "{name}",')
        lines.append("]")

        return "\n".join(lines)

    def _collect_all_exports(self, domain: Domain) -> list[str]:
        exports = []

        exports.extend(t.id for t in domain.types)

        if domain.commands:
            exports.append(f"{domain.domain}Command")
            for cmd in domain.commands:
                pascal = to_pascal_case(cmd.name)
                if cmd.parameters:
                    exports.append(f"{pascal}Params")
                if cmd.returns:
                    exports.append(f"{pascal}Result")

        if domain.events:
            exports.append(f"{domain.domain}Event")
            for event in domain.events:
                exports.append(f"{to_pascal_case(event.name)}Event")

        exports.append(f"{domain.domain}Client")

        return sorted(exports)
