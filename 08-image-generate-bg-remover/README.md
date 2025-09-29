# AI Agent Hub 🤖

A comprehensive web application that provides AI-powered image processing capabilities through a unified Streamlit interface. This project leverages Amazon Bedrock's Titan models to offer two main features: AI image generation from text prompts and intelligent background removal from existing images.

![AI Agent Hub Screenshot](./img/02-aws-bedrock-image-bg-remover.gif)

## ✨ Features

### 🎨 AI Image Generator
- **Text-to-Image Generation**: Create unique images from descriptive text prompts
- **High-Quality Output**: Generate 1024x1024 pixel images using Amazon Titan Image Generator V1
- **Customizable Parameters**: Fine-tune image generation with configurable settings
- **Download Capability**: Save generated images directly to your device

### ✂️ Background Remover
- **AI-Powered Processing**: Remove backgrounds from images using Amazon Titan Image Generator V2
- **Multiple Format Support**: Upload PNG, JPG, and JPEG files
- **Before/After Comparison**: Visual comparison of original and processed images
- **High-Quality Results**: Maintain image quality while removing backgrounds

## 🏗️ Architecture

The application is built with a modern, scalable architecture:

- **Frontend**: Streamlit web interface for user interaction
- **Backend**: Python modules handling AI model interactions
- **AI Models**: Amazon Bedrock Titan models for image processing
- **Infrastructure**: AWS ECS Fargate for containerized deployment
- **Load Balancing**: Application Load Balancer for high availability
- **Container Registry**: Amazon ECR for image storage

## 🚀 Technology Stack

- **Framework**: Streamlit
- **Language**: Python 3.x
- **AI Platform**: Amazon Bedrock
- **Models**: 
  - Amazon Titan Image Generator V1 (Text-to-Image)
  - Amazon Titan Image Generator V2 (Background Removal)
- **Infrastructure**: AWS CDK (Python)
- **Deployment**: AWS ECS Fargate
- **Storage**: Amazon ECR
- **Load Balancing**: AWS Application Load Balancer

## 📁 Project Structure

```
ai-agent-hub/
├── app.py                          # Main Streamlit application
├── image_generator/
│   └── image_generate_backend.py   # Image generation backend
├── bg_remover/
│   └── bg_remover_backend.py       # Background removal backend
├── infrastructure/
│   └── image_generate_bg_remove_ecs_stack.py  # CDK infrastructure
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
└── README.md                      # This file
```

## 🛠️ Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.8 or higher
- Node.js (for AWS CDK)
- Docker (for local development)

## 📋 Required AWS Permissions

Ensure your AWS credentials have access to:
- Amazon Bedrock (InvokeModel permissions)
- Amazon ECS
- Amazon ECR
- AWS VPC
- AWS Application Load Balancer
- AWS IAM
- AWS CloudFormation

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-agent-hub
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials
```bash
aws configure
```

### 4. Install AWS CDK
```bash
npm install -g aws-cdk
```

### 5. Bootstrap CDK (if first time)
```bash
cdk bootstrap
```

## 🚀 Deployment

### Deploy with AWS CDK

1. **Deploy the infrastructure:**
```bash
cdk deploy --all
```

2. **Access the application:**
After successful deployment, the CDK will output the Application Load Balancer DNS name. Access your application at:
```
http://<your-alb-dns-name>
```

### Local Development

1. **Run locally with Streamlit:**
```bash
streamlit run app.py
```

2. **Access at:**
```
http://localhost:8501
```

## 🎯 Usage

### Image Generation
1. Navigate to the "🎨 Image Generator" tab
2. Enter a descriptive text prompt (e.g., "A serene mountain landscape at sunset")
3. Click "🎨 Generate Image"
4. Wait for the AI to process your request
5. Download the generated image using the "💾 Download Image" button

### Background Removal
1. Navigate to the "✂️ Background Remover" tab
2. Upload an image file (PNG, JPG, or JPEG)
3. Click "✂️ Remove Background"
4. View the before/after comparison
5. Download the processed image with transparent background

## 🔧 Configuration

### Image Generation Settings
- **Model**: Amazon Titan Image Generator V1
- **Output Size**: 1024x1024 pixels
- **CFG Scale**: 8.0 (creativity vs adherence balance)
- **Number of Images**: 1 per request

### Background Removal Settings
- **Model**: Amazon Titan Image Generator V2
- **Task Type**: Background Removal
- **Supported Formats**: PNG, JPG, JPEG
- **Output Format**: PNG with transparency

## 📊 Infrastructure Details

### ECS Configuration
- **Platform**: AWS Fargate
- **CPU**: 512 units (0.5 vCPU)
- **Memory**: 1024 MB
- **Port**: 8501 (Streamlit default)

### Security
- **VPC**: Custom VPC with public and private subnets
- **Security Groups**: Restrictive rules for ECS and ALB
- **IAM Roles**: Least privilege access for ECS tasks and execution

### Monitoring
- **CloudWatch Logs**: Centralized logging
- **Health Checks**: Application and load balancer level
- **Retention**: 1 week log retention

## 🔍 Troubleshooting

### Common Issues

1. **"Import error" messages:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that backend modules are in the correct directories

2. **Bedrock access denied:**
   - Verify AWS credentials and permissions
   - Ensure Bedrock service is available in your region
   - Check IAM roles have necessary Bedrock permissions

3. **Image generation fails:**
   - Check CloudWatch logs for detailed error messages
   - Verify the text prompt is appropriate and not empty
   - Ensure Titan models are accessible in your AWS account

4. **Background removal not working:**
   - Verify uploaded image format is supported
   - Check image file size (large images may timeout)
   - Review CloudWatch logs for processing errors

### Health Check Endpoints
- **Streamlit Health**: `http://your-app-url/_stcore/health`
- **Application Status**: Check ECS service status in AWS Console

## 📈 Performance Optimization

- **Image Size**: Keep uploaded images under 5MB for optimal processing
- **Prompt Length**: Detailed prompts (50-200 words) typically yield better results
- **Resource Scaling**: Consider increasing ECS task resources for heavy usage

## 🔐 Security Considerations

- The application runs in private subnets with NAT gateway access
- All AWS resources follow least privilege access principles
- Load balancer accepts HTTP traffic (consider adding HTTPS in production)
- Container images should be regularly updated for security patches

## 🔗 Useful Links

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [AWS CDK Python Documentation](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [Amazon Titan Model Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-models.html)

---

**Note**: This application uses AWS services that may incur costs. Monitor your AWS billing dashboard and set up billing alerts to avoid unexpected charges.