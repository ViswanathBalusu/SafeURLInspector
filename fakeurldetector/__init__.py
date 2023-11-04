from databases import Database
from fakeurldetector.data import MODEL_DIR
from logging.handlers import RotatingFileHandler
import logging

from .BaseConfig import Config
from .version import __version__

# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

if Config.OPEN_PAGE_RANK_API_KEY == -1 or Config.OPEN_PAGE_RANK_API_KEY is None:
    LOGGER.error("Cant Start the Program Without the Open Page Rank API Key")
    exit(1)

DATABASE = Database(Config.DB_URL)
