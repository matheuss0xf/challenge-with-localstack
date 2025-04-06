import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EnrollmentStatus(str, Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class EnrollmentBase(BaseModel):
    name: str = Field(max_length=35, min_length=3, description='Name of the user enrolling')
    cpf: str = Field(
        pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        description='CPF format: XXX.XXX.XXX-XX',
    )
    age: int = Field(description='Age of the user enrolling')

    @classmethod
    @field_validator('cpf')
    def validate_cpf(cls, cpf):
        return re.sub(r'\D', '', cpf)


class EnrollmentIn(EnrollmentBase):
    """Schema for creating a new enrollment."""

    pass


class EnrollmentOut(EnrollmentBase):
    id: str = Field(description='Unique identifier for the enrollment')
    status: str = Field(
        default=EnrollmentStatus.pending,
        description='Status of the enrollment (pending, approved, rejected)',
    )
    age_group_id: str = Field(default='', description='Age of the user enrolling')

    model_config = ConfigDict(from_attributes=True)


class EnrollmentResponse(BaseModel):
    message: str = Field(description='Response message')
    data: Optional[EnrollmentOut] = Field(default=None, description='Enrollment data')
