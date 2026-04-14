"""
Database access.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

# Build the full path to the database file.
DB_PATH = Path(__file__).resolve().parent.parent / "instance" / "tickets.db"


def _ensure_schema(connection: sqlite3.Connection) -> None:
    """Create the tickets table if it does not already exist"""

    connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,               -- unique ticket ID
                title TEXT NOT NULL,                                -- short ticket summary
                category TEXT NOT NULL,                             -- type of issue
                description TEXT NOT NULL,                          -- details about the problem
                attachment TEXT,                                    -- file path or attachment reference
                requester_account_id INTEGER,                       -- linked university account
                status TEXT NOT NULL DEFAULT 'Pending',             -- ticket state
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- auto timestamp
                claimed_by TEXT                                     -- name of staff who claimed the ticket if there exists one
            )
            """
)

    # Create university accounts table
    connection.execute(
      """
        CREATE TABLE IF NOT EXISTS UniversityAccount (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- unique account ID
            email TEXT NOT NULL UNIQUE,                -- university email
            password_hash TEXT NOT NULL,               -- password hashed
            full_name TEXT NOT NULL,                   -- name of account owner
            role TEXT NOT NULL,                        -- student staff or manager
            department TEXT NOT NULL                   -- IT Facilities or Academic Support
        )
       """
    )

    connection.commit()


def connect_db():
    """Establish connection."""

    # Make sure the folder for the database exists. If it doesn't, create it
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)

    # This lets us access row values by column name instead of index.
    # Example: row["category"] instead of row[1]
    connection.row_factory = sqlite3.Row

    # Ensure the table exists before using the database
    _ensure_schema(connection)

    return connection


def save_ticket(ticket_data):
    """Save ticket."""

    # Open database connection
    connection = connect_db()

    try:
        # Insert ticket data into the database
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                title,
                category,
                description,
                attachment,
                requester_account_id,
                status,
                claimed_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_data["title"],                  # required
                ticket_data["category"],               # required
                ticket_data["description"],            # required
                ticket_data.get("attachment"),         # optional
                ticket_data.get("requester_account_id"),
                ticket_data.get("status", "Pending"),  # default if missing
                ticket_data.get("claimed_by", "")
            ),
        )

        # Save changes
        connection.commit()

        # Return ID of the newly created ticket
        return cursor.lastrowid
    finally:
        # Always close database connection
        connection.close()


def get_ticket_count():
    """Return the current number of ticket rows."""

    connection = connect_db()

    try:
        cursor = connection.execute("SELECT COUNT(*) AS count FROM tickets")
        row = cursor.fetchone()
        return row["count"]
    finally:
        connection.close()


def get_university_account_by_email(email):
    """Retrieve university account by email address."""

    connection = connect_db()

    try:
        # Match email case-insensitively so submitted form values are flexible
        cursor = connection.execute(
            """
            SELECT id, email, password_hash, full_name, role, department
            FROM UniversityAccount
            WHERE lower(email) = lower(?)
            """,
            (email.strip(),),
        )

        return cursor.fetchone()
    finally:
        connection.close()


def save_university_account(account_data):
    """Save university account if it does not already exist."""

    connection = connect_db()
    query = """
            INSERT OR IGNORE INTO UniversityAccount
            (email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?)
            """
    
    params = [account_data["email"],
                account_data["password_hash"],
                account_data["full_name"],
                account_data["role"],
                account_data["department"]]
    try:
        # Insert account only when the email does not already exist
        # Using IGNORE for safer startup seeding
        connection.execute(query, params)

        connection.commit()
    finally:
        connection.close()


def update_ticket(ticket_id, status, claimed_by=""):
    """Update ticket."""
    print("Updating ticket ", ticket_id, " to be claimed by ", claimed_by)
    try:
        connection = connect_db()

        cursor = connection.execute("UPDATE tickets SET status = ?, claimed_by = ? WHERE id = ?",
                                    (status, claimed_by, ticket_id)
                                    )

        connection.commit()

        return cursor.fetchone()
    finally:
        connection.close()

def claim_ticket(ticket_id, staff_name)-> None:
    """Claim Ticket"""
    print("Ticket ID: ", ticket_id)
    print("Staff Name: ", staff_name)
    try:
        connection = connect_db()

        cursor = connection.execute("UPDATE tickets SET claimed_by = ? WHERE id = ?", (staff_name, ticket_id))
        print(cursor.rowcount)

        connection.commit()

    finally:
        connection.close()


def get_ticket(ticket_id,):
    """Retrieve ticket data."""

    try:
        connection = connect_db()

        cursor = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        )

        return cursor.fetchone()
    finally:
        connection.close()


def log_event(event_data):
    """Log system errors."""
