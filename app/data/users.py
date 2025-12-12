from app.data.db import connect_database
import bcrypt

class User:
    """
    Core User entity.

    Attributes:
        username: str
        password_hash: str
        role: str
    """
    # A special method that initializes a new object's state
    def __init__(self, username: str, password_hash: str, role: str="user", id: int | None = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role


    @staticmethod # makes a method belong to the class without getting self, so it can be called on the class without needing an instance.
    def hash_password(password: str):
        """Return a bcrypt hash for a plain text password."""
        # Encode the password to bytes required by bcrypt (unicode 8  byte)
        password_bytes = password.encode('utf-8')
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        # Decode the hash back to a string to store in a text file
        return hashed_password.decode('utf-8')

    def verify_password(self, password: str):
        """Check a plain password against this user's stored hash."""
        # Encode both the plaintext password and stored hash to bytes
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = self.password_hash.encode('utf-8')
        # bycrypt.checkpw handles extracting the salt and comparing
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    def get_role(self) -> str:
        return self.role

    @staticmethod
    def get_user_by_username(username):
        """Retrieve user from users.db by username and return a User."""
        conn = connect_database()
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
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)",
            (self.username, self.role, self.password_hash),
        )
        conn.commit()
        self.id = cursor.lastrowid #object now matches the row in the database exactly: same id
        conn.close()

    @staticmethod
    def register(username: str, raw_password: str, role: str = "user"):
        """Create a new user with hashed password and save to DB."""
        password_hash = User.hash_password(raw_password)
        user = User(username=username, password_hash=password_hash, role=role)
        user.insert_user()
        return user

    @staticmethod
    def authenticate(username: str, raw_password: str):
        """Return User if credentials are correct, else None."""
        user = User.get_user_by_username(username)
        if user and user.verify_password(raw_password):
            return user
        return None

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



