from pydantic import BaseModel, ConfigDict, Field, model_validator


class AgeGroupBase(BaseModel):
    min_age: int = Field(ge=0, lt=110, description='Minimum age of the group')
    max_age: int = Field(gt=0, le=110, description='Maximum age of the group')

    @model_validator(mode='after')
    def check_age_range(self):
        if self.min_age >= self.max_age:
            raise ValueError('min_age must be less than max_age')
        return self


class AgeGroupIn(AgeGroupBase):
    """Schema for creating an age group."""

    pass


class AgeGroupOut(AgeGroupBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
