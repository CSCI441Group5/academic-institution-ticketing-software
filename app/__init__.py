# Creates the Flask app and registers shared routes
# Also loads starter data so login and dashboard pages have usable data on first run

# Used to read environmental variables
import os
from flask import Flask, redirect, url_for
import re

def create_app():
    # Creates and configures the Flask app, then registers blueprints
    app = Flask(__name__)


    # Adding a regex test to use in the dashboards to protect against invalid strings
    def regex_test(value, pattern):
        return re.match(pattern, value) is not None
    
    app.jinja_env.tests['regex'] = regex_test

     # Set Flask SECRET_KEY from environment variable
     # If it’s not set, it can cause issues, so use a temporary fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "replace_later")

    from app.seed_accounts import seed_demo_tickets, seed_university_accounts

    with app.app_context():
        # Seed default accounts first so demo tickets can link back to valid users
        seed_university_accounts()
        seed_demo_tickets()

    from app.auth.routes import auth_bp
    # Register blueprint with the Flask app so routes defined in auth_bp become active
    app.register_blueprint(auth_bp)

    @app.get("/")
    def index():
        # Redirect root URL to login page
        return redirect(url_for("auth.login"))

    return app
