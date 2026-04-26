import io
from pathlib import Path

import app.database as database

# Covers TC-4 - TC-9, TC-13, TC-15

# Helper function for looking up the seeded account ID by email
# Tickets are linked to requester_account_id, so several tests need this
def account_id(email):
    account = database.get_university_account_by_email(email)
    assert account is not None
    return account["id"]


# Helper function for adding test tickets directly to the temporary database
def create_ticket(
    title,
    category,
    description,
    requester_email,
    status="Pending",
    claimed_by="",
):
    return database.save_ticket(
        {
            "title": title,
            "category": category,
            "description": description,
            "attachment": None,
            "requester_account_id": account_id(requester_email),
            "status": status,
            "claimed_by": claimed_by,
        }
    )


# TC-4: Valid Ticket Submission
# Verifies that a ticket with valid required fields is accepted and stored correctly
def test_post_new_ticket_valid_student_request_saves_ticket(client, login, app):
    # Sign in as a student because new tickets should be linked to the
    # currently logged-in requester
    login("student1@parkfield.edu")

    # Counts how many tickets already exist
    starting_count = database.get_ticket_count()

    # Submit the same form fields used by the Create Ticket page
    response = client.post(
        "/tickets/new",
        data={
            "title": "Cannot access lab printer",
            "category": "IT",
            "description": "The printer in the computer lab rejects my login.",
            # Flask test client uses this tuple to upload a fake file
            "attachment": (
                io.BytesIO(b"fake image contents"),
                "printer-error.png",
            ),
        },
        follow_redirects=False,
    )

    # After submitting ticket, check that the app should redirect
    # and that excatly one new ticket was added
    assert response.status_code == 302
    assert database.get_ticket_count() == starting_count + 1

    # Load the saved row from the database
    connection = database.connect_db()
    try:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE title = ?",
            ("Cannot access lab printer",),
        ).fetchone()
    finally:
        connection.close()

    # Check if all of the fields match
    assert ticket is not None
    assert ticket["category"] == "IT"
    assert ticket["description"] == "The printer in the computer lab rejects my login."
    assert ticket["attachment"] == f"uploads/ticket_{ticket['id']}_printer-error.png"
    assert ticket["requester_account_id"] == account_id("student1@parkfield.edu")

    # Check that the uploaded file was saved in the server-side upload folder
    saved_file = Path(app.config["UPLOAD_FOLDER"]) / Path(ticket["attachment"]).name
    assert saved_file.exists()

    # Check that the saved attachment can be viewed through the ticket route
    attachment_response = client.get(f"/tickets/{ticket['id']}/attachment")
    assert attachment_response.status_code == 200
    assert attachment_response.data == b"fake image contents"


# TC-5: Ticket Submission With Missing Required Fields
# Verifies that incomplete ticket submissions are rejected and validation errors are returned
def test_post_new_ticket_missing_title_does_not_save_ticket(client, login):
    # Sign in as a student so the request acts like it came from a real user
    login("student1@parkfield.edu")

    # Counts how many tickets already exist before submitting the bad form
    starting_count = database.get_ticket_count()

    # Submit the ticket form with a missing title
    response = client.post(
        "/tickets/new",
        data={
            "title": "",
            "category": "IT",
            "description": "The required title is missing.",
        },
    )

    # Turn the response into normal text so it is easier to read and check
    text = response.get_data(as_text=True)

    # Since the title is missing, the page should show an error
    # and the number of tickets should stay the same
    assert response.status_code == 200
    assert "Title, category, and description are required." in text
    assert database.get_ticket_count() == starting_count

# TC-6: Invalid Attachment Handling
# Verifies that unsupported or invalid attachments are rejected safely, and 
# that valid attachments are saved server-side while only their attachmentRef is stored with the ticket.
def test_post_new_ticket_invalid_attachment_type_does_not_save_ticket(client, login):
    # Sign in as a student so the request acts like it came from a real user
    login("student1@parkfield.edu")

    # Counts how many tickets already exist before submitting the bad form
    starting_count = database.get_ticket_count()

    # Submit a ticket with an unsupported attachment extension
    response = client.post(
        "/tickets/new",
        data={
            "title": "Invalid attachment check",
            "category": "IT",
            "description": "This ticket should not save because the attachment is invalid.",
            # .exe is not an allowed attachment type
            "attachment": (
                io.BytesIO(b"fake executable contents"),
                "malware.exe",
            ),
        },
        follow_redirects=False,
    )

    text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Attachment must be a PNG, JPG, or GIF image." in text
    assert database.get_ticket_count() == starting_count


# TC-7: Correct Ticket Routing
# Verifies that the routing logic assigns a submitted ticket 
# to the correct department based on category and *stored routing rules (need to add this later)
def test_get_staff_dashboard_it_staff_user_shows_only_it_tickets(client, login):
    # Create one IT ticket and one Facilities ticket
    create_ticket(
        "IT routing check",
        "IT",
        "Unique IT department ticket for routing test.",
        "student1@parkfield.edu",
    )
    create_ticket(
        "Facilities routing check",
        "Facilities",
        "Unique facilities ticket that IT staff should not see.",
        "student1@parkfield.edu",
    )

    # Sign in as staff1, who is Carl from the IT department
    login("staff1@parkfield.edu")

    # Load the staff dashboard
    response = client.get("/staff_dashboard")

    # Turn the response into normal text so it is easier to read and check
    text = response.get_data(as_text=True)

    # Check that the IT ticket appears, but the Facilities ticket does not
    assert response.status_code == 200
    assert "Unique IT department ticket for routing test." in text
    assert "Unique facilities ticket that IT staff should not see." not in text


# TC-8: Initial Ticket Status Assignment
# Verifies that a newly submitted ticket receives the correct initial status (Pending)
def test_post_new_ticket_valid_student_request_sets_pending_status(client, login):
    # Sign in as a student because new tickets should be linked to the
    # currently logged-in requester
    login("student1@parkfield.edu")

    # Submit the same form fields used by the Create Ticket page
    response = client.post(
        "/tickets/new",
        data={
            "title": "Pending status check",
            "category": "IT",
            "description": "This ticket is used to check the starting status.",
            "attachment": "",
        },
        follow_redirects=False,
    )

    # After submitting ticket, check that the app should redirect
    assert response.status_code == 302

    # Load the saved row from the database
    connection = database.connect_db()
    try:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE title = ?",
            ("Pending status check",),
        ).fetchone()
    finally:
        connection.close()

    # Check if the ticket starts as Pending
    assert ticket is not None
    assert ticket["status"] == "Pending"


# TC-9: Authorized Status Update
# Verifies that support staff can update ticket status successfully
def test_post_update_ticket_staff_user_updates_status_successfully(client, login):
    # Create a ticket first so there is something for the support staff to update
    # Since staff edit their own claimed tickets, assign this ticket to Carl
    ticket_id = create_ticket(
        "Status update check",
        "IT",
        "Ticket used to test staff status updates.",
        "student1@parkfield.edu",
        status="Pending",
        claimed_by="Carl",
    )

    # Sign in as Carl from the IT department
    login("staff1@parkfield.edu")

    # Submit the update form with the new status
    response = client.post(
        f"/tickets/{ticket_id}/update",
        data={"status": "In Progress", "claimed_by": "Carl"},
        follow_redirects=False,
    )

    # After updating the ticket, the app should redirect
    assert response.status_code == 302

    # Load the ticket from the database again
    ticket = database.get_ticket(ticket_id)

    # Check if the new status was saved
    assert ticket["status"] == "In Progress"


# TC-13: Retrieval of Requester Tickets
# Verifies that requesters can retrieve their own tickets and view associated history records
def test_get_dashboard_student_user_shows_only_own_tickets(client, login):
    # Create one ticket for student1
    create_ticket(
        "Student one visibility check",
        "IT",
        "Unique ticket belonging to student one.",
        "student1@parkfield.edu",
    )

    # Create one ticket for student2
    create_ticket(
        "Student two visibility check",
        "IT",
        "Unique ticket belonging to student two.",
        "student2@parkfield.edu",
    )

    # Sign in as student1 and load the student dashboard
    login("student1@parkfield.edu")
    response = client.get("/dashboard")

    # Turn the response into normal text so it is easier to read and check
    text = response.get_data(as_text=True)

    # Check that student1's ticket appears, but student2's ticket does not
    assert response.status_code == 200
    assert "Unique ticket belonging to student one." in text
    assert "Unique ticket belonging to student two." not in text


# TC-15: Staff Ticket Claiming
# Verifies that support staff can claim an unclaimed ticket from their dashboard
def test_post_claim_ticket_unclaimed_ticket_sets_claimed_by_staff(client, login):
    # Create a ticket first so there is something for the staff member to claim
    ticket_id = create_ticket(
        "Claim check",
        "IT",
        "Ticket used to test staff claiming.",
        "student1@parkfield.edu",
    )

    # Sign in as staff1, who is Carl from the seeded test data
    login("staff1@parkfield.edu")

    # Submit the claim form with Carl's name
    response = client.post(
        f"/tickets/{ticket_id}/claim",
        data={"user_name": "Carl"},
        follow_redirects=False,
    )

    # After claiming the ticket, the app should redirect
    assert response.status_code == 302

    # Load the ticket from the database again
    ticket = database.get_ticket(ticket_id)

    # Check if claimed_by was saved as Carl
    assert ticket["claimed_by"] == "Carl"
