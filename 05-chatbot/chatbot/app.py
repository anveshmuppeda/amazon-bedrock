#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Tags

from chatbot.chatbot_ecs_stack import ChatbotEcsStack
from chatbot.chatbot_ecr_stack import ChatbotEcrStack

app = cdk.App()

ecr_stack = ChatbotEcrStack(
    app, "ChatbotEcrStack"
    )

ecs_stack = ChatbotEcsStack(
    app, "ChatbotEcsStack",
    chatbot_ecr_stack=ecr_stack
    )

app.synth()

ecs_stack.add_dependency(ecr_stack)

Tags.of(app).add("Application", "chatbot")
Tags.of(app).add("Owner", "Anvesh Muppeda")
Tags.of(app).add("Environment", "Sandbox")
Tags.of(app).add("Project", "Amazon Bedrock Demos")
Tags.of(app).add("ManagedBy", "CDK")