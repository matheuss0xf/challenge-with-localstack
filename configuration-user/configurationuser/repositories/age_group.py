from typing import Dict, List

from boto3.dynamodb.conditions import Attr  # Para filtros eficientes
from botocore.exceptions import ClientError

from configurationuser.aws.dynamodb import get_age_groups_table
from configurationuser.logger import get_logger

logger = get_logger()


class AgeGroupRepository:
    def __init__(self):
        self.table = get_age_groups_table()

    def create(self, id: str, min_age: int, max_age: int):
        item = {'id': id, 'min_age': min_age, 'max_age': max_age}
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            logger.error(f'Error creating age group: {e} | error: repository')
            raise RuntimeError('Failed to create age group')

    def delete(self, id: str) -> bool:
        try:
            response = self.table.delete_item(Key={'id': id}, ReturnValues='ALL_OLD')
            return 'Attributes' in response
        except ClientError as e:
            logger.error(f'Error deleting age group: {e} | error: repository')
            raise RuntimeError('Failed to delete age group')

    def get_all(self) -> List[Dict]:
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f'Error retrieving age groups: {e} | error: repository')
            return []

    def check_conflict(self, min_age: int, max_age: int) -> bool:
        try:
            response = self.table.scan(
                FilterExpression=Attr('min_age').lte(max_age) & Attr('max_age').gte(min_age)
            )
            return len(response.get('Items', [])) > 0
        except ClientError as e:
            logger.error(f'Error checking conflict: {e} | error: repository')
            raise RuntimeError('Failed to check age group conflict')
