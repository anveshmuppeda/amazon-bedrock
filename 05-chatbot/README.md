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


# Method 1: Build with explicit platform flag (Recommended)
docker build --platform linux/amd64 -t ecs-devops-repository .

# Method 2: Build and tag for ECR with platform
docker build --platform linux/amd64 -t ecs-devops-repository:latest .
docker tag ecs-devops-repository:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ecs-devops-repository:latest

# Method 3: Use buildx for multi-platform builds (if needed)
docker buildx build --platform linux/amd64 -t ecs-devops-repository:latest .

# Complete deployment workflow:

# 1. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 2. Build for Linux/AMD64 platform
docker build --platform linux/amd64 -t ecs-devops-repository:latest .

# 3. Tag for ECR
docker tag ecs-devops-repository:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ecs-devops-repository:latest

# 4. Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ecs-devops-repository:latest

# Alternative: One-liner build and tag
docker build --platform linux/amd64 -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/ecs-devops-repository:latest .

# For Apple Silicon Macs (M1/M2), you might also want to check current platform
docker info | grep "Server Platform"

# Verify the image architecture after building
docker inspect ecs-devops-repository:latest | grep Architecture