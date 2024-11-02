import os
import pathlib

from .errors import MissingEnvironmentVariableError

# Path to the base directory of the project (i.e., same level as the README)
ROOT = pathlib.Path(__file__).parents[1]
# Path to the directory containing external data (e.g., homeowners.csv)
DATA = ROOT.joinpath("data")

try:
    import dotenv
except ImportError:
    pass  # If dotenv isn't available, skip loading the .env file.
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
        "expected Google Service Account key at {SERVICE_ACCOUNT_KEY!r}"
    )

# ...
if (MONGODB_URL := os.getenv("MONGODB_URL")) is None:
    raise MissingEnvironmentVariableError("MONGODB_URL")
