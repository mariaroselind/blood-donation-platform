# models/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # "admin", "patient", "donor"

    # Relationships (The Magic Bridges)
    # uselist=False ensures this is a One-to-One relationship
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    donor_profile = relationship("Donor", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    # One-to-Many: A patient can have multiple requests
    blood_requests = relationship("BloodRequest", back_populates="patient")

class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    address = Column(String, nullable=False)
    location = Column(String, nullable=False)
    last_donation_date = Column(Date, nullable=True)
    availability_status = Column(String, default="Available") 

    # Relationships
    user = relationship("User", back_populates="donor_profile")
    matches = relationship("Match", back_populates="donor")

class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    bystander_name = Column(String, nullable=False)
    bystander_phone = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    hospital = Column(String, nullable=False)
    hospital_location = Column(String, nullable=False)
    units_required = Column(Integer, nullable=False)
    required_date = Column(Date, nullable=False)
    additional_notes = Column(Text, nullable=True)
    
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="blood_requests")
    matches = relationship("Match", back_populates="blood_request")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("donors.id"), nullable=False)
    
    # "Pending", "Accepted", "Ignored"
    match_status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    blood_request = relationship("BloodRequest", back_populates="matches")
    donor = relationship("Donor", back_populates="matches")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Integer, default=0) # 0 for false, 1 for true
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")