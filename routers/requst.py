from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from dependency import get_db
from schemas.request import HelpRequestCreate, HelpRequest
from models.request import HelpRequest as HelpRequestModel
from models.patient import Patient
from models.doctor import Doctor
import shutil
import os

router = APIRouter(prefix="/help_requests", tags=["help_requests"])

UPLOAD_DIR = "uploads"

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print(f"Created directory: {UPLOAD_DIR}")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    print(f"Receiving file: {file.filename}, saving to: {file_path}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"File {file.filename} saved successfully.")
    return {"filename": file.filename}


@router.post("/", response_model=HelpRequest)
def create_help_request(hr_in: HelpRequestCreate, db: Session = Depends(get_db)):
 

    patient = db.query(Patient).filter(Patient.patient_id == hr_in.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid patient_id")
    

  
    doctor = db.query(Doctor).filter(Doctor.doctor_id == hr_in.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=400, detail="Invalid doctor_id")

    help_request = HelpRequestModel(**hr_in.dict())
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    return help_request
   



@router.get("/{request_id}", response_model=HelpRequest)
def get_help_request(request_id: int, db: Session = Depends(get_db)):
    help_request = db.query(HelpRequestModel).filter(HelpRequestModel.request_id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found")
    return help_request




@router.put("/{request_id}", response_model=HelpRequest)
def update_help_request(request_id: int, data: HelpRequestCreate, db: Session = Depends(get_db)):
    help_request = db.query(HelpRequestModel).filter(HelpRequestModel.request_id == request_id).first()
    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found")
    for key, value in data.dict().items():
        setattr(help_request, key, value)

    db.commit()
    db.refresh(help_request)
    return help_request




@router.delete("/{request_id}", status_code=204)
def delete_help_request(request_id: int, db: Session = Depends(get_db)):
    help_request = db.query(HelpRequestModel).filter(HelpRequestModel.request_id == request_id).first()

    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found")
    db.delete(help_request)
    db.commit()
    return {"user delete  succufully"}
   

@router.get("/help-requests/doctor/{doctor_id}/count")
def get_doctor_request_count(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    total = db.query(HelpRequestModel).filter(
        HelpRequestModel.doctor_id == doctor_id
        
    ).count()

    return {
        "doctor_id": doctor_id,
        "total_patient_requests": total
    }
    
@router.get("/help-requests/doctor/{doctor_id}")
def get_requests_with_patient_details(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    # Return dict-like rows and convert date to ISO string for JSON
    results = (
        db.query(
            HelpRequestModel.request_id.label("request_id"),
            Patient.patient_id.label("patient_id"),
            Patient.name.label("patient_name"),
            Patient.age.label("patient_age"),
            HelpRequestModel.request_date.label("request_date"),
            HelpRequestModel.final_date.label("final_date"),
            HelpRequestModel.document_name.label("document_name"),
            HelpRequestModel.problem_description.label("problem_description"),
            HelpRequestModel.status.label("status"),
        )
        .join(Patient, HelpRequestModel.patient_id == Patient.patient_id)
        .filter(HelpRequestModel.doctor_id == doctor_id)
        .all()
    )

    details = []
    for i in results:
        # Check if this patient already has an accepted request from ANY doctor
        # This helps remind the current doctor if the patient is already being helped
        other_accepted = db.query(HelpRequestModel).filter(
            HelpRequestModel.patient_id == i.patient_id,
            HelpRequestModel.status == "accepted",
            HelpRequestModel.request_id != i.request_id
        ).first()

        row_dict = {
            "request_id": i.request_id,
            "patient_id": i.patient_id,
            "patient_name": i.patient_name,
            "patient_age": i.patient_age,
            "request_date": i.request_date.isoformat() if i.request_date else None,
            "final_date": i.final_date.isoformat() if i.final_date else None,
            "document_name": i.document_name,
            "problem_description": i.problem_description,
            "status": i.status,
            "already_accepted_elsewhere": True if other_accepted else False
        }
        details.append(row_dict)

    return details

@router.get("/requests/{request_id}/status")
def get_request_status(request_id: int, db: Session = Depends(get_db)):
    request = db.query(HelpRequestModel).filter(
        HelpRequestModel.request_id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return {
        "request_id": request.request_id,
        "patient_id": request.patient_id,
        "doctor_id": request.doctor_id,
        "message": getattr(request, "message", None),
        "status": request.status,
        "updated_at": getattr(request, "updated_at", None)
    }


@router.put("/help-requests/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    request = db.query(HelpRequestModel).filter(
        HelpRequestModel.request_id == request_id
    ).first()

    if not request:
        return {"error": "Request not found"}

    setattr(request, "status", "accepted")
    db.commit()

    return {"message": "Request accepted"}
@router.put("/help-requests/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    request = db.query(HelpRequestModel).filter(
        HelpRequestModel.request_id == request_id
    ).first()

    if not request:
        return {"error": "Request not found"}

    setattr(request, "status", "rejected")
    db.commit()

    return {"message": "Request rejected"}





