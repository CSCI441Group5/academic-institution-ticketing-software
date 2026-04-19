"""
Handles notifications.
"""

import smtplib
from email.message import EmailMessage
from flask import current_app


def _send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email using SMTP configuration from Flask config."""
    mail_server = current_app.config.get("MAIL_SERVER")
    if not mail_server:
        print("MAIL_SERVER is not configured. Skipping email send.")
        print("Email to:", to_email)
        print("Subject:", subject)
        print("Body:\n", body)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config.get("MAIL_DEFAULT_SENDER")
    message["To"] = to_email
    message.set_content(body)

    mail_port = current_app.config.get("MAIL_PORT", 587)
    use_ssl = current_app.config.get("MAIL_USE_SSL", False)
    use_tls = current_app.config.get("MAIL_USE_TLS", True)
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")

    if use_ssl:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    try:
        with smtp_class(mail_server, mail_port, timeout=10) as server:
            if use_tls and not use_ssl:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(message)

        print(f"Sent notification email to {to_email}.")
        return True
    except Exception as exc:
        print("Failed to send email:", exc)
        return False


def send_ticket_confirmation(email, ticket_id):
    """Notify user of ticket submission."""
    subject = f"Ticket #{ticket_id} received"
    body = (
        f"Hello,\n\n"
        f"We have received your ticket submission. Your ticket number is {ticket_id}.\n"
        f"We will notify you whenever the status changes.\n\n"
        f"Thank you,\n"
        f"Support Team"
    )
    return _send_email(email, subject, body)


def send_status_update(email, ticket_id, status):
    """Notify user of ticket status update."""
    subject = f"Update for ticket #{ticket_id}: {status}"
    body = (
        f"Hello,\n\n"
        f"Your ticket #{ticket_id} status has been updated to '{status}'.\n"
        f"If you need more information, please reply or log in to the support portal.\n\n"
        f"Thank you,\n"
        f"Support Team"
    )
    return _send_email(email, subject, body)
