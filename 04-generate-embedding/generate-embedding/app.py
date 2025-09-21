#!/usr/bin/env python3

import aws_cdk as cdk

from generate_embedding.generate_embedding_stack import GenerateEmbeddingStack


app = cdk.App()
GenerateEmbeddingStack(app, "GenerateEmbeddingStack")

app.synth()
