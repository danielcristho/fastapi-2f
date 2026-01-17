from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_elasticache as elasticache,
    aws_iam as iam,
    CfnOutput,
    Tags
)
from constructs import Construct


class EksStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "EksVpc",
            max_azs=2,
            nat_gateways=1
        )

        cluster = eks.Cluster(
            self, "EksCluster",
            cluster_name="eks-cluster",
            version=eks.KubernetesVersion.V1_27,
            vpc=vpc,
            default_capacity=2,
            default_capacity_instance=ec2.InstanceType("t3.medium")
        )

        redis_sg = ec2.SecurityGroup(
            self, "RedisSecurityGroup",
            vpc=vpc,
            description="Security group for ElastiCache Redis",
            allow_all_outbound=False
        )

        redis_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(6379),
            description="Allow Redis access from VPC"
        )

        redis_subnet_group = elasticache.CfnSubnetGroup(
            self, "RedisSubnetGroup",
            description="Subnet group for ElastiCache Redis",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            cache_subnet_group_name="feature-flag-redis-subnet-group"
        )

        redis_cluster = elasticache.CfnCacheCluster(
            self, "RedisCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=redis_subnet_group.cache_subnet_group_name,
            vpc_security_group_ids=[redis_sg.security_group_id],
            cluster_name="feature-flag-redis"
        )
        redis_cluster.add_dependency(redis_subnet_group)

        service_account = cluster.add_service_account(
            "FeatureFlagServiceAccount",
            name="feature-flag-sa",
            namespace="default"
        )

        service_account.role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath",
                    "ssm:PutParameter",
                    "ssm:DeleteParameter",
                    "ssm:DescribeParameters"
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/feature-flags/*"
                ]
            )
        )

        service_account.role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:DescribeParameters"
                ],
                resources=["*"]
            )
        )

        CfnOutput(
            self, "RedisEndpoint",
            value=redis_cluster.attr_redis_endpoint_address,
            description="ElastiCache Redis endpoint"
        )

        CfnOutput(
            self, "RedisPort",
            value=redis_cluster.attr_redis_endpoint_port,
            description="ElastiCache Redis port"
        )

        CfnOutput(
            self, "FeatureFlagRoleArn",
            value=service_account.role.role_arn,
            description="IAM Role ARN for Feature Flag Service (IRSA)"
        )

        CfnOutput(
            self, "ClusterName",
            value=cluster.cluster_name,
            description="EKS Cluster name"
        )

        CfnOutput(
            self, "VpcId",
            value=vpc.vpc_id,
            description="VPC ID"
        )

        Tags.of(self).add("Project", "FeatureFlagService")
        Tags.of(self).add("ManagedBy", "CDK")
