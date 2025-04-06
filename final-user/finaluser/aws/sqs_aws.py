import boto3

from finaluser.config import settings


def get_sqs_client():
    return boto3.client(
        'sqs',
        endpoint_url=settings.AWS_ENDPOINT_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def get_queue_url():
    sqs = get_sqs_client()
    response = sqs.get_queue_url(QueueName=settings.QUEUE_NAME)
    return response['QueueUrl']
