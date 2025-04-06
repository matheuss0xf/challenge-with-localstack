import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from configurationuser.config import settings

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.BASIC_AUTH_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.BASIC_AUTH_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Credentials are not valid',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials
