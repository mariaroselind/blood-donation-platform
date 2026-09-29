# routers/donor.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models import models
from schemas import schemas
from authentication.security import get_password_hash
# routers/donor.py (Update top imports)
from authentication.dependencies import get_current_donor # <--- NEW IMPORT

# 1. Create a Router for Donors
router = APIRouter(
    prefix="/api/donors",
    tags=["Donors"]
)

# 2. Registration Endpoint
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_donor(donor_data: schemas.DonorCreate, db: Session = Depends(get_db)):
    """
    Register a new blood donor into the system.
    """
    # Step A: Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == donor_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Step B: Create the User account (for login)
    hashed_pw = get_password_hash(donor_data.password)
    new_user = models.User(
        email=donor_data.email,
        hashed_password=hashed_pw,
        role="donor" # Set role securely to donor
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Step C: Create the Donor profile linked to the User account
    new_donor = models.Donor(
        user_id=new_user.id,
        name=donor_data.name,
        phone=donor_data.phone,
        blood_group=donor_data.blood_group,
        age=donor_data.age,
        gender=donor_data.gender,
        address=donor_data.address,
        location=donor_data.location,
        last_donation_date=donor_data.last_donation_date  # <--- THIS IS THE FIX
    )
    
    db.add(new_donor)
    db.commit()

    return {"message": "Donor registered successfully!"}

    # Step C: Create the Donor profile linked to the User account
    new_donor = models.Donor(
        user_id=new_user.id,
        name=donor_data.name,
        phone=donor_data.phone,
        blood_group=donor_data.blood_group,
        age=donor_data.age,
        gender=donor_data.gender,
        address=donor_data.address,
        location=donor_data.location,
        # Notice we don't set last_donation_date or availability_status yet, 
        # they will use the defaults we set in models.py!
    )
    
    db.add(new_donor)
    db.commit()

    return {"message": "Donor registered successfully!"}

# Update the imports at the top of routers/donor.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # <--- NEW
from sqlalchemy.orm import Session

from database.database import get_db
from models import models
from schemas import schemas
from authentication.security import get_password_hash, verify_password, create_access_token # <--- NEW

# Paste this at the bottom of routers/donor.py

@router.post("/login", response_model=schemas.Token)
def login_donor(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a donor and return a JWT token.
    """
    # Step A: Find the user in the database by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Step B: Security Check - Ensure they exist AND are actually a donor
    if not user or user.role != "donor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # Step C: Verify the password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # Step D: Create the JWT Token
    # We embed their role as "donor" inside the token. 
    # Later, we will use this to grant them access to donor-only features!
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {"access_token": access_token, "token_type": "bearer"}


# routers/donor.py (Add to bottom)

@router.get("/dashboard")
def get_donor_dashboard(
    current_user: models.User = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """
    Protected route: Get donor dashboard data.
    """
    # 1. Fetch the donor's specific profile
    donor_profile = db.query(models.Donor).filter(models.Donor.user_id == current_user.id).first()
    
    # 2. Fetch all currently 'Pending' blood requests
    # (We will upgrade this to strict matching in Step 16)
    available_requests = db.query(models.BloodRequest).filter(models.BloodRequest.status == "Pending").all()
    
    return {
        "profile": {
            "name": donor_profile.name,
            "blood_group": donor_profile.blood_group,
            "availability": donor_profile.availability_status
        },
        "available_requests": available_requests
    }

# routers/donor.py (Replace your existing dashboard and add the new endpoint below)

# routers/donor.py (Replace get_donor_dashboard)

@router.get("/dashboard")
def get_donor_dashboard(
    current_user: models.User = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    donor_profile = db.query(models.Donor).filter(models.Donor.user_id == current_user.id).first()
    if not donor_profile:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    my_matches = db.query(models.Match).filter(models.Match.donor_id == donor_profile.id).all()
    
    detailed_matches = []
    for match in my_matches:
        req = db.query(models.BloodRequest).filter(models.BloodRequest.id == match.request_id).first()
        if req:
            patient = db.query(models.Patient).filter(models.Patient.id == req.patient_id).first()
            patient_name = patient.name if patient else req.bystander_name
            
            detailed_matches.append({
                "id": match.id,
                "match_status": match.match_status,
                "patient_name": patient_name,
                "blood_group": req.blood_group,
                "hospital": req.hospital,
                "hospital_location": req.hospital_location,
                "units_required": req.units_required,
                "required_date": req.required_date
            })
    
    return {
        "profile": {
            "name": donor_profile.name,
            "blood_group": donor_profile.blood_group,
            "availability": donor_profile.availability_status
        },
        "my_matches": detailed_matches
    }

@router.put("/matches/{match_id}")
def update_match_status(
    match_id: int,
    status_data: schemas.MatchUpdate,
    current_user: models.User = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Allow a donor to Accept or Decline a blood request match."""
    donor_profile = db.query(models.Donor).filter(models.Donor.user_id == current_user.id).first()
    
    # Find the specific match
    match = db.query(models.Match).filter(
        models.Match.id == match_id,
        models.Match.donor_id == donor_profile.id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    # Update the status
    match.match_status = status_data.match_status
    db.commit()
    
    return {"message": f"Match {status_data.match_status} successfully!"}

@router.post("/requests/{request_id}/accept", status_code=status.HTTP_200_OK)
def accept_blood_request(
    request_id: int,
    current_user: models.User = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Allows a donor to accept a pending blood request, creating an active match."""
    donor_profile = db.query(models.Donor).filter(models.Donor.user_id == current_user.id).first()
    if not donor_profile:
        raise HTTPException(status_code=404, detail="Donor profile not found")
    
    blood_request = db.query(models.BloodRequest).filter(models.BloodRequest.id == request_id).first()
    if not blood_request:
        raise HTTPException(status_code=404, detail="Blood request not found")
    
    # Create the match record
    new_match = models.Match(
        request_id=blood_request.id,
        donor_id=donor_profile.id,
        match_status="Accepted"
    )
    
    # Update request status to reflect progress
    blood_request.status = "Accepted"
    
    db.add(new_match)
    db.commit()

    return {"message": "Request accepted successfully!"}



