from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from finaluser.aws.dynamodb import get_age_groups_table
from finaluser.logger import get_logger

logger = get_logger()


class AgeGroupRepository:
    def __init__(self):
        self.table = get_age_groups_table()

    def get_by_age(self, age: int):
        try:
            response = self.table.scan(
                FilterExpression=Attr('min_age').lte(age) & Attr('max_age').gte(age)
            )

            items = response.get('Items', [])
            return items[0] if items else None

        except ClientError:
            logger.error('Error getting age group id by age | error: respositories')
            raise RuntimeError('Failed to get age group id by age')

        except Exception:
            logger.error('Unexpected error getting age group id by age | error: respositories')
            raise RuntimeError('Unexpected error occurred')
