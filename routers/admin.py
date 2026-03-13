from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency import get_db
from schemas.admin import AdminCreate, Admin
from models.admin import Admin as AdminModel
from auth.hash import hash_password

router = APIRouter(prefix="/admins", tags=["admins"])

@router.post("/", response_model=Admin)
def create_admin(admin_in: AdminCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_admin = db.query(AdminModel).filter(AdminModel.email == admin_in.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = hash_password(admin_in.password)
    admin = AdminModel(**admin_in.dict(exclude={"password"}), password=hashed_password)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.get("/{admin_id}", response_model=Admin)
def get_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(AdminModel).filter(AdminModel.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from models.doctor import Doctor
    from models.patient import Patient
    from models.request import HelpRequest
    
    total_doctors = db.query(Doctor).count()
    total_patients = db.query(Patient).count()
    
    # Fetch all help requests with patient and doctor names
    results = db.query(
        HelpRequest.request_id,
        HelpRequest.request_date,
        HelpRequest.final_date,
        HelpRequest.status,
        Patient.name.label("patient_name"),
        Doctor.name.label("doctor_name")
    ).join(Patient, HelpRequest.patient_id == Patient.patient_id)\
     .join(Doctor, HelpRequest.doctor_id == Doctor.doctor_id).all()
    
    recent_requests = []
    for r in results:
        recent_requests.append({
            "request_id": r.request_id,
            "request_date": r.request_date.isoformat() if r.request_date else None,
            "final_date": r.final_date.isoformat() if r.final_date else None,
            "status": r.status,
            "patient_name": r.patient_name,
            "doctor_name": r.doctor_name
        })
        
    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "recent_requests": recent_requests
    }
