import bcrypt

def hash_password(password):
    #Encode the password to bytes required by bcrypt (unicode 8  byte)
    password_bytes = password.encode('utf-8')
    #Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    #Decode the hash back to a string to store in a text file
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    #Encode both the plaintext password and stored hash to bytes
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    #bycrypt.checkpw handles extracting the salt and comparing
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def register_user(username, role, password):
    hashed_password = hash_password(password)
    with open("users.txt", "a") as file:
        file.write(f"{username}, {role}, {hashed_password}\n")
    print(f"User {username} registered")
    return True

def user_exists(username):
    try:
        with open("users.txt", "r") as f:
            for line in f.readlines():
                user, role = line.strip().split(",", 1)
                if user == username:
                    print(f"User {username} exists already")
                    return True
            return False
    except FileNotFoundError:
        with open("users.txt", "a") as f:
            f.write(" ")
            pass
        print("file has been created")
    return False

def login_user(username, password):
    with open("users.txt", "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",", 2)
            if len(parts) == 3:
                user, role, hashed_password = parts
                if user == username:
                    if verify_password(password, hashed_password.strip()):
                        print("User Logged in")
                        return True
    return False

def validate_username(username):
    if len(username) < 5:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"
    if not username[0].isalpha():
        return False, "Username must start with a letter"
    for char in username:
        if not (char.isalnum() or char == '_'):
            return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 20:
        return False, "Password must be no more than 20 characters long"
    return True, "Password is valid"

def display_menu():
 """Displays the main menu options."""
 print("\n" + "="*50)
 print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
 print(" Secure Authentication System")
 print("="*50)
 print("\n[1] Register a new user")
 print("[2] Login")
 print("[3] Exit")
 print("-"*50)

def main():
 """Main program loop."""
 print("\nWelcome to the Week 7 Authentication System!")

 while True:
     display_menu()
     choice = input("\nPlease select an option (1-3): ").strip()

     if choice == '1':
         # Registration flow
         print("\n--- USER REGISTRATION ---")
         username = input("Enter a username: ").strip()
         role = input("Enter your role: ").strip()

         # Validate username
         is_valid, error_msg = validate_username(username)
         if not is_valid:
             print(f"Error: {error_msg}")
             continue
         password = input("Enter a password: ").strip()

         if user_exists(username):
             continue

        # Validate password
         is_valid, error_msg = validate_password(password)
         if not is_valid:
             print(f"Error: {error_msg}")
             continue

         # Confirm password
         password_confirm = input("Confirm password: ").strip()
         if password != password_confirm:
             print("Error: Passwords do not match.")
             continue

         # Register the user
         register_user(username, role, password)

     elif choice == '2':
         # Login flow
         print("\n--- USER LOGIN ---")
         username = input("Enter your username: ").strip()
         password = input("Enter your password: ").strip()

         if login_user(username, password):
             print("\nYou are now logged in.")
             print("(In a real application, you would now access the database)")

             input("\nPress Enter to return to main menu...")
         else:
             print("\nError: Invalid username or password. Please try again.")

     elif choice == '3':
         # Exit
         print("\nThank you for using the authentication system.")
         print("Exiting...")
         break

     else:
        print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
