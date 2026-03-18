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


@auth_bp.post("/auth/login")
def login_submit():
    # Authenticate against the mock university account table
    # Pull submitted credentials from the university sign in form
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    account, error = app.auth.service.authenticate_mock_university_account(
        email, password
    )

    # Re-render the login page with an error if credentials are invalid
    if error:
        # Keep the current page and show the validation error
        return render_template(
            "university_login.html",
            error=error,
            email=email,
        ), 401

    # Store a minimal mock user session so the sign-in can be tracked later
    session["mock_university_account_id"] = account.id
    session["mock_university_email"] = account.email
    session["mock_university_full_name"] = account.full_name

    return redirect(url_for("auth.dashboard"))


@auth_bp.route("/dashboard")
def dashboard():
    # Pull all tickets from database so dashboard can render current data
    connection = app.database.connect_db()
    status_filter = request.args.get("status_filter", "")
    category_filter = request.args.get("category_filter", "")
    date_before = request.args.get("date_before", "")
    date_after = request.args.get("date_after", "")

    try:
        tickets = connection.execute(
            """
            SELECT id, category, description, status, created_at
            FROM tickets
            ORDER BY id DESC
            """
        ).fetchall()
        filtered = tickets

        filtered = app.tickets.search_tickets(
            tickets, (status_filter, category_filter, date_before, date_after))

    finally:
        # Always close DB connection after query
        connection.close()

    # Pass tickets list to dashboard template
    return render_template("dashboard.html", tickets=filtered,
                           status_filter=status_filter,
                           category_filter=category_filter,
                           date_before=date_before,
                           date_after=date_after)


@auth_bp.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    # Optional UI messages after submission or validation failure
    error = None
    success = request.args.get("success") == "1"
    ticket_id = request.args.get("ticket_id")

    if request.method == "POST":
        # Pull and sanitize form values
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        attachment = request.form.get("attachment", "").strip()

        if not category or not description:
            # Basic required-field check before DB insert
            error = "Category and description are required."
        else:
            # Save new ticket and redirect so refresh does not resubmit form
            new_id = app.database.save_ticket(
                {
                    "category": category,
                    "description": description,
                    "attachment": attachment or None,
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
