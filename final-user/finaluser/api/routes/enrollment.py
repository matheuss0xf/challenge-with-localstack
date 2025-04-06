from fastapi import APIRouter, Depends, HTTPException, status

from finaluser.exceptions import EnrollmentNotFoundError, EnrollmentSQSError
from finaluser.schemas.enrollment import EnrollmentIn, EnrollmentOut, EnrollmentResponse
from finaluser.services.enrollment import EnrollmentService
from starlette.responses import JSONResponse

router = APIRouter()

STATUS_RESPONSE = {
    "approved": {
        "status_code": status.HTTP_200_OK,
        "message": "enrollment already approved"
    },
    "rejected": {
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "message": "enrollment rejected, age group not found"
    },
    "pending": {
        "status_code": status.HTTP_201_CREATED,
        "message": "enrollment pending"
    }
}

@router.post('/', response_model=EnrollmentResponse)
def create_enrollment(
    enrollment: EnrollmentIn,
    service: EnrollmentService = Depends(),
):
    try:
        response = service.create_enrollment(enrollment)
        status_info = STATUS_RESPONSE[response.status]
        content = EnrollmentResponse(
            message=status_info["message"],
            data=response if response.status == "pending" else None
        )
        return JSONResponse(
            status_code=status_info["status_code"],
            content=content.model_dump()
        )

    except EnrollmentSQSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create enrollment'
        )


@router.get('/{enrollment_id}', response_model=EnrollmentOut, status_code=status.HTTP_200_OK)
def check_enrollment(
    enrollment_id: str,
    service: EnrollmentService = Depends(),
):
    try:
        response = service.get_enrollment(enrollment_id)
    except EnrollmentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Enrollment not found')
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response
