# role logic & validation

from werkzeug.security import check_password_hash
import app.database
from app.model import MockUniversityAccount


def authenticate_mock_university_account(email, password):
    """Authenticate user against the mock university account table."""

    # Normalize email input before lookup so matching is consistent
    normalized_email = email.strip().lower()

    # If email or password field is empty
    if not normalized_email or not password:
        return None, "Enter your Parkfield email address and password."

    # Load the submitted account email from the mock university table
    account_row = app.database.get_mock_university_account_by_email(
        normalized_email
    )

    if account_row is None:
        return None, "Incorrect email address or password."

    account = MockUniversityAccount.from_row(account_row)

    # Compare the submitted password to the stored hash
    if not check_password_hash(account.password_hash, password):
        return None, "Incorrect email address or password."

    return account, None
