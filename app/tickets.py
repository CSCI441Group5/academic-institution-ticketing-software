"""
Handles ticket creation/management.
"""
from flask import Flask, request, render_template
from datetime import datetime
from app.database import update_ticket

app = Flask(__name__)


@app.route("/tickets/new", methods=["GET", "POST"])
def submit_ticket():
    """ Creating a ticket.  """
    if request.method == "POST":

        category = request.form.get("category")
        description = request.form.get("description")
        attachment = request.form.get("attachment")

        if not category or not description:
            return render_template(
                "submit_ticket.html",
                error="Category and description are required."
            )

        ticket_id = 101
        """ Ticket ID for Testing purposes """

        print("Ticket Submitted")
        print(category, description, attachment)

        return render_template(
            "submit_ticket.html",
            success=True,
            ticket_id=ticket_id
        )

    return render_template("submit_ticket.html")


def auto_route_ticket(ticket_id):
    """
    Route ticket to department.
    """


def view_ticket(ticket_id):
    """
    Retrieve ticket data.
    """


def update_ticket_status(ticket_id: int, status: str, notes: str):
    """
    Update ticket status.
    """

    ticket = update_ticket(status, ticket_id)
    return ticket


def search_tickets(tickets, filters):
    """
    Search tickets by date, description, etc.
    """
    status_filter = filters[0]
    category_filter = filters[1]
    before_date = filters[2]
    after_date = filters[3]
    filtered = tickets

    if status_filter != "":
        filtered = [t for t in filtered if t["status"] == status_filter]
    else:
        print(f"Status Filter: {status_filter}")

    if category_filter != "":
        filtered = [t for t in filtered if t["category"]
                    == category_filter]
    else:
        print(f"Category Filter: {category_filter}")

    if before_date != "":
        cutoff = datetime.strptime(before_date, "%Y-%m-%d").date()
        filtered = [t for t in filtered
                    if datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S").date() < cutoff]

    if after_date != "":
        cutoff = datetime.strptime(after_date, "%Y-%m-%d").date()
        filtered = [t for t in filtered
                    if datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S").date() > cutoff]

    return filtered
