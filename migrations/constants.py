import logging
import os
import pathlib

from .errors import MissingEnvironmentVariableError

_log = logging.getLogger(__name__)

# Path to the base directory of the project (i.e., same level as the README)
ROOT = pathlib.Path(__file__).parents[1]
# Path to the directory containing external data (e.g., homeowners.csv)
DATA = ROOT.joinpath("data")

try:
    import dotenv
except ImportError:
    _log.warning("Unable to import dotenv. Skipping loading the .env file")
else:
    env_filepath = ROOT.joinpath(".env")
    _ = dotenv.load_dotenv(env_filepath)

# For querying Clerk's user database.
if (CLERK_SECRET_KEY := os.getenv("CLERK_SECRET_KEY")) is None:
    raise MissingEnvironmentVariableError("CLERK_SECRET_KEY")

# For making API requests to Google Sheets.
SERVICE_ACCOUNT_KEY = ROOT.joinpath("service-account-key.json")

if not SERVICE_ACCOUNT_KEY.exists():
    raise FileNotFoundError(
        f"expected Google Service Account key at {SERVICE_ACCOUNT_KEY.as_posix()}"  # noqa: E501
    )

# ...
if (MONGODB_URL := os.getenv("MONGODB_URL")) is None:
    raise MissingEnvironmentVariableError("MONGODB_URL")
