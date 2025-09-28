import aws_cdk
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs,
    aws_elasticloadbalancingv2 as elbv2
)

class RagEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, rag_ecr_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Store ECR stack reference
        self.rag_ecr_stack = rag_ecr_stack

        vpc = ec2.Vpc(
            self, "RagVpc",
            max_azs=3
        )

        ecs_cluster = ecs.Cluster(
            self, "RagEcsCluster",
            cluster_name="rag-ecs-cluster",
            vpc=vpc
        )

        # Create log group FIRST
        log_group = aws_logs.LogGroup(
            self, "RagLogGroup",
            log_group_name="/rag/logs",
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        # Enhanced execution role with Bedrock permissions
        execution_role = iam.Role(
            self, "RagEcsExecutionRole", 
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"), 
            role_name="rag-ecs-execution-role"
        )

        execution_role.add_to_policy(
            iam.PolicyStatement( 
                effect=iam.Effect.ALLOW, 
                resources=["*"], 
                actions=[
                    "ecr:GetAuthorizationToken",  
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",  
                    "ecr:BatchGetImage",  
                    "logs:CreateLogStream",  
                    "logs:PutLogEvents"  
                ]  
            )
        )

        # Task role for application permissions (Bedrock access)
        task_role = iam.Role(
            self, "RagEcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="rag-ecs-task-role"
        )

        # Add Bedrock permissions to task role
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:ListFoundationModels",
                    "bedrock:GetFoundationModel"
                ]
            )
        )
        
        # Task Definition with proper CPU/Memory and roles
        task_definition = ecs.FargateTaskDefinition(
            self, "RagEcsTaskDef", 
            execution_role=execution_role,
            task_role=task_role,  # Added task role for Bedrock
            family="rag-ecs-task-def",
            cpu=512,  # Increased for Streamlit + ML workloads
            memory_limit_mib=1024  # Increased for better performance
        )
        
        # Container with all required configurations
        container = task_definition.add_container(
            "RagEcsContainer", 
            image=ecs.ContainerImage.from_registry(
                f"{rag_ecr_stack.rag_ecr_repository.repository_uri}:latest"
            ),
            # Environment variables from your docker-compose
            environment={
                "AWS_DEFAULT_REGION": "us-east-1",
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
                "BEDROCK_EMBEDDING_MODEL_ID": "amazon.titan-embed-text-v1"
            },
            # Logging configuration
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="rag",
                log_group=log_group
            ),
            # Port mapping for Streamlit
            port_mappings=[
                ecs.PortMapping(
                    container_port=8501, 
                    protocol=ecs.Protocol.TCP,
                    name="streamlit-port"
                )
            ],
            # Health check (Streamlit-specific)
            health_check=ecs.HealthCheck(
                command=[
                    "CMD-SHELL", 
                    "curl --fail http://localhost:8501/_stcore/health || exit 1"
                ],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                retries=3,
                start_period=Duration.seconds(60)  # Give Streamlit time to start
            )
        )

        # Security Groups
        ecs_security_group = ec2.SecurityGroup(
            self, "EcsSecurityGroup",
            vpc=vpc,
            description="Security group for ECS service",
            allow_all_outbound=True
        )

        alb_security_group = ec2.SecurityGroup(
            self, "AlbSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True
        )

        # Allow HTTP traffic to ALB
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from internet"
        )

        # Allow ALB to communicate with ECS service on port 8501
        ecs_security_group.add_ingress_rule(
            alb_security_group,
            ec2.Port.tcp(8501),
            "Allow traffic from ALB to Streamlit"
        )

        # Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "RagAlb",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group,
            load_balancer_name="rag-alb"
        )

        # Target Group for Streamlit
        target_group = elbv2.ApplicationTargetGroup(
            self, "RagTargetGroup",
            vpc=vpc,
            port=8501,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                enabled=True,
                path="/_stcore/health",  # Streamlit health endpoint
                protocol=elbv2.Protocol.HTTP,
                port="8501",
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
                timeout=Duration.seconds(10),
                interval=Duration.seconds(30)
            )
        )

        # ALB Listener
        listener = alb.add_listener(
            "RagListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group]
        )

        # ECS Service
        service = ecs.FargateService(
            self, "RagEcsService", 
            cluster=ecs_cluster, 
            task_definition=task_definition, 
            service_name="rag-ecs-service",
            desired_count=1,
            security_groups=[ecs_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            enable_execute_command=True  # For debugging
        )

        # Attach service to target group
        service.attach_to_application_target_group(target_group)

        # Outputs
        aws_cdk.CfnOutput(
            self, "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="DNS name of the load balancer"
        )

        aws_cdk.CfnOutput(
            self, "StreamlitURL",
            value=f"http://{alb.load_balancer_dns_name}",
            description="URL to access the Streamlit application"
        )