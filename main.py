# main.py
from fastapi import FastAPI
from database.database import engine, Base, SessionLocal # <--- NEW: Imported SessionLocal
from models import models 
from routers import patient, donor, admin # <--- NEW: Imported admin router
from authentication.security import get_password_hash # <--- NEW: To hash the admin password

# 1. Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# 2. Function to seed the database with an Admin user
def create_admin_user():
    db = SessionLocal()
    # Check if an admin already exists
    admin_user = db.query(models.User).filter(models.User.email == "admin@bloodbank.com").first()
    
    if not admin_user:
        print("No admin found. Creating default admin account...")
        hashed_pw = get_password_hash("admin123") # Default password
        new_admin = models.User(
            email="admin@bloodbank.com",
            hashed_password=hashed_pw,
            role="admin"
        )
        db.add(new_admin)
        db.commit()
        print("Admin account created successfully!")
    
    db.close()

# Run the function immediately before the app starts
create_admin_user()

# 3. Initialize FastAPI App
app = FastAPI(
    title="Digital Blood Donation Platform",
    description="API for managing blood donations, patients, and donors.",
    version="1.0.0"
)

# 4. Connect our routers
app.include_router(patient.router)
app.include_router(donor.router, prefix="/api/donors", tags=["Donors"])
app.include_router(admin.router) # <--- NEW: Attached admin router

# main.py (Update the bottom section)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ... (keep your app.include_router lines) ...
app.include_router(patient.router)
app.include_router(donor.router)
app.include_router(admin.router)

# 1. Ensure the frontend folder exists
os.makedirs("frontend", exist_ok=True)

# 2. Mount the frontend folder so FastAPI can serve CSS/JS files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 3. Serve the main HTML page when visiting the root URL
# main.py (Add these routes near the bottom)
@app.get("/login.html")
async def serve_login():
    return FileResponse("frontend/login.html")

@app.get("/register.html")
async def serve_register():
    return FileResponse("frontend/register.html")

@app.get("/dashboard.html")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

