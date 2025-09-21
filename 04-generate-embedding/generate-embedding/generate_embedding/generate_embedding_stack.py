from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
)


class GenerateEmbeddingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        embedding_generate_function = _lambda.Function(
            self, "EmbeddingGenerationFunction",
            runtime=_lambda.Runtime.PYTHON_3_13,
            function_name="GenerateEmbeddingFunction",
            description="Generates embeddings using Amazon Titan Embeddings G1 - Text model (on demand).",
            handler="index.lambda_handler", 
            code=_lambda.Code.from_asset("lambda"),  # This uses your local lambda folder
            timeout=Duration.seconds(300),
        )

        # Grant the Lambda function comprehensive Bedrock permissions
        embedding_generate_function.add_to_role_policy(iam.PolicyStatement(
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
            self, "EmbeddingGenerationAPI",
            rest_api_name="Embedding Generation Service",
            description="This service generates embeddings using Amazon Titan Embeddings G1 - Text model (on demand).",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # Create Lambda integration
        lambda_integration = apigw.LambdaIntegration(
            embedding_generate_function,
            proxy=False,
            request_templates={"application/json": '{"input_text": "$input.params(\'input_text\')"}'},
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    content_handling=apigw.ContentHandling.CONVERT_TO_TEXT
                )
            ]
        )

        # Add GET & POST methods to the API
        remove_bg_resource = api.root.add_resource("generate-embedding")
        remove_bg_resource.add_method(
            "GET", 
            lambda_integration,
            request_parameters={
                "method.request.querystring.input_text": True  # Make input_text query parameter required
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