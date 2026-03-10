from pydantic import BaseModel, ConfigDict

class AdminBase(BaseModel):
    name: str
    email: str
    phone: str | None = None

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    admin_id: int

    model_config = ConfigDict(from_attributes=True)
