import pytest
from fastapi.testclient import TestClient

from finaluser.main import app
from finaluser.schemas.enrollment import EnrollmentStatus


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


@pytest.fixture
def enrollment_data():
    return {
        'id': '1234567890enrollment',
        'name': 'Testando',
        'cpf': '123.456.789-00',
        'age': 20,
        'age_group_id': '1234567890',
        'status': EnrollmentStatus.pending,
    }
