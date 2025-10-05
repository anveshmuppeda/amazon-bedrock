# 🔤 Generate Embeddings with Amazon Titan

**Level:** Intermediate | **Duration:** 45 minutes | **Cost:** ~$1.00

Build a text embedding generation service using Amazon Titan Embeddings G1 model. Convert text into numerical vectors for semantic search, similarity matching, and AI applications.

## 🎯 What You'll Build

- **Text Embedding API** that converts text to 1536-dimensional vectors
- **RESTful Service** with API Gateway and Lambda integration
- **Semantic Search Foundation** for building AI applications
- **Vector Generation Pipeline** for machine learning workflows
- **Production-Ready Infrastructure** with CDK

## 🏗️ Architecture Overview

```
📝 Text Input → 🌐 API Gateway → ⚡ Lambda Function → 🤖 Titan Embeddings → 📊 Vector Output
     ↓              ↓               ↓                    ↓                   ↓
"Hello World"   REST API      Python Handler    Amazon Bedrock      [0.1, -0.3, 0.8, ...]
                                                                    (1536 dimensions)
```

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Implementation Deep Dive](#-implementation-deep-dive)
- [Step-by-Step Guide](#-step-by-step-guide)
- [Example Flows](#-example-flows)
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
```

### AWS Account Setup
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI configured with credentials
- ✅ Amazon Bedrock model access enabled
- ✅ Lambda and API Gateway permissions

### Enable Bedrock Models
1. Navigate to Amazon Bedrock Console
2. Go to "Model access" → "Enable specific models"
3. Enable: `amazon.titan-embed-text-v1`
4. Wait for approval (usually immediate)

## 📁 Project Structure

```
04-generate-embedding/
├── generate-embedding/             # CDK infrastructure
│   ├── app.py                      # CDK app entry point
│   ├── generate_embedding/
│   │   └── generate_embedding_stack.py  # CDK stack definition
│   └── lambda/
│       └── index.py                # Lambda function code
├── requirements.txt                # Python dependencies
└── README.md                       # This guide
```

## 🔧 Implementation Deep Dive

### Lambda Function Architecture (`lambda/index.py`)

#### 1. **Embedding Generation Core**
```python
def generate_embedding(model_id, body):
    """
    Generate vector representation of text using Amazon Titan
    
    Process:
    1. Connect to Bedrock runtime
    2. Send text to Titan Embeddings model
    3. Receive 1536-dimensional vector
    4. Return embedding with metadata
    """
    bedrock = boto3.client(service_name='bedrock-runtime')
    
    response = bedrock.invoke_model(
        body=body, 
        modelId=model_id,
        accept="application/json",
        contentType="application/json"
    )
    
    return json.loads(response.get('body').read())
```

#### 2. **Request Processing**
```python
def lambda_handler(event, context):
    """
    Lambda entry point for embedding generation
    
    Input Processing:
    1. Extract text from API Gateway event
    2. Validate input text
    3. Create Bedrock request body
    4. Generate embedding
    5. Return formatted response
    """
    model_id = "amazon.titan-embed-text-v1"
    input_text = event['input_text']
    
    body = json.dumps({
        "inputText": input_text,
    })
    
    response = generate_embedding(model_id, body)
    
    return {
        'statusCode': 200,
        'body': response
    }
```

### CDK Infrastructure (`generate_embedding_stack.py`)

#### 1. **Lambda Function Configuration**
```python
embedding_generate_function = _lambda.Function(
    self, "EmbeddingGenerationFunction",
    runtime=_lambda.Runtime.PYTHON_3_13,
    function_name="GenerateEmbeddingFunction",
    handler="index.lambda_handler", 
    code=_lambda.Code.from_asset("lambda"),
    timeout=Duration.seconds(300),  # 5 minutes for large texts
)
```

#### 2. **Bedrock Permissions**
```python
embedding_generate_function.add_to_role_policy(iam.PolicyStatement(
    actions=[
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:GetFoundationModel",
        "bedrock:ListFoundationModels"
    ],
    resources=["*"]  # Bedrock requires * for dynamic model ARNs
))
```

#### 3. **API Gateway Setup**
```python
api = apigw.RestApi(
    self, "EmbeddingGenerationAPI",
    rest_api_name="Embedding Generation Service",
    default_cors_preflight_options=apigw.CorsOptions(
        allow_origins=apigw.Cors.ALL_ORIGINS,
        allow_methods=apigw.Cors.ALL_METHODS
    )
)

# Lambda integration with request mapping
lambda_integration = apigw.LambdaIntegration(
    embedding_generate_function,
    request_templates={
        "application/json": '{"input_text": "$input.params(\'input_text\')"}'
    }
)
```

## 🚀 Step-by-Step Guide

### Phase 1: Setup and Configuration

#### 1. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock/04-generate-embedding

# Create virtual environment
python -m venv embedding-env
source embedding-env/bin/activate  # Windows: embedding-env\Scripts\activate

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
# Test Titan Embeddings model access
aws bedrock invoke-model \
    --model-id "amazon.titan-embed-text-v1" \
    --body '{"inputText":"Hello world"}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    embedding-test.json

# Check output
cat embedding-test.json
```

### Phase 2: Deploy Infrastructure

#### 1. Bootstrap CDK (First Time Only)
```bash
cd generate-embedding
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-east-1
```

#### 2. Deploy the Stack
```bash
# Deploy embedding generation service
cdk deploy GenerateEmbeddingStack

# Note the API Gateway URL from output
```

#### 3. Verify Deployment
```bash
# Check Lambda function
aws lambda list-functions --query 'Functions[?FunctionName==`GenerateEmbeddingFunction`]'

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?name==`Embedding Generation Service`]'
```

## 📊 Example Flows

### Example 1: Simple Text Embedding

**Input Text**: "Hello, how are you today?"

**API Request**:
```bash
curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=Hello,%20how%20are%20you%20today?"
```

**Processing Flow**:
1. **API Gateway**: Receives GET request with query parameter
2. **Request Mapping**: Converts to Lambda event format
3. **Lambda Function**: Extracts text and calls Bedrock
4. **Titan Model**: Processes text and generates embedding
5. **Response**: Returns 1536-dimensional vector

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "embedding": [0.123, -0.456, 0.789, ..., 0.321],
    "inputTextTokenCount": 6
  }
}
```

### Example 2: Long Text Processing

**Input Text**: "This is a longer text that demonstrates how the Amazon Titan Embeddings model can process more complex content and generate meaningful vector representations for semantic search applications."

**Processing Details**:
- **Token Count**: ~35 tokens
- **Processing Time**: ~2-3 seconds
- **Vector Dimensions**: 1536 (fixed)
- **Use Cases**: Document similarity, semantic search, clustering

### Example 3: Batch Processing Simulation

**Multiple Texts**:
```bash
# Process multiple texts sequentially
texts=(
  "Machine learning is fascinating"
  "AI will transform the future"
  "Natural language processing"
)

for text in "${texts[@]}"; do
  curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=$text"
done
```

## 🧪 Testing

### Functional Tests

#### 1. **Basic Embedding Generation**
```bash
# Test with simple text
curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=test"

# Expected: 200 status, embedding array, token count
```

#### 2. **Empty Input Handling**
```bash
# Test with empty input
curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text="

# Expected: Error handling or empty embedding
```

#### 3. **Large Text Processing**
```bash
# Test with long text (up to 8192 tokens)
long_text="This is a very long text that tests the limits of the Titan embedding model..."
curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=$long_text"
```

### Performance Tests

#### 1. **Response Time Measurement**
```bash
# Measure API response time
time curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=performance%20test"
```

#### 2. **Concurrent Requests**
```bash
# Test concurrent processing
for i in {1..10}; do
  curl -X GET "https://[API-ID].execute-api.us-east-1.amazonaws.com/prod/generate-embedding?input_text=concurrent%20test%20$i" &
done
wait
```

#### 3. **Lambda Cold Start**
```bash
# Test cold start performance
aws lambda invoke \
    --function-name GenerateEmbeddingFunction \
    --payload '{"input_text":"cold start test"}' \
    response.json
```

### Vector Quality Tests

#### 1. **Similarity Verification**
```python
import numpy as np
from scipy.spatial.distance import cosine

# Generate embeddings for similar texts
text1 = "The cat sat on the mat"
text2 = "A cat was sitting on a mat"

# Get embeddings (using API)
embedding1 = [...]  # From API response
embedding2 = [...]  # From API response

# Calculate similarity
similarity = 1 - cosine(embedding1, embedding2)
print(f"Similarity: {similarity}")  # Should be high (>0.8)
```

#### 2. **Semantic Relationships**
```python
# Test semantic relationships
texts = [
    "dog",
    "puppy",
    "car",
    "automobile"
]

# Generate embeddings and compare
# dog vs puppy should be more similar than dog vs car
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Bedrock Access Denied**
```
Error: AccessDeniedException
Solution: Enable amazon.titan-embed-text-v1 in Bedrock console
```

#### 2. **Lambda Timeout**
```
Error: Task timed out after 300.00 seconds
Solution: Reduce input text size or increase timeout
```

#### 3. **API Gateway 502 Error**
```
Error: Internal server error
Solution: Check Lambda function logs in CloudWatch
```

#### 4. **Invalid Input Format**
```
Error: ValidationException
Solution: Ensure input_text is properly URL encoded
```

### Debug Commands

```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/GenerateEmbeddingFunction"

# Get recent log events
aws logs get-log-events \
    --log-group-name "/aws/lambda/GenerateEmbeddingFunction" \
    --log-stream-name [STREAM-NAME]

# Test Lambda directly
aws lambda invoke \
    --function-name GenerateEmbeddingFunction \
    --payload '{"input_text":"debug test"}' \
    debug-response.json

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix "API-Gateway-Execution-Logs"
```

## 💰 Cost Optimization

### Estimated Costs (Monthly)

| Component | Cost | Usage |
|-----------|------|-------|
| **Lambda Requests** | ~$0.20 | 1K requests |
| **Lambda Compute** | ~$0.10 | 1K executions @ 1GB |
| **API Gateway** | ~$3.50 | 1K API calls |
| **Bedrock Embeddings** | ~$0.10 | 1K embedding generations |
| **CloudWatch Logs** | ~$0.50 | Standard logging |
| **Total** | **~$4.40/month** | Light usage |

### Cost Reduction Tips

1. **Batch Processing**: Combine multiple texts in single requests
2. **Caching**: Store frequently used embeddings
3. **Request Optimization**: Minimize API Gateway calls
4. **Lambda Optimization**: Right-size memory allocation

### Cleanup Resources

```bash
# Destroy the stack
cdk destroy GenerateEmbeddingStack

# Verify cleanup
aws lambda list-functions --query 'Functions[?FunctionName==`GenerateEmbeddingFunction`]'
aws apigateway get-rest-apis --query 'items[?name==`Embedding Generation Service`]'
```

## 🎯 Key Learning Outcomes

After completing this guide, you'll understand:

- ✅ **Text Embeddings**: Converting text to numerical vectors
- ✅ **Amazon Titan**: Bedrock's embedding model capabilities
- ✅ **Vector Dimensions**: 1536-dimensional vector space
- ✅ **API Design**: RESTful embedding services
- ✅ **Lambda Integration**: Serverless AI model invocation
- ✅ **Semantic Applications**: Foundation for AI search and similarity

## 🔗 Related Guides

- **[06-rag-server](../06-rag-server/)**: Use embeddings for document Q&A
- **[05-chatbot](../05-chatbot/)**: Conversational AI applications
- **[02-image-generation](../02-image-generation/)**: Multi-modal AI services

## 📚 Additional Resources

- [Amazon Titan Embeddings Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [Vector Embeddings Guide](https://aws.amazon.com/what-is/embeddings-in-machine-learning/)
- [Semantic Search Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/embeddings.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

---

**Ready to build semantic search applications?** Start with [setup](#phase-1-setup-and-configuration) and create your first embeddings! 🔤✨