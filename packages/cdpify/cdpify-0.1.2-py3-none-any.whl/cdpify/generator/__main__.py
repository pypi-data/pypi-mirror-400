import asyncio
import logging

from cdpify.generator.downloader import download_specs
from cdpify.generator.generator import generate_all_domains
from cdpify.generator.parser import filter_domains

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("🚀 CDP Pydantic Generator\n")

    specs = await download_specs()
    logger.info(f"✓ CDP Version: {specs.version_string}")
    logger.info(f"✓ Total domains: {len(specs.all_domains)}")

    domains = filter_domains(specs)
    logger.info(f"✓ Selected: {len(domains)} domains")

    generate_all_domains(domains)
    logger.info("\n✅ Generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
