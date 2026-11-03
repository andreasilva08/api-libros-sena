from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import get_settings

settings = get_settings()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un token JWT de acceso con tiempo de expiración configurable."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """Verifica y decodifica un token JWT."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception