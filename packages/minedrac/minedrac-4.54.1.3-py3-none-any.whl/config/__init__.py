import logging
import os

import icat_plus_client
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Setup logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("minedrac")

# --- Global configuration ---
ICAT_PLUS_SERVER = os.getenv("icat_plus_server", "http://localhost:8080")

# --- Warn if using localhost ---
if ICAT_PLUS_SERVER in ("http://localhost:8080", "localhost"):
    logger.warning(
        "ICAT_PLUS_SERVER is set to localhost. You might want to change it to the actual server URL."
    )

configuration = icat_plus_client.Configuration(host=ICAT_PLUS_SERVER)

logger.debug(f"Configuration initialized with host={ICAT_PLUS_SERVER}, log_level={LOG_LEVEL}")
