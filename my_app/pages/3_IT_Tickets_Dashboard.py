import streamlit as st
from app.data.db import connect_database
from openai import OpenAI
from app.data.it_tickets import Tickets

st.set_page_config(
    page_title="IT Tickets Dashboard",
    page_icon="🛠️",
    layout="wide"
)
# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
     st.error("You must be logged in to view the dashboard.")
     if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
     st.stop()

# If logged in, show dashboard content
st.title("🛠️ IT Tickets Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

tickets_tab, analytics_tab, AI_tab = st.tabs(["Tickets", "Analytics", "AI assistant"])

with tickets_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Display tickets in a table
    tickets = Tickets.get_all_tickets(conn)
    st.dataframe(tickets, use_container_width=True)

    # CREATE: Add new ticket with a form
    with st.form("new_ticket"):
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        description = st.text_input("Ticket Description")
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for user"])
        assigned_to = st.selectbox("Assigned to", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
        resolution_time_hours = st.text_input("Resolution Time (Hours)")
        # Form submit button
        submitted = st.form_submit_button("Add Ticket")

    # When form is submitted
    if submitted:
        if priority and description and status and assigned_to and resolution_time_hours:
            # Call Week 8 function to insert into database
            Tickets(priority=priority, description=description, status=status, assigned_to=assigned_to, resolution_time_hours=resolution_time_hours).insert_ticket()
            st.success("✓ Ticket added successfully!")
            st.rerun()  # Refresh the page to show new ticket
        else:
            st.error("You must fill in all the fields")

    # Update form
    with st.form("update_ticket"):
        ticket_id = st.text_input("Ticket ID")
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for user"])
        update = st.form_submit_button("Update")

    if update:
        if ticket_id:
            Tickets.update_ticket_status(conn, ticket_id, new_status)
            st.rerun()
        else:
            st.error("You must fill in all the fields.")

    ticket_ids = [str(inc["ticket_id"]) for _, inc in tickets.iterrows()]
    selected_id = st.selectbox("Select incident to delete", ticket_ids)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.warning(f"Delete Ticket {selected_id}? This cannot be undone.")

    with col2:
        if st.button("Delete", type="primary"):
            Tickets.delete_ticket(conn, selected_id)  # your DB function
            st.success("Incident deleted.")
            st.rerun()

with analytics_tab:
    conn = connect_database()

    st.subheader("Service Desk Performance")

    # Staff performance anomaly
    staff_df = Tickets.get_ticket_perf_by_staff(conn)
    st.markdown("#### Average Resolution Time by Staff (hours)")
    st.dataframe(staff_df, use_container_width=True)

    st.bar_chart(
        staff_df.set_index("assigned_to")["avg_hours_to_resolve"],
        use_container_width=True
    )

    # Process / status bottleneck
    status_df = Tickets.get_ticket_perf_by_status(conn)
    st.markdown("#### Average Resolution Time by Status (hours)")
    st.dataframe(status_df, use_container_width=True)

    st.bar_chart(
        status_df.set_index("status")["avg_hours"],
        use_container_width=True
    )
with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input("Your OpenAI API key", type="password")
    # Get user input
    prompt = st.chat_input("Say	something...")

    if api_key:
        # Create OpenAI client from the key STRING
        client = OpenAI(api_key=api_key)

        #	Page	title
        st.title("🛡 IT Operations AI	Assistant")
        st.caption("Powered by GPT-5-nano")

        TICKETS_KEY = "tickets_messages"

        #	Initialize	session	state	for	messages
        if TICKETS_KEY not in st.session_state:
            st.session_state[TICKETS_KEY] = [
                {
                    "role": "system",
                    "content": """You are an IT operations expert. 
                    Help troubleshoot issues, optimize systems, manage tickets, and provide infrastructure guidance. 
                    Focus on practical solutions.
                    Tone: Professional, technical
                    Format: Clear, structured responses"""
                }
            ]
        messages  = st.session_state[TICKETS_KEY]
        # Sidebar with controls
        with st.sidebar:
            st.subheader("Chat controls")

            #	Display	message	count
            message_count = len([m for m in messages if m["role"] != "system"])
            st.metric("Messages", message_count)

            # Clear chat button
            if st.button("🗑 Clear	Chat", use_container_width=True):
                st.session_state[TICKETS_KEY] = []
                st.rerun()

        # Display all previous messages
        for message in messages:
            if message["role"] != "system":  # Don't display system prompt
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


        if prompt:
            #	Display	user	message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to session state
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Call OpenAI API (with streaming)
            with st.spinner("Thinking..."):
                completion = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=messages,
                    stream=True  # Enable streaming (response appears word by word)
                    # Returns a generator instead of complete response
                )

            # Display streaming response
            with st.chat_message("assistant"):
                container = st.empty()  # Create empty container(placeholder) to update
                full_reply = ""  # string to accumulate the full response

                # Process each chunk as it arrives
                for chunk in completion:  # Loop through each chunk of response
                    delta = chunk.choices[0].delta  # Get the new content
                    if delta.content:  # Check if chunk has content
                        full_reply += delta.content  # Add to full response (connects the new text in each chunk)
                        container.markdown(full_reply + "▌")  # Update display with current text

                    # Remove cursor and show final response
                    container.markdown(full_reply)

            # save complete response to session state
            messages.append({
                "role": "assistant",
                "content": full_reply
            })

    else:
        st.info("Enter your OpenAI API key to start chatting.")
