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
            category TEXT NOT NULL,                             -- type of issue
            description TEXT NOT NULL,                          -- details about the problem
            attachment TEXT,                                    -- file path or attachment reference
            status TEXT NOT NULL DEFAULT 'Pending',             -- ticket state (default = Pending)
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP  -- auto timestamp
        )
        """
    )

    # Create mock university accounts table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS MockUniversityAccount (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- unique account ID
            email TEXT NOT NULL UNIQUE,                -- university email
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL
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
            INSERT INTO tickets (category, description, attachment, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket_data["category"],               # required
                ticket_data["description"],            # required
                ticket_data.get("attachment"),         # optional
                ticket_data.get("status", "Pending"),  # default if missing
            ),
        )

        # Save changes
        connection.commit()

        # Return ID of the newly created ticket
        return cursor.lastrowid
    finally:
        # Always close database connection
        connection.close()


def get_mock_university_account_by_email(email):
    """Retrieve mock university account by email address."""

    connection = connect_db()

    try:
        # Match email case-insensitively so submitted form values are flexible
        cursor = connection.execute(
            """
            SELECT id, email, password_hash, full_name
            FROM MockUniversityAccount
            WHERE lower(email) = lower(?)
            """,
            (email.strip(),),
        )

        return cursor.fetchone()
    finally:
        connection.close()


def save_mock_university_account(account_data):
    """Save mock university account if it does not already exist."""

    connection = connect_db()

    try:
        # Insert account only when the email does not already exist
        connection.execute(
            """
            INSERT OR IGNORE INTO MockUniversityAccount
            (email, password_hash, full_name)
            VALUES (?, ?, ?)
            """,
            (
                account_data["email"],
                account_data["password_hash"],
                account_data["full_name"],
            ),
        )

        connection.commit()
    finally:
        connection.close()


def update_ticket(ticket_id, status, description=""):
    """Update ticket."""

    try:
        connection = connect_db()

        cursor = connection.execute("UPDATE tickets SET status = ?, description = ? WHERE id = ?",
                                    (status, description, ticket_id)
                                    )

        connection.commit()

        return cursor.fetchone()
    finally:
        connection.close()


def get_ticket(ticket_id):
    """Retrieve ticket data."""

    try:
        connection = connect_db()

        cursor = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id)
        )

        return cursor.fetchone()
    finally:
        connection.close()


def log_event(event_data):
    """Log system errors."""
