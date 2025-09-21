#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Tags

from background_removal.background_removal_stack import BackgroundRemovalStack

APP_PREFIX = "background-removal"

app = cdk.App()
BackgroundRemovalStack(app, "BackgroundRemovalStack")

Tags.of(app).add("Application", APP_PREFIX)
Tags.of(app).add("Owner", "Anvesh Muppeda")
Tags.of(app).add("Environment", "Sandbox")
Tags.of(app).add("Project", "Amazon Bedrock Demos")
Tags.of(app).add("ManagedBy", "CDK")

app.synth()
