from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import NoAutenticado, Prohibido
from app.models.usuario import RolUsuario, Usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "rol", "type", "iat", "exp", "jti"]},
        )
    except jwt.InvalidTokenError as exc:
        raise NoAutenticado() from exc

    subject = claims.get("sub")
    if (
        claims.get("type") != "access"
        or not isinstance(subject, str)
        or not subject.isdecimal()
        or claims.get("rol") not in {"admin", "bibliotecario", "socio"}
        or not isinstance(claims.get("jti"), str)
    ):
        raise NoAutenticado()

    usuario = db.scalar(
        select(Usuario).where(Usuario.id == int(subject))
    )
    if usuario is None:
        raise NoAutenticado()
    if not usuario.is_active:
        raise Prohibido("La cuenta está inactiva")
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def requiere_rol(*roles: RolUsuario) -> Callable[..., Usuario]:
    if not roles:
        raise ValueError("Debe especificarse al menos un rol")

    def verificar_rol(usuario: CurrentUser) -> Usuario:
        if usuario.rol not in roles:
            raise Prohibido()
        return usuario

    return verificar_rol


Admin = Annotated[Usuario, Depends(requiere_rol(RolUsuario.admin))]
Staff = Annotated[
    Usuario,
    Depends(requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)),
]
SocioActual = Annotated[Usuario, Depends(requiere_rol(RolUsuario.socio))]


def paginacion(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Límite de registros por página")
):
    return {"skip": skip, "limit": limit}
