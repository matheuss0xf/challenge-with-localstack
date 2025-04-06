from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from configurationuser.exceptions import (
    AgeGroupConflictError,
    AgeGroupInternalError,
    AgeGroupNotFoundError,
)
from configurationuser.schemas.age_group_schema import AgeGroupIn, AgeGroupOut
from configurationuser.security import verify_credentials
from configurationuser.services.age_group import AgeGroupService

router = APIRouter(dependencies=[Depends(verify_credentials)])


@router.post(
    '',
    response_model=AgeGroupOut,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new age group',
    description='Creates a new age group with the specified minimum and maximum ages.',
)
def create_age_group(
    age_group: AgeGroupIn,
    service: AgeGroupService = Depends(),
):
    try:
        return service.create_age_group(age_group)
    except AgeGroupConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Age group conflicts with an existing one',
        )
    except AgeGroupInternalError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server',
        )


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete an age group',
    description='Deletes an age group by its ID.',
)
def delete_age_group(
    id: str,
    service: AgeGroupService = Depends(),
):
    try:
        return service.delete_age_group(id)
    except AgeGroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Age group not found',
        )
    except AgeGroupInternalError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server',
        )


@router.get(
    '',
    response_model=List[AgeGroupOut],
    status_code=status.HTTP_200_OK,
    summary='List all age groups',
    description='Retrieves a list of all registered age groups.',
)
def get_age_groups(
    service: AgeGroupService = Depends(),
):
    try:
        return service.get_age_groups()
    except AgeGroupInternalError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server',
        )
