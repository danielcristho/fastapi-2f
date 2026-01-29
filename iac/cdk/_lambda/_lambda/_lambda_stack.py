from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_ecr as ecr
)
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = ecr.Repository.from_repository_name(self, "FastApiRepo", "fastapi-2f")
        
        fn = _lambda.DockerImageFunction(
            self,
            "FastApiLambda",
            code=_lambda.DockerImageCode.from_ecr(
                repository=repo,
                tag_or_digest="latest"
            ),
            memory_size=512,
            timeout=Duration.seconds(30)
        )