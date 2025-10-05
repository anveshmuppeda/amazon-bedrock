# 🎨 AI Image Generator UI with Amazon Titan

**Level:** Intermediate | **Duration:** 55 minutes | **Cost:** ~$3.50

Build a beautiful web-based AI image generator using Amazon Titan Image Generator G1, Streamlit, and AWS ECS. Create stunning images from text descriptions with an intuitive user interface.

## 🎯 What You'll Build

- **Interactive Web UI** for AI image generation from text prompts
- **Real-time Image Generation** using Amazon Titan Image Generator G1
- **Streamlit Frontend** with modern, responsive design
- **Image Download Functionality** for saving generated images
- **Production Deployment** on AWS ECS with complete infrastructure

## 🏗️ Architecture Overview

```
💭 Text Prompt → 🌐 Streamlit UI → 🤖 Titan Generator → 🖼️ Generated Image → 💾 Download
      ↓              ↓                ↓                   ↓                ↓
"Mountain sunset"  Web Interface   AI Processing      1024x1024 PNG    User Device
                                                     High Quality
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
3. Enable: `amazon.titan-image-generator-v1`
4. Wait for approval (usually immediate)

## 📁 Project Structure

```
07-image-generation-ui/
├── source/                         # Application source code
│   ├── image_generate_backend.py   # Titan image generation logic
│   └── image_generate_frontend.py  # Streamlit web interface
├── image-generate/                 # CDK infrastructure
│   ├── app.py                      # CDK app entry point
│   └── image_generate/
│       ├── image_generate_ecr_stack.py  # ECR repository
│       └── image_generate_ecs_stack.py  # ECS service & ALB
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Local development
├── requirements.txt                # Python dependencies
└── README.md                       # This guide
```

## 🔧 Implementation Deep Dive

### Backend Architecture (`image_generate_backend.py`)

#### 1. **Titan Image Generation Core**
```python
def generate_image(model_id, body):
    """
    Generate image using Amazon Titan Image Generator G1
    
    Process:
    1. Connect to Bedrock runtime service
    2. Send JSON request with text prompt and configuration
    3. Receive base64-encoded image from Titan model
    4. Convert base64 to bytes for frontend display
    5. Handle errors and validation
    """
    bedrock_client = boto3.client(service_name='bedrock-runtime')
    
    response = bedrock_client.invoke_model(
        body=body, 
        modelId=model_id,
        accept="application/json",
        contentType="application/json"
    )
    
    response_body = json.loads(response.get("body").read())
    base64_image = response_body["images"][0]
    image_bytes = base64.b64decode(base64_image.encode('ascii'))
    
    return image_bytes
```

#### 2. **Request Configuration**
```python
def generate_image_from_prompt(prompt):
    """
    Simplified interface for frontend integration
    
    Configuration:
    - Task Type: TEXT_IMAGE (text-to-image generation)
    - Resolution: 1024x1024 (high quality)
    - CFG Scale: 8.0 (balance creativity vs prompt adherence)
    - Seed: 0 (random generation each time)
    """
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8.0,  # Higher = more prompt adherence
            "seed": 0         # 0 = random seed
        }
    })
    
    return generate_image('amazon.titan-image-generator-v1', body)
```

#### 3. **Error Handling**
```python
class ImageError(Exception):
    """Custom exception for Titan image generation errors"""
    
try:
    image_bytes = generate_image(model_id, body)
except ClientError as err:
    # AWS service errors (permissions, throttling)
    message = err.response["Error"]["Message"]
    raise ImageError(f"AWS error: {message}")
except json.JSONDecodeError:
    # Invalid response format
    raise ImageError("Failed to parse Bedrock response")
```

### Frontend Architecture (`image_generate_frontend.py`)

#### 1. **Streamlit UI Setup**
```python
# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Attractive title with custom styling
page_title = '<p style="font-family:sans-serif; color:Purple; font-size: 42px;">🎨 AI Image Generator 🖼️</p>'
st.markdown(page_title, unsafe_allow_html=True)
```

#### 2. **Session State Management**
```python
# Persistent image storage across page interactions
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# User input processing
user_prompt = st.text_area(
    "Type your image description here...",
    placeholder="Example: A serene mountain landscape at sunset with a lake reflecting the orange sky",
    height=100
)
```

#### 3. **Image Generation Flow**
```python
if generate_button and user_prompt.strip():
    with st.spinner("🎨 Generating your image... This may take a few moments..."):
        try:
            # Backend integration
            image_bytes = image_gen.generate_image_from_prompt(user_prompt)
            
            # Store in session for persistence
            st.session_state.generated_image = image_bytes
            
            st.success("✅ Image generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating image: {str(e)}")
