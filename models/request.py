from sqlalchemy import Column, Integer, Date, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from db.session import Base

class HelpRequest(Base):
    __tablename__ = "help_request"

    request_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor.doctor_id"), nullable=False)
    request_date = Column(Date, nullable=False)
    final_date = Column(Date, nullable=True)
    document_name = Column(String(255), nullable=True)
    problem_description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="pending")
 