# Blood Donation Management System

A web-based blood donation management platform built with Python and FastAPI. The system connects patients, donors, and administrators, allowing users to manage blood requests, donations, notifications, and user information through dedicated dashboards.

## System Architecture

- **Frontend:** HTML, CSS, JavaScript
- **Backend Framework:** Python, FastAPI
- **Database:** SQLite (managed via SQLAlchemy)
- **API:** FastAPI REST APIs

## Features

- **Role-Based Dashboards:** Separate dashboards for patients, donors, and administrators.
- **Blood Request Management:** Patients can create and track blood requests with required blood group and quantity.
- **Donor Management:** Donors can manage their profiles, availability, and view relevant blood requests.
- **Blood Group Matching:** Identifies suitable donors based on blood group and availability.
- **Notifications:** Sends notifications to relevant donors when a new blood request is created.
- **Donation Management:** Tracks successful donations and donor donation history.
- **Admin Analytics:** Provides graphical representations of total and successful donations along with other system statistics.
