#!/usr/bin/env python3

import aws_cdk as cdk

from background_removal.background_removal_stack import BackgroundRemovalStack


app = cdk.App()
BackgroundRemovalStack(app, "BackgroundRemovalStack")

app.synth()
