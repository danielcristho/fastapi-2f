#!/usr/bin/env python3
import aws_cdk as cdk
from eks_stack import EksStack

app = cdk.App()
EksStack(app, "EksStack", env=cdk.Environment(region="us-east-1"))

app.synth()
