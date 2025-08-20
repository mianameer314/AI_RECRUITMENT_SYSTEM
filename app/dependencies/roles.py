from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user

def require_candidate(user=Depends(get_current_user)):
    if user["role"] != "candidate":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Candidates only")
    return user
