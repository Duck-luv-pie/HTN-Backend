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

## API Documentation:
**Get All Users Endpoint** - Returns a list of all users registered in the system.
- GET /users

ex response:
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1 555-1234",
    "badge_code": "user123",
    "updated_at": "2025-02-08T15:30:00Z"
  }
]


**Get User Information Endpoint** - Fetches details of a specific user by their badge code, including scan history, check-in status, and friend list.
- GET /users/{badge_code}

ex response:
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 555-1234",
  "badge_code": "user123",
  "updated_at": "2025-02-08T15:30:00Z",
  "checked_in": "OUT",
  "friends": ["friend456"],
  "scans": [
    {
      "activity_name": "Opening Ceremony",
      "scanned_at": "2025-02-08T10:00:00Z",
      "activity_category": "ceremony"
    }
  ]
}


**Create a New User Endpoint** - Registers a new user with a unique email and badge code.
- POST /users

ex. request:
{
  "id": 2,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1 555-9876",
  "badge_code": "user456",
  "updated_at": "2025-02-08T16:00:00Z"
}


**Update User Information Endpoint** - Updates user details (supports partial updates).
- PUT /users/{badge_code}

ex response 
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 555-9999",
  "badge_code": "user123",
  "updated_at": "2025-02-08T17:00:00Z"
}

**Add a Scan for a User Endpoint** - Logs a badge scan for an activity, enforcing scan limits per activity.

ex response: 
{
  "id": 5,
  "user_id": 1,
  "activity_name": "Midnight Snack",
  "activity_category": "food",
  "scanned_at": "2025-02-08T18:30:00Z"
}

if user exceeds limit expect
{
  "detail": "Scan limit exceeded for Midnight Snack. Max allowed: 1"
}


**Get All Scans** - Fetches all recorded scans. Supports optional filtering by activity category.
- GET /scans

ex response:
[
  {
    "id": 3,
    "user_id": 2,
    "activity_name": "Lunch",
    "activity_category": "food",
    "scanned_at": "2025-02-08T12:45:00Z"
  }
]


**Get Activity Scan Analytics** - Returns the number of scans per hour for a given activity.
- GET /activity-scans

ex response:
[
  {
    "time_period": "2025-02-09 12:00:00",
    "scan_count": 15
  },
  {
    "time_period": "2025-02-09 13:00:00",
    "scan_count": 8
  }
]

**Check-In & Check-Out EndPoints**
- Check-In: POST /check-in/{badge_code}
- Check-Out: POST /check-out/{badge_code}
- Check Status: GET /check-status/{badge_code}

ex responses:
{
  "message": "User user123 checked in successfully",
  "status": "IN"
}

{
  "badge_code": "user123",
  "checked_in": "IN"
}

**Friend System Endpoint** - Users can add each other as mutual friends.
- POST /users/{badge_code}/add-friend/{friend_badge}

ex response:
{
  "message": "user123 and user456 are now friends!",
  "friends": ["user456"]
}


**Get All Checked-In Users** - Returns a list of all currently checked-in users.
- GET /checked-in-users

ex response:
{
  "checked_in_users": ["user123", "user456"]
}

## Error Handling:
All endpoints return appropriate HTTP error codes:

400 - Bad Request (e.g., missing required fields)
403 - Forbidden (e.g., exceeded scan limit)
404 - Not Found (e.g., user doesn’t exist)
500 - Internal Server Error

## Important Decisions:

**Choosing FastAPI for the Backend**
I chose FastAPI because it’s lightweight, fast, and built for modern Python development. It has automatic documentation with Swagger UI, making API testing seamless. Additionally, Pydantic provides strong data validation, reducing the chances of malformed requests.

**Using SQLAlchemy with SQLite**
I used SQLAlchemy for ORM because it offers flexibility and direct control over queries. SQLite was chosen for local development because it’s lightweight, but the system can easily switch to PostgreSQL or MySQL for production.

**Enforcing Scan Limits**
To prevent users from over-scanning activities (e.g., taking too many snacks), I implemented a scan limit system. Each activity has a predefined limit, and users attempting to scan beyond that get a 403 Forbidden error.

**Real-Time Check-In System**
Instead of persisting check-in data in the database, I used an in-memory dictionary (checked_in_users) to track active check-ins. This keeps operations fast and efficient, as check-in state doesn’t need to persist between sessions.

**Mutual Friend System**
The friend system ensures that friendships are always mutual—if User A adds User B, then User B also has User A as a friend. This prevents one-sided friendships and makes querying relationships easier.

**Testing Strategy**
I set up pytest with a temporary SQLite database that resets before every test. This ensures tests are isolated, consistent, and repeatable, avoiding data conflicts between test runs.

**Deployment: Google Cloud + Kubernetes**
I deployed the backend on Google Cloud using Kubernetes (GKE) to ensure scalability and containerized orchestration.
Google Cloud Kubernetes Engine (GKE): Manages deployment and auto-scaling.
Dockerized Backend: The API runs in a container, ensuring a consistent environment across deployments.
Ingress for Routing: Configured Kubernetes ingress for exposing the API securely.
Cloud IAM & Authentication: Ensured that API access is controlled via Google Cloud IAM.
This setup makes the backend scalable, resilient, and production-ready, while also giving me hands-on experience with cloud deployment.


## BONUS FEATURES ADDED:
- Real-time Check-In System: Users can check in and out of events, and their status is updated live.
- Friend Badge Scanning: Allows mutual friend connections by scanning friends' badges.
- Activity Analytics: Provides insights on scan frequencies per hour for activities.
- Deployment Ready: Configurations included for Google cloud deployment


