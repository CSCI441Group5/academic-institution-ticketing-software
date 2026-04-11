"""Default university accounts used by the local login flow."""

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
            "department": ""
        },
        {
            "email": "student2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Bob",
            "role": "student",
            "department": ""
        },
        {
            "email": "staff1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Carl",
            "role": "staff",
            "department": "IT"
        },
        {
            "email": "staff2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Dana",
            "role": "staff",
            "department": "Facilities"
        },
        {
            "email": "staff3@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Notch",
            "role": "staff",
            "department": "Academic Support"
        },
        {
            "email": "staff4@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Jeff",
            "role": "staff",
            "department": "Academic Support"
        },
        {
            "email": "manager1@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Evan",
            "role": "manager",
            "department": "Academic Support"
        },
        {
            "email": "manager2@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Fred",
            "role": "manager",
            "department": "IT"
        },
        {
            "email": "manager3@parkfield.edu",
            "password_hash": generate_password_hash("password"),
            "full_name": "Jeb",
            "role": "manager",
            "department": "Facilities"
        }
    ]


def seed_university_accounts():
    """Insert the default accounts when they are missing."""

    for account_data in build_seeded_accounts():
        app.database.save_university_account(account_data)


def build_seeded_tickets():
    """Return demo tickets grouped by requester email."""

    return {
        "student1@parkfield.edu": [
            {
                "title": "Blackboard login loop",
                "category": "IT",
                "description": "Can sign in to Blackboard but it keeps returning me to the login page.",
                "status": "Pending",
                "claimed_by": ""
            },
            {
                "title": "Projector not connecting",
                "category": "Facilities",
                "description": "Classroom projector powers on but it doesn't display laptop input.",
                "status": "In Progress",
                "claimed_by": ""
            },
            {
                "title": "Need tutoring session access",
                "category": "Academic Support",
                "description": "Can't access tutoring resources in the student portal.",
                "status": "Resolved",
                "claimed_by": ""
            },
        ],
        "student2@parkfield.edu": [
            {
                "title": "Wi-Fi disconnects in library",
                "category": "IT",
                "description": "Campus Wi-Fi drops every few minutes while studying in the library.",
                "status": "Pending",
                "claimed_by": ""
            },
            {
                "title": "Broken desk in science lab",
                "category": "Facilities",
                "description": "Desk in assigned lab station is unstable and unsafe to use.",
                "status": "Closed",
                "claimed_by": ""
            },
            {
                "title": "Advisor meeting request issue",
                "category": "Academic Support",
                "description": "Appointment system shows no available advising slots even after hold was removed.",
                "status": "In Progress",
                "claimed_by": ""
            },
        ],
    }


def seed_demo_tickets():
    """ Insert demo tickets only when the tickets table is empty, 
        otherwise it'd create duplicate seeded tickets on every launch."""

    if app.database.get_ticket_count() > 0:
        return

    for email, tickets in build_seeded_tickets().items():
        account = app.database.get_university_account_by_email(email)
        if account is None:
            continue

        for ticket_data in tickets:
            app.database.save_ticket(
                {
                    "title": ticket_data["title"],
                    "category": ticket_data["category"],
                    "description": ticket_data["description"],
                    "attachment": None,
                    "requester_account_id": account["id"],
                    "status": ticket_data["status"],
                    "claimed_by": ticket_data["claimed_by"]
                }
            )
