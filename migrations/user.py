import csv
import logging
import pathlib
import time
from typing import TypedDict

import requests

from .constants import CLERK_SECRET_KEY, DATA

_log = logging.getLogger(__name__)

UserDataRaw = TypedDict(
    "UserDataRaw",
    {
        "Property Owner": str,
        "Commission Percentage": str,
        "Nightly vs. Gross": str,
        "Payout timing": str,
        "Notification Limit": str,
        "Email": str,
        "Google Drive Folders": str,
        "Link here": str,
        "All Props": str,
        "Individual 1": str,
        "Individual 2": str,
        "Individual 3": str,
        "Individual 4": str,
        "Individual 5": str,
        "Individual 6": str,
        "Individual 7": str,
        "Individual 8": str,
        "Individual 9": str,
        "Individual 10": str,
    },
)


class UserPayload(TypedDict):
    first_name: str
    last_name: str
    email_address: list[str]


def get_user_raw_from_csv(filepath: pathlib.Path) -> list[UserDataRaw]:
    """Read existing user data from a CSV file.

    Parameters
    ----------
    filepath:
        The path to the target CSV file containing the user's data

    Returns
    -------
    :class:`list`: A list of all existing users.
    """
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    return data


def get_user_raw_from_google_sheets() -> list[UserDataRaw]:
    """Query the Google Sheets API to get existing user data.

    Returns
    -------
    :class:`list`: A list of all existing users.
    """
    raise NotImplementedError


def get_existing_users() -> list[UserPayload]:
    """Returns existing users filtered, normalized and ready to go
    into the new database.

    Returns
    -------
    :class:`list` containing valid existing users.
    """
    homeowners_csv = DATA.joinpath("homeowners.csv")

    if not homeowners_csv.exists():
        # TODO: Implement the following function...
        # data = get_user_raw_from_google_sheets()
        raise FileNotFoundError(
            f"Export the 'All Homeowners' spreadsheet as CSV to {homeowners_csv.as_posix()}"  # noqa: E501
        )
    else:
        data = get_user_raw_from_csv(homeowners_csv)

    data_filtered = filter(valid_user, data)
    users = list(map(convert_user_raw_to_clerk_payload, data_filtered))
    return users


def valid_user(entry: UserDataRaw, /) -> bool:
    """Check whether an entry is movable to the new database."""
    return (
        # An empty Property Owner value means there was a placeholder in
        # one of the other fields, so Google Sheets returned the whole entry.
        # We can safely discard these entries.
        entry.get("Property Owner", "") != ""
        # Users with no email do not need to be moved.
        and entry.get("Email", "") != ""
        # This user has no properties with Bojano Homes.
        and entry.get("All Props", "") != ""
    )


def convert_user_raw_to_clerk_payload(entry: UserDataRaw, /) -> UserPayload:
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


def insert_users_into_clerk(
    users: list[UserPayload],
    *,
    sleep_duration_sec: float,
) -> None:
    """Insert a batch of users into the Clerk database."""
    for user_payload in users:
        try:
            url = "https://api.clerk.com/v1/users"
            headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
            response = requests.post(url, json=user_payload, headers=headers)
        except Exception as exc:
            _log.error(f"failed to add new user to Clerk: {exc}")
        else:
            _log.info(f"added a new user to Clerk: {response.json()}")
        finally:
            time.sleep(sleep_duration_sec)
