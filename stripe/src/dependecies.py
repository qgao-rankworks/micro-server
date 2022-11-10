from re import S
from fastapi import Depends, HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwt
from .settings import pwd_context, db, oauth2_scheme, SECRET_KEY, ALGORITHM



def get_password_hash(password):
    return pwd_context.hash(password)



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



async def get_user(id: str):
    if (user := await db["users"].find_one({"_id": id})) is not None:
        return user



async def authenticate_user(id: str, password: str):
    user = await get_user(id)
    if not user:
        return False
    if not verify_password(password, user["hashed_pass"]):
        return False

    return user

    

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
        user = await get_user(username)
        if user is None:
            raise credentials_exception
        return user
    except ExpiredSignatureError:
        # Signature has expired
        raise token_expired_exception
    except JWTError:
        raise credentials_exception


