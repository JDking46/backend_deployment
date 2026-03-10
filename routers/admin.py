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
