import asyncio
from datetime import datetime
import boto3
import numpy as np
import logging
from fastapi import HTTPException, APIRouter, Depends

from config import load_config

router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def load_and_validate_config():
    config = load_config()
    if 'AWS' not in config or 'aws_region' not in config['AWS']:
        raise HTTPException(
            status_code=500,
            detail="Invalid AWS configuration."
        )
    return config


@router.get("", response_model=dict, tags=["status"])
async def get_status(
        stack_set_id: str,
        num_requests: int = 1,
        config: dict = Depends(load_and_validate_config),
):
    try:
        logger.info("status.py#get_status()")

        aws_region = config['AWS']['aws_region']

        cloudformation = boto3.client(
            'cloudformation', region_name=aws_region,
            endpoint_url=f'https://cloudformation.{aws_region}.amazonaws.com'
        )

        total_durations = []
        accounts = None
        errors = {}

        logger.info(f"Processing {num_requests} requests for stack set {stack_set_id}.")

        async def process_request(i):
            nonlocal errors

            start_time = datetime.now()
            logger.debug(f"Request {i + 1}: Start time - {start_time}")

            try:
                response = await asyncio.to_thread(cloudformation.list_stack_instances, StackSetName=stack_set_id)
                nonlocal accounts

                if i == 0:
                    aws_account_ids = []

                    for stack_instance in response.get('Summaries', []):
                        account_id = stack_instance.get('Account', '')
                        if account_id:
                            aws_account_ids.append(account_id)

                    accounts = aws_account_ids

            except Exception as e:
                logger.error(f"Error in AWS API call: {e}")
                errors[str(e)] = errors.get(str(e), 0) + 1
            finally:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
                logger.debug(f"Request {i + 1}: End time - {end_time}, Duration - {duration} ms")

                total_durations.append(duration)

        logger.info('before await')
        tasks = [asyncio.create_task(process_request(i)) for i in range(num_requests)]
        await asyncio.gather(*tasks)

        logger.info(f"Requests processed. Calculating additional metrics.")

        if not total_durations:
            raise HTTPException(
                status_code=500,
                detail="No duration data available."
            )

        # Create the response JSON
        response_data = {
            'accounts': accounts,
            'avg': (np.mean(total_durations)),
            'median': (np.median(total_durations)),
            'min': (np.min(total_durations)),
            'max': (np.max(total_durations)),
            'percentile_25': (np.percentile(total_durations, 25)),
            'percentile_75': (np.percentile(total_durations, 75)),
            'total': (np.sum(total_durations)),
            'errors': errors,
        }

        logger.info(f"Additional metrics calculated.")

        logger.info(f"Response generated successfully: {response_data}")

        return response_data

    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        raise e
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )
