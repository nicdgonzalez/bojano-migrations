import csv
import pathlib
from typing import TypedDict

RawUserData = TypedDict(
    "RawUserData",
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
