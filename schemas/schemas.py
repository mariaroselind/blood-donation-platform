# schemas/schemas.py
from pydantic import BaseModel

# This class defines exactly what we expect from the user when they register
class PatientCreate(BaseModel):
    name: str
    email: str
    password: str

# Add this class to the bottom of schemas/schemas.py

class Token(BaseModel):
    access_token: str
    token_type: str

# Add this to the bottom of schemas/schemas.py

from datetime import date
from typing import Optional
from pydantic import BaseModel

class DonorCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    blood_group: str
    age: int
    gender: str
    address: str
    location: str
    last_donation_date: Optional[date] = None

# schemas/schemas.py (Add to bottom)
from datetime import date
from typing import Optional

class BloodRequestCreate(BaseModel):
    bystander_name: str
    bystander_phone: str
    blood_group: str
    hospital: str
    hospital_location: str
    units_required: int
    required_date: date
    additional_notes: Optional[str] = None

# schemas/schemas.py (Add to bottom)

class MatchUpdate(BaseModel):
    match_status: str  # Expected: "Accepted" or "Declined"

