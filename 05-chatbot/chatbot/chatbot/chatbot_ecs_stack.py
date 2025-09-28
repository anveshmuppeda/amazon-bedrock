import aws_cdk
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_logs
)


class ChatbotEcsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, chatbot_ecr_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Store network stack reference
        self.chatbot_ecr_stack = chatbot_ecr_stack

        vpc = ec2.Vpc(
            self,  "ecs-devops-vpc",  
            max_azs=3
            )

        ecs_cluster = ecs.Cluster(
            self, "ChatbotEcsCluster",
            cluster_name="chatbot-ecs-cluster",
            vpc=vpc
            )

        execution_role = iam.Role(
            self,  "ChatbotEcsExecutionRole", 
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"), 
            role_name="chatbot-ecs-execution-role"
            )

        execution_role.add_to_policy(
            iam.PolicyStatement( 
                effect=iam.Effect.ALLOW, 
                resources=["*"], 
                actions=["ecr:GetAuthorizationToken",  
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:GetDownloadUrlForLayer",  
                            "ecr:BatchGetImage",  
                            "logs:CreateLogStream",  
                            "logs:PutLogEvents"  
                        ]  
                )
            )
        
        task_definition = ecs.FargateTaskDefinition(
            self,  "ChatbotEcsTaskDef", 
            execution_role=execution_role, 
            family="chatbot-ecs-task-def",
            )
        
        container = task_definition.add_container(
            "ChatbotEcsContainer", 
            image=ecs.ContainerImage.from_registry(
                f"{self.chatbot_ecr_stack.chatbot_ecr_repository.repository_uri}:latest"
                )
            )
        service = ecs.FargateService(
            self,  "ChatbotEcsService", 
            cluster=ecs_cluster, 
            task_definition=task_definition, 
            service_name="chatbot-ecs-service",
            desired_count=1,
            )
        
        log_group = aws_logs.LogGroup(
            self, "ChatbotLogGroup",
            log_group_name="/chatbot/logs",
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
            )