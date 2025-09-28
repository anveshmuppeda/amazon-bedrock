from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
)


class ImageGenerateBgRemoveEcrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.image_generator_ecr_repository = ecr.Repository(
            self, "ImageGeneratorBgRemoverEcrRepository", 
            repository_name="image-generator-bg-remover-ecr-repository"
            )

        