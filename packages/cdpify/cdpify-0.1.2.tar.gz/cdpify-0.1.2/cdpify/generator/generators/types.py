from cdpify.generator.generators.base import BaseGenerator
from cdpify.generator.generators.utils import (
    format_docstring,
    map_cdp_type,
    to_snake_case,
)
from cdpify.generator.models import Domain, Parameter, TypeDefinition


class TypesGenerator(BaseGenerator):
    def generate(self, domain: Domain) -> str:
        self._reset_tracking()

        sections = [
            self._header(),
        ]

        type_defs = self._generate_type_definitions(domain)
        sections.append(self._imports())

        if self._cross_domain_refs:
            sections.append(self._cross_domain_imports())

        if type_defs:
            sections.append(type_defs)
        else:
            sections.append("# No types defined")

        return "\n\n".join(sections)

    def _imports(self) -> str:
        if self._cross_domain_refs:
            self._build_cross_domain_imports(use_type_checking=True)

        lines = []

        typing_imports = self._build_typing_imports()
        if typing_imports:
            lines.append(typing_imports)

        lines.append("from dataclasses import dataclass")
        lines.append("from cdpify.domains.shared import CDPModel")

        return "\n".join(lines)

    def _cross_domain_imports(self) -> str:
        return self._build_cross_domain_imports(use_type_checking=True)

    def _generate_type_definitions(self, domain: Domain) -> str:
        if not domain.types:
            return ""

        type_defs = []
        for type_def in domain.types:
            code = self._generate_single_type(type_def)
            if code:
                type_defs.append(code)

        return "\n\n".join(type_defs)

    def _generate_single_type(self, type_def: TypeDefinition) -> str:
        if type_def.enum:
            return self._create_enum_type(type_def)

        if type_def.properties:
            return self._create_object_model(type_def)

        return self._create_type_alias(type_def)

    def _create_enum_type(self, type_def: TypeDefinition) -> str:
        lines = []

        if type_def.description:
            lines.append(format_docstring(type_def.description, indent=0))

        values = ", ".join(f'"{v}"' for v in type_def.enum)
        literal_type = f"Literal[{values}]"

        self._uses_literal = True

        lines.append(f"{type_def.id} = {literal_type}")

        return "\n".join(lines)

    def _create_object_model(self, type_def: TypeDefinition) -> str:
        lines = ["@dataclass(kw_only=True)"]
        lines.append(f"class {type_def.id}(CDPModel):")

        if type_def.description:
            doc = format_docstring(type_def.description, indent=4)
            lines.extend(doc.rstrip().splitlines())

        for prop in type_def.properties:
            lines.append(f"    {self._create_field(prop)}")

        return "\n".join(lines)

    def _create_field(self, param: Parameter) -> str:
        field_name = to_snake_case(param.name)
        py_type = self._resolve_type(param)

        if param.ref and "." in param.ref:
            self._cross_domain_refs.add(param.ref)

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

    def _create_type_alias(self, type_def: TypeDefinition) -> str:
        lines = []

        if type_def.description:
            lines.append(format_docstring(type_def.description, indent=0))

        py_type = map_cdp_type(
            Parameter(name=type_def.id, type=type_def.type, optional=False)
        )

        self._track_type_usage(py_type)

        lines.append(f"{type_def.id} = {py_type}")

        return "\n".join(lines)
