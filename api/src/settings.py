from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

import os
import motor.motor_asyncio

# ================= Creating necessary variables ========================
#------------------ Token, authentication variables ---------------------
SECRET_KEY = "08uihdsjHls5Jdg8d57f783197985ceeca6768d10a314f54cda4be83de584ab5befe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#----------------- Database variables (MongoDB) --------------------------
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["DB_URL"])
db = client.rankworksDB


