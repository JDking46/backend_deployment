from pydantic import BaseModel, ConfigDict

class PatientBase(BaseModel):
    name: str
    email: str
    age: int | None = None
    gender: str | None = None
    health_condition: str | None = None
    required_treatment: str | None = None
    phone: str | None = None

class PatientCreate(PatientBase):
    password: str

class Patient(PatientBase):
    patient_id: int

    model_config = ConfigDict(from_attributes=True)
