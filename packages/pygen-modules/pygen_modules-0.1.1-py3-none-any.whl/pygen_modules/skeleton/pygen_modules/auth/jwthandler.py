from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

load_dotenv()  # Load environment variables from .env file

security = HTTPBearer()
SECRET_KEY = os.getenv("APP_JWT_SECRET")
ALGORITHM = os.getenv("APP_JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("APP_JWT_EXPIRY_MINUTES"))
bearer_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # valid token

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Token expired. Please login again."
        )

    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token signature.")

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or malformed token.")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("❌ Invalid token")
        return None


def encode_token(self, user_id):
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
        "sub": user_id,
    }
    return jwt.encode(payload, self.secret, algorithm="HS256")


# def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
#     return self.decode_token(auth.credentials)
