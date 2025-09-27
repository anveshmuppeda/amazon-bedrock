import streamlit as st 
import chatbot_backend as backend

st.title("Amazon Bedrock Chatbot 🤖")

# Initialize chat memory
if 'chat_memory' not in st.session_state: 
    st.session_state.chat_memory = backend.create_chat_memory()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history: 
    with st.chat_message(message["role"]): 
        st.markdown(message["text"]) 

# Chat input
user_input = st.chat_input("Ask me anything...")
if user_input: 
    # Display user message
    with st.chat_message("user"): 
        st.markdown(user_input) 
    st.session_state.chat_history.append({"role":"user", "text":user_input}) 

    # Get AI response
    ai_response = backend.get_ai_response(user_input, st.session_state.chat_memory)
    
    # Display AI response
    with st.chat_message("assistant"): 
        st.markdown(ai_response) 
    st.session_state.chat_history.append({"role":"assistant", "text":ai_response}) 