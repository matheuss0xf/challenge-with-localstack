import uuid
from http import HTTPStatus
from unittest.mock import patch


@patch('configurationuser.repositories.age_group.AgeGroupRepository.check_conflict')
@patch('configurationuser.repositories.age_group.AgeGroupRepository.create')
def test_create_age_group_success(
    mock_create,
    mock_check_conflict,
    client,
    age_group_data,
):
    mock_check_conflict.return_value = False
    mock_create.return_value = None

    response = client.post(
        '/api/v1/age-groups',
        json={'min_age': age_group_data['min_age'], 'max_age': age_group_data['max_age']},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['min_age'] == age_group_data['min_age']
    assert data['max_age'] == age_group_data['max_age']
    assert 'id' in data


@patch('configurationuser.repositories.age_group.AgeGroupRepository.check_conflict')
def test_create_age_group_conflict(
    mock_check_conflict,
    client,
    age_group_data,
):
    mock_check_conflict.return_value = True

    response = client.post(
        '/api/v1/age-groups',
        json={'min_age': age_group_data['min_age'], 'max_age': age_group_data['max_age']},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Age group conflicts with an existing one'


@patch('configurationuser.repositories.age_group.AgeGroupRepository.get_all')
def test_get_all_age_groups(
    mock_get_all,
    client,
    age_group_data,
):
    mock_get_all.return_value = [age_group_data]

    response = client.get('/api/v1/age-groups')

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)
    assert response.json()[0]['id'] == age_group_data['id']


@patch('configurationuser.repositories.age_group.AgeGroupRepository.delete')
def test_delete_age_group_success(
    mock_delete,
    client,
    age_group_data,
):
    mock_delete.return_value = True

    response = client.delete(f'/api/v1/age-groups/{age_group_data["id"]}')

    assert response.status_code == HTTPStatus.NO_CONTENT


@patch('configurationuser.repositories.age_group.AgeGroupRepository.delete')
def test_delete_age_group_not_found(
    mock_delete,
    client,
):
    mock_delete.return_value = False

    response = client.delete(f'/api/v1/age-groups/{uuid.uuid4()}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Age group not found'
