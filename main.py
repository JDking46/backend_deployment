from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine, Base
from routers.docters import router as doctors_router
from routers.patient import router as patient_router
from routers.requst import router as help_requests_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()


@app.get("/")
def read_root(): return {"Hello": "World"}

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR) 
  
# Mount uploads directory to serve files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Include all routers with /api prefix to match frontend fetch calls
app.include_router(auth_router, prefix="/api")
app.include_router(doctors_router, prefix="/api")
app.include_router(patient_router, prefix="/api")
app.include_router(help_requests_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

 





 
