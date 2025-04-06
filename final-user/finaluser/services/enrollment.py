import json
import uuid
from http import HTTPStatus

from finaluser.aws.sqs_aws import get_queue_url, get_sqs_client
from finaluser.exceptions import EnrollmentNotFoundError, EnrollmentSQSError
from finaluser.logger import get_logger
from finaluser.repositories.age_group import AgeGroupRepository
from finaluser.repositories.enrollment import EnrollmentRepository
from finaluser.schemas.enrollment import (
    EnrollmentIn,
    EnrollmentOut,
    EnrollmentStatus,
)

logger = get_logger()


class EnrollmentService:
    def __init__(self):
        self.repository = EnrollmentRepository()
        self.age_group_repository = AgeGroupRepository()

    def create_enrollment(self, enrollment: EnrollmentIn) -> EnrollmentOut:
        enrollment_exists = self.repository.get_by_cpf(enrollment.cpf)
        if enrollment_exists:
            age_group = self.age_group_repository.get_by_age(enrollment_exists.get('age'))
            enrollment_out = EnrollmentOut(**enrollment_exists)
            if enrollment_exists.get('status') == EnrollmentStatus.approved:
                return enrollment_out

            if enrollment_exists.get('status') == EnrollmentStatus.rejected and age_group:
                enrollment_out.age_group_id = age_group.get('id')
                enrollment_out.status = EnrollmentStatus.pending

                response = self.publish_enrollment_message(enrollment_out)
                if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != HTTPStatus.OK:
                    logger.error(f'Failed to publish message to SQS: {response} | error: services')
                    raise EnrollmentSQSError()
            return enrollment_out

        age_group = self.age_group_repository.get_by_age(enrollment.age)
        enrollment_id = str(uuid.uuid4())
        enrollment_base = {
            'id': enrollment_id,
            'name': enrollment.name,
            'cpf': enrollment.cpf,
            'age': enrollment.age,
        }

        if not age_group:
            enrollment_out = EnrollmentOut(**enrollment_base, status=EnrollmentStatus.rejected)
        else:
            enrollment_out = EnrollmentOut(
                **enrollment_base,
                age_group_id=age_group.get('id'),
                status=EnrollmentStatus.pending,
            )

        response = self.publish_enrollment_message(enrollment_out)
        if response.get('ResponseMetadata').get('HTTPStatusCode') != HTTPStatus.OK:
            logger.error(f'Failed to publish message to SQS: {response} | error: services')
            raise EnrollmentSQSError()

        return enrollment_out

    def get_enrollment(self, enrollment_id: str) -> EnrollmentOut:
        enrollment = self.repository.get_by_id(enrollment_id)

        if not enrollment:
            logger.error(f'Enrollment with id {enrollment_id} not found | error: services')
            raise EnrollmentNotFoundError()

        return enrollment

    @staticmethod
    def publish_enrollment_message(enrollment: EnrollmentOut):
        sqs = get_sqs_client()
        queue_url = get_queue_url()

        message_body = {
            'id': enrollment.id,
            'name': enrollment.name,
            'cpf': enrollment.cpf,
            'age': enrollment.age,
            'status': enrollment.status,
            'age_group_id': enrollment.age_group_id,
        }

        try:
            response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body))
        except Exception as e:
            logger.error(f'Exception when sending message to SQS: {e} | error: services')
            raise EnrollmentSQSError()

        return response
