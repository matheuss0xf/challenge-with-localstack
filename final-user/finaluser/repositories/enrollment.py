from typing import Optional

from botocore.exceptions import ClientError

from finaluser.aws.dynamodb import get_enrollments_table
from finaluser.logger import get_logger
from finaluser.schemas.enrollment import EnrollmentOut

logger = get_logger()


class EnrollmentRepository:
    def __init__(self):
        self.table = get_enrollments_table()

    def get_by_id(self, enrollment_id: str) -> Optional[EnrollmentOut]:
        try:
            enrollment = self.table.get_item(Key={'id': enrollment_id})
            item = enrollment.get('Item')

            if not item:
                logger.warning(
                    f'Enrollment with id {enrollment_id} not found | error: respositories'
                )
                return None

            return EnrollmentOut(**item)

        except ClientError:
            logger.error('Error getting enrollment by id | error: respositories')
            raise RuntimeError('Failed to get enrollment by id')

    def get_by_cpf(self, cpf: str) -> Optional[EnrollmentOut]:
        try:
            enrollment = self.table.query(
                IndexName='CpfIndex',
                KeyConditionExpression='#cpf = :cpf_val',
                ExpressionAttributeNames={'#cpf': 'cpf'},
                ExpressionAttributeValues={':cpf_val': cpf},
            )

            items = enrollment.get('Items', [])
            return items[0] if items else None

        except ClientError as e:
            logger.error(f'Error fetching enrollment by CPF: {e} | error: respositories')
            return None
