# routers/patient.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import our database, models, schemas, and security functions
from database.database import get_db
from models import models
from schemas import schemas
from authentication.security import get_password_hash
# Add this to the top imports of routers/patient.py
from authentication.dependencies import get_current_patient
# routers/patient.py (Add to top imports)
from services.matching import find_and_create_matches


# 1. Create a Router
# prefix="/api/patients" means every URL in this file starts with that path
# tags=["Patients"] groups these endpoints neatly in Swagger UI
router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"]
)

# 2. Create the Registration Endpoint
# It's a POST request because we are sending secure data to create something new.
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_patient(patient_data: schemas.PatientCreate, db: Session = Depends(get_db)):
    """
    Register a new patient into the system.
    """
    # Step A: Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == patient_data.email).first()
    if existing_user:
        # If user exists, stop and return a 400 Bad Request error
        raise HTTPException(status_code=400, detail="Email already registered")

    # Step B: Create the User account
    hashed_pw = get_password_hash(patient_data.password)
    new_user = models.User(
        email=patient_data.email,
        hashed_password=hashed_pw,
        role="patient" # Hardcode the role so they can't trick us into making them an admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # This grabs the newly created ID from the database

    # Step C: Create the Patient profile linked to the User account
    new_patient = models.Patient(
        user_id=new_user.id, # Link it using the Foreign Key!
        name=patient_data.name
    )
    
    db.add(new_patient)
    db.commit()

    return {"message": "Patient registered successfully!"}

# Update your imports at the top of routers/patient.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # <--- NEW
from sqlalchemy.orm import Session

from database.database import get_db
from models import models
from schemas import schemas
from authentication.security import get_password_hash, verify_password, create_access_token # <--- NEW

# Paste this at the bottom of routers/patient.py

@router.post("/login", response_model=schemas.Token)
def login_patient(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a patient and return a JWT token.
    """
    # Step A: Find the user in the database
    # Note: OAuth2 always uses the word 'username', so we map 'username' to our 'email' column
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # If the user doesn't exist, or if an admin/donor tries to log in through the patient portal
    if not user or user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # Step B: Verify the password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # Step C: Create the JWT Token
    # We store the user's email and role inside the token payload
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    # Return the token to the user
    return {"access_token": access_token, "token_type": "bearer"}

# Paste this at the bottom of routers/patient.py

@router.get("/dashboard")
def get_patient_dashboard(
    current_user: models.User = Depends(get_current_patient), 
    db: Session = Depends(get_db)
):
    """
    Protected route: Get patient dashboard data. 
    Requires a valid Patient JWT token.
    """
    # 1. Fetch the patient profile linked to this user
    patient_profile = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    
    # 2. Return their profile data
    # (In Step 14, we will also fetch and return their blood requests here!)
    return {
        "message": f"Welcome to your dashboard, {patient_profile.name}!",
        "profile": {
            "name": patient_profile.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }

# routers/patient.py (Add to bottom)

@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_blood_request(
    request_data: schemas.BloodRequestCreate,
    current_user: models.User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new blood request linked to the logged-in patient."""
    # Find the patient profile
    patient_profile = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    
    # Create the request (Patient Name is automatically linked via patient_id)
    new_request = models.BloodRequest(
        patient_id=patient_profile.id,
        bystander_name=request_data.bystander_name,
        bystander_phone=request_data.bystander_phone,
        blood_group=request_data.blood_group,
        hospital=request_data.hospital,
        hospital_location=request_data.hospital_location,
        units_required=request_data.units_required,
        required_date=request_data.required_date,
        additional_notes=request_data.additional_notes
    )
    
    db.add(new_request)
    db.commit()
    return {"message": "Blood request created successfully!"}

# --- UPDATE YOUR EXISTING DASHBOARD ENDPOINT ---
# Replace your previous get_patient_dashboard with this updated one:
@router.get("/dashboard")
def get_patient_dashboard(
    current_user: models.User = Depends(get_current_patient), 
    db: Session = Depends(get_db)
):
    patient_profile = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    
    # Fetch all requests made by this patient
    requests = db.query(models.BloodRequest).filter(models.BloodRequest.patient_id == patient_profile.id).all()
    
    return {
        "profile": {"name": patient_profile.name, "email": current_user.email},
        "my_requests": requests # Now the dashboard returns their requests!
    }

# routers/patient.py (Replace your existing create_blood_request function)

@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_blood_request(
    request_data: schemas.BloodRequestCreate,
    current_user: models.User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # 1. Create the new request
    new_request = models.BloodRequest(
        patient_id=patient.id,
        bystander_name=request_data.bystander_name,
        bystander_phone=request_data.bystander_phone,
        blood_group=request_data.blood_group,
        hospital=request_data.hospital,
        hospital_location=request_data.hospital_location,
        units_required=request_data.units_required,
        required_date=request_data.required_date,
        status="Pending"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # 2. Automatically link matching donors to this request
    eligible_donors = db.query(models.Donor).filter(
        models.Donor.blood_group == request_data.blood_group
    ).all()

    for donor in eligible_donors:
        new_match = models.Match(
            request_id=new_request.id,
            donor_id=donor.id,
            match_status="Pending"
        )
        db.add(new_match)
    
    db.commit()

    return {"message": "Blood request created and broadcasted to matching donors!"}
