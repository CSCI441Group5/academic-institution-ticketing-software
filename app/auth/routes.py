# URL routes
# Main request flow for login, dashboard display, ticket submit, and ticket update

from flask import Blueprint, redirect, render_template, request, session, url_for
import app.auth.service
import app.database
import app.tickets

# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)

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
    department = session.get("department")
    session_data = get_ticket_data(department)
    staff_names = get_staff_accounts(department)
    return render_template("staff_dashboard.html", tickets=session_data[0],
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

        print(filtered)

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
        attachment = request.form.get("attachment", "").strip()

        if not title or not category or not description:
            # Basic required-field check before DB insert
            error = "Title, category, and description are required."
        else:
            # Save new ticket and link it to the current session user when available
            new_id = app.database.save_ticket(
                {
                    "title": title,
                    "category": category,
                    "description": description,
                    "attachment": attachment or None,
                    "requester_account_id": session.get("user_account_id"),
                    "status": "Pending",
                }
            )
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


@auth_bp.route("/tickets/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):
    # Reads the edited fields from the dashboard form
    status = request.form["status"]
    claimed_by = request.form["claimed_by"]
    print(claimed_by, " is getting a new ticket")
    # Current update path only changes status and description
    app.database.update_ticket(ticket_id, status, claimed_by)
    return redirect(url_for("auth.staff_dashboard"))

@auth_bp.route("/tickets/<int:ticket_id>/claim", methods=["POST"])
def claim_ticket(ticket_id):
    staff_name = request.form["user_name"]
    
    app.database.claim_ticket(ticket_id, staff_name)
    return redirect(url_for("auth.staff_dashboard"))
