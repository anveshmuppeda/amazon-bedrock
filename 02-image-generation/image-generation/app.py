#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Tags

from image_generation.image_generation_stack import ImageGenerationStack

APP_PREFIX = "image-generation"

app = cdk.App()
ImageGenerationStack(app, "ImageGenerationStack")

Tags.of(app).add("Application", APP_PREFIX)
Tags.of(app).add("Owner", "Anvesh Muppeda")
Tags.of(app).add("Environment", "Sandbox")
Tags.of(app).add("Project", "Amazon Bedrock Demos")
Tags.of(app).add("ManagedBy", "CDK")

app.synth()