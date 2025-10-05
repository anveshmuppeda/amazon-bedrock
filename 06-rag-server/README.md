# 📚 RAG Server - Document Q&A with Amazon Bedrock

**Level:** Advanced | **Duration:** 75 minutes | **Cost:** ~$4.00

Build a production-ready Retrieval-Augmented Generation (RAG) system that enables intelligent Q&A over your documents using Amazon Bedrock, LangChain, and FAISS vector database.

## 🎯 What You'll Build

- **Document Processing Pipeline** that converts PDFs to searchable vectors
- **Intelligent Q&A System** that answers questions based on document content
- **Vector Search Engine** using FAISS for fast similarity matching
- **RAG Architecture** combining retrieval and generation
- **Production Deployment** on AWS ECS with complete infrastructure

## 🏗️ RAG Architecture Flow

```
📄 PDF Documents → 🔪 Text Chunking → 🔢 Embeddings → 🗄️ Vector DB → 🔍 Search → 🤖 AI Answer
     ↓                    ↓                ↓              ↓           ↓         ↓
  Load PDFs        Split into chunks   Titan Embeddings   FAISS     Similarity  Claude 3
                   (1000 chars)       (1536 dimensions)  Database   Matching   Generation
```

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [RAG Implementation Deep Dive](#-rag-implementation-deep-dive)
- [Step-by-Step Guide](#-step-by-step-guide)
- [Example Flows](#-example-flows)
- [Local Development](#-local-development)
- [AWS Deployment](#-aws-deployment)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Cost Optimization](#-cost-optimization)

## ✅ Prerequisites

### Required Tools
```bash
# AWS CLI v2
aws --version

# AWS CDK
npm install -g aws-cdk
cdk --version

# Python 3.11+
python --version

# Docker
docker --version
```

### AWS Account Setup
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI configured with credentials
- ✅ Amazon Bedrock model access enabled
- ✅ ECR repository permissions
- ✅ ECS and VPC permissions

### Enable Bedrock Models
1. Navigate to Amazon Bedrock Console
2. Go to "Model access" → "Enable specific models"
3. Enable: 
   - `anthropic.claude-3-sonnet-20240229-v1:0` (for text generation)
   - `amazon.titan-embed-text-v1` (for embeddings)
4. Wait for approval (usually immediate)

## 📁 Project Structure

```
06-rag-server/
├── source/                     # Application source code
│   ├── rag_backend.py          # RAG processing logic
│   ├── rag_frontend.py         # Streamlit UI
│   └── docs/                   # PDF documents folder
│       └── Leave-Policy-India.pdf  # Sample document
├── rag-server/                 # CDK infrastructure
│   ├── app.py                  # CDK app entry point
│   └── rag_server/
│       ├── rag_ecr_stack.py    # ECR repository
│       └── rag_ecs_stack.py    # ECS service & ALB
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Local development
├── requirements.txt            # Python dependencies
└── README.md                   # This guide
```

## 🔧 RAG Implementation Deep Dive

### Phase 1: Document Processing (`create_document_search_engine()`)

#### 1. **PDF Loading**
```python
# Load all PDFs from docs/ folder
pdf_loader = DirectoryLoader('docs/', glob="*.pdf", loader_cls=PyPDFLoader)
```

**What happens:**
- Scans `docs/` folder for all PDF files
- Uses PyPDFLoader to extract text from each PDF
- Maintains document metadata (filename, page numbers)

#### 2. **Text Chunking**
```python
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],  # Split hierarchy
    chunk_size=1000,    # Each chunk = 1000 characters
    chunk_overlap=20    # 20 characters overlap
)
```

**Why chunking is crucial:**
- **LLM Context Limits**: Models have token limits (Claude 3: ~200K tokens)
- **Relevance**: Smaller chunks = more precise retrieval
- **Overlap**: Prevents losing context at chunk boundaries

**Chunking Process:**
1. **Primary Split**: Paragraphs (`\n\n`)
2. **Secondary Split**: Lines (`\n`)
3. **Tertiary Split**: Sentences (`. `)
4. **Final Split**: Words (` `)

#### 3. **Embedding Generation**
```python
embedding_model = BedrockEmbeddings(
    model_id='amazon.titan-embed-text-v1',  # 1536-dimensional vectors
    region_name='us-east-1'
)
```

**Titan Embedding Process:**
- **Input**: Text chunk (up to 8192 tokens)
- **Output**: 1536-dimensional vector
- **Purpose**: Convert text to numerical representation for similarity search

#### 4. **Vector Database Creation**
```python
search_engine_creator = VectorstoreIndexCreator(
    text_splitter=text_splitter,
    embedding=embedding_model,
    vectorstore_cls=FAISS  # Fast similarity search
)
```

**FAISS Database:**
- **Storage**: All document vectors in memory
- **Search**: Cosine similarity for finding relevant chunks
- **Speed**: Optimized for fast nearest neighbor search

### Phase 2: Question Answering (`get_rag_answer()`)

#### 1. **Question Embedding**
```python
# User question converted to same 1536-dimensional space
question_vector = embedding_model.embed_query(user_question)
```

#### 2. **Similarity Search**
```python
# FAISS finds most similar document chunks
relevant_chunks = vector_db.similarity_search(question_vector, k=4)
```

**Search Process:**
- **Input**: Question vector (1536 dimensions)
- **Comparison**: Cosine similarity with all document vectors
- **Output**: Top 4 most relevant text chunks
- **Ranking**: Highest similarity scores first

#### 3. **Context Assembly**
```python
# Combine question + relevant chunks into prompt
context = "\n".join([chunk.page_content for chunk in relevant_chunks])
prompt = f"Context: {context}\n\nQuestion: {user_question}\n\nAnswer:"
```

#### 4. **Answer Generation**
```python
answer_generator = ChatBedrock(
    model_id='anthropic.claude-3-sonnet-20240229-v1:0',
    model_kwargs={
        "max_tokens": 3000,
        "temperature": 0.1,  # Low creativity for factual answers
        "top_p": 0.9
    }
)
```

**Claude 3 Processing:**
- **Input**: Question + relevant document context
- **Processing**: Generates answer based only on provided context
- **Output**: Factual answer grounded in documents

## 🚀 Step-by-Step Guide

### Phase 1: Local Development Setup

#### 1. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock/06-rag-server

# Create virtual environment
python -m venv rag-env
source rag-env/bin/activate  # Windows: rag-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure AWS Credentials
```bash
# Configure AWS CLI
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)

# Verify configuration
aws sts get-caller-identity
```

#### 3. Test Bedrock Access
```bash
# Test embedding model
aws bedrock invoke-model \
    --model-id "amazon.titan-embed-text-v1" \
    --body '{"inputText":"Hello world"}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    embedding-output.json

# Test Claude model
aws bedrock invoke-model \
    --model-id "anthropic.claude-3-sonnet-20240229-v1:0" \
    --body '{"messages":[{"role":"user","content":[{"text":"Hello"}]}],"max_tokens":100}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    claude-output.json
```

#### 4. Add Your Documents
```bash
# Navigate to docs folder
cd source/docs

# Add your PDF files (replace or add to existing)
cp /path/to/your/document.pdf .

# Verify documents
ls -la *.pdf
```

### Phase 2: Local Testing

#### 1. Run with Docker Compose (Recommended)
```bash
# Start the application
docker-compose up --build

# Access application
open http://localhost:8501
```

#### 2. Run Locally (Development)
```bash
# Navigate to source directory
cd source

# Set environment variables
export AWS_DEFAULT_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
export BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Run Streamlit
streamlit run rag_frontend.py
```

### Phase 3: AWS Deployment

#### 1. Bootstrap CDK (First Time Only)
```bash
cd rag-server
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-east-1
```

#### 2. Deploy ECR Repository
```bash
# Deploy ECR stack
cdk deploy RagEcrStack

# Note the ECR repository URI from output
```

#### 3. Build and Push Docker Image
```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
docker login --username AWS --password-stdin \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build for Linux/AMD64 (required for ECS)
docker build --platform linux/amd64 -t rag-ecr-repository:latest .

# Tag for ECR
docker tag rag-ecr-repository:latest \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/rag-ecr-repository:latest

# Push to ECR
docker push \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/rag-ecr-repository:latest
```

#### 4. Deploy ECS Infrastructure
```bash
# Deploy ECS stack
cdk deploy RagEcsStack

# Note the LoadBalancer DNS from output
```

## 📊 Example Flows

### Example 1: Leave Policy Query

**Document Content** (Leave-Policy-India.pdf):
```
Annual Leave: Employees are entitled to 21 days of annual leave per calendar year.
Sick Leave: 12 days of sick leave are provided annually.
Maternity Leave: 26 weeks of maternity leave as per Indian law.
```

**User Question**: "How many annual leave days do I get?"

**RAG Process Flow:**

1. **Question Embedding**:
   ```
   "How many annual leave days do I get?" → [0.1, -0.3, 0.8, ..., 0.2] (1536 dims)
   ```

2. **Document Chunks** (created during startup):
   ```
   Chunk 1: "Annual Leave: Employees are entitled to 21 days..." → [0.2, -0.1, 0.7, ..., 0.3]
   Chunk 2: "Sick Leave: 12 days of sick leave are provided..." → [-0.1, 0.4, 0.2, ..., 0.1]
   Chunk 3: "Maternity Leave: 26 weeks of maternity leave..." → [0.3, 0.1, -0.2, ..., 0.4]
   ```

3. **Similarity Search**:
   ```
   Question vector vs Chunk 1: Similarity = 0.89 ✅ (High match)
   Question vector vs Chunk 2: Similarity = 0.34
   Question vector vs Chunk 3: Similarity = 0.12
   ```

4. **Context Assembly**:
   ```
   Context: "Annual Leave: Employees are entitled to 21 days of annual leave per calendar year."
   Question: "How many annual leave days do I get?"
   ```

5. **Claude 3 Response**:
   ```
   "Based on the leave policy, employees are entitled to 21 days of annual leave per calendar year."
   ```

### Example 2: Complex Multi-Document Query

**User Question**: "What's the difference between sick leave and annual leave policies?"

**RAG Process:**

1. **Retrieval**: Finds chunks about both sick leave AND annual leave
2. **Context**: Multiple relevant chunks combined
3. **Answer**: Comparative analysis based on document content

**Expected Response**:
```
Based on the leave policy:

Annual Leave: 21 days per calendar year
Sick Leave: 12 days per year

The key differences are:
- Annual leave provides more days (21 vs 12)
- Annual leave is for planned time off
- Sick leave is specifically for health-related absences
```

### Example 3: Information Not in Documents

**User Question**: "What's the weather like today?"

**RAG Process:**

1. **Retrieval**: No relevant chunks found (low similarity scores)
2. **Context**: Empty or irrelevant context
3. **Claude Response**: "I can only answer questions based on the provided documents. I don't have information about current weather."

## 🧪 Testing

### Functional Tests

#### 1. **Document Processing Test**
```bash
# Check if documents are loaded
curl http://localhost:8501/_stcore/health

# Verify in logs
docker logs [container-id] | grep "Document search engine ready"
```

#### 2. **Embedding Generation Test**
```python
# Test embedding creation
from rag_backend import create_document_search_engine
search_engine = create_document_search_engine()
print("✅ Embeddings created successfully")
```

#### 3. **Question-Answer Test**
```python
# Test Q&A functionality
from rag_backend import get_rag_answer, create_document_search_engine

search_engine = create_document_search_engine()
answer = get_rag_answer(search_engine, "What is the leave policy?")
print(f"Answer: {answer}")
```

### Performance Tests

#### 1. **Response Time Test**
```bash
# Measure response time
time curl -X POST http://localhost:8501/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is annual leave?"}'
```

#### 2. **Memory Usage Test**
```bash
# Monitor memory during document processing
docker stats [container-id]
```

#### 3. **Concurrent Users Test**
```bash
# Simulate multiple users
for i in {1..5}; do
  curl -X POST http://localhost:8501/ \
    -H "Content-Type: application/json" \
    -d '{"question": "Question '$i'"}' &
done
```

### Accuracy Tests

#### 1. **Factual Accuracy**
- Ask questions with known answers from documents
- Verify responses match document content
- Check for hallucinations (made-up information)

#### 2. **Retrieval Quality**
- Test edge cases (very specific questions)
- Verify relevant chunks are retrieved
- Check similarity scores

## 🔧 Troubleshooting

### Common Issues

#### 1. **Document Loading Failures**
```
Error: No PDF files found in docs/
Solution: Ensure PDFs are in source/docs/ folder
```

#### 2. **Embedding Model Access**
```
Error: AccessDeniedException for titan-embed-text-v1
Solution: Enable Titan embedding model in Bedrock console
```

#### 3. **Memory Issues**
```
Error: Out of memory during FAISS indexing
Solution: Reduce chunk_size or increase container memory
```

#### 4. **Slow Response Times**
```
Issue: Long delays in answer generation
Solutions:
- Reduce number of retrieved chunks (k=2 instead of k=4)
- Optimize chunk size
- Use smaller embedding model
```

### Debug Commands

```bash
# Check document processing
docker exec -it [container-id] ls -la docs/

# Verify embeddings
docker exec -it [container-id] python -c "
from rag_backend import create_document_search_engine
engine = create_document_search_engine()
print('Embeddings created successfully')
"

# Test Bedrock connectivity
aws bedrock list-foundation-models --region us-east-1

# Check ECS service health
aws ecs describe-services \
    --cluster rag-ecs-cluster \
    --services rag-ecs-service
```

## 💰 Cost Optimization

### Estimated Costs (Monthly)

| Component | Cost | Usage |
|-----------|------|-------|
| **ECS Fargate** | ~$15 | 1 task, 0.5 vCPU, 1GB RAM |
| **Application Load Balancer** | ~$18 | Standard ALB |
| **Bedrock Embeddings** | ~$8 | 10K embedding calls |
| **Bedrock Claude 3** | ~$12 | 1K Q&A interactions |
| **CloudWatch Logs** | ~$2 | Standard logging |
| **Total** | **~$55/month** | Light usage |

### Cost Reduction Tips

1. **Batch Processing**: Process documents in batches to reduce API calls
2. **Caching**: Cache embeddings to avoid regeneration
3. **Model Selection**: Use smaller models for development
4. **Auto Scaling**: Scale down during low usage periods

### Cleanup Resources

```bash
# Destroy ECS stack
cdk destroy RagEcsStack

# Destroy ECR stack
cdk destroy RagEcrStack

# Verify cleanup
aws ecs list-clusters
aws ecr describe-repositories
```

## 🎯 Key Learning Outcomes

After completing this guide, you'll understand:

- ✅ **RAG Architecture**: How retrieval and generation work together
- ✅ **Vector Embeddings**: Converting text to numerical representations
- ✅ **Similarity Search**: Finding relevant content using vector math
- ✅ **Document Processing**: PDF loading, chunking, and indexing
- ✅ **Production Deployment**: Scalable RAG systems on AWS
- ✅ **Performance Optimization**: Balancing accuracy and speed

## 🔗 Related Guides

- **[04-generate-embedding](../04-generate-embedding/)**: Text embeddings fundamentals
- **[05-chatbot](../05-chatbot/)**: Conversational AI with memory
- **[02-image-generation](../02-image-generation/)**: AI image generation

## 📚 Additional Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://faiss.ai/)
- [RAG Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/rag.html)

---

**Ready to build your intelligent document Q&A system?** Start with [local development](#phase-1-local-development-setup) and create your own knowledge base! 📚🤖