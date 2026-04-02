"""Default mock university accounts used by the local login flow."""

from werkzeug.security import generate_password_hash

import app.database


def build_seeded_accounts():
    """Return the default Parkfield accounts for local development."""

    return [
        {
            "email": "student1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Amy",
            "role": "student",
        },
        {
            "email": "student2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Bob",
            "role": "student",
        },
        {
            "email": "staff1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Carl",
            "role": "staff",
        },
        {
            "email": "staff2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Dana",
            "role": "staff",
        },
        {
            "email": "manager1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Evan",
            "role": "manager",
        },
        {
            "email": "manager2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Fred",
            "role": "manager",
        },
    ]


def seed_mock_university_accounts():
    """Insert the default accounts when they are missing."""

    for account_data in build_seeded_accounts():
        app.database.save_mock_university_account(account_data)
