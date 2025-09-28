#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Tags

from image_generate_bg_remover.image_generate_bg_remover_ecs_stack import ImageGenerateEcsStack
from image_generate_bg_remover.image_generate_bg_remover_ecr_stack import ImageGenerateEcrStack

app = cdk.App()

ecr_stack = ImageGenerateEcrStack(
    app, "ImageGenerateEcrStack"
    )

ecs_stack = ImageGenerateEcsStack(
    app, "ImageGenerateEcsStack",
    image_gen_ecr_stack=ecr_stack
    )

app.synth()

ecs_stack.add_dependency(ecr_stack)

Tags.of(app).add("Application", "ImageGenerationUI")
Tags.of(app).add("Owner", "Anvesh Muppeda")
Tags.of(app).add("Environment", "Sandbox")
Tags.of(app).add("Project", "Amazon Bedrock Demos")
Tags.of(app).add("ManagedBy", "CDK")