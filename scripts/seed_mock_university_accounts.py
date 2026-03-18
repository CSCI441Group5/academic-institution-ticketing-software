"""
Seeds mock university accounts for development and testing.
Keeps the test account setup separate from application startup so runtime logic stays cleaner
and the mock login flow behaves more like an external identity provider.
Stores hashed passwords in the database
plaintext test passwords exist only in this dev script.
"""

from pathlib import Path
import sys

from werkzeug.security import generate_password_hash

# Make the application package importable when this file is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
import app.database


def seed_mock_university_accounts():
    """Insert default Parkfield test accounts into the local database."""

    # Create a small set of test accounts for the fictional login page
    seeded_accounts = [
        {
            "email": "student1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Amy",
        },
        {
            "email": "student2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Bob",
        },
        {
            "email": "staff1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Carl",
        },
        {
            "email": "staff2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Dana",
        },
        {
            "email": "manager1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Evan",
        },
        {
            "email": "manager2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Fred",
        },
    ]

    for account_data in seeded_accounts:
        # Insert each account once and keep existing local records intact
        app.database.save_mock_university_account(account_data)


if __name__ == "__main__":
    # Create the app so local configuration and database setup are available
    flask_app = create_app()

    with flask_app.app_context():
        seed_mock_university_accounts()

    print("Mock university accounts seeded.")
