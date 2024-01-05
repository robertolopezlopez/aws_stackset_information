# resources/status.py
import logging
from datetime import datetime

import boto3
import falcon
from botocore.exceptions import EndpointConnectionError, NoCredentialsError

from config import load_config


class StatusResource:
    def __init__(self):
        self.config = self.load_and_validate_config()
        self.logger = logging.getLogger(__name__)

    def load_and_validate_config(self):
        config = load_config()
        if 'AWS' not in config or 'aws_region' not in config['AWS']:
            self.logger.error("Invalid AWS configuration.")
            raise falcon.HTTPInternalServerError(description="Invalid AWS configuration.")
        return config

    def get_aws_info(self):
        try:
            return self.config['AWS']['aws_region']

        except Exception as e:
            # Handle the exception appropriately for your application
            self.logger.error(f"Error getting AWS config: {e}")
            return None, None, None

    def on_get(self, req, resp):
        try:
            # Retrieve stack_set_id from query parameters
            stack_set_id = req.get_param('stack_set_id')
            if not stack_set_id:
                raise falcon.HTTPBadRequest("Missing stack_set_id", "The 'stack_set_id' query parameter is required.")

            start_time = datetime.now()

            # Fetch aws region from server.conf
            aws_region = self.get_aws_info()

            # Explicitly set the CloudFormation endpoint
            try:
                cloudformation = boto3.client(
                    'cloudformation', region_name=aws_region,
                    endpoint_url=f'https://cloudformation.{aws_region}.amazonaws.com')

            except (EndpointConnectionError, NoCredentialsError) as boto3_error:
                self.logger.error(f"Boto3 error: {boto3_error}")
                raise falcon.HTTPInternalServerError(description="Failed to initialize AWS connection.")

            # List all stack instances for the specified stack set
            response = cloudformation.list_stack_instances(StackSetName=stack_set_id)
            aws_account_ids = list(set())

            for stack_instance in response.get('Summaries', []):
                account_id = stack_instance.get('Account', '')
                if account_id:
                    aws_account_ids.append(account_id)
            aws_account_ids = list(set(aws_account_ids))

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds

            if aws_account_ids:
                # Create the response JSON
                response_data = {
                    'accounts': aws_account_ids,
                    'duration': duration
                }

                resp.media = response_data
                resp.status = falcon.HTTP_200
            else:
                raise falcon.HTTPInternalServerError(description="Failed to retrieve stack information.")

        except falcon.HTTPError as e:
            resp.media = {'error': str(e)}
            resp.status = e.status
