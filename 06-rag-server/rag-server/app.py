#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Tags

from rag_server.rag_ecs_stack import RagEcsStack
from rag_server.rag_ecr_stack import RagEcrStack

app = cdk.App()

ecr_stack = RagEcrStack(
    app, "RagEcrStack"
    )

ecs_stack = RagEcsStack(
    app, "RagEcsStack",
    rag_ecr_stack=ecr_stack
    )

app.synth()

ecs_stack.add_dependency(ecr_stack)

Tags.of(app).add("Application", "RAG-Server")
Tags.of(app).add("Owner", "Anvesh Muppeda")
Tags.of(app).add("Environment", "Sandbox")
Tags.of(app).add("Project", "Amazon Bedrock Demos")
Tags.of(app).add("ManagedBy", "CDK")