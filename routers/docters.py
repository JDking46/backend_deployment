from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.doctors import DoctorCreate, Doctor
from dependency import get_db
from models.doctor import Doctor as DoctorModel
from models.request import HelpRequest as HelpRequestModel
from auth.hash import hash_password


router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/", response_model=Doctor)
def create_doctor(doctor_in: DoctorCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(doctor_in.password)
    doctor = DoctorModel(**doctor_in.dict(exclude={"password"}), password=hashed_password)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/", response_model=list[Doctor])
def list_doctors(db: Session = Depends(get_db)):
    return db.query(DoctorModel).all()


@router.get("/all", response_model=list[Doctor])
def list_all_doctors(db: Session = Depends(get_db)):
    # Return ALL doctors (for admin panel)
    return db.query(DoctorModel).all()

@router.get("/{doctor_id}", response_model=Doctor)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=Doctor)
def update_doctor(doctor_id: int, data: DoctorCreate, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    update_data = data.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items(): 
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    # Prevent deleting a doctor who has existing help requests
    existing = db.query(HelpRequestModel).filter(HelpRequestModel.doctor_id == doctor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cannot delete doctor with existing help requests")

    db.delete(doctor)
    db.commit()
    return

@router.put("/{doctor_id}/approve", response_model=Doctor)
def approve_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.is_approved = True
    db.commit()
    db.refresh(doctor)
    return doctor

@router.put("/{doctor_id}/reject", response_model=Doctor)
def reject_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Rejection currently deletes the doctor to keep it simple as requested in past conversations
    db.delete(doctor)
    db.commit()
    return doctor
