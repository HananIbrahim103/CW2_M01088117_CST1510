import streamlit as st
from app.data.users import User
from app.data.db import connect_database
from app.services.auth_manager import Authentication

conn = connect_database()

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

# Show basic profile info
st.title("⚙️ Settings")

st.subheader("🧑 My profile")
st.write(f"Username: **{st.session_state.username}**")
st.write(f"Role: **{st.session_state.role}**")  # if you store role

st.markdown("----")
st.subheader("Change password")

current_pw = st.text_input("Current password", type="password")
new_pw = st.text_input("New password", type="password")
confirm_pw = st.text_input("Confirm new password", type="password")

if st.button("Change password", type="primary"):
    if not current_pw or not new_pw:
        st.error("Please fill in all fields.")
    elif new_pw != confirm_pw:
        st.error("New passwords do not match.")
    else:
        ok, msg = Authentication.validate_password(new_pw)
        if not ok:
            st.error(msg)
        else:
            # Verify current password against DB
            user = User.get_user_by_username(st.session_state.username)
            if not user or not user.verify_password(current_pw):
                st.error("Current password is incorrect.")
            else:
                # Update password in the DB
                updated = User.update_user_password(conn, st.session_state.username, new_pw)
                if updated:
                    st.success("Password updated successfully.")
                else:
                    st.error("Could not update password. Please try again.")

st.divider()
if st.button("Log out", type="primary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out")
    st.switch_page("Home.py")