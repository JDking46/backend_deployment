from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency import get_db
from schemas.patient import PatientCreate, Patient
from models.patient import Patient as PatientModel
from models.request import HelpRequest as HelpRequestModel
from models.doctor import Doctor as DoctorModel
from sqlalchemy import func
from auth.hash import verify_password,hash_password 

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", response_model=Patient)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(patient_in.password)
    patient = PatientModel(**patient_in.dict(exclude={"password"}), password=hashed_password)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
 

@router.get("/", response_model=list[Patient])
def list_patients(db: Session = Depends(get_db)):
    return db.query(PatientModel).all()

@router.put("/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, data: PatientCreate, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(
        PatientModel.patient_id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = data.dict(exclude_unset=True)

    # 🔐 If password is updated → hash it
    if update_data.get("password"):
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return


@router.get("/{patient_id}/requests/")
def get_patient_request_breakdown(patient_id: int, db: Session = Depends(get_db)):
    # total and counts grouped by status
    total = db.query(HelpRequestModel).filter(HelpRequestModel.patient_id == patient_id).count()
    rows = (
        db.query(HelpRequestModel.status, func.count().label("count"))
        .filter(HelpRequestModel.patient_id == patient_id)
        .group_by(HelpRequestModel.status)
        .all()
    )
    breakdown = {r.status: r.count for r in rows}
    return {"patient_id": patient_id, "total_requests": total, "by_status": breakdown}


@router.get("/{patient_id}/requests/all")
def get_all_patient_requests(patient_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(
            HelpRequestModel.request_id.label("request_id"),
            HelpRequestModel.doctor_id.label("doctor_id"),
            DoctorModel.name.label("doctor_name"),
            HelpRequestModel.request_date.label("request_date"),
            HelpRequestModel.problem_description.label("problem_description"),
            HelpRequestModel.status.label("status"),
        )
        .join(DoctorModel, HelpRequestModel.doctor_id == DoctorModel.doctor_id)
        .filter(HelpRequestModel.patient_id == patient_id)
        .all()
    )

    result = []
    for r in rows:
        row_dict = {
            "request_id": r.request_id,
            "doctor_id": r.doctor_id,
            "doctor_name": r.doctor_name,
            "request_date": r.request_date.isoformat() if r.request_date else None,
            "problem_description": r.problem_description,
            "status": r.status,
        }
        result.append(row_dict)

    return result

