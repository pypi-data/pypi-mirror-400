import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.credentials import Credentials
from icat_plus_client.models.session import Session

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_session(authenticator: str, username: str, password: str):
    """Get the sessionId"""
    with icat_plus_client.ApiClient(configuration) as api_client:
        api_instance = icat_plus_client.SessionApi(api_client)
        try:
            cred = Credentials(
                username=username,
                password=password,
                plugin=authenticator,
            )
            api_response = api_instance.session_post(cred)
            return api_response.session_id
        except icat_plus_client.rest.ApiException as api_exc:
            logger.error(
                "API Exception when calling SessionApi->session_post: %s",
                api_exc,
            )
        except Exception as e:
            logger.exception("Unexpected error while logging in: %s", e)

        return []


def get_info(token: str) -> Session:
    """Get the sessionId"""
    with icat_plus_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = icat_plus_client.SessionApi(api_client)

        try:
            # Gets information about the session in ICAT
            api_response: Session = api_instance.session_session_id_get(token)
            return api_response

        except Exception as e:
            print(f"Exception when calling SessionApi->session_session_id_get: {e}\n")
