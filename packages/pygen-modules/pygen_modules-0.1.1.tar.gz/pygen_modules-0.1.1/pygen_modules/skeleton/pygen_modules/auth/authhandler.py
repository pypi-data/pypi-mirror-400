from fastapi.security import HTTPBearer
import bcrypt
from utils.app_utils import AppUtils


class AuthHandler:
    security = HTTPBearer()
    secret = AppUtils.getSettings().AUTH_SECRET

    def getPasswordHash(self, password: str) -> str:
        """Hash password using bcrypt with 72-byte limit handling"""
        try:
            # Encode and truncate to 72 bytes
            password_bytes = password.encode('utf-8')[:72]
            
            # Generate hash
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error hashing password: {str(e)}")

    def verifyPassword(self, pwd: str, hashedPwd: str) -> bool:
        """Verify password against hash"""
        try:
            pwd_bytes = pwd.encode('utf-8')[:72]
            hash_bytes = hashedPwd.encode('utf-8')
            
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False