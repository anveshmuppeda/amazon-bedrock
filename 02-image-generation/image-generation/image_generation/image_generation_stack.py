from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)


class ImageGenerationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_source_bucket = s3.Bucket(
            self, 
            "ImageSourceBucket",
            bucket_name="amazon-bedrock-image-source-bucket-002",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        image_generator_function = _lambda.Function(
            self, "ImageGeneratorFunction",
            runtime=_lambda.Runtime.PYTHON_3_13,
            function_name="ImageGeneratorUsingTitanG1",
            handler="index.index", 
            code=_lambda.Code.from_asset("lambda"),  # This uses your local lambda folder
            timeout=Duration.seconds(300),
            environment={
                "IMAGE_SOURCE_BUCKET": image_source_bucket.bucket_name
            }
        )

        # Grant the Lambda function permissions to read/write to the S3 bucket
        image_source_bucket.grant_read_write(image_generator_function)

        # Grant the Lambda function comprehensive Bedrock permissions
        image_generator_function.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels",
                "bedrock:GetModelInvocationLoggingConfiguration",
                "bedrock:CreateModelCustomizationJob",
                "bedrock:GetModelCustomizationJob",
                "bedrock:ListModelCustomizationJobs",
                "bedrock:StopModelCustomizationJob",
                "bedrock:CreateProvisionedModelThroughput",
                "bedrock:GetProvisionedModelThroughput",
                "bedrock:ListProvisionedModelThroughputs",
                "bedrock:UpdateProvisionedModelThroughput",
                "bedrock:DeleteProvisionedModelThroughput",
                "bedrock:TagResource",
                "bedrock:UntagResource",
                "bedrock:ListTagsForResource"
            ],
            resources=["*"]  # Bedrock requires * for most actions due to dynamic model ARNs
        ))

        # Create API Gateway
        api = apigw.RestApi(
            self, "ImageGenerationApi",
            rest_api_name="Image Generation Service",
            description="This service generates images using Amazon Bedrock Titan Image Generator.",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # Create Lambda integration
        lambda_integration = apigw.LambdaIntegration(
            image_generator_function,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )

        # Add GET method to the API
        generate_resource = api.root.add_resource("generate-image")
        generate_resource.add_method(
            "GET", 
            lambda_integration,
            request_parameters={
                "method.request.querystring.prompt": True  # Make prompt query parameter required
            }
        )