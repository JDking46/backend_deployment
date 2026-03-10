from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from models.request import HelpRequest
 
from db.session import Base

class Doctor(Base):
    __tablename__ = "doctor"

    doctor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    specialization = Column(String(100))
    hospital_name = Column(String(150))
    availability = Column(String(50))
    phone = Column(String(15))
    is_approved = Column(Boolean, default=True)
    profile_picture = Column(String(255), nullable=True)

    help_requests = relationship("HelpRequest", backref="doctor")