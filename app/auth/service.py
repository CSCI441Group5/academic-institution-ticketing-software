# role logic & validation

from werkzeug.security import check_password_hash
import app.database
from app.model import UniversityAccount

# Validates submitted credentials against the UniversityAccount table
# Returns an account object on success, or an error message on failure
def authenticate_university_account(email, password):
    """Authenticate user against the university account table."""

    # Normalize email input before lookup so matching is consistent
    normalized_email = email.strip().lower()

    # If email or password field is empty
    if not normalized_email or not password:
        return None, "Enter your Parkfield email address and password."

    # Load the matching account row from the database
    account_row = app.database.get_university_account_by_email(
        normalized_email
    )

    if account_row is None:
        return None, "Incorrect email address."

    # Convert the raw database row into the account model used by the route layer
    account = UniversityAccount.from_row(account_row)

    # Compare the submitted password to the stored hash
    if not check_password_hash(account.password_hash, password):
        return None, "Incorrect password."

    return account, None
