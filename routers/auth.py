from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency import get_db
from models.doctor import Doctor
from models.patient import Patient
from models.admin import Admin
from schemas.auth import LoginRequest, LoginResponse, ResetPasswordRequest
from auth.hash import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login/doctor", response_model=LoginResponse)
def login_doctor(data: LoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.email == data.email).first()
    if not doctor or not verify_password(data.password, doctor.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return LoginResponse(
        id=doctor.doctor_id,
        name=doctor.name,
        email=doctor.email,
        role="doctor"
    )

@router.post("/login/patient", response_model=LoginResponse)
def login_patient(data: LoginRequest, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.email == data.email).first()
    if not patient or not verify_password(data.password, patient.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return LoginResponse(
        id=patient.patient_id,
        name=patient.name,
        email=patient.email,
        role="patient"
    )

@router.post("/login/admin", response_model=LoginResponse)
def login_admin(data: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.email).first()
    if not admin or not verify_password(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return LoginResponse(
        id=admin.admin_id,
        name=admin.name,
        email=admin.email,
        role="admin"
    )

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    if data.role == "doctor":
        user = db.query(Doctor).filter(Doctor.email == data.email).first()
    elif data.role == "patient":
        user = db.query(Patient).filter(Patient.email == data.email).first()
    elif data.role == "admin":
        user = db.query(Admin).filter(Admin.email == data.email).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password reset successful"}
