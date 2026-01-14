import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.dataset import Dataset

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_datasets(
    token: str,
    investigation_ids: str | None = None,
    instrument_name: str | None = None,
    dataset_ids: str | None = None,
    dataset_type: str | None = None,
    nested: str | None = None,
    sample_id: str | None = None,
    limit: int | None = None,
    skip: int | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> list[Dataset]:
    with icat_plus_client.ApiClient(configuration) as api_client:
        api_instance = icat_plus_client.CatalogueApi(api_client)
        try:
            datasets: list[Dataset] = api_instance.catalogue_session_id_dataset_get(
                token,
                investigation_ids=investigation_ids,
                dataset_ids=dataset_ids,
                sample_id=sample_id,
                instrument_name=instrument_name,
                limit=limit,
                skip=skip,
                search=search,
                dataset_type=dataset_type,
                nested=nested,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            if datasets:
                logger.debug("Fetched %d datasets successfully.", len(datasets))
                return datasets
            else:
                logger.debug("No datasets found for the given parameters.")
                return []

        except icat_plus_client.rest.ApiException as api_exc:
            logger.error(
                "API Exception when CatalogueApi->catalogue_session_id_dataset_get: %s",
                api_exc,
            )
        except Exception as e:
            logger.exception("Unexpected error while fetching datasets: %s", e)

        return []
