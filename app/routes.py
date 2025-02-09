from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models import User, Scan
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import re

router = APIRouter()

#User class
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    badge_code: str

#Activity Class
class ScanCreate(BaseModel):
    activity_name: str
    activity_category: str

#Update (user) Class
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

#Check-in (Bool kinda)
class CheckInOut(BaseModel):
    status: str  #"IN" or "OUT"

#All Checked in users
checked_in_users = {}  #{badge_code: "IN" or "OUT"}

""" 
Set scan limit for activities
Format:
"Activity Name"; #of scans allowed,
"""  
activity_scan_limits = {
    "Midnight Snack": 1,  
    "Hackathon Swag": 2, 
    "Lunch": 3,
}

friendships = {} 

#Get all users
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

#Create a new user
@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validate badge code format
    if not re.match(r'^[a-z0-9-]+$', user.badge_code):
        raise HTTPException(status_code=400, detail="Invalid badge code format")
    
    # Check if email or badge_code already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    if db.query(User).filter(User.badge_code == user.badge_code).first():
        raise HTTPException(status_code=400, detail="Badge code already in use.")

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        badge_code=user.badge_code,
        updated_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "phone": new_user.phone,
        "badge_code": new_user.badge_code,
        "updated_at": new_user.updated_at.isoformat()
    }

#Get a specific user (Their info, scans, check-in status and friend list)
@router.get("/users/{badge_code}")
def get_user(badge_code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_code == badge_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "badge_code": user.badge_code,
        "updated_at": user.updated_at.isoformat(),
        "checked_in": checked_in_users.get(badge_code, "OUT"),  # Check-in status
        "friends": list(friendships.get(badge_code, [])),  # Friend list
        "scans": [
            {
                "activity_name": scan.activity_name,
                "scanned_at": scan.scanned_at.isoformat(),
                "activity_category": scan.activity_category
            }
            for scan in user.scans
        ]
    }

#Let users make friends 
@router.post("/users/{badge_code}/add-friend/{friend_badge}")
def add_friend(badge_code: str, friend_badge: str, db: Session = Depends(get_db)):
    if badge_code == friend_badge:
        raise HTTPException(status_code=400, detail="You cannot add yourself as a friend.")

    user = db.query(User).filter(User.badge_code == badge_code).first()
    friend = db.query(User).filter(User.badge_code == friend_badge).first()

    if not user or not friend:
        raise HTTPException(status_code=404, detail="One or both users not found.") #Schizo friend someone doesn't exist

    friendships.setdefault(badge_code, set()).add(friend_badge)
    friendships.setdefault(friend_badge, set()).add(badge_code)  #Mutual friendship (no one sided love)

    return {
        "message": f"{badge_code} and {friend_badge} are now friends!",
        "friends": list(friendships.get(badge_code, []))  #Returns an updated friend list to confirm
    }


#Update user details (Supports partial updates)
@router.put("/users/{badge_code}")
def update_user(badge_code: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_code == badge_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.phone is not None:
        user.phone = user_update.phone
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "badge_code": user.badge_code,
        "updated_at": user.updated_at.isoformat(),
        "checked_in": checked_in_users.get(badge_code, "OUT"),
        "friends": list(friendships.get(badge_code, [])),
        "scans": [
            {
                "activity_name": scan.activity_name,
                "scanned_at": scan.scanned_at.isoformat(),
                "activity_category": scan.activity_category
            }
            for scan in user.scans
        ]
    }

#Post a scan for a user
@router.post("/scan/{badge_code}")
def scan_user(badge_code: str, scan_data: ScanCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_code == badge_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #Check the scan limit for the activity
    if scan_data.activity_name in activity_scan_limits:
        max_scans = activity_scan_limits[scan_data.activity_name]

        #Count number of scans to this activity
        scan_count = db.query(Scan).filter(
            Scan.user_id == user.id,
            Scan.activity_name == scan_data.activity_name
        ).count()

        #Scan limit policing
        if scan_count >= max_scans:
            raise HTTPException(
                status_code=403, 
                detail=f"Scan limit exceeded for {scan_data.activity_name}. Max allowed: {max_scans}"
            )

    #Passed the scan (vibe) limit check
    scan = Scan(
        user_id=user.id,
        activity_name=scan_data.activity_name,
        activity_category=scan_data.activity_category,
        scanned_at=datetime.utcnow()
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    return {
        "id": scan.id,
        "user_id": scan.user_id,
        "activity_name": scan.activity_name,
        "activity_category": scan.activity_category,
        "scanned_at": scan.scanned_at.isoformat()
    }

#Get all scans
@router.get("/scans")
def get_scans(activity_category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Scan)
    if activity_category:
        query = query.filter(Scan.activity_category == activity_category)

    return query.all()

#Activity's scnas by the hour
@router.get("/activity-scans")
def get_activity_scans(
    activity_name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        func.strftime('%Y-%m-%d %H:00:00', Scan.scanned_at).label("time_period"),
        func.count(Scan.id).label("scan_count")
    ).filter(Scan.activity_name == activity_name)

    if start_time:
        start_dt = datetime.fromisoformat(start_time)
        query = query.filter(Scan.scanned_at >= start_dt)

    if end_time:
        end_dt = datetime.fromisoformat(end_time)
        query = query.filter(Scan.scanned_at <= end_dt)

    query = query.group_by("time_period").order_by("time_period")

    result = query.all()
    return [{"time_period": row.time_period, "scan_count": row.scan_count} for row in result]

#Check-in a user
@router.post("/check-in/{badge_code}")
def check_in_user(badge_code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_code == badge_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    checked_in_users[badge_code] = "IN"
    return {"message": f"User {badge_code} checked in successfully", "status": "IN"}

#Check-out a user
@router.post("/check-out/{badge_code}")
def check_out_user(badge_code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_code == badge_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    checked_in_users[badge_code] = "OUT"
    return {"message": f"User {badge_code} checked out successfully", "status": "OUT"}

#Get check-in status of a user
@router.get("/check-status/{badge_code}")
def check_user_status(badge_code: str):
    status = checked_in_users.get(badge_code, "OUT")
    return {"badge_code": badge_code, "checked_in": status}

#Get all checked-in users (at the moment of)
@router.get("/checked-in-users")
def get_checked_in_users():
    return {"checked_in_users": [badge for badge, status in checked_in_users.items() if status == "IN"]}
