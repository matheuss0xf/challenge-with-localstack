from fastapi import FastAPI

from configurationuser.api import age_group_router

app = FastAPI(title='Configuration User', version='0.1.0')

app.include_router(age_group_router, prefix='/api/v1/age-groups', tags=['Age Groups'])
