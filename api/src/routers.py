from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException
)
from fastapi.responses import (
    JSONResponse,
    HTMLResponse
)

from .models import (
    UserModel,
    ShowUserModel,
    UpdateUserModel
)
from .dependecies import (
    get_current_user,
    authenticate_user,
    create_access_token,
    create_access_super_token,
    get_password_hash
)
from .settings import db, ACCESS_TOKEN_EXPIRE_MINUTES

from typing import Optional, List

from datetime import datetime, timedelta
import pytz
from urllib.parse import (
    quote_plus,
    unquote_plus
)
import uuid

import re
import os


router = APIRouter()

# ============= Creating path operations ==============
@router.get("/")
def get_readme():
    return HTMLResponse(
        """
            <!DOCTYPE html>
            <html>            
                 <head>
                    <title>L'Aquarium</title>
                    <link rel="icon" type="image/png" sizes="32x32" href="">
                    <link rel="icon" type="image/png" sizes="16x16" href="">
                    <link rel="manifest" href="">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                    <h4>AQU-API: FastAPI Python 3.9</h4>
                    
                    <p>Server: nginx/unit:1.22.0</p>
                    
                        <p>In your production system, you probably have a frontend created with a modern framework like React, Vue.js, Angular or Laravel.</p> 

                        <p>And to communicate using APIs & WebSocket-APIs with your backend you would probably use your frontend's utilities.</p> 

                        <p>Or you might have a native mobile application that communicates with your WebSocket backend directly, in native code.</p> 

                        <p>Or you might have any other way to communicate with the API endpoint.</p> 
                            
                    <p>RESTful APIs Document: <a href='https://stage.api.waas.rankworks.com/docs#'>Swagger</a> <img src="https://htmlcodeeditor.com/images/smiley.png" alt="smiley" /></p>
                
                </body>
            </html>
        """
    )
# ============= Creating auth path operations ==============
@router.post("/admin", response_description="Add new user", response_model=UserModel)
async def create_user(user: UserModel, current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == "admin":
        if re.match("dev|simple mortal", user.role):
            datetime_now = datetime.now(pytz.utc)
            user.created_at = datetime_now.strftime("%Y-%m-%d %I:%M:%S %p %Z")
            user.password = get_password_hash(user.password)
            user = jsonable_encoder(user)
            new_user = await db["users"].insert_one(user)
            await db["users"].update_one({"_id": new_user.inserted_id}, {
                                        "$rename": {"password": "hashed_pass"}})

            created_user = await db["users"].find_one({"_id": new_user.inserted_id})
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

        raise HTTPException(status_code=406, detail="Not Acceptable")
    else:
        raise HTTPException(status_code=401, detail=f"Unauthorized")



@router.get("/admin/list", response_description="List all users", response_model=List[ShowUserModel])
async def list_users(current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == "admin":
        users = await db["users"].find().to_list(None)
        for user in users:
            user["is_active"] = "false"
            try:
                last_login = datetime.strptime(user["last_login"], "%Y-%m-%d %I:%M:%S %p %Z")
                my_delta = datetime.now() - last_login
                if my_delta <= timedelta(days=30):
                    user["is_active"] = "true"
            except ValueError:
                pass
        return users
    else:
        raise HTTPException(status_code=401, detail=f"Unauthorized")



@router.put("/admin/{user_id}", response_description="Update a user", response_model=UpdateUserModel)
async def update_user(user_id: str, user: UpdateUserModel, current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == "admin":
        user = {k: v for k, v in user.dict().items() if v is not None}


        if len(user) >= 1:
            update_result = await db["users"].update_one({"_id": user_id}, {"$set": user})

            if update_result.modified_count == 1:
                if (
                    updated_user := await db["users"].find_one({"_id": user_id})
                ) is not None:
                    return updated_user

        if (existing_user := await db["users"].find_one({"_id": user_id})) is not None:
            return existing_user

        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        raise HTTPException(status_code=401, detail=f"Unauthorized")



@router.delete("/admin/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str, current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == "admin":
        delete_result = await db["users"].delete_one({"_id": user_id})

        if delete_result.deleted_count == 1:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        raise HTTPException(status_code=401, detail=f"Unauthorized")




@router.get("/whoamI", response_description="Current User", response_model=ShowUserModel)
async def current_user(current_user: ShowUserModel = Depends(get_current_user)):
    return current_user




@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorect ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if re.match("admin|dev", user["role"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["_id"]}, expires_delta=access_token_expires
        )
        await db["users"].update_one({"_id": form_data.username}, {"$set": {
            "last_login": datetime.now(pytz.utc).strftime("%Y-%m-%d %I:%M:%S %p %Z"),
            "is_active": "true"
        }})

        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail=f"Unauthorized")



@router.post("/super-token")
async def login_for_super_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorect ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if re.match("admin|dev", user["role"]):
        super_token = create_access_super_token(
            data={"sub": user["_id"]}
        )

        return {"super_token": super_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail=f"Unauthorized")


        
@router.post("/url-parce", response_description="", status_code=200)
async def url_parce(query: str):
    return quote_plus(query)
   
   
