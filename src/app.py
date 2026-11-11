"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Activities are loaded from activities.json, making it easy for non-technical
users to add, edit, or remove activities without modifying code.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import json
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


def load_activities():
    """Load activities from activities.json file"""
    activities_file = Path(__file__).parent / "activities.json"
    
    try:
        with open(activities_file, 'r') as f:
            activities = json.load(f)
        return activities
    except FileNotFoundError:
        raise RuntimeError(f"activities.json not found at {activities_file}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in activities.json: {e}")


def save_activities(activities):
    """Save activities to activities.json file"""
    activities_file = Path(__file__).parent / "activities.json"
    
    try:
        with open(activities_file, 'w') as f:
            json.dump(activities, f, indent=2)
    except IOError as e:
        raise RuntimeError(f"Failed to save activities.json: {e}")


# Load activities on startup
activities = load_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    
    # Save changes to file
    save_activities(activities)
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    
    # Save changes to file
    save_activities(activities)
    
    return {"message": f"Unregistered {email} from {activity_name}"}
