# HTN 2025 Backend Challenge

## INFO FOR REVIEWER:

## Table of Contents

## Introduction:
This is my submission for the Hack the North 2025 Backend Challenge. The project implements a backend API that tracks hackathon attendees, their badge scans, and activities. The system is built to store user data, check them into activities, and provide aggregated insights.

Use http://34.170.197.1/docs to access FastAPI deployment. This was done using Google Cloud and Kubernetes cluster

## Key Features:
- Attendee Management: Store and manage hackathon attendee data (name, email, phone, badge code).
- Activity Tracking: Track badge scans for different activities with built-in scan limit restrictions (e.g., midnight snack).
- Check-In System: Allow users to check in/out of activities with real-time status updates.
- Friend System: Users can add other attendees as friends, creating a mutual friend relationship.
- Analytics: Aggregated endpoints to analyze scan frequencies over time.
- RESTful API: Well-structured endpoints with validation and error handling.
- Database Persistence: Leveraging SQLAlchemy for robust and scalable data management.

## Tech Stack:
- Backend Framework: FastAPI
- Database: SQLite 
- ORM: SQLAlchemy
- Hosting: Google Cloud (with Kubernetes)
- Containerization: Docker
- Testing: pytest with FastAPI's TestClient

## Set-up Instructions (your own repo):
Clone the repo:
    git clone https://github.com/Duck-luv-pie/HTN-Backend.git
    cd HTN-Backend
Install Dependencies:
    pip install -r requirements.txt
Set up Database:
    python setup_db.py
Run server (local):
    uvicorn main:app --reload
Access Interactive Doc:
    http://localhost:8000/docs


## Assumptions & Edge Cases Fulfilled
- Users must have a unique email and badge code. 
- Scan limits are strictly enforced.
- Users cannot add themselves as friends.
- Check-in status persists until checkout is called.

## pytest Testing:
Run " pytest test_main.py " in terminal
What are the tests? Well they are:

- Test #1: Test User Creation
- Test #2: Test Getting a User
- Test #3: Test Updating User Info
- Test #4: Test Adding a Scan
- Test #5: Test Scan Restrictions (No Double Dip)
- Test #6: Test Check-in and Check-out
- Test #7: Test Friend System
- Test #8: Test Activity Scans by Hour
- Test #9: Test Duplicate User Creation
- Test #10: Test Non-Existent User Retrieval
- Test #11: Test Updating Non-Existent User
- Test #12: Test Adding a Scan for a Non-Existent User
- Test #13: Test Friend Request to Non-Existent User
- Test #14: Test Self Friendship Request
- Test #15: Test Check-In for Non-Existent User
- Test #16: Test Check-Out for Non-Existent User
- Test #17: Test Get Check-In Status for Non-Existent User
- Test #18: Test Checked-In Users List
- Test #19: Test Scan Limit for Multiple Activities
- Test #20: Test User Without Friends List
- Test #21: Test Invalid Badge Code Format
- Test #22: Test Fetching Scans with Filters

## BONUS FEATURES ADDED:
- Real-time Check-In System: Users can check in and out of events, and their status is updated live.
- Friend Badge Scanning: Allows mutual friend connections by scanning friends' badges.
- Activity Analytics: Provides insights on scan frequencies per hour for activities.
- Deployment Ready: Configurations included for Google cloud deployment