```

#### 4. **Image Display and Download**
```python
if st.session_state.generated_image:
    # Convert bytes to PIL Image for display
    image = Image.open(io.BytesIO(st.session_state.generated_image))
    
    # Display with full width
    st.image(image, caption="Your AI-generated image", use_container_width=True)
    
    # Download functionality
    st.download_button(
        label="💾 Download Image",
        data=st.session_state.generated_image,
        file_name="ai_generated_image.png",
        mime="image/png"
    )
```

### Infrastructure Architecture

#### ECR Stack (`image_generate_ecr_stack.py`)
- **Purpose**: Container registry for Streamlit application
- **Repository**: `image-generate-ecr-repository`

#### ECS Stack (`image_generate_ecs_stack.py`)
- **VPC**: Multi-AZ setup with public/private subnets
- **ECS Cluster**: Fargate-based container orchestration
- **Task Definition**: Container specs with Bedrock permissions
- **Application Load Balancer**: Internet-facing with health checks
- **Security Groups**: Controlled network access for Streamlit (port 8501)

## 🚀 Step-by-Step Guide

### Phase 1: Local Development Setup

#### 1. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock/07-image-generation-ui

# Create virtual environment
python -m venv image-gen-env
source image-gen-env/bin/activate  # Windows: image-gen-env\Scripts\activate

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
# Test Titan Image Generator access
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query 'modelSummaries[?modelId==`amazon.titan-image-generator-v1`]'
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

# Run Streamlit
streamlit run image_generate_frontend.py
```

#### 3. Test Image Generation

**Test Prompts:**
1. **Simple**: "A red apple on a wooden table"
2. **Complex**: "A futuristic city skyline at night with neon lights reflecting in the water"
3. **Artistic**: "An oil painting of a peaceful garden with blooming flowers"

### Phase 3: AWS Deployment

#### 1. Bootstrap CDK (First Time Only)
```bash
cd image-generate
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-east-1
```

#### 2. Deploy ECR Repository
```bash
# Deploy ECR stack
cdk deploy ImageGenerateEcrStack

# Note the ECR repository URI from output
```

#### 3. Build and Push Docker Image
```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
docker login --username AWS --password-stdin \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build for Linux/AMD64 (required for ECS)
docker build --platform linux/amd64 -t image-generate-ecr-repository:latest .

# Tag for ECR
docker tag image-generate-ecr-repository:latest \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/image-generate-ecr-repository:latest

# Push to ECR
docker push \
$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/image-generate-ecr-repository:latest
```

#### 4. Deploy ECS Infrastructure
```bash
# Deploy ECS stack
cdk deploy ImageGenerateEcsStack

# Note the LoadBalancer DNS from output
```

## 📊 Example Flows

### Example 1: Landscape Generation

**User Input**: "A serene mountain landscape at sunset with a lake reflecting the orange sky"

**Processing Flow**:
1. **User Interface**: User enters prompt in Streamlit text area
2. **Frontend Processing**: Streamlit validates input and shows spinner
3. **Backend Call**: `generate_image_from_prompt()` called with user text
4. **Titan Request**: JSON payload sent to Bedrock with configuration:
   ```json
   {
     "taskType": "TEXT_IMAGE",
     "textToImageParams": {"text": "A serene mountain landscape..."},
     "imageGenerationConfig": {
       "numberOfImages": 1,
       "height": 1024,
       "width": 1024,
       "cfgScale": 8.0,
       "seed": 0
     }
   }
   ```
5. **AI Processing**: Titan analyzes prompt and generates 1024x1024 image
6. **Response**: Base64 image returned and converted to bytes
7. **Display**: Image shown in Streamlit with download option

**Expected Result**: High-quality landscape image with mountains, sunset colors, and lake reflection

### Example 2: Portrait Generation

**User Input**: "A professional headshot of a businesswoman in a modern office"

**Processing Details**:
- **Generation Time**: 8-12 seconds
- **Image Quality**: 1024x1024 PNG, ~2-3MB
- **Style**: Photorealistic based on prompt
- **Features**: Professional lighting, modern background

### Example 3: Artistic Style

**User Input**: "An abstract painting with vibrant colors and geometric shapes"

**Processing Details**:
- **Artistic Interpretation**: Titan creates abstract composition
- **Color Palette**: Vibrant as requested
- **Style**: Non-photorealistic, artistic rendering
- **Composition**: Geometric elements as specified

## 🧪 Testing

### Functional Tests

#### 1. **Basic Image Generation**
```bash
# Access deployed application
curl -I http://[ALB-DNS-NAME]

# Expected: 200 OK, Streamlit application loads
```

#### 2. **Prompt Validation**
- Test empty prompts (should show warning)
- Test very long prompts (should handle gracefully)
- Test special characters and emojis

#### 3. **Image Quality**
- Verify 1024x1024 resolution
- Check PNG format and file size
- Validate image clarity and prompt adherence

### Performance Tests

#### 1. **Generation Speed**
```python
import time

start_time = time.time()
# Generate image
end_time = time.time()

print(f"Generation time: {end_time - start_time:.2f} seconds")
# Expected: 8-15 seconds depending on complexity
```

#### 2. **Concurrent Users**
- Test multiple users generating images simultaneously
- Monitor ECS task performance and scaling
- Check for memory or CPU bottlenecks

#### 3. **Memory Usage**
```bash
# Monitor container memory
docker stats [container-id]

# Check ECS task metrics
aws ecs describe-services \
    --cluster image-generator-ecs-cluster \
    --services image-generator-ecs-service
```

### User Experience Tests

#### 1. **UI Responsiveness**
- Test on different screen sizes
- Verify mobile compatibility
- Check loading states and error messages

#### 2. **Download Functionality**
- Verify PNG download works correctly
- Check file naming and format
- Test download on different browsers

## 🔧 Troubleshooting

### Common Issues

#### 1. **Bedrock Access Denied**
```
Error: AccessDeniedException
Solution: Enable amazon.titan-image-generator-v1 in Bedrock console
```

#### 2. **Image Generation Timeout**
```
Error: Generation takes too long
Solution: Complex prompts may take 15+ seconds, increase timeout
```

#### 3. **Memory Issues**
```
Error: Container out of memory
Solution: Increase ECS task memory allocation
```

#### 4. **UI Not Loading**
```
Error: Streamlit application not accessible
Solution: Check ALB health checks and ECS service status
```

### Debug Commands

```bash
# Check ECS service health
aws ecs describe-services \
    --cluster image-generator-ecs-cluster \
    --services image-generator-ecs-service

# View application logs
aws logs get-log-events \
    --log-group-name "/ImageGenerator/logs" \
    --log-stream-name [stream-name]

# Test Bedrock connectivity
aws bedrock invoke-model \
    --model-id "amazon.titan-image-generator-v1" \
    --body '{"taskType":"TEXT_IMAGE","textToImageParams":{"text":"test"},"imageGenerationConfig":{"numberOfImages":1,"height":512,"width":512}}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    test-output.json
```

## 💰 Cost Optimization

### Estimated Costs (Monthly)

| Component | Cost | Usage |
|-----------|------|-------|
| **ECS Fargate** | ~$15 | 1 task, 0.5 vCPU, 1GB RAM |
| **Application Load Balancer** | ~$18 | Standard ALB |
| **Bedrock Image Generation** | ~$20 | 100 image generations |
| **CloudWatch Logs** | ~$2 | Standard logging |
| **ECR Storage** | ~$1 | Container images |
| **Total** | **~$56/month** | Light usage |

### Cost Reduction Tips

1. **Auto Scaling**: Scale down ECS tasks during low usage
2. **Image Caching**: Cache frequently generated images
3. **Batch Processing**: Generate multiple variations in one request
4. **Resource Optimization**: Right-size ECS task resources

### Cleanup Resources

```bash
# Destroy ECS stack
cdk destroy ImageGenerateEcsStack

# Destroy ECR stack
cdk destroy ImageGenerateEcrStack

# Verify cleanup
aws ecs list-clusters
aws ecr describe-repositories
```

## 🎯 Key Learning Outcomes

After completing this guide, you'll understand:

- ✅ **AI Image Generation**: Text-to-image using Amazon Titan
- ✅ **Streamlit Development**: Interactive web applications
- ✅ **Session Management**: Persistent state in web apps
- ✅ **Container Deployment**: ECS Fargate for web applications
- ✅ **User Experience**: Intuitive AI application design
- ✅ **Production Scaling**: Load balancing and auto-scaling

## 🔗 Related Guides

- **[02-image-generation](../02-image-generation/)**: API-based image generation
- **[03-background-removal](../03-background-removal/)**: AI image editing
- **[08-image-generate-bg-remover](../08-image-generate-bg-remover/)**: Combined generation and editing

## 📚 Additional Resources

- [Amazon Titan Image Generator Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Image Generation Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/image-generation.html)
- [ECS Fargate Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)

---

**Ready to create stunning AI-generated images?** Start with [local development](#phase-2-local-testing) and build your creative AI application! 🎨✨