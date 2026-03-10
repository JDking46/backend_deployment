from pydantic import BaseModel, ConfigDict

class DoctorBase(BaseModel):
    name: str
    email: str
    specialization: str | None = None
    hospital_name: str | None = None
    availability: str | None = "Available"
    phone: str | None = None
    is_approved: bool = False
    profile_picture: str | None = None

class DoctorCreate(DoctorBase):
    password: str

class Doctor(DoctorBase):
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)