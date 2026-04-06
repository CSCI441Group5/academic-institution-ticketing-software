# URL routes

from flask import Blueprint, redirect, render_template, request, session, url_for
import app.auth.service
import app.database
import app.tickets


# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    # When user visits /login, render the app-side entry page
    # This page links out to the separate university login screen
    return render_template("login.html")


@auth_bp.get("/university-login")
def university_login():
    # Render the fictional university identity-provider style page
    return render_template("university_login.html")


@auth_bp.post("/auth/login_submit")
def login_submit():
    # Authenticate against the university account table
    # Pull submitted credentials from the university sign in form
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    account, error = app.auth.service.authenticate_university_account(
        email, password
    )

    # Re-render the login page with an error if credentials are invalid
    if error or account is None:
        # Keep the current page and show the validation error
        return render_template(
            "university_login.html",
            error=error,
            email=email,
        ), 401

    # Store a minimal user session so the sign-in can be tracked later
    session["user_account_id"] = account.id
    session["user_email"] = account.email
    session["user_full_name"] = account.full_name
    session["user_role"] = account.role
    if(session["user_role"] == "staff"):
        session["department"] = account.department

    if(session["user_role"] == "student"):
        return redirect(url_for("auth.dashboard"))
    else:
        return redirect(url_for("auth.staff_dashboard"))

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
    return render_template("staff_dashboard.html", tickets=session_data[0],
                           status_filter=session_data[1],
                           category_filter=session_data[2],
                           date_before=session_data[3],
                           date_after=session_data[4])

def get_ticket_data(department = None):
    # Pull all tickets from database so dashboard can render current data
    connection = app.database.connect_db()
    status_filter = request.args.get("status_filter", "")
    category_filter = request.args.get("category_filter", "")
    date_before = request.args.get("date_before", "")
    date_after = request.args.get("date_after", "")

    try:
        tickets = connection.execute(
            """
            SELECT id, title, category, description, status, created_at
            FROM tickets
            ORDER BY id DESC
            """
        ).fetchall()
        filtered = tickets

        filtered = app.tickets.search_tickets(
            tickets, (status_filter, category_filter, date_before, date_after, department))

    finally:
        # Always close DB connection after query
        connection.close()

    session_data = [filtered, status_filter, category_filter, date_before, date_after]

    # Pass tickets list to dashboard template
    return session_data

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
            # Save new ticket and redirect so refresh does not resubmit form
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
    status = request.form["status"]
    description = request.form["description"]

    app.database.update_ticket(ticket_id, status, description)
    return redirect(url_for("auth.dashboard"))
