from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from datetime import timedelta
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)
from models import UserCreate, UserBase
from database import users_collection
from bson import ObjectId

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    try:
        print(f"DEBUG: Attempting to find user with email: {user.email}")
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_dict = user.dict()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        
        print("DEBUG: Inserting new user into database...")
        result = await users_collection.insert_one(user_dict)
        return {"message": "User created successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"DATABASE ERROR during registration: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )

@router.post("/login")
async def login(response: Response, user_data: UserCreate): # Using UserCreate for email/password
    user = await users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    # Use secure=True and samesite="none" for cross-domain cookies in production
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none",
        secure=True, 
    )
    return {"message": "Logged in successfully", "user": {"email": user["email"], "full_name": user.get("full_name")}}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "full_name": current_user.get("full_name")}
