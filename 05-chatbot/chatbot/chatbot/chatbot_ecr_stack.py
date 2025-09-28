from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
)


class ChatbotEcrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.chatbot_ecr_repository = ecr.Repository(
            self, "chatbotEcrRepository", 
            repository_name="chatbot-ecr-repository"
            )

        