from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    RemovalPolicy,
)


class BackgroundRemovalStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_source_bucket = s3.Bucket(
            self, 
            "ImageSourceBucket",
            bucket_name="amazon-bedrock-bg-removal-source-bucket-002",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        bg_removal_function = _lambda.Function(
            self, "ImageBackgroundRemovalFunction",
            runtime=_lambda.Runtime.PYTHON_3_13,
            function_name="ImageBackgroundRemovalUsingTitanG1",
            description="Remove Image Background using Amazon Titan Image Generator G1 model on demand.",
            handler="index.lambda_handler", 
            code=_lambda.Code.from_asset("lambda"),  # This uses your local lambda folder
            timeout=Duration.seconds(300),
            environment={
                "S3_BUCKET_NAME": image_source_bucket.bucket_name
            }
        )

        # Grant the Lambda function permissions to read/write to the S3 bucket
        image_source_bucket.grant_read_write(bg_removal_function)

        # Grant the Lambda function comprehensive Bedrock permissions
        bg_removal_function.add_to_role_policy(iam.PolicyStatement(
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
            self, "ImageBackgroundRemovalService",
            rest_api_name="Image Background Removal Service",
            description="This service removes the backgroumd for images using Amazon Bedrock Titan Image Generator.",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # Create Lambda integration
        lambda_integration = apigw.LambdaIntegration(
            bg_removal_function,
            proxy=False,
            request_templates={"application/json": '{"prompt": "$input.params(\'prompt\')"}'},
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    content_handling=apigw.ContentHandling.CONVERT_TO_TEXT
                )
            ]
        )

        # Add GET & POST methods to the API
        generate_resource = api.root.add_resource("generate-image")
        generate_resource.add_method(
            "GET", 
            lambda_integration,
            request_parameters={
                "method.request.querystring.prompt": True  # Make prompt query parameter required
            },
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigw.Model.EMPTY_MODEL
                    }
                )
            ]
        )