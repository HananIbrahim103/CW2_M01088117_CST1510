import bcrypt
from app.data.users import User

class Authentication:
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

    @staticmethod
    def verify_password(password: str, hashed_password: str):
        """Check a plain password against this user's stored hash."""
        # Encode both the plaintext password and stored hash to bytes
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        # bycrypt.checkpw handles extracting the salt and comparing
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    @staticmethod
    def validate_password(password: str):
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        if len(password) > 20:
            return False, "Password must be no more than 20 characters long."
        return True, "OK"

    @staticmethod
    def register(username: str, raw_password: str, role: str = "user"):
        """Create a new user with hashed password and save to DB."""
        password_hash = Authentication.hash_password(raw_password)
        user = User(username=username, password_hash=password_hash, role=role)
        user.insert_user()
        return user

    @staticmethod
    def authenticate(username: str, raw_password: str):
        """Return User if credentials are correct, else None."""
        user = User.get_user_by_username(username)
        if user and Authentication.verify_password(raw_password, user.password_hash):
            return user
        return None

