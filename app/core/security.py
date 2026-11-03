from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.models.usuario import Usuario

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def crear_token(
    usuario: Usuario,
    tipo: str,
    duracion: timedelta,
) -> str:
    if tipo not in {"access", "refresh"}:
        raise ValueError("El tipo de token debe ser 'access' o 'refresh'")
    if duracion <= timedelta(0):
        raise ValueError("La duración del token debe ser positiva")
    if usuario.id is None:
        raise ValueError("El usuario debe estar persistido para crear un token")

    ahora = datetime.now(timezone.utc)
    claims = {
        "sub": str(usuario.id),
        "rol": usuario.rol,
        "type": tipo,
        "iat": ahora,
        "exp": ahora + duracion,
        "jti": str(uuid4()),
    }
    return jwt.encode(
        claims,
        get_settings().secret_key,
        algorithm="HS256",
    )