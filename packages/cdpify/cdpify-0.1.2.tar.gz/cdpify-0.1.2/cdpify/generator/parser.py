import logging

from cdpify.generator.config import DOMAINS_TO_GENERATE
from cdpify.generator.models import CDPSpecs, Domain

logger = logging.getLogger(__name__)


def filter_domains(specs: CDPSpecs) -> list[Domain]:
    domains = []

    for domain_name in DOMAINS_TO_GENERATE:
        domain = specs.get_domain(domain_name)
        if domain:
            domains.append(domain)
            logger.info(
                f"  ✓ {domain_name}: {len(domain.commands)} commands, "
                f"{len(domain.events)} events"
            )
        else:
            logger.warning(f"  ✗ {domain_name}: NOT FOUND")

    return domains
