import streamlit as st
import requests
import uuid

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Streamlit page configuration
st.set_page_config(page_title="LLM Chat Interface", layout="centered")
st.title("LLM-based RAG Search")
st.markdown("Ask a question and get answers powered by our LLM backend.")

# Container for chat history
chat_container = st.container()

# Input form for query
with st.form(key="query_form", clear_on_submit=True):
    query = st.text_input("Enter your question:", placeholder="Type your question here...")
    submit_button = st.form_submit_button("Send")

# Function to send query to backend
def send_query_to_backend(query_text):
    url = "http://localhost:5001/query"  # Adjust URL if your backend runs elsewhere
    payload = {"query": query_text}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Backend request failed: {str(e)}"}

# Handle form submission
if submit_button and query.strip():
    with st.spinner("Processing your query..."):
        # Send query to backend
        result = send_query_to_backend(query)
        
        # Process response
        if "error" in result:
            error_message = f"Error: {result['error']}"
            st.error(error_message)
            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "query": query,
                "answer": error_message,
                "articles": []
            })
        else:
            answer = result.get("answer", "No answer received.")
            articles = result.get("articles", [])
            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "query": query,
                "answer": answer,
                "articles": articles
            })

# Display chat history
with chat_container:
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            # User query
            with st.chat_message("user"):
                st.markdown(f"**You**: {chat['query']}")
            # AI response
            with st.chat_message("assistant"):
                st.markdown(f"**AI**: {chat['answer']}")
                # Display Processing Details with links
                if chat['articles']:
                    st.markdown("**Processing Details:**")
                    for article in chat['articles']:
                        if "title" in article and "link" in article:
                            st.markdown(f"- Processing link: [{article['title']}]({article['link']})")
                        else:
                            st.write("Invalid article format:", article)
                else:
                    st.write("All processed details are given above.")
    else:
        st.info("No conversation history yet. Ask a question to start!")

# Add a button to clear chat history
if st.button("Clear Conversation"):
    st.session_state.chat_history = []
    st.success("Conversation history cleared!")