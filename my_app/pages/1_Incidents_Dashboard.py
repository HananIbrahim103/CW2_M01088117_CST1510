import streamlit as st
from openai import OpenAI
from app.data.db import connect_database
from app.data.incidents import Incident

st.set_page_config(
    page_title="Incident Dashboard",
    page_icon="🚨",
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
st.title("🚨 Cyber Incidents Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

incident_tab, analytics_tab, AI_tab = st.tabs(["Incidents", "Analytics", "AI Assistant"])

with incident_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Read and display the database as a table
    incidents = Incident.get_all_incidents(conn)
    st.dataframe(incidents, use_container_width=True)

    # Add new incidents to the database with a form
    with st.form("new_incident"):
        # Form inputs
        description = st.text_input("Incident Description")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        category = st.selectbox("Category", ["Phishing", "DDos", "Malware", "Unauthorized Access", "Misconfiguration"])
        # Form submit button
        submitted = st.form_submit_button("Add Incident")

    # When form is submitted
    if submitted:
        if description:
            Incident(severity=severity, category=category, status=status, description=description).insert_incident()
            st.success("✓ Incident added successfully!")
            st.rerun()  # Refresh the page to show new incident
        else:
            st.error("You must fill in all the fields")

    # Update form
    with st.form("update_status"):
        incident_id = st.text_input("Incident ID")
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        update = st.form_submit_button("Update")

    # When the form is submitted
    if update:
        if incident_id:
            Incident.update_incident_status(conn, incident_id, new_status)
            st.rerun()
        else:
            st.error("You must select an Incident ID.")

    # Delete Incident
    incident_ids = [str(inc["incident_id"]) for _, inc in incidents.iterrows()]
    selected_id = st.selectbox("Select incident to delete", incident_ids)

    col1, col2 = st.columns([2, 1])

    # Display a warning message
    with col1:
        st.warning(f"Delete incident {selected_id}? This cannot be undone.")

    with col2:
        if st.button("Delete", type="primary"):
            Incident.delete_incident(selected_id)
            st.success("Incident deleted.")
            st.rerun()

with analytics_tab:
    total, open_count, critical, phishing_total = Incident.compute_incident_metrics(conn)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Incidents", total, delta=+25)

    with col2:
        st.metric("Open Incidents", open_count, delta=+10)

    with col3:
        st.metric("Critical Incidents", critical, delta=-1)


    st.subheader("📊 Attack Types Overview")
    df_attacks =Incident.get_incidents_by_type_count(conn)
    st.bar_chart(
        df_attacks,
        x="category",
        y="count"
    )

    st.subheader("📈 Phishing attack Trends Over Time")
    df_trends = Incident.get_daily_phishing_counts(conn)
    st.line_chart(df_trends, x="date", y="count")


with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input(
        "Your OpenAI API key",
        type="password"
    )
    # Create OpenAI client from the key STRING
    client = OpenAI(api_key=api_key)

    st.title("🔍 AI Incident Analyzer")

    conn = connect_database()
    incidents = Incident.get_all_incidents(conn)

    if incidents is None or len(incidents) == 0:
        st.info("No incidents found in the database.")
    else:
        # build options from dataframe rows
        incident_options = [
            f"{row['incident_id']}: {row['category']} - {row['severity']}"
            for _, row in incidents.iterrows()
        ]

        selected_idx = st.selectbox(
            "Select incident to analyze:",
            range(len(incidents)),
            format_func=lambda i: incident_options[i]
        )

        # get the selected row as a dict-like object
        incident = incidents.iloc[selected_idx]

        st.subheader("📋 Incident Details")
        st.write(f"**Type:** {incident['category']}")
        st.write(f"**Severity:** {incident['severity']}")
        st.write(f"**Description:** {incident['description']}")
        st.write(f"**Status:** {incident['status']}")

        if st.button("🤖 Analyze with AI", type="primary"):
            with st.spinner("AI analyzing incident..."):
                analysis_prompt = f"""Analyze this cybersecurity incident:

                                Type: {incident['category']}
                                Severity: {incident['severity']}
                                Description: {incident['description']}
                                Status: {incident['status']}

                                Provide:
                                1. Root cause analysis
                                2. Immediate actions needed
                                3. Long-term prevention measures
                                4. Risk assessment"""
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity expert.Analyse incidents and threats.Format: Clear, structured responses"},
                        {"role": "user", "content": analysis_prompt}
                    ]
                )

                st.subheader("🧠 AI Analysis")
                st.write(response.choices[0].message.content)


