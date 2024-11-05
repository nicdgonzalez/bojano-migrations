# Migrations

A tool for Bojano Homes that moves data from Google Sheets to MongoDB/Clerk.

## Getting Started

**Python 3.12 or higher is required**

First, clone the repository onto your machine:

```bash
git clone https://github.com/nicdgonzalez/bojano-migrations
cd bojano-migrations
```

Copy the following into a `.env` file, and fill out the values:

```bash
# Clerk (https://clerk.com)
CLERK_SECRET_KEY=

# MongoDB (https://www.mongodb.com)
MONGODB_URL=
```

Create a [Google Service Account key] and save it as `service-account-key.json`.
Make sure this new user has access to the necessary spreadsheets!

Then, install the project's dependencies:

> [!NOTE]
> If you don't already have [uv] installed, you can do so by running
> `python -m pip install uv`.

```bash
uv venv
source .venv/bin/activate
uv sync
```

Finally, run the program:

```bash
python -m migrations
```


<!-- Links referenced in the document -->

[Google Service Account key]: https://cloud.google.com/iam/docs/keys-create-delete
[uv]: https://github.com/astral-sh/uv
