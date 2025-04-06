import uuid

from configurationuser.exceptions import (
    AgeGroupConflictError,
    AgeGroupInternalError,
    AgeGroupNotFoundError,
)
from configurationuser.logger import get_logger
from configurationuser.repositories.age_group import AgeGroupRepository
from configurationuser.schemas.age_group_schema import AgeGroupIn, AgeGroupOut

logger = get_logger()


class AgeGroupService:
    def __init__(self):
        self.repository = AgeGroupRepository()

    def create_age_group(self, age_group: AgeGroupIn) -> AgeGroupOut:
        if self.repository.check_conflict(age_group.min_age, age_group.max_age):
            logger.error(f'Age group conflict detected: {age_group} | error: services')
            raise AgeGroupConflictError()

        age_group_id = str(uuid.uuid4())
        try:
            self.repository.create(age_group_id, age_group.min_age, age_group.max_age)
        except Exception as e:
            logger.error(f'Error creating age group in DynamoDB: {e} | error: services')
            raise AgeGroupInternalError()

        return AgeGroupOut(id=age_group_id, min_age=age_group.min_age, max_age=age_group.max_age)

    def delete_age_group(self, id: str) -> bool:
        response = self.repository.delete(id)
        if not response:
            logger.warning(f'Age group not found for deletion: {id} | error: services')
            raise AgeGroupNotFoundError()

        return response

    def get_age_groups(self) -> list[dict]:
        try:
            age_groups = self.repository.get_all()
            return age_groups
        except Exception as e:
            logger.error(
                f'AgeGroupService.get_age_groups: Error retrieving age groups from DynamoDB: {e} '
                f'| error: services'
            )
            raise AgeGroupInternalError()
