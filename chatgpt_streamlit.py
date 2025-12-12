import streamlit	as st
from openai	import OpenAI

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
    st.title("🛡 IT Operations AI	Assistant")
    st.caption("Powered by GPT-5-nano")

    #	Initialize	session	state	for	messages
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content":"""You are an IT operations expert. 
                Help troubleshoot issues, optimize systems, manage tickets, and provide infrastructure guidance. 
                Focus on practical solutions.
                Tone: Professional, technical
                Format: Clear, structured responses"""
            }
        ]

    #Sidebar with controls
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
        temperature=st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Higher values make output more random"
        )

    # Display all previous messages
    for message in st.session_state.messages:
        if message["role"] != "system": # Don't display system prompt
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
                stream=True #Enable streaming (response appears word by word)
                # Returns a generator instead of complete response
            )

        #Display streaming response
        with st.chat_message("assistant"):
            container=st.empty() # Create empty container(placeholder) to update
            full_reply="" # string to accumulate the full response

            #Process each chunk as it arrives
            for chunk in completion: # Loop through each chunk of response
                delta=chunk.choices[0].delta # Get the new content
                if delta.content: #  Check if chunk has content
                    full_reply+=delta.content # Add to full response (connects the new text in each chunk)
                    container.markdown(full_reply + "▌") # Update display with current text

                # Remove cursor and show final response
                container.markdown(full_reply)

        # save complete response to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_reply
        })

else:
    st.info("Enter your OpenAI API key to start chatting.")
