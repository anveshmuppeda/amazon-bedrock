"""
Shows how to remove background from images using the
Amazon Titan Image Generator V2 model (on demand).
"""
import base64
import json
import logging
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize bedrock client once for better performance
bedrock_client = boto3.client(service_name='bedrock-runtime')


class ImageError(Exception):
    "Custom exception for errors returned by Amazon Titan Image Generator V2"

    def __init__(self, message):
        self.message = message


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_image_from_s3(bucket_name, object_key, s3_client=None):
    """
    Download an image from S3 and return it as base64 string.
    
    Args:
        bucket_name (str): The S3 bucket name
        object_key (str): The S3 object key (file path)
        s3_client: Optional S3 client (will create one if not provided)
    
    Returns:
        str: Base64 encoded image data
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    try:
        logger.info(f"Downloading image from S3: s3://{bucket_name}/{object_key}")
        
        # Download the file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_bytes = response['Body'].read()
        
        # Convert to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        logger.info(f"Successfully downloaded image from S3, size: {len(image_bytes)} bytes")
        return base64_image
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            raise ImageError(f"S3 bucket '{bucket_name}' does not exist")
        elif error_code == 'NoSuchKey':
            raise ImageError(f"S3 object '{object_key}' does not exist in bucket '{bucket_name}'")
        elif error_code == 'AccessDenied':
            raise ImageError(f"Access denied to S3 object s3://{bucket_name}/{object_key}")
        else:
            raise ImageError(f"Error downloading from S3: {e}")
    except Exception as e:
        raise ImageError(f"Unexpected error downloading from S3: {str(e)}")


def process_image(model_id, body):
    """
    Process image using Amazon Titan Image Generator V2 model for background removal.
    Args:
        model_id (str): The model ID to use.
        body (str) : The request body to use.
    Returns:
        image_bytes (bytes): The processed image with background removed.
    """

    logger.info(
        "Removing background with Amazon Titan Image Generator V2 model %s", model_id)

    accept = "application/json"
    content_type = "application/json"

    try:
        response = bedrock_client.invoke_model(
            body=body, modelId=model_id, accept=accept, contentType=content_type
        )
        response_body = json.loads(response.get("body").read())

        # Improved error handling for response parsing
        if "images" not in response_body or not response_body["images"]:
            raise ImageError("No images returned in response")
            
        base64_image = response_body["images"][0]
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)

        finish_reason = response_body.get("error")
        if finish_reason is not None:
            raise ImageError(f"Image processing error. Error is {finish_reason}")

        logger.info(
            "Successfully removed background with Amazon Titan Image Generator V2 model %s", model_id)

        return image_bytes
        
    except json.JSONDecodeError as e:
        raise ImageError(f"Failed to parse response: {str(e)}")
    except (KeyError, IndexError) as e:
        raise ImageError(f"Invalid response format: {str(e)}")


def remove_background_from_image(image_bytes):
    """
    Remove background from uploaded image using Amazon Titan Image Generator V2.
    Args:
        image_bytes (bytes): The input image as bytes.
    Returns:
        bytes: The processed image with background removed.
    """
    model_id = 'amazon.titan-image-generator-v2:0'
    
    # Convert image bytes to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    body = json.dumps({
        "taskType": "BACKGROUND_REMOVAL",
        "backgroundRemovalParams": {
            "image": base64_image,
        }
    })
    
    try:
        return process_image(model_id=model_id, body=body)
    except Exception as e:
        logger.error(f"Error removing background: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Entrypoint for Amazon Titan Image Generator V2 background removal.
    """
    try:
        # Get image data from event
        if 'image_data' not in event:
            raise ValueError("Missing required parameter: image_data")
            
        image_data = event['image_data']
        
        # If image_data is base64 string, decode it to bytes
        if isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        # Remove background
        processed_image_bytes = remove_background_from_image(image_bytes)
        
        return {
            'statusCode': 200,
            'body': processed_image_bytes
        }

    except ValueError as err:
        logger.error(f"Validation error: {str(err)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Validation error: {str(err)}'})
        }
    except ImageError as err:
        logger.error(f"Image processing error: {err.message}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Image processing error: {err.message}'})
        }
    except Exception as err:
        logger.error(f"Unexpected error: {str(err)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unexpected error: {str(err)}'})
        }