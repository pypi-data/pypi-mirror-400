import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.instrument import Instrument

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_instruments() -> list[Instrument]:
    """Fetch all instruments from ICAT Catalogue."""
    with icat_plus_client.ApiClient(configuration) as api_client:
        api_instance = icat_plus_client.CatalogueApi(api_client)
        try:
            instruments: list[Instrument] = api_instance.catalogue_instruments_get()

            if instruments:
                logger.debug("Fetched %d instruments successfully.", len(instruments))
                return instruments
            else:
                logger.warning("No instruments found in the catalogue.")
                return []

        except icat_plus_client.rest.ApiException as api_exc:
            logger.error(
                "API Exception when calling CatalogueApi->catalogue_instruments_get: %s",
                api_exc,
            )
        except Exception as e:
            logger.exception("Unexpected error while fetching instruments: %s", e)

        return []
