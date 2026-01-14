import logging
import shutil
import subprocess
from pathlib import Path

from cdpify.generator.generators import (
    ClientGenerator,
    CommandsGenerator,
    EventsGenerator,
    InitGenerator,
    TypesGenerator,
)
from cdpify.generator.models import Domain

CDP_DIR = Path(__file__).parent.parent / "domains"
logger = logging.getLogger(__name__)


class DomainGenerator:
    def __init__(self):
        self._types_gen = TypesGenerator()
        self._commands_gen = CommandsGenerator()
        self._events_gen = EventsGenerator()
        self._client_gen = ClientGenerator()
        self._init_gen = InitGenerator()

    def generate_all(self, domains: list[Domain]) -> None:
        self._prepare_output_dir()
        logger.info(f"\n📝 Generating {len(domains)} domains...")

        for domain in domains:
            self._generate_domain(domain)

        self._generate_base_file()
        self._generate_init_file(domains)
        self._format_with_ruff()

        logger.info("\n✅ Generation complete!")

    def _prepare_output_dir(self) -> None:
        if CDP_DIR.exists():
            shutil.rmtree(CDP_DIR)

        CDP_DIR.mkdir(parents=True, exist_ok=True)

    def _generate_domain(self, domain: Domain) -> None:
        domain_dir = self._create_domain_directory(domain)
        self._print_domain_summary(domain)
        self._write_domain_files(domain, domain_dir)

    def _create_domain_directory(self, domain: Domain) -> Path:
        domain_dir = CDP_DIR / domain.domain.lower()
        domain_dir.mkdir(exist_ok=True)

        return domain_dir

    def _print_domain_summary(self, domain: Domain) -> None:
        logger.info(f"  ✓ {domain.domain}")
        logger.info(f"    - {len(domain.types)} types")
        logger.info(f"    - {len(domain.commands)} commands")
        logger.info(f"    - {len(domain.events)} events")

    def _write_domain_files(self, domain: Domain, domain_dir: Path) -> None:
        (domain_dir / "types.py").write_text(self._types_gen.generate(domain))
        (domain_dir / "commands.py").write_text(self._commands_gen.generate(domain))
        (domain_dir / "events.py").write_text(self._events_gen.generate(domain))
        (domain_dir / "client.py").write_text(self._client_gen.generate(domain))
        (domain_dir / "__init__.py").write_text(self._init_gen.generate(domain))

    def _generate_base_file(self) -> None:
        (CDP_DIR / "shared.py").write_text(self._build_shared_content())
        logger.info("  ✓ shared.py")

    def _build_shared_content(self) -> str:
        return """import re
from dataclasses import asdict, dataclass, fields
from cdpify.generator.generators.utils import to_snake_case
from typing import Any, Self


_ACRONYMS = frozenset({
    "api", "css", "dom", "html", "id", "json", "pdf", "spc",
    "ssl", "url", "uuid", "xml", "xhr", "ax", "cpu", "gpu",
    "io", "js", "os", "ui", "uri", "usb", "wasm", "http", "https",
})


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
"""

    def _generate_init_file(self, domains: list[Domain]) -> None:
        content = self._build_main_init_content(domains)
        (CDP_DIR / "__init__.py").write_text(content)
        logger.info("  ✓ __init__.py")

    def _build_main_init_content(self, domains: list[Domain]) -> str:
        imports = self._build_domain_imports(domains)
        exports = self._build_domain_exports(domains)

        return f'''"""Generated CDP domains."""

{imports}

{exports}
'''

    def _build_domain_imports(self, domains: list[Domain]) -> str:
        lines = []
        for domain in domains:
            domain_lower = domain.domain.lower()
            lines.append(f"from .{domain_lower} import {domain.domain}Client")

        return "\n".join(lines)

    def _build_domain_exports(self, domains: list[Domain]) -> str:
        lines = ["__all__ = ["]
        for domain in domains:
            lines.append(f'    "{domain.domain}Client",')
        lines.append("]")

        return "\n".join(lines)

    def _format_with_ruff(self) -> None:
        logger.info("\n✨ Formatting generated code with Ruff...")

        try:
            self._run_ruff_format()
        except FileNotFoundError:
            self._handle_ruff_not_found()
        except Exception as e:
            self._handle_ruff_error(e)

    def _run_ruff_format(self) -> None:
        result = subprocess.run(
            ["ruff", "format", str(CDP_DIR)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info("  ✓ Code formatted successfully")
        else:
            self._handle_ruff_warnings(result.stderr)

    def _handle_ruff_warnings(self, stderr: str) -> None:
        logger.warning("  ⚠️  Ruff formatting had warnings:")
        if stderr:
            logger.warning(f"     {stderr}")

    def _handle_ruff_not_found(self) -> None:
        logger.warning("  ⚠️  Ruff not found - skipping formatting")
        logger.warning("     Install with: uv add --dev ruff")

    def _handle_ruff_error(self, error: Exception) -> None:
        logger.warning(f"  ⚠️  Error during formatting: {error}")


def generate_all_domains(domains: list[Domain]) -> None:
    generator = DomainGenerator()
    generator.generate_all(domains)
