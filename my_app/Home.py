import streamlit as st
from app.data.users import User
from app.services.auth_manager import Authentication

st.set_page_config(
    page_title="Login / Register",
    page_icon="🔑",
    layout="centered"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Logged in as **{st.session_state.username}**.")
    page_choice = st.selectbox(
        "Where would you like to go?",
        [
            "Incidents Dashboard",
            "Datasets Dashboard",
            "IT Tickets Dashboard",
            "Settings"
        ],
    )

    if st.button("Go", type="primary"):
        if page_choice == "Incidents Dashboard":
            st.switch_page("pages/1_Incidents_Dashboard.py")
        elif page_choice == "Datasets Dashboard":
            st.switch_page("pages/2_Datasets_Dashboard.py")
        elif page_choice == "IT Tickets Dashboard":
            st.switch_page("pages/3_IT_Tickets_Dashboard.py")
        elif page_choice == "Settings":
            st.switch_page("pages/4_Settings.py")

    st.stop()  # do not show login form again

# Login / Register Tabs
tab_login, tab_register = st.tabs(["Login", "Register"])

# Login tab
with tab_login:
    st.subheader("Login")
    login_username = st.text_input("Username",key="login_username")
    login_password = st.text_input("Password", type="password",key="login_password")
    if st.button("Log in", type="primary"):
        if not login_username or not login_password:
            st.error("Please enter both username and password.")
        else:
            # Use User.authenticate to check user in user.db
            user = Authentication.authenticate(login_username, login_password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.rerun()
            else:
                # Either username not found or wrong password
                st.error("Invalid username or password. Please register if you don't have an account.")

# Register tab
with tab_register:
     st.subheader("Register")
     new_username = st.text_input("Choose a username", key="register_username")
     new_password = st.text_input("Choose a password", type="password", key="register_password")
     confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
     new_role = st.selectbox("Choose a role", ["user", "admin", "analyst"], key="register_role")
     if st.button("Create account", type="primary"):
         if not new_username or not new_password:
             st.warning("Please enter username and password.")
         elif new_password != confirm_password:
             st.error("Passwords do not match.")
         else:
             username_valid, username_msg = Authentication.validate_username(new_username)
             if not username_valid:
                 st.error(username_msg)
             else:
                 ok, msg = Authentication.validate_password(new_password)
                 if not ok:
                     st.error(msg)
                 else:
                     existing = User.get_user_by_username(new_username)
                     if existing: #not none
                         st.error("Username already exists. Choose another username.")
                     else:
                         user = Authentication.register(username=new_username,
                                              raw_password=new_password,
                                              role=new_role)
                         st.success("Account created! You can now log in.")
