import argparse
import os
import logging

from .logger import enable_logging
from .rate_limit import RateLimit, get_sleep_duration_between_requests
from .user import get_existing_users, insert_users_into_clerk
from .constants import ROOT

_log = logging.getLogger(__name__)


def main() -> None:
    """The main entry point into the program"""
    enable_logging()
    args = get_argv()

    if not args.skip_users:
        users = get_existing_users()
        sleep_duration_sec = get_sleep_duration_between_requests(
            requests_total=len(users),
            # https://clerk.com/docs/reference/backend-api/tag/Users
            rate_limit=RateLimit(requests_max=20, duration_sec=10.0),
        )
        insert_users_into_clerk(users, sleep_duration_sec=sleep_duration_sec)

    # TODO: Cache results from Clerk database to a JSON file.
    # TODO: Migrate properties from Google Sheets to MongoDB.


def get_argv() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-users",
        help="Skip over the migration of users",
        action="store_true",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    lock_file = ROOT.joinpath("migration.lock")

    if lock_file.exists():
        raise RuntimeError(
            "Migrations are currently being ran by another process. "
            "If you believe this to be a mistake, delete the lock file at "
            f"{lock_file.as_posix()!r} and rerun."
        )

    try:
        # Create a lock file and store the process ID inside. The existence
        # of the file prevents the program from running in two separate
        # instances, as this will pretty much guarantee we hit the rate limit.
        # The process ID inside is for manually debugging in case of failures.
        lock_file.write_text(str(os.getpid()))

        main()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            os.remove(lock_file)
        except FileNotFoundError:
            pass
