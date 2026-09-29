# authentication/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration variables
# In a real production app, SECRET_KEY should be inside your .env file!
# For this learning project, we will define it here.
SECRET_KEY = "super-secret-digital-blood-donation-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token lasts for 24 hours

# 1. Set up the Password Hashing Context
# We are using 'bcrypt', which is the industry standard for password hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Function to Hash a Password (used during Registration)
def get_password_hash(password: str) -> str:
    """Takes a plain text password and returns a scrambled, secure hash."""
    return pwd_context.hash(password)

# 3. Function to Verify a Password (used during Login)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain text password against the stored hash to see if they match."""
    return pwd_context.verify(plain_password, hashed_password)

# 4. Function to Create a JWT Token (used during Login)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JSON Web Token containing user data (like their user ID)."""
    to_encode = data.copy()
    
    # Calculate when the token should expire
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    # Add the expiration time into the token payload
    to_encode.update({"exp": expire})
    
    # Cryptographically sign the token using our SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt