# URL routes
# Main request flow for login, dashboard display, ticket submit, and ticket update

from pathlib import Path

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import app.auth.service
import app.database
import app.notifications
import app.tickets

# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)

# File types allowed for ticket attachments
ALLOWED_ATTACHMENT_EXTENSIONS = {"gif", "jpeg", "jpg", "png"}


def is_allowed_attachment(filename):
    #Check if the uploaded attachment has an allowed file extension

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_ATTACHMENT_EXTENSIONS
    )


# Login entry page
# Sends users to the university sign-in form
@auth_bp.get("/login")
def login():
    return render_template("login.html")

# University sign-in form
@auth_bp.get("/university-login")
def university_login():
    return render_template("university_login.html")

# Processes sign-in form submission
# If credentials are valid, stores user info in session and redirects to dashboard
# If not, shows the same page with an error
@auth_bp.post("/auth/login_submit")
def login_submit():
    # Pull submitted credentials from the university sign-in form
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    # Pass the login check to the auth service
    account, error = app.auth.service.authenticate_university_account(
        email, password
    )

    # Re-render the sign-in page with an error if credentials are invalid
    if error or account is None:
        # Keep the current page and show the validation error
        return render_template(
            "university_login.html",
            error=error,
            email=email,
        ), 401

    # Store user info in session so later requests know who is signed in
    # Dashboard display and ticket ownership both depend on these values
    session["user_account_id"] = account.id
    session["user_email"] = account.email
    session["user_full_name"] = account.full_name
    session["user_role"] = account.role
    session["department"] = account.department

    if(account.role == "student"):
        return redirect(url_for("auth.dashboard"))
    else:
        return redirect(url_for("auth.staff_dashboard"))



@auth_bp.post("/logout")
def logout():
    # Remove any session data for the current user and return to login
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    session_data = get_ticket_data()
    return render_template("dashboard.html", tickets=session_data[0],
                           status_filter=session_data[1],
                           category_filter=session_data[2],
                           date_before=session_data[3],
                           date_after=session_data[4])
    
@auth_bp.route("/staff_dashboard")
def staff_dashboard():

    # If a ticket is currently being edited, get staff from the same department as the ticket category
    staff_names = []
    if session.get("user_role") == "manager":
        edit_ticket_id = request.args.get("edit")
        if edit_ticket_id:
            ticket = app.database.get_ticket(edit_ticket_id)
            department = ticket['category']
            staff_names = get_staff_accounts(department)
    
    # Staff only see their department. Managers see all departments.
    department = None
    if session.get("user_role") == "staff":
        department = session.get("department")
    session_data = get_ticket_data(department)

    return render_template("staff_dashboard.html", 
                           tickets=session_data[0],
                           status_filter=session_data[1],
                           category_filter=session_data[2],
                           date_before=session_data[3],
                           date_after=session_data[4],
                           staff = staff_names)

# This function is not a route, it does not return a render_template
def get_ticket_data(department = None):
    # Pull all tickets from database so dashboard can render current data
    connection = app.database.connect_db()

    status_filter = request.args.get("status_filter", "")
    category_filter = request.args.get("category_filter", "")
    date_before = request.args.get("date_before", "")
    date_after = request.args.get("date_after", "")

    try:
        # Session values decide whether to show all tickets or just this user's tickets
        user_role = session.get("user_role")
        user_id = session.get("user_account_id")

        if user_role in ["staff", "manager"]:
            # Staff/manager path
            # Loads every ticket so support roles can manage the full queue
            query = """
                SELECT id, title, category, description, status, created_at, claimed_by
                FROM tickets
                ORDER BY id DESC
            """
            params = ()
        else:
            # Student path
            # Only loads tickets linked to the logged-in student's account ID
            query = """
                SELECT id, title, category, description, status, created_at, claimed_by
                FROM tickets
                WHERE requester_account_id = ?
                ORDER BY id DESC
            """
            params = (user_id,)

        # Main dashboard query
        tickets = connection.execute(query, params).fetchall()

        # Filter helper narrows the list after the query runs
        filtered = app.tickets.search_tickets(
            tickets,
            (status_filter, category_filter, date_before, date_after, department)
        )

        filtered = app.tickets.filter_active_tickets(filtered)


    finally:
        # Close DB connection after the dashboard data is loaded
        connection.close()

    return [filtered, status_filter, category_filter, date_before, date_after]

# Not a route
def get_staff_accounts(department):
    connection = app.database.connect_db()
    query = """
                SELECT full_name
                FROM UniversityAccount
                WHERE role == "staff"
                AND department = ?
            """

    params = (department,)
    accounts = connection.execute(query, params).fetchall()

    connection.close()

    return accounts

@auth_bp.route("/archive")
def archive():
    # Pull tickets from database so archive page can render closed tickets.
    # Staff can view their department's tickets; managers can view all; students can only view their own.
    connection = app.database.connect_db()

    status_filter = request.args.get("status_filter", "")
    category_filter = request.args.get("category_filter", "")
    date_before = request.args.get("date_before", "")
    date_after = request.args.get("date_after", "")

    try:
        user_role = session.get("user_role")
        user_id = session.get("user_account_id")

        if user_role in ["staff", "manager"]:
            query = """
                SELECT id, title, category, description, status, created_at
                FROM tickets
                ORDER BY id DESC
            """
            params = ()
        else:
            query = """
                SELECT id, title, category, description, status, created_at
                FROM tickets
                WHERE requester_account_id = ?
                ORDER BY id DESC
            """
            params = (user_id,)

        tickets = connection.execute(query, params).fetchall()
        department = None
        if user_role == "staff":
            department = session.get("department")

        filtered = app.tickets.search_tickets(
            tickets,
            (status_filter, category_filter, date_before, date_after, department)
        )

        filtered = app.tickets.filter_archived_tickets(filtered)

    finally:
        connection.close()

    return render_template(
        "archive.html",
        tickets=filtered,
        status_filter=status_filter,
        category_filter=category_filter,
        date_before=date_before,
        date_after=date_after
    )

# Handles ticket form display and submission
# GET shows the form
# POST validates required fields, saves the ticket, then redirects with success info
@auth_bp.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    # Optional UI messages after submission or validation failure
    error = None
    success = request.args.get("success") == "1"
    ticket_id = request.args.get("ticket_id")

    if request.method == "POST":
        # Pull and sanitize form values
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        # File uploads are stored in request.files instead of request.form
        attachment_file = request.files.get("attachment")
        attachment_filename = None

        if not title or not category or not description:
            # Basic required-field check before DB insert
            error = "Title, category, and description are required."
        elif attachment_file and attachment_file.filename:
            # Clean the uploaded filename before saving it on the server
            attachment_filename = secure_filename(attachment_file.filename)
            if not attachment_filename or not is_allowed_attachment(attachment_filename):
                error = "Attachment must be a PNG, JPG, or GIF image."
        
        if error is None:
            # Save new ticket and link it to the current session user when available
            # Attachment is first saved as None because we need the ticket ID to name it
            new_id = app.database.save_ticket(
                {
                    "title": title,
                    "category": category,
                    "description": description,
                    "attachment": None,
                    "requester_account_id": session.get("user_account_id"),
                    "status": "Pending",
                }
            )

            if attachment_file and attachment_file.filename:
                # Decides where the file should be saved
                upload_dir = Path(
                    current_app.config.get(
                        "UPLOAD_FOLDER",
                        Path(current_app.instance_path) / "uploads",
                    )
                )
                # Creates the uploads folder if it does not already exist
                upload_dir.mkdir(parents=True, exist_ok=True)

                # Creates a safer saved filename using the ticket ID
                saved_name = f"ticket_{new_id}_{attachment_filename}"
                saved_path = upload_dir / saved_name
                attachment_file.save(saved_path)
                attachment_ref = f"uploads/{saved_name}"
                # Store only the attachment reference in SQLite
                app.database.update_ticket_attachment(new_id, attachment_ref)

            requester_email = session.get("user_email")
            if requester_email:
                app.notifications.send_ticket_confirmation(requester_email, new_id)

            # Redirect after POST avoids duplicate ticket creation on refresh
            return redirect(
                url_for("auth.new_ticket", success="1", ticket_id=new_id)
            )

    return render_template(
        "submit_ticket.html",
        error=error,
        success=success,
        ticket_id=ticket_id,
    )

@auth_bp.route("/new_account", methods = ["GET"])
def create_account():
    return render_template("create_account.html")

@auth_bp.route("/create_new_account", methods = ["GET", "POST"])
def create_new_account():
    # Optional UI messages after submission or validation failure
    error = None
    success = request.args.get("success") == "1"

    if request.method == "POST":
        # Pull and sanitize form values
        email = request.form.get("user_name", "").strip()
        password = request.form.get("password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "").strip()
        department = request.form.get("department", "").strip()

        if not email or not password or not full_name or not role:
            # Basic required-field check before DB insert
            error = "Username, Password, Name, and Role are required."
        else:
            # Save new account
            app.database.save_university_account(
                {
                    "email": email,
                    "password_hash": generate_password_hash(password),
                    "full_name": full_name,
                    "role": role,
                    "department": department,
                }
            )

    return render_template(
        "university_login.html",
        error=error,
        success=success
    )


@auth_bp.route("/tickets/<int:ticket_id>/edit", methods=["POST"])
def edit_ticket(ticket_id):
    ticket = app.database.get_ticket(ticket_id)
    department = ticket['category']
    staff = get_staff_accounts(department)
    return redirect(url_for("auth.staff_dashboard"))

@auth_bp.route("/tickets/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):
    # Reads the edited fields from the dashboard form
    status = request.form["status"]
    claimed_by = request.form["claimed_by"]
    app.database.update_ticket(ticket_id, status, claimed_by)

    ticket = app.database.get_ticket(ticket_id)
    if ticket is not None and ticket["requester_account_id"]:
        account = app.database.get_university_account_by_id(ticket["requester_account_id"])
        if account is not None:
            app.notifications.send_status_update(account["email"], ticket_id, status)

    return redirect(url_for("auth.staff_dashboard"))

@auth_bp.route("/tickets/<int:ticket_id>/claim", methods=["POST"])
def claim_ticket(ticket_id):
    staff_name = request.form["user_name"]
    
    app.database.claim_ticket(ticket_id, staff_name)
    return redirect(url_for("auth.staff_dashboard"))
