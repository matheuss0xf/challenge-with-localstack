from fastapi import FastAPI

from finaluser.api import enrollment_router

app = FastAPI(title='Final User API', version='0.1.0')

app.include_router(enrollment_router, prefix='/api/v1/enrollments', tags=['Enrollments'])
