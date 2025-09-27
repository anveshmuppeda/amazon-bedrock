# AWS Bedrock Chatbot

A Streamlit-based chatbot application using AWS Bedrock and LangChain.

## Quick Start

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

### Using Docker
```bash
# Build the image
docker build -t bedrock-chatbot .

# Run the container
docker run -p 8501:8501 -v ~/.aws:/root/.aws:ro bedrock-chatbot
```

### Local Development
```bash
pip install -r requirements.txt
streamlit run chatbot_frontend.py
```

## Access
Open http://localhost:8501 in your browser

## Prerequisites
- AWS credentials configured
- Access to AWS Bedrock models
- Docker installed