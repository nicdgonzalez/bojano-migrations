import argparse
import logging

from .rate_limit import RateLimit, get_sleep_duration_between_requests
from .user import get_existing_users, insert_users_into_clerk

_log = logging.getLogger(__name__)


def main() -> None:
    """The main entry point into the program"""
    args = get_argv()

    if not args.skip_users:
        users = get_existing_users()
    else:
        # Since all of the user migration logic lies in the following for loop,
        # creating an empty users list gives the for loop nothing to iterate
        # over, essentially skipping over that block of code.
        users = []

    sleep_duration_sec = get_sleep_duration_between_requests(
        requests_total=len(users),
        # https://clerk.com/docs/reference/backend-api/tag/Users
        rate_limit=RateLimit(requests_max=20, duration_sec=10.0),
    )

    insert_users_into_clerk(users, sleep_duration_sec)

    # TODO: Cache results from Clerk database to a JSON file.
    # TODO: Migrate properties from Google Sheets to MongoDB.


def get_argv() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-users",
        help="Skip over the migration of users",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
