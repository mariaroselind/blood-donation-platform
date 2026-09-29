# authentication/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.database import get_db
from models import models
from authentication.security import SECRET_KEY, ALGORITHM

# 1. This tells FastAPI where to get the token from (useful for the Swagger UI padlock feature)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/patients/login")

# 2. Base Guard: Checks if a valid token exists and returns the User
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token using our Secret Key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Find the user in the database
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

# 3. Specific Guard: Ensures the user is specifically a PATIENT
def get_current_patient(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access the patient dashboard."
        )
    return current_user

# authentication/dependencies.py (Add to bottom)

# Specific Guard: Ensures the user is specifically a DONOR
def get_current_donor(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access the donor dashboard."
        )
    return current_user

# authentication/dependencies.py (Add to bottom)

# Specific Guard: Ensures the user is specifically an ADMIN
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access the admin dashboard."
        )
    return current_user