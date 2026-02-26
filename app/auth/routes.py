# URL routes

from flask import Blueprint, redirect, render_template, request, url_for
from app.database import save_ticket

# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # On submit (POST), skip auth checks (for now) and send the user to dashboard
    if request.method == "POST":
        return redirect(url_for("auth.dashboard"))

    # When user visits /login, Flask renders login.html
    # render_template looks inside app/templates/
    return render_template("login.html")

@auth_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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
            new_id = save_ticket(
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
