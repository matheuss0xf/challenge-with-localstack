import pytest
from fastapi.testclient import TestClient

from configurationuser.main import app
from configurationuser.security import verify_credentials

test_user = {'username': 'testuser', 'password': 'testpassword'}


@pytest.fixture
def client():
    app.dependency_overrides[verify_credentials] = lambda: test_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def age_group_data():
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'min_age': 10,
        'max_age': 20,
    }
