# 🤖 AI Agent Hub - Image Generation & Background Removal

**Level:** Advanced | **Duration:** 70 minutes | **Cost:** ~$5.00

Build a comprehensive AI-powered image processing hub that combines image generation and background removal in a single, unified web interface using Amazon Titan models.

## 🎯 What You'll Build

- **Unified AI Hub** with multiple image processing capabilities
- **Text-to-Image Generation** using Amazon Titan Image Generator G1
- **AI Background Removal** using Amazon Titan Image Generator V2
- **Tabbed Interface** for seamless feature switching
- **Before/After Comparisons** for background removal results
- **Production Deployment** on AWS ECS with complete infrastructure

## 🏗️ Architecture Overview

```
🌐 Streamlit Hub → 🎨 Image Generator → 🤖 Titan G1 → 🖼️ Generated Image
                 ↘                                              ↓
                  ✂️ Background Remover → 🤖 Titan V2 → 🖼️ Processed Image
                                                              ↓
                                                        💾 Download Options
```

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Implementation Deep Dive](#-implementation-deep-dive)
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
   - `amazon.titan-image-generator-v1` (for image generation)
   - `amazon.titan-image-generator-v2:0` (for background removal)
4. Wait for approval (usually immediate)

## 📁 Project Structure

```
08-image-generate-bg-remover/
├── source/                         # Application source code
│   ├── frontend.py                 # Unified Streamlit interface
│   ├── image_generator/
│   │   └── image_generate_backend.py  # Image generation logic
│   └── bg_remover/
│       └── bg_remover_backend.py   # Background removal logic
├── image-generate-bg-remover/      # CDK infrastructure
│   ├── app.py                      # CDK app entry point
│   └── image_generate_bg_remover/
│       ├── image_generate_bg_remover_ecr_stack.py  # ECR repository
│       └── image_generate_bg_remover_ecs_stack.py  # ECS service & ALB
├── img/                            # Sample images and results
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Local development
├── requirements.txt                # Python dependencies
└── README.md                       # This guide
```

## 🔧 Implementation Deep Dive

### Unified Frontend Architecture (`frontend.py`)

#### 1. **Multi-Tab Interface**
```python
# Create tabs for different AI features
tab1, tab2 = st.tabs(["🎨 Image Generator", "✂️ Background Remover"])

# Unified page configuration
st.set_page_config(
    page_title="AI Agent Hub",
    page_icon="🤖",
    layout="wide"
)
```

#### 2. **Dynamic Module Loading**
```python
# Add subdirectories to path for modular imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'image_generator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'bg_remover'))

# Import backend modules
import image_generate_backend as image_gen
import bg_remover_backend as bg_remover
```

#### 3. **Session State Management**
```python
# Separate session states for each feature
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
```

### Image Generation Module (`image_generator/image_generate_backend.py`)

#### 1. **Titan G1 Integration**
```python
def generate_image_from_prompt(prompt):
    """
    Generate image using Amazon Titan Image Generator G1
    
    Configuration:
    - Model: amazon.titan-image-generator-v1
    - Task: TEXT_IMAGE (text-to-image generation)
    - Resolution: 1024x1024 (high quality)
    - CFG Scale: 8.0 (prompt adherence)
    """
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8.0,
            "seed": 0
        }
    })
    
    return generate_image('amazon.titan-image-generator-v1', body)
```

#### 2. **Error Handling**
```python
class ImageError(Exception):
    """Custom exception for image generation errors"""

try:
    response = bedrock_client.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get("body").read())
    
    if "images" not in response_body or not response_body["images"]:
        raise ImageError("No images returned in response")
        
except json.JSONDecodeError as e:
    raise ImageError(f"Failed to parse response: {str(e)}")
```

### Background Removal Module (`bg_remover/bg_remover_backend.py`)

#### 1. **Titan V2 Integration**
```python
def remove_background_from_image(image_bytes):
    """
    Remove background using Amazon Titan Image Generator V2
    
    Process:
    1. Convert uploaded image bytes to base64
    2. Send to Titan V2 with BACKGROUND_REMOVAL task
    3. Receive processed image with transparent background
    4. Return as bytes for frontend display
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    body = json.dumps({
        "taskType": "BACKGROUND_REMOVAL",
        "backgroundRemovalParams": {
            "image": base64_image,
        }
    })
    
    return process_image('amazon.titan-image-generator-v2:0', body)
```

#### 2. **Image Processing Pipeline**
```python
def process_image(model_id, body):
    """
    Core image processing with Titan V2
    
    Flow:
    1. Send request to Bedrock runtime
    2. Parse JSON response
    3. Extract base64 image data
    4. Convert to bytes for frontend
    5. Handle errors and validation
    """
    response = bedrock_client.invoke_model(
        body=body, modelId=model_id,
        accept="application/json",
        contentType="application/json"
    )
    
    response_body = json.loads(response.get("body").read())
    base64_image = response_body["images"][0]
    image_bytes = base64.b64decode(base64_image.encode('ascii'))
    
    return image_bytes
```

### Infrastructure Architecture

#### ECR Stack (`image_generate_bg_remover_ecr_stack.py`)
- **Purpose**: Container registry for unified AI hub
- **Repository**: `image-generator-bg-remover-ecr-repository`

#### ECS Stack (`image_generate_bg_remover_ecs_stack.py`)
- **VPC**: Multi-AZ setup with public/private subnets
- **ECS Cluster**: Fargate-based container orchestration
- **Task Definition**: Enhanced resources for dual AI workloads
- **Application Load Balancer**: Internet-facing with health checks
- **Security Groups**: Controlled network access

## 🚀 Step-by-Step Guide

### Phase 1: Local Development Setup

#### 1. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock/08-image-generate-bg-remover

# Create virtual environment
python -m venv ai-hub-env
source ai-hub-env/bin/activate  # Windows: ai-hub-env\Scripts\activate

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
# Test both Titan models
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query 'modelSummaries[?contains(modelId, `titan-image-generator`)]'
```

### Phase 2: Local Testing

#### 1. Run with Docker Compose (Recommended)
```bash
# Start the unified AI hub
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

# Run Streamlit
streamlit run frontend.py
```

#### 3. Test Both Features

**Image Generation Test:**
1. Navigate to "🎨 Image Generator" tab
2. Enter prompt: "A futuristic robot in a cyberpunk city"
3. Click "🎨 Generate Image"
4. Verify high-quality 1024x1024 image generation

**Background Removal Test:**
1. Navigate to "✂️ Background Remover" tab
2. Upload a photo with clear subject and background
3. Click "✂️ Remove Background"
4. Verify clean background removal with transparent result

### Phase 3: AWS Deployment

#### 1. Bootstrap CDK (First Time Only)
```bash
cd image-generate-bg-remover
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-east-1
```

#### 2. Deploy ECR Repository
```bash
# Deploy ECR stack
cdk deploy ImageGenerateBgRemoveEcrStack

# Note the ECR repository URI from output
```

#### 3. Build and Push Docker Image
```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
docker login --username AWS --password-stdin \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build for Linux/AMD64 (required for ECS)
docker build --platform linux/amd64 -t image-generator-bg-remover-ecr-repository:latest .

# Tag for ECR
docker tag image-generator-bg-remover-ecr-repository:latest \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/image-generator-bg-remover-ecr-repository:latest

# Push to ECR
docker push \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/image-generator-bg-remover-ecr-repository:latest
```

#### 4. Deploy ECS Infrastructure
```bash
# Deploy ECS stack
cdk deploy ImageGenerateBgRemoveEcsStack

# Note the LoadBalancer DNS from output
```

## 📊 Example Flows

### Example 1: Complete Workflow - Generate and Edit

**Step 1: Generate Base Image**
- **Tab**: Image Generator
- **Prompt**: "A professional headshot of a person in business attire"
- **Result**: High-quality portrait with office background

**Step 2: Remove Background**
- **Tab**: Background Remover
- **Action**: Upload generated image from Step 1
- **Result**: Same portrait with transparent background

**Use Case**: Create professional profile photos for websites/LinkedIn

### Example 2: Product Photography Workflow

**Step 1: Generate Product Image**
- **Prompt**: "A sleek smartphone on a wooden desk with natural lighting"
- **Result**: Product image with realistic background

**Step 2: Create Transparent Version**
- **Action**: Remove background from generated product image
- **Result**: Clean product image for e-commerce catalogs

### Example 3: Creative Art Pipeline

**Step 1: Generate Artwork**
- **Prompt**: "A mystical dragon in an enchanted forest with magical lighting"
- **Result**: Fantasy artwork with detailed background

**Step 2: Extract Subject**
- **Action**: Remove background to isolate dragon
- **Result**: Dragon character for use in other compositions

## 🧪 Testing

### Functional Tests

#### 1. **Tab Navigation**
```python
# Test tab switching functionality
def test_tab_navigation():
    # Verify both tabs are accessible
    # Check session state persistence across tabs
    # Validate independent functionality
```

#### 2. **Image Generation Quality**
- Test various prompt types (realistic, artistic, abstract)
- Verify 1024x1024 resolution output
- Check generation time (8-15 seconds expected)
- Validate PNG format and file size

#### 3. **Background Removal Accuracy**
- Test with different image types (portraits, objects, animals)
- Verify clean edge detection
- Check transparency quality
- Validate before/after comparison display

### Performance Tests

#### 1. **Concurrent Feature Usage**
```bash
# Test simultaneous generation and background removal
# Monitor memory usage during dual operations
# Check ECS task performance under load
```

#### 2. **Memory Management**
```bash
# Monitor container memory with both features active
docker stats [container-id]

# Check for memory leaks during extended usage
```

#### 3. **Response Times**
- **Image Generation**: 8-15 seconds (depending on complexity)
- **Background Removal**: 5-10 seconds (depending on image size)
- **UI Responsiveness**: < 1 second for tab switching

### Integration Tests

#### 1. **End-to-End Workflow**
```python
def test_complete_workflow():
    # Generate image from prompt
    # Switch to background removal tab
    # Process generated image
    # Verify both results are available
    # Test download functionality for both
```

#### 2. **Error Handling**
- Test invalid prompts for generation
- Test unsupported file formats for background removal
- Verify graceful error messages
- Check recovery from Bedrock service errors

## 🔧 Troubleshooting

### Common Issues

#### 1. **Module Import Errors**
```
Error: ImportError for backend modules
Solution: Check sys.path configuration and file structure
```

#### 2. **Bedrock Model Access**
```
Error: AccessDeniedException for titan models
Solution: Enable both titan-image-generator-v1 and v2 in Bedrock console
```

#### 3. **Memory Issues**
```
Error: Container out of memory during dual operations
Solution: Increase ECS task memory allocation to 2GB+
```

#### 4. **Session State Conflicts**
```
Error: Images not persisting across tabs
Solution: Check session state key naming and initialization
```

### Debug Commands

```bash
# Check both Titan models availability
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query 'modelSummaries[?contains(modelId, `titan-image-generator`)]'

# Test image generation directly
aws bedrock invoke-model \
    --model-id "amazon.titan-image-generator-v1" \
    --body '{"taskType":"TEXT_IMAGE","textToImageParams":{"text":"test"},"imageGenerationConfig":{"numberOfImages":1,"height":512,"width":512}}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    gen-test.json

# Monitor ECS service health
aws ecs describe-services \
    --cluster image-generator-bg-remover-ecs-cluster \
    --services image-generator-bg-remover-ecs-service

# Check application logs
aws logs get-log-events \
    --log-group-name "/ImageGeneratorBgRemove/logs" \
    --log-stream-name [stream-name]
```

## 💰 Cost Optimization

### Estimated Costs (Monthly)

| Component | Cost | Usage |
|-----------|------|-------|
| **ECS Fargate** | ~$20 | 1 task, 0.5 vCPU, 2GB RAM |
| **Application Load Balancer** | ~$18 | Standard ALB |
| **Bedrock Image Generation** | ~$25 | 100 generations (G1) |
| **Bedrock Background Removal** | ~$15 | 100 removals (V2) |
| **CloudWatch Logs** | ~$3 | Enhanced logging |
| **ECR Storage** | ~$1 | Container images |
| **Total** | **~$82/month** | Moderate usage |

### Cost Reduction Tips

1. **Feature Usage Optimization**: Monitor which features are used most
2. **Auto Scaling**: Scale down during low usage periods
3. **Image Caching**: Cache frequently generated images
4. **Batch Processing**: Process multiple images in workflows
5. **Resource Right-Sizing**: Optimize ECS task resources based on usage

### Cleanup Resources

```bash
# Destroy ECS stack
cdk destroy ImageGenerateBgRemoveEcsStack

# Destroy ECR stack
cdk destroy ImageGenerateBgRemoveEcrStack

# Verify cleanup
aws ecs list-clusters
aws ecr describe-repositories
```

## 🎯 Key Learning Outcomes

After completing this guide, you'll understand:

- ✅ **Multi-Feature AI Applications**: Combining multiple AI capabilities
- ✅ **Modular Architecture**: Organizing complex Streamlit applications
- ✅ **Dual Model Integration**: Using multiple Bedrock models together
- ✅ **Session Management**: Complex state handling in web apps
- ✅ **Workflow Design**: Creating intuitive AI application flows
- ✅ **Production Scaling**: Deploying resource-intensive AI applications

## 🔗 Related Guides

- **[07-image-generation-ui](../07-image-generation-ui/)**: Single-feature image generation
- **[03-background-removal](../03-background-removal/)**: API-based background removal
- **[02-image-generation](../02-image-generation/)**: Basic image generation service

## 📚 Additional Resources

- [Amazon Titan Image Models Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html)
- [Streamlit Multi-Page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)
- [AI Workflow Design Patterns](https://docs.aws.amazon.com/bedrock/latest/userguide/image-generation.html)
- [ECS Resource Optimization](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/fargate-resource-optimization.html)

---

**Ready to build your comprehensive AI image processing hub?** Start with [local development](#phase-2-local-testing) and create the ultimate AI-powered image toolkit! 🤖✨