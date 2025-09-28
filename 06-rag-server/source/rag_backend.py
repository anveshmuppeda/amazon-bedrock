# RAG Backend: Document Processing and Question Answering System
# This file handles: PDF loading → Text chunking → Embeddings → Vector search → LLM response

import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_community.vectorstores import FAISS
from langchain.indexes import VectorstoreIndexCreator

def create_document_search_engine():
    """
    PHASE 1: Document Processing (Runs once at startup)
    
    This function creates a "search engine" from PDF documents:
    1. Loads all PDFs from docs/ folder
    2. Splits text into small chunks (1000 characters each)
    3. Converts text chunks to numerical vectors using Amazon Titan
    4. Stores vectors in FAISS database for fast similarity search
    5. Returns a complete search engine that remembers everything
    """
    
    # Step 1: Load all PDF files from the docs/ folder
    pdf_loader = DirectoryLoader('docs/', glob="*.pdf", loader_cls=PyPDFLoader)
    
    # Step 2: Split long documents into smaller, manageable chunks
    # Why? LLMs work better with smaller pieces of context
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],  # Split on paragraphs, then lines, then words
        chunk_size=1000,    # Each chunk = 1000 characters
        chunk_overlap=20    # 20 characters overlap between chunks (prevents losing context)
    )
    
    # Step 3: Create embedding model connection to Amazon Titan
    # This model converts text to 1536 numerical values (vectors)
    embedding_model = BedrockEmbeddings(
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        model_id=os.getenv('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1'),  # Amazon's text-to-vector model
    )
    
    # Step 4: Create the complete search engine
    # This combines: text splitter + embedding model + vector database
    search_engine_creator = VectorstoreIndexCreator(
        text_splitter=text_splitter,
        embedding=embedding_model,      # Titan model for converting text to vectors
        vectorstore_cls=FAISS          # Fast vector similarity search database
    )
    
    # Step 5: Process all documents and create the searchable index
    # This does the heavy work: loads PDFs → splits text → creates embeddings → stores in FAISS
    document_search_engine = search_engine_creator.from_loaders([pdf_loader])
    
    # Return the complete search engine (contains documents, vectors, and search capability)
    return document_search_engine

def create_answer_generator():
    """
    Creates the AI model that will generate answers based on retrieved context
    
    Uses Claude 3 Sonnet - Amazon's advanced language model
    Temperature 0.1 = more focused, less creative responses
    """
    
    answer_generator = ChatBedrock(
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),  # Claude 3 Sonnet model
        model_kwargs={
            "max_tokens": 3000,    # Maximum response length
            "temperature": 0.1,    # Low creativity (more factual)
            "top_p": 0.9          # Focus on most likely words
        }
    )
    
    return answer_generator

def get_rag_answer(search_engine, user_question):
    """
    PHASE 2: Question Answering (Runs every time user asks a question)
    
    This is where the RAG magic happens:
    1. Takes user's question (text)
    2. Converts question to vector using SAME Titan model from search_engine
    3. Searches document vectors for most similar chunks
    4. Combines question + relevant document chunks
    5. Sends combined context to Claude 3 for answer generation
    6. Returns AI-generated answer based on your documents
    
    Args:
        search_engine: The document search engine created by create_document_search_engine()
        user_question: The question typed by user (e.g., "What is leave policy?")
    
    Returns:
        AI-generated answer based on relevant document content
    """
    
    # Create the answer generator (Claude 3)
    answer_generator = create_answer_generator()
    
    # The magic happens here! search_engine.query() does:
    # 1. Converts user_question to vector using stored Titan model
    # 2. Searches FAISS database for similar document vectors
    # 3. Retrieves most relevant text chunks
    # 4. Combines question + context and sends to Claude 3
    # 5. Returns generated answer
    rag_answer = search_engine.query(question=user_question, llm=answer_generator)
    
    return rag_answer

