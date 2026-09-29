# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.database import get_db
from models import models
from schemas import schemas
from authentication.security import verify_password, create_access_token
# routers/admin.py (Update top imports)
from datetime import date
from authentication.dependencies import get_current_admin # <--- NEW IMPORT


# 1. Create a Router for the Admin
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

# 2. Admin Login Endpoint
@router.post("/login", response_model=schemas.Token)
def login_admin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate the master Admin and return a JWT token.
    """
    # Step A: Find the user in the database by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Step B: Security Check - Ensure they exist AND are actually the admin
    if not user or user.role != "admin":
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

    # Step D: Create the JWT Token with the "admin" role embedded
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {"access_token": access_token, "token_type": "bearer"}

# routers/admin.py (Add to bottom)

@router.put("/matches/{match_id}/complete")
def complete_donation(
    match_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin marks a donation as completed, updating the donor's eligibility."""
    # 1. Find the match
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    if match.match_status != "Accepted":
        raise HTTPException(status_code=400, detail="Match must be 'Accepted' by donor first.")

    # 2. Find the connected Donor and Request
    donor = db.query(models.Donor).filter(models.Donor.id == match.donor_id).first()
    blood_request = db.query(models.BloodRequest).filter(models.BloodRequest.id == match.request_id).first()

    # 3. Update all three records
    match.match_status = "Completed"
    blood_request.status = "Fulfilled"
    donor.last_donation_date = date.today() # Locks them out for 90 days!

    db.commit()
    
    return {"message": "Donation completed successfully. Donor eligibility updated."}

# routers/admin.py (Add to bottom)

# routers/admin.py
@router.get("/dashboard")
def get_admin_dashboard(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    patients = db.query(models.Patient).all()
    donors = db.query(models.Donor).all()
    all_requests = db.query(models.BloodRequest).all()
    all_matches = db.query(models.Match).all()
    
    # Filter completed donations for analytics
    completed_matches = [m for m in all_matches if m.match_status == "Completed"]
    
    return {
        "system_stats": {
            "total_patients": len(patients),
            "total_donors": len(donors),
            "total_requests": len(all_requests),
            "total_matches": len(all_matches),
            "total_completed": len(completed_matches)
        },
        "all_patients": patients,
        "all_donors": donors,
        "all_requests": all_requests,
        "all_matches": all_matches
    }

