"""
System models.
"""

class User:
    def __init__(self, email, role):
        self.email = email
        self.role = role

class Ticket:
    def __init__(self, ticket_id, category, description, status):
        self.ticket_id = ticket_id
        self.category = category
        self.description = description
        self.status = status

# University account model used by the local identity flow.
class UniversityAccount:
    def __init__(self, account_id, email, password_hash, full_name, role, department):
        self.id = account_id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.department = department

    @classmethod
    def from_row(cls, row):
        """Build account model from sqlite row."""

        return cls(
            row["id"],
            row["email"],
            row["password_hash"],
            row["full_name"],
            row["role"],
            row["department"]
        )
