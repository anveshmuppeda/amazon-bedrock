"""
RAG Chatbot Frontend - Streamlit Web Interface

This creates a simple web interface where users can:
1. Ask questions about documents
2. Get AI-powered answers based on document content
3. See the RAG (Retrieval-Augmented Generation) system in action
"""

import streamlit as st 
import rag_backend as rag_system  # Our document processing and AI backend

# Configure the web page
st.set_page_config(
    page_title="Document Q&A with RAG",
    page_icon="🤖",
    layout="wide"
)

# Create attractive title
page_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">📚 Document Q&A with RAG 🤖</p>'
st.markdown(page_title, unsafe_allow_html=True)

# Add explanation for users
st.markdown("""
**How it works:**
- 📄 System loads and processes all PDFs from `docs/` folder
- 🔍 Your questions are matched against document content
- 🤖 AI generates answers based on relevant document sections
- ✅ Get accurate, document-specific responses (not general knowledge)
""")

# PHASE 1: One-time setup - Create document search engine
# This happens only once when the app starts or refreshes
if 'document_search_engine' not in st.session_state:
    with st.spinner("🔄 Processing documents... Creating search engine from your PDFs"):
        # This calls create_document_search_engine() which:
        # 1. Loads all PDFs from docs/ folder
        # 2. Splits text into chunks
        # 3. Converts chunks to vectors using Amazon Titan
        # 4. Stores vectors in FAISS database
        # 5. Returns complete search engine
        st.session_state.document_search_engine = rag_system.create_document_search_engine()
        st.success("✅ Document search engine ready! You can now ask questions.")

# PHASE 2: User interaction - Question and Answer
st.subheader("💬 Ask a question about your documents:")

# Text input for user question
user_question = st.text_area(
    "Type your question here...",
    placeholder="Example: What is the leave policy? How many vacation days do I get?",
    height=100,
    label_visibility="collapsed"
)

# Submit button
ask_question_button = st.button("🔍 Get Answer from Documents", type="primary")

# Process question when button is clicked
if ask_question_button and user_question.strip():
    with st.spinner("🧠 Searching documents and generating answer..."):
        # This calls get_rag_answer() which:
        # 1. Converts user question to vector (using same Titan model)
        # 2. Searches document vectors for similar content
        # 3. Retrieves most relevant text chunks
        # 4. Combines question + context
        # 5. Sends to Claude 3 for answer generation
        # 6. Returns AI-generated answer based on documents
        ai_answer = rag_system.get_rag_answer(
            search_engine=st.session_state.document_search_engine, 
            user_question=user_question
        )
        
        # Display the answer
        st.subheader("🤖 AI Answer:")
        st.write(ai_answer)
        
elif ask_question_button and not user_question.strip():
    st.warning("⚠️ Please enter a question first!")

# Add helpful information in sidebar
with st.sidebar:
    st.header("📋 System Info")
    st.info("""
    **RAG System Status:**
    - ✅ Documents processed
    - ✅ Vector database ready
    - ✅ AI model connected
    
    **Models Used:**
    - 🔤 Embeddings: Amazon Titan
    - 🧠 AI: Claude 3 Sonnet
    - 🔍 Vector DB: FAISS
    """)
    
    st.header("💡 Tips")
    st.markdown("""
    - Ask specific questions about document content
    - The AI only knows what's in your PDFs
    - For best results, ask clear, focused questions
    """)