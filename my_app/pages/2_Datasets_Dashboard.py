import streamlit as st
from app.data.datasets import Dataset
from app.data.db import connect_database
from openai import OpenAI
import plotly.express as px




st.set_page_config(
    page_title="Dataset Dashboard",
    page_icon="📊",
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
st.title("📊 Dataset Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

dataset_tab, analytics_tab, AI_tab = st.tabs(["Datasets", "Analytics", "AI Assistant"])

with dataset_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Display datasets in a table
    datasets = Dataset.get_all_datasets(conn)
    st.dataframe(datasets, use_container_width=True)

    #Add new dataset with a form
    with st.form("new_dataset"):
        # Form inputs (Streamlit widgets)
        name = st.text_input("Name")
        rows = st.text_input("Number of rows")
        columns = st.text_input("Number of columns")
        uploaded_by = st.selectbox("Uploaded by", ["data_scientist", "cyber_admin", "it_admin"])
        upload_date = st.date_input("Date")
        # Form submit button
        submitted = st.form_submit_button("Add Dataset")

    # When form is submitted
    if submitted and name and rows and columns and uploaded_by and upload_date:
        # Call Week 8 function to insert into database
        Dataset(name=name, rows=rows, columns=columns, uploaded_by=uploaded_by, upload_date=upload_date).insert_dataset()
        st.success("✓ Dataset added successfully!")
        st.rerun()  # Refresh the page to show new dataset
    else:
        st.error("You must fill in all the fields")

    # Update form
    with st.form("Update rows and columns"):
        dataset_id = st.text_input("Dataset ID")
        new_rows = st.text_input("Rows")
        new_columns = st.text_input("Columns")
        update = st.form_submit_button("Update")

    if dataset_id and update and new_rows:
        Dataset.update_dataset_rows_and_columns(conn, dataset_id, new_rows, new_columns)
        st.rerun()
    else:
        st.error("You must fill in all fields.")

    dataset_ids = [str(inc["dataset_id"]) for _, inc in datasets.iterrows()]
    selected_id = st.selectbox("Select dataset to delete", dataset_ids)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.warning(f"Delete Dataset {selected_id}? This cannot be undone.")

    with col2:
        if st.button("Delete", type="primary"):
            Dataset.delete_dataset(conn, selected_id)  # your DB function
            st.success("Dataset deleted.")
            st.rerun()

with analytics_tab:
    df, total_datasets, total_rows, avg_columns = Dataset.get_dataset_metrics(conn)

    c1, c2, c3 = st.columns(3)
    c1.metric("Datasets", total_datasets)
    c2.metric("Total Rows", f"{total_rows:,}")
    c3.metric("Avg Columns per Dataset", f"{avg_columns:.1f}")

    # Bar chart to show which department consumes the most storage
    st.markdown("#### Data Volume by Department")

    by_owner = df.groupby("uploaded_by")["rows"].sum().reset_index()
    by_owner = by_owner.set_index("uploaded_by")

    st.bar_chart(by_owner, use_container_width=True)

    # Pie chart using plotly
    df = Dataset.count_datasets_grouped_by_uploaded_by(conn)

    if df.empty:
        st.info("No datasets found.")
    else:
        fig = px.pie(
            df,
            names="uploaded_by",
            values="count",
            title="Datasets by uploader"
        )
        st.plotly_chart(fig, use_container_width=True)


with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input("Your OpenAI API key", type="password")

    if api_key:
        # Create OpenAI client from the key STRING
        client = OpenAI(api_key=api_key)

        # Page configuration
        st.set_page_config(
            page_title="ChatGPT	Assistant",
            page_icon="💬",
            layout="wide"
        )

        #	Page	title
        st.title("🛡 Datascience AI	Assistant")
        st.caption("Powered by GPT-5-nano")

        #	Initialize	session	state	for	messages
        if 'messages' not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": """You are a data science expert. 
                    Help with data analysis, visualization, statistical methods, and machine learning. 
                    Explain concepts clearly and suggest appropriate techniques.
                    Tone: Professional, technical
                    Format: Clear, structured responses"""
                }
            ]

        # Sidebar with controls
        with st.sidebar:
            st.subheader("Chat controls")

            #	Display	message	count
            message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
            st.metric("Messages", message_count)

            # Clear chat button
            if st.button("🗑 Clear	Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

            # Model selection
            model = st.selectbox(
                "Model",
                ["gpt-4o", "gpt-5-nano"],
                index=0
            )

            # Temperature slider
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="Higher values make output more random"
            )

        # Display all previous messages
        for message in st.session_state.messages:
            if message["role"] != "system":  # Don't display system prompt
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Get user input
        prompt = st.chat_input("Say	something...")

        if prompt:
            #	Display	user	message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to session state
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            # Call OpenAI API (with streaming)
            with st.spinner("Thinking..."):
                completion = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=st.session_state.messages,
                    temperature=temperature,
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
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_reply
            })

    else:
        st.info("Enter your OpenAI API key to start chatting.")


