# 🖼️ Image Background Removal with Amazon Titan

**Level:** Intermediate | **Duration:** 50 minutes | **Cost:** ~$2.00

Build an intelligent background removal service using Amazon Titan Image Generator V2. Automatically remove backgrounds from images with AI-powered precision for professional photo editing.

## 🎯 What You'll Build

- **AI Background Removal API** that processes images automatically
- **S3 Integration** for secure image storage and retrieval
- **RESTful Service** with API Gateway and Lambda
- **Presigned URL Generation** for secure image access
- **Production-Ready Infrastructure** with CDK

## 🏗️ Architecture Overview

```
📷 Input Image → 📤 S3 Upload → 🌐 API Gateway → ⚡ Lambda → 🤖 Titan V2 → 🖼️ Processed Image
      ↓              ↓              ↓             ↓           ↓              ↓
   Original.jpg   S3 Bucket    REST API    Python Handler  AI Processing  Background Removed
                                                                          + Presigned URL
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
- ✅ S3, Lambda, and API Gateway permissions

### Enable Bedrock Models
1. Navigate to Amazon Bedrock Console
2. Go to "Model access" → "Enable specific models"
3. Enable: `amazon.titan-image-generator-v2:0`
4. Wait for approval (usually immediate)

## 📁 Project Structure

```
03-background-removal/
├── background-removal/             # CDK infrastructure
│   ├── app.py                      # CDK app entry point
│   ├── background_removal/
│   │   └── background_removal_stack.py  # CDK stack definition
│   └── lambda/
│       └── index.py                # Lambda function code
├── img/                            # Sample images
│   ├── cat.png                     # Original image
│   └── cat_bg_removed_*.png        # Processed results
├── requirements.txt                # Python dependencies
└── README.md                       # This guide
```

## 🔧 Implementation Deep Dive

### Lambda Function Architecture (`lambda/index.py`)

#### 1. **S3 Image Download**
```python
def download_image_from_s3(bucket_name, object_key, s3_client=None):
    """
    Download image from S3 and convert to base64
    
    Process:
    1. Connect to S3 using boto3
    2. Download image bytes from specified bucket/key
    3. Convert to base64 for Bedrock API
    4. Handle errors (missing bucket, access denied, etc.)
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    image_bytes = response['Body'].read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    return base64_image
```

#### 2. **Background Removal Core**
```python
def generate_image(model_id, body):
    """
    Remove background using Titan Image Generator V2
    
    Process:
    1. Connect to Bedrock runtime
    2. Send base64 image to Titan V2 model
    3. Specify BACKGROUND_REMOVAL task type
    4. Receive processed image as base64
    5. Convert back to bytes for storage
    """
    bedrock = boto3.client(service_name='bedrock-runtime')
    
    response = bedrock.invoke_model(
        body=body, 
        modelId=model_id,
        accept="application/json",
        contentType="application/json"
    )
    
    response_body = json.loads(response.get("body").read())
    base64_image = response_body.get("images")[0]
    image_bytes = base64.b64decode(base64_image.encode('ascii'))
    
    return image_bytes
```

#### 3. **Request Processing Pipeline**
```python
def lambda_handler(event, context):
    """
    Complete background removal pipeline
    
    Flow:
    1. Extract input_key from API Gateway event
    2. Generate timestamped output filename
    3. Download original image from S3
    4. Process with Titan V2 background removal
    5. Upload processed image to S3
    6. Generate presigned URL for secure access
    7. Return URL to client
    """
    # Input processing
    input_key = event['input_key']
    filename = os.path.basename(input_key)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_key = f"outputs/{name}_bg_removed_{timestamp}.png"
    
    # Image processing
    input_image = download_image_from_s3(bucket_name, input_key)
    
    body = json.dumps({
        "taskType": "BACKGROUND_REMOVAL",
        "backgroundRemovalParams": {
            "image": input_image,
        }
    })
    
    processed_image = generate_image(model_id, body)
    
    # Storage and URL generation
    s3_client.put_object(Bucket=bucket_name, Body=processed_image, Key=output_key)
    presigned_url = s3_client.generate_presigned_url('get_object', 
        Params={'Bucket': bucket_name, 'Key': output_key}, ExpiresIn=3600)
    
    return {'statusCode': 200, 'body': presigned_url}
```

### CDK Infrastructure (`background_removal_stack.py`)

#### 1. **S3 Bucket Configuration**
```python
image_source_bucket = s3.Bucket(
    self, "ImageSourceBucket",
    bucket_name="amazon-bedrock-bg-removal-source-bucket-002",
    removal_policy=RemovalPolicy.DESTROY,  # For demo purposes
    auto_delete_objects=True  # Cleanup on stack deletion
)
```

#### 2. **Lambda Function Setup**
```python
bg_removal_function = _lambda.Function(
    self, "ImageBackgroundRemovalFunction",
    runtime=_lambda.Runtime.PYTHON_3_13,
    function_name="ImageBackgroundRemovalUsingTitanG1",
    handler="index.lambda_handler", 
    code=_lambda.Code.from_asset("lambda"),
    timeout=Duration.seconds(300),  # 5 minutes for large images
    environment={
        "S3_BUCKET_NAME": image_source_bucket.bucket_name
    }
)
```

#### 3. **Permissions Configuration**
```python
# S3 permissions
image_source_bucket.grant_read_write(bg_removal_function)

# Bedrock permissions
bg_removal_function.add_to_role_policy(iam.PolicyStatement(
    actions=[
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:GetFoundationModel",
        "bedrock:ListFoundationModels"
    ],
    resources=["*"]
))
```

#### 4. **API Gateway Integration**
```python
api = apigw.RestApi(
    self, "ImageBackgroundRemovalService",
    rest_api_name="Image Background Removal Service",
    default_cors_preflight_options=apigw.CorsOptions(
        allow_origins=apigw.Cors.ALL_ORIGINS,
        allow_methods=apigw.Cors.ALL_METHODS
    )
)

lambda_integration = apigw.LambdaIntegration(
    bg_removal_function,
    request_templates={
        "application/json": '{"input_key": "$input.params(\'input_key\')"}'
    }
)
```

## 🚀 Step-by-Step Guide

### Phase 1: Setup and Configuration

#### 1. Clone and Setup Environment
```bash
# Clone repository
git clone https://github.com/anveshmuppeda/amazon-bedrock.git
cd amazon-bedrock/03-background-removal

# Create virtual environment
python -m venv bg-removal-env
source bg-removal-env/bin/activate  # Windows: bg-removal-env\Scripts\activate

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
# Test Titan Image Generator V2 access
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query 'modelSummaries[?modelId==`amazon.titan-image-generator-v2:0`]'
```

### Phase 2: Deploy Infrastructure

#### 1. Bootstrap CDK (First Time Only)
```bash
cd background-removal
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/us-east-1
```

#### 2. Deploy the Stack
```bash
# Deploy background removal service
cdk deploy BackgroundRemovalStack

# Note the API Gateway URL and S3 bucket name from output
```

#### 3. Verify Deployment
```bash
# Check Lambda function
aws lambda list-functions --query 'Functions[?FunctionName==`ImageBackgroundRemovalUsingTitanG1`]'

# Check S3 bucket
aws s3 ls | grep bg-removal

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?name==`Image Background Removal Service`]'
```

### Phase 3: Upload Test Images

#### 1. Upload Sample Images
```bash
# Get bucket name from CDK output or use the default
BUCKET_NAME="amazon-bedrock-bg-removal-source-bucket-002"

# Upload test images
aws s3 cp img/cat.png s3://$BUCKET_NAME/inputs/cat.png
aws s3 cp img/lion.png s3://$BUCKET_NAME/inputs/lion.png

# Verify upload
aws s3 ls s3://$BUCKET_NAME/inputs/
```

## 📊 Example Flows

### Example 1: Cat Image Background Removal

**Original Image**: `cat.png` (cat sitting on a couch)

**API Request**:
```bash
# API Gateway URL from CDK output
API_URL="https://[API-ID].execute-api.us-east-1.amazonaws.com/prod"

curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/cat.png"
```

**Processing Flow**:
1. **API Gateway**: Receives GET request with input_key parameter
2. **Lambda Trigger**: Extracts `inputs/cat.png` from request
3. **S3 Download**: Downloads original image from S3 bucket
4. **Base64 Conversion**: Converts image to base64 for Bedrock API
5. **Titan Processing**: AI removes background, keeps cat subject
6. **Result Storage**: Saves processed image as `outputs/cat_bg_removed_20241201_143022.png`
7. **Presigned URL**: Generates secure 1-hour access URL
8. **Response**: Returns presigned URL to client

**Response**:
```json
{
  "statusCode": 200,
  "body": "https://amazon-bedrock-bg-removal-source-bucket-002.s3.amazonaws.com/outputs/cat_bg_removed_20241201_143022.png?AWSAccessKeyId=...&Signature=...&Expires=1701445822"
}
```

### Example 2: Batch Processing Multiple Images

**Multiple Images Processing**:
```bash
# Process multiple images
images=("inputs/cat.png" "inputs/lion.png" "inputs/dog.png")

for image in "${images[@]}"; do
  echo "Processing: $image"
  curl -X GET "$API_URL/image-bg-removeal?input_key=$image"
  echo ""
done
```

**Expected Results**:
- `cat_bg_removed_[timestamp].png` - Cat with transparent background
- `lion_bg_removed_[timestamp].png` - Lion with transparent background  
- `dog_bg_removed_[timestamp].png` - Dog with transparent background

### Example 3: Error Handling Flow

**Invalid Input**: Non-existent image key

**Request**:
```bash
curl -X GET "$API_URL/image-bg-removeal?input_key=nonexistent/image.png"
```

**Error Flow**:
1. **Lambda Processing**: Attempts to download from S3
2. **S3 Error**: NoSuchKey exception raised
3. **Error Handling**: Custom ImageError with descriptive message
4. **Response**: 500 status with error details

**Response**:
```json
{
  "statusCode": 500,
  "body": "Error: S3 object 'nonexistent/image.png' does not exist in bucket 'amazon-bedrock-bg-removal-source-bucket-002'"
}
```

## 🧪 Testing

### Functional Tests

#### 1. **Basic Background Removal**
```bash
# Upload test image
aws s3 cp img/cat.png s3://$BUCKET_NAME/inputs/test-cat.png

# Process image
curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/test-cat.png"

# Expected: 200 status, presigned URL returned
```

#### 2. **Large Image Processing**
```bash
# Test with high-resolution image (up to 4096x4096)
aws s3 cp large-image.jpg s3://$BUCKET_NAME/inputs/large-image.jpg

curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/large-image.jpg"

# Expected: Successful processing within timeout limits
```

#### 3. **Invalid Format Handling**
```bash
# Test with unsupported format
aws s3 cp document.pdf s3://$BUCKET_NAME/inputs/document.pdf

curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/document.pdf"

# Expected: Error response from Titan model
```

### Performance Tests

#### 1. **Processing Time Measurement**
```bash
# Measure end-to-end processing time
time curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/cat.png"

# Typical times:
# Small images (< 1MB): 3-5 seconds
# Medium images (1-5MB): 5-10 seconds
# Large images (5-10MB): 10-15 seconds
```

#### 2. **Concurrent Processing**
```bash
# Test concurrent requests
for i in {1..5}; do
  curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/cat.png" &
done
wait

# Monitor Lambda concurrency and performance
```

#### 3. **Memory Usage Monitoring**
```bash
# Check Lambda metrics
aws logs filter-log-events \
    --log-group-name "/aws/lambda/ImageBackgroundRemovalUsingTitanG1" \
    --filter-pattern "REPORT"
```

### Quality Tests

#### 1. **Background Removal Accuracy**
- Test with various image types (portraits, objects, animals)
- Verify clean background removal without artifacts
- Check edge preservation around subjects

#### 2. **Supported Image Formats**
```bash
# Test different formats
formats=("jpg" "jpeg" "png" "webp")

for format in "${formats[@]}"; do
  aws s3 cp "test.$format" s3://$BUCKET_NAME/inputs/
  curl -X GET "$API_URL/image-bg-removeal?input_key=inputs/test.$format"
done
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Bedrock Access Denied**
```
Error: AccessDeniedException
Solution: Enable amazon.titan-image-generator-v2:0 in Bedrock console
```

#### 2. **S3 Permission Errors**
```
Error: Access denied to S3 object
Solution: Check Lambda execution role has S3 read/write permissions
```

#### 3. **Lambda Timeout**
```
Error: Task timed out after 300.00 seconds
Solution: Reduce image size or increase Lambda timeout
```

#### 4. **Invalid Image Format**
```
Error: Image generation error
Solution: Ensure image is in supported format (JPEG, PNG, WebP)
```

### Debug Commands

```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/ImageBackgroundRemoval"

# Get recent log events
aws logs get-log-events \
    --log-group-name "/aws/lambda/ImageBackgroundRemovalUsingTitanG1" \
    --log-stream-name [STREAM-NAME] \
    --start-time $(date -d '1 hour ago' +%s)000

# Test Lambda directly
aws lambda invoke \
    --function-name ImageBackgroundRemovalUsingTitanG1 \
    --payload '{"input_key":"inputs/cat.png"}' \
    response.json

# Check S3 bucket contents
aws s3 ls s3://$BUCKET_NAME/inputs/
aws s3 ls s3://$BUCKET_NAME/outputs/
```

## 💰 Cost Optimization

### Estimated Costs (Monthly)

| Component | Cost | Usage |
|-----------|------|-------|
| **Lambda Requests** | ~$0.20 | 100 requests |
| **Lambda Compute** | ~$2.00 | 100 executions @ 3GB, 10s avg |
| **API Gateway** | ~$0.35 | 100 API calls |
| **S3 Storage** | ~$1.00 | 10GB images |
| **S3 Requests** | ~$0.10 | GET/PUT operations |
| **Bedrock Image Processing** | ~$5.00 | 100 background removals |
| **Total** | **~$8.65/month** | Light usage |

### Cost Reduction Tips

1. **Image Optimization**: Resize images before processing
2. **S3 Lifecycle**: Auto-delete processed images after 30 days
3. **Lambda Memory**: Right-size memory allocation based on image sizes
4. **Batch Processing**: Process multiple images in single Lambda invocation

### Cleanup Resources

```bash
# Empty S3 bucket first
aws s3 rm s3://$BUCKET_NAME --recursive

# Destroy the stack
cdk destroy BackgroundRemovalStack

# Verify cleanup
aws s3 ls | grep bg-removal
aws lambda list-functions --query 'Functions[?FunctionName==`ImageBackgroundRemovalUsingTitanG1`]'
```

## 🎯 Key Learning Outcomes

After completing this guide, you'll understand:

- ✅ **AI Image Processing**: Background removal using computer vision
- ✅ **Amazon Titan V2**: Advanced image generation and editing capabilities
- ✅ **S3 Integration**: Secure image storage and retrieval patterns
- ✅ **Presigned URLs**: Secure, time-limited access to private content
- ✅ **Error Handling**: Robust error management for image processing
- ✅ **API Design**: RESTful services for image processing workflows

## 🔗 Related Guides

- **[02-image-generation](../02-image-generation/)**: AI image creation from text
- **[07-image-generation-ui](../07-image-generation-ui/)**: Web UI for image generation
- **[08-image-generate-bg-remover](../08-image-generate-bg-remover/)**: Combined generation and removal

## 📚 Additional Resources

- [Amazon Titan Image Generator Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html)
- [Image Processing Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/image-generation.html)
- [S3 Presigned URLs Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [Lambda Image Processing Patterns](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)

---

**Ready to build professional image editing services?** Start with [setup](#phase-1-setup-and-configuration) and remove backgrounds with AI! 🖼️✨