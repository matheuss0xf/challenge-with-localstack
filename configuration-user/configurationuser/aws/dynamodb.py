import boto3

from configurationuser.config import settings


def get_dynamodb_resource():
    return boto3.resource(
        'dynamodb',
        endpoint_url=settings.AWS_ENDPOINT_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def get_age_groups_table():
    return get_dynamodb_resource().Table(settings.AGE_GROUPS_TABLE)
