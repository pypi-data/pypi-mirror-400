import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.item import Item
from icat_plus_client.models.parcel import Parcel

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_parcels_by(
    token: str,
    investigation_id: str | None = None,
) -> list[Parcel]:
    with icat_plus_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = icat_plus_client.TrackingApi(api_client)

        try:
            # Lists shipments associated to an investigation
            shipments = api_instance.tracking_session_id_shipment_get(
                investigation_id=investigation_id, session_id=token
            )
            if len(shipments) == 1:
                parcels = api_instance.tracking_session_id_parcel_get(
                    shipments[0].id, token, investigation_id=investigation_id
                )
                logger.debug("Fetched %d parcels successfully.", len(parcels))
                if parcels:
                    return parcels
        except Exception as e:
            logger.error(f"Exception when TrackingApi->tracking_session_id_parcel_get: {e}")
        return []


def get_declared_samples_by(
    token: str,
    investigation_id: str | None = None,
) -> list[Item]:
    try:
        parcels = get_parcels_by(token, investigation_id)
        samples = []
        for parcel in parcels:
            for item in parcel.content:
                if item.type == "CONTAINER":
                    samples.extend(item.content)
                else:
                    samples.extend(item)
        return samples
    except Exception as e:
        logger.error(f"Exception when get_declared_samples_by: {e}")
    return []
