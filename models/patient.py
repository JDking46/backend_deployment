from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from db.session import Base

class Patient(Base):
    __tablename__ = "patient"

    patient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    health_condition = Column(Text)
    required_treatment = Column(Text)
    phone = Column(String(15))

    help_requests = relationship("HelpRequest", backref="patient")