# This file prepares the app before each test runs

import pytest

from app import create_app
import app.database as database

# fixture is a function that prepares something your test needs

@pytest.fixture()
def app(tmp_path, monkeypatch):
    # Tests should not touch the real app database, so create new temporary database
    test_db_path = tmp_path / "tickets.db"
    # temporarily change the app’s database path
    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    # create the app and put it into test mode
    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    return flask_app


# client is like a fake browser that lets us make GET and POST requests without
# starting the web server with ./run.sh
@pytest.fixture()
def client(app):
    return app.test_client()


# Helper used by ticket tests that need a signed-in user
# It posts to the same login route that the real form uses
@pytest.fixture()
def login(client):
    def _login(email, password="password"):
        return client.post(
            "/auth/login_submit",
            data={"email": email, "password": password},
            follow_redirects=False,
        )

    return _login
