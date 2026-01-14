import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.investigation import Investigation

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_investigation_by_id(
    session_id: str,
    investigation_id: str | None = None,
    instrument_name: str | None = None,
    investigation_name: str | None = None,
    filter: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
    skip: int | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    with_has_access: bool | None = None,
) -> list[Investigation]:
    """Fetch investigations by session ID with optional filters."""

    with icat_plus_client.ApiClient(configuration) as api_client:
        api_instance = icat_plus_client.CatalogueApi(api_client)
        try:
            investigations: list[Investigation] = api_instance.catalogue_session_id_investigation_get(
                session_id=session_id,
                instrument_name=instrument_name,
                investigation_name=investigation_name,
                ids=investigation_id,
                filter=filter,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                skip=skip,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                with_has_access=with_has_access,
            )

            if investigations:
                logger.debug("Fetched %d investigations successfully.", len(investigations))
                return investigations
            else:
                logger.debug("No investigations found for the given parameters.")
                return []

        except icat_plus_client.rest.ApiException as api_exc:
            logger.error(f"API Exception CatalogueApi->catalogue_session_id_investigation_get: {api_exc}")
        except Exception as e:
            logger.exception("Unexpected error while fetching investigations: %s", e)

        return []
