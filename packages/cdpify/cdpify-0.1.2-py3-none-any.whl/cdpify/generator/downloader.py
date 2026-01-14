import json
import logging
from pathlib import Path

import httpx

from cdpify.generator.constants import BROWSER_PROTOCOL_URL, JS_PROTOCOL_URL
from cdpify.generator.models import CDPSpecs, ProtocolSpec

SPECS_DIR = Path(__file__).parent.parent.parent / "specs"
logger = logging.getLogger(__name__)


async def download_specs() -> CDPSpecs:
    SPECS_DIR.mkdir(exist_ok=True)

    async with httpx.AsyncClient() as client:
        logger.info("📥 Downloading browser_protocol.json...")
        browser_response = await client.get(BROWSER_PROTOCOL_URL)
        browser_response.raise_for_status()
        browser_data = browser_response.json()

        logger.info("📥 Downloading js_protocol.json...")
        js_response = await client.get(JS_PROTOCOL_URL)
        js_response.raise_for_status()
        js_data = js_response.json()

    (SPECS_DIR / "browser_protocol.json").write_text(json.dumps(browser_data, indent=2))
    (SPECS_DIR / "js_protocol.json").write_text(json.dumps(js_data, indent=2))

    logger.info("✅ Specs downloaded and saved to specs/")

    return CDPSpecs(
        browser=ProtocolSpec.model_validate(browser_data),
        js=ProtocolSpec.model_validate(js_data),
    )


def load_specs() -> CDPSpecs:
    browser_data = json.loads((SPECS_DIR / "browser_protocol.json").read_text())
    js_data = json.loads((SPECS_DIR / "js_protocol.json").read_text())

    return CDPSpecs(browser=ProtocolSpec(**browser_data), js=ProtocolSpec(**js_data))
