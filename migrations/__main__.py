import csv
import logging
import pathlib
import time

import requests

from .constants import CLERK_SECRET_KEY, DATA
from .rate_limit import RateLimit, get_sleep_duration_between_requests
from .user import RawUserData, UserPayload

_log = logging.getLogger(__name__)


def main() -> None:
    """The main entry point into the program"""
    homeowners_csv = DATA.joinpath("homeowners.csv")

    if not homeowners_csv.exists():
        # data = get_user_data_from_google_sheets()
        raise FileNotFoundError(
            f"Export the 'All Homeowners' spreadsheet as CSV to {homeowners_csv!r}"  # noqa: E501
        )
    else:
        data = get_user_data_from_csv(homeowners_csv)

    data_filtered = filter(valid_homeowner, data)
    users = list(map(convert_raw_data_to_clerk_payload, data_filtered))
    sleep_duration_sec = get_sleep_duration_between_requests(
        len(users),
        # https://clerk.com/docs/reference/backend-api/tag/Users
        rate_limit=RateLimit(requests_max=20, duration_sec=10.0),
    )

    for user_payload in users:
        try:
            url = "https://api.clerk.com/v1/users"
            headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
            response = requests.post(url, json=user_payload, headers=headers)
        except Exception as exc:
            _log.error(f"failed to create user in Clerk: {exc}")
        else:
            _log.info(f"added a new user to Clerk database: {response.json()}")
        finally:
            time.sleep(sleep_duration_sec)

    # TODO: Cache results from Clerk database to a JSON file.
    # TODO: Migrate properties from Google Sheets to MongoDB.


def get_user_data_from_csv(filepath: pathlib.Path) -> list[RawUserData]:
    """Read the user data from a CSV file.

    Parameters
    ----------
    filepath:
        The path to the target CSV file containing the user's data

    Returns
    -------
    :class:`dict`: A dictionary representation of the CSV data.
    """
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    return data


def valid_homeowner(entry: RawUserData, /) -> bool:
    """Check whether an entry is movable to the new database."""
    return (
        # An empty Property Owner value means there was a placeholder in
        # one of the other fields, so Google Sheets returned the whole entry.
        entry.get("Property Owner", "") != ""
        # Users with no email do not need to be moved.
        and entry.get("Email", "") != ""
        # This user has no properties with Bojano Homes.
        and entry.get("All Props", "") != ""
    )


def convert_raw_data_to_clerk_payload(entry: RawUserData, /) -> UserPayload:
    assert "Property Owner" in entry and entry["Property Owner"] != "", entry
    # Some users have company names as their name (e.g., "My Company LLC").
    names = entry["Property Owner"].rsplit(" ", maxsplit=1)
    assert len(names) <= 2, len(names)

    if len(names) == 2:
        first_name, last_name = names
    else:
        first_name, last_name = names[0], ""

    return UserPayload(
        first_name=first_name,
        last_name=last_name,
        email_address=[e.strip() for e in entry["Email"].split(",")],
    )


if __name__ == "__main__":
    main()
