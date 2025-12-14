from app.services.database_manager import DatabaseManager
import bcrypt

class User:
    """
    Core User entity.

    Attributes:
        username: str
        password_hash: str
        role: str
        id: int
    """
    # A special method that initializes a new object's state
    def __init__(self, username: str, password_hash: str, role: str="user", id: int | None = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def __str__(self) -> str:
        return f"User({self.username}, role={self.role})"

    def get_role(self) -> str:
        """Retrive the role of the user."""
        return self.role

    @staticmethod
    def get_user_by_username(username):
        """Retrieve user from users.db by username and return a User."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, password_hash FROM users WHERE username = ?",
            (username,),
        )
        user_row = cursor.fetchone() #returns one row at a time as a tuple
        conn.close()
        # If no row found, return None
        if user_row is None:
            return None

        user_id, username, role, password_hash = user_row
        return User(username=username, password_hash=password_hash, role=role, id=user_id)

    def insert_user(self):
        """Insert new user."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)",
            (self.username, self.role, self.password_hash),
        )
        conn.commit()
        self.id = cursor.lastrowid #object now matches the row in the database exactly: same id
        conn.close()

    @staticmethod
    def update_user_password(conn, username: str, new_password: str) -> int:
        """Update a user's password (hashed) in the database."""
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (hashed, username),
        )
        conn.commit()
        return cur.rowcount



