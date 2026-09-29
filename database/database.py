# database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Build the Database URL for SQLite
# This tells SQLAlchemy to create a file named 'blood_donation.db' in your current folder.
SQLALCHEMY_DATABASE_URL = "sqlite:///./blood_donation.db"

# 2. Create the SQLAlchemy Engine
# The 'connect_args={"check_same_thread": False}' is a special requirement ONLY for SQLite.
# FastAPI can receive multiple requests at once (on different threads). 
# By default, SQLite blocks this, so we turn that restriction off.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal class
# This creates a temporary workspace for database queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Declarative Base
# Our future database tables will inherit from this Base class.
Base = declarative_base()

# 5. Dependency function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 6. Quick test to verify the connection
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("Successfully connected to the SQLite database!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")