from datetime import date
from pydantic import BaseModel, ConfigDict

class HelpRequestBase(BaseModel):
    patient_id: int
    doctor_id: int
    request_date: date
    final_date: date | None = None
    document_name: str | None = None
    problem_description: str | None = None
    status: str | None = None
    

class HelpRequestCreate(HelpRequestBase):
    pass


class HelpRequest(HelpRequestBase):
    request_id: int

    model_config = ConfigDict(from_attributes=True)