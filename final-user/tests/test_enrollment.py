from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from finaluser.schemas.enrollment import (
    EnrollmentIn,
    EnrollmentOut,
    EnrollmentStatus,
)
from finaluser.services.enrollment import EnrollmentService, EnrollmentSQSError


def mock_common_behavior(
    mock_get_by_cpf,
    mock_get_age_group,
    mock_publish_sqs,
    enrollment_data,
    rejected=False,
):
    mock_get_by_cpf.return_value = (
        {
            **enrollment_data,
            'status': EnrollmentStatus.rejected,
            'age_group_id': '',
        }
        if rejected
        else None
    )

    mock_get_age_group.return_value = {'id': enrollment_data['age_group_id']}
    mock_publish_sqs.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}


def assert_enrollment_response(response, expected_status, expected_group_id, expected_message):
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['message'] == expected_message
    assert data['data']['status'] == expected_status
    assert data['data']['age_group_id'] == expected_group_id


@patch('finaluser.services.enrollment.EnrollmentService.publish_enrollment_message')
@patch('finaluser.repositories.age_group.AgeGroupRepository.get_by_age')
@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_cpf')
def test_create_enrollment(
    mock_get_by_cpf,
    mock_get_age_group,
    mock_publish_sqs,
    client,
    enrollment_data,
):
    mock_common_behavior(mock_get_by_cpf, mock_get_age_group, mock_publish_sqs, enrollment_data)

    response = client.post(
        '/api/v1/enrollments/',
        json={
            'name': enrollment_data['name'],
            'cpf': enrollment_data['cpf'],
            'age': enrollment_data['age'],
        },
    )

    assert_enrollment_response(
        response,
        EnrollmentStatus.pending,
        enrollment_data.get('age_group_id'),
        'enrollment pending',
    )


@patch('finaluser.services.enrollment.EnrollmentService.publish_enrollment_message')
@patch('finaluser.repositories.age_group.AgeGroupRepository.get_by_age')
@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_cpf')
def test_reprocess_rejected_enrollment_when_age_group_now_exists(
    mock_get_by_cpf,
    mock_get_age_group,
    mock_publish_sqs,
    client,
    enrollment_data,
):
    mock_common_behavior(
        mock_get_by_cpf,
        mock_get_age_group,
        mock_publish_sqs,
        enrollment_data,
        rejected=True,
    )

    response = client.post(
        '/api/v1/enrollments/',
        json={
            'name': enrollment_data['name'],
            'cpf': enrollment_data['cpf'],
            'age': enrollment_data['age'],
        },
    )

    assert_enrollment_response(
        response,
        EnrollmentStatus.pending,
        enrollment_data.get('age_group_id'),
        'enrollment pending',
    )


@patch('finaluser.repositories.age_group.AgeGroupRepository.get_by_age')
@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_cpf')
def test_enrollment_already_approved(
    mock_get_by_cpf,
    mock_get_by_age,
    client,
    enrollment_data,
):
    mock_get_by_cpf.return_value = {
        **enrollment_data,
        'status': EnrollmentStatus.approved,
    }
    mock_get_by_age.return_value = {'id': enrollment_data['age_group_id']}

    response = client.post(
        '/api/v1/enrollments/',
        json={
            'name': enrollment_data['name'],
            'cpf': enrollment_data['cpf'],
            'age': enrollment_data['age'],
        },
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['message'] == 'enrollment already approved'


@patch('finaluser.services.enrollment.EnrollmentService.publish_enrollment_message')
@patch('finaluser.repositories.age_group.AgeGroupRepository.get_by_age')
@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_cpf')
def test_create_enrollment_rejected_due_to_missing_age_group(
    mock_get_by_cpf,
    mock_get_age_group,
    mock_publish_sqs,
    client,
    enrollment_data,
):
    mock_get_by_cpf.return_value = None

    mock_get_age_group.return_value = None

    mock_publish_sqs.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

    response = client.post(
        '/api/v1/enrollments/',
        json={
            'name': enrollment_data['name'],
            'cpf': enrollment_data['cpf'],
            'age': 150,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.json()

    assert body['message'] == 'enrollment rejected, age group not found'


@patch('finaluser.services.enrollment.EnrollmentService.publish_enrollment_message')
@patch('finaluser.repositories.age_group.AgeGroupRepository.get_by_age')
@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_cpf')
def test_create_enrollment_with_missing_age_group(
    mock_get_by_cpf,
    mock_get_by_age,
    mock_publish_sqs,
    enrollment_data,
):
    service = EnrollmentService()

    enrollment_input = EnrollmentIn(
        name=enrollment_data['name'],
        cpf=enrollment_data['cpf'],
        age=150,  # idade fora de faixa
    )

    mock_get_by_cpf.return_value = None
    mock_get_by_age.return_value = None
    mock_publish_sqs.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

    result = service.create_enrollment(enrollment_input)

    assert isinstance(result, EnrollmentOut)
    assert result.status == EnrollmentStatus.rejected


@patch('finaluser.services.enrollment.get_sqs_client')
@patch('finaluser.services.enrollment.get_queue_url')
def test_publish_enrollment_message_success(
    mock_get_queue_url,
    mock_get_sqs_client,
    enrollment_data,
):
    mock_queue_url = 'http://localhost:4566/000000000000/enrollments'
    mock_get_queue_url.return_value = mock_queue_url

    mock_sqs = MagicMock()
    mock_sqs.send_message.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200},
        'MessageId': '12345678Sqs',
    }
    mock_get_sqs_client.return_value = mock_sqs

    enrollment = EnrollmentOut(**enrollment_data)

    response = EnrollmentService.publish_enrollment_message(enrollment)

    mock_sqs.send_message.assert_called_once()
    assert response['ResponseMetadata']['HTTPStatusCode'] == HTTPStatus.OK


@patch('finaluser.services.enrollment.get_sqs_client')
@patch('finaluser.services.enrollment.get_queue_url')
def test_publish_enrollment_message_failure(
    mock_get_queue_url,
    mock_get_sqs_client,
    enrollment_data,
):
    mock_queue_url = 'http://localhost:4566/000000000000/enrollments'
    mock_get_queue_url.return_value = mock_queue_url

    mock_sqs = MagicMock()
    mock_sqs.send_message.side_effect = Exception('SQS failure')
    mock_get_sqs_client.return_value = mock_sqs

    enrollment = EnrollmentOut(**enrollment_data)

    with pytest.raises(EnrollmentSQSError):
        EnrollmentService.publish_enrollment_message(enrollment)


@patch('finaluser.repositories.enrollment.EnrollmentRepository.get_by_id')
def test_get_enrollment(
    mock_get_by_id,
    client,
    enrollment_data,
):
    mock_get_by_id.return_value = enrollment_data

    response = client.get(f'/api/v1/enrollments/{enrollment_data["id"]}')
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['cpf'] == enrollment_data['cpf']
    assert data['age_group_id'] == enrollment_data['age_group_id']
