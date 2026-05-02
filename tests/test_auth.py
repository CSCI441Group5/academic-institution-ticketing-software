import pytest

# Covers TC-1 - TC-3

# TC-1: Successful Authentication Callback Handling
# Verifies that valid university authentication data creates a logged-in session
@pytest.mark.parametrize(
    ("email", "expected_name", "expected_role", "expected_department"),
    [
        ("student1@parkfield.edu", "Amy", "student", ""),
        ("staff1@parkfield.edu", "Carl", "staff", "IT"),
        ("manager1@parkfield.edu", "Evan", "manager", ""),
    ],
)
def test_post_login_submit_valid_account_creates_session(
    client,
    email,
    expected_name,
    expected_role,
    expected_department,
):
    # Submit credentials for the university account
    response = client.post(
        "/auth/login_submit",
        data={"email": email, "password": "password"},
        follow_redirects=False,
    )

    # Successful sign-in should leave the login form and redirect
    # Where it redirects to is checked in TC3
    assert response.status_code == 302

    # Check that the route stored the expected authentication values in session
    # so later requests know who is signed in
    with client.session_transaction() as session:
        assert session["user_email"] == email
        assert session["user_full_name"] == expected_name
        assert session["user_role"] == expected_role
        assert session["department"] == expected_department
        assert session["user_account_id"] is not None


# TC-2: Failed Authentication Handling
# Verifies that failed or incomplete authentication data does not create a session.
@pytest.mark.parametrize(
    ("email", "password", "expected_error"),
    [
        ("", "", "Enter your Parkfield email address and password."),
        ("student1@parkfield.edu", "wrong-password", "Incorrect password."),
        ("missing@parkfield.edu", "password", "Incorrect email address."),
    ],
)
def test_post_login_submit_invalid_data_rejects_session(
    client,
    email,
    password,
    expected_error,
):
    # Submit bad or incomplete credentials to simulate failed authentication
    response = client.post(
        "/auth/login_submit",
        data={"email": email, "password": password},
        follow_redirects=False,
    )

    # Turn the response into normal text so it is easier to read and check
    text = response.get_data(as_text=True)

    # Failed login should keep the user on the sign-in page and show the
    # matching validation error
    assert response.status_code == 401
    assert expected_error in text

    # Since authentication failed, no logged-in user data should exist
    with client.session_transaction() as session:
        assert "user_account_id" not in session
        assert "user_email" not in session
        assert "user_full_name" not in session
        assert "user_role" not in session
        assert "department" not in session


# TC-3: Role Mapping and Dashboard Redirect
# Verifies that each authenticated role is redirected to the correct dashboard.
@pytest.mark.parametrize(
    ("email", "expected_role", "expected_department", "expected_redirect"),
    [
        ("student1@parkfield.edu", "student", "", "/dashboard"),
        ("staff1@parkfield.edu", "staff", "IT", "/staff_dashboard"),
        ("manager1@parkfield.edu", "manager", "", "/staff_dashboard"),
    ],
)
def test_post_login_submit_maps_role_to_dashboard_redirect(
    client,
    email,
    expected_role,
    expected_department,
    expected_redirect,
):
    # Sign in with a seeded account for the role being checked
    response = client.post(
        "/auth/login_submit",
        data={"email": email, "password": "password"},
        follow_redirects=False,
    )

    # After authentication, the role should decide which dashboard loads
    assert response.status_code == 302
    assert response.headers["Location"] == expected_redirect

    # Check that the session role and department match the seeded account
    # mapping used by the dashboard authorization logic
    with client.session_transaction() as session:
        assert session["user_email"] == email
        assert session["user_role"] == expected_role
        assert session["department"] == expected_department
