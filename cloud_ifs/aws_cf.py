import boto3


def get_cloudformation_client(aws_region):
    return boto3.client(
        'cloudformation', region_name=aws_region,
        endpoint_url=f'https://cloudformation.{aws_region}.amazonaws.com'
    )


def list_stack_instances(cloudformation_client, stack_set_id):
    return cloudformation_client.list_stack_instances(StackSetName=stack_set_id)
