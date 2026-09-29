# services/matching.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta
from models import models

def find_and_create_matches(db: Session, blood_request: models.BloodRequest) -> int:
    """
    Finds eligible donors enforcing the 90-day donation rule.
    """
    # Calculate the exact date 90 days ago from today
    ninety_days_ago = date.today() - timedelta(days=90)
    
    # Query: Exact blood group AND Available AND (Never Donated OR Donated >= 90 days ago)
    eligible_donors = db.query(models.Donor).filter(
        models.Donor.blood_group == blood_request.blood_group,
        models.Donor.availability_status == "Available",
        or_(
            models.Donor.last_donation_date == None,
            models.Donor.last_donation_date <= ninety_days_ago
        )
    ).all()

    matches_created = 0
    
    for donor in eligible_donors:
        new_match = models.Match(
            request_id=blood_request.id,
            donor_id=donor.id,
            match_status="Pending"
        )
        db.add(new_match)
        matches_created += 1
        
    db.commit()
    return matches_created