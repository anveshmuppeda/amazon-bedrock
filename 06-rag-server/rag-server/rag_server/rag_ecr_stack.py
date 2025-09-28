from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
)


class RagEcrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.rag_ecr_repository = ecr.Repository(
            self, "ragEcrRepository", 
            repository_name="rag-ecr-repository"
            )

        