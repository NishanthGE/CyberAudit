"""
Behavioral Profiler Route — Per-user activity profiles and deviation scores
"""

from fastapi import APIRouter, HTTPException
from models.behavioral_profiler import get_user_profile, get_all_user_ids

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/users")
async def list_users():
    """Return all user IDs that have profiled activity."""
    users = get_all_user_ids()
    return {"users": users, "count": len(users)}


@router.get("/{user_id}")
async def get_profile(user_id: str):
    """Return behavioral profile for a specific user."""
    profile = get_user_profile(user_id)
    if profile["total_events"] == 0:
        raise HTTPException(status_code=404, detail=f"No activity found for user: {user_id}")
    return profile
