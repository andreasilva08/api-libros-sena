from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, Response, status
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import bloquear_email_registro, get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    Conflicto,
    CuentaBloqueada,
    ErrorAplicacion,
    NoAutenticado,
    Prohibido,
)
from app.core.limiter import limiter
from app.core.security import crear_token, hash_password, verify_password
from app.models.refresh_token import RefreshToken
from app.models.socio import Socio
from app.models.solicitud_registro import SolicitudRegistro
from app.models.usuario import Usuario
from app.schemas.auth import CambioPassword, RefreshSolicitud, TokenRespuesta
from app.schemas.solicitud import SolicitudCreate, SolicitudOut
from app.schemas.usuario import UsuarioRespuesta


router = APIRouter(prefix="/auth", tags=["Autenticación"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def _decodificar_token(token: str, tipo_esperado: str) -> dict[str, Any]:
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "rol", "type", "iat", "exp", "jti"]},
        )
    except jwt.InvalidTokenError as exc:
        raise NoAutenticado("Token inválido o expirado") from exc

    subject = claims.get("sub")
    if (
        claims.get("type") != tipo_esperado
        or not isinstance(subject, str)
        or not subject.isdecimal()
        or claims.get("rol") not in {"admin", "bibliotecario", "socio"}
        or not isinstance(claims.get("jti"), str)
    ):
        raise NoAutenticado("Token inválido o expirado")
    return claims


def _crear_par_de_tokens(db: Session, usuario: Usuario) -> TokenRespuesta:
    settings = get_settings()
    access_token = crear_token(
        usuario,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = crear_token(
        usuario,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )
    claims = _decodificar_token(refresh_token, "refresh")
    expira_en = datetime.fromtimestamp(claims["exp"], timezone.utc)
    db.add(
        RefreshToken(
            jti=claims["jti"],
            usuario_id=usuario.id,
            expira_en=expira_en,
        )
    )
    return TokenRespuesta(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/registro", status_code=status.HTTP_410_GONE, include_in_schema=False)
def registro_inmediato_desactivado() -> None:
    raise ErrorAplicacion(
        status.HTTP_410_GONE,
        "El registro inmediato fue desactivado; envía una solicitud de cuenta.",
    )


@router.post(
    "/solicitudes",
    response_model=SolicitudOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def crear_solicitud_registro(
    request: Request,
    datos: SolicitudCreate,
    db: DbSession,
) -> SolicitudOut:
    _ = request
    email = str(datos.email).strip().lower()
    bloquear_email_registro(db, email)
    usuario_existente = db.scalar(
        select(Usuario.id).where(func.lower(Usuario.email) == email)
    )
    socio_existente = db.scalar(
        select(Socio.id).where(func.lower(Socio.email) == email)
    )
    solicitud_pendiente = db.scalar(
        select(SolicitudRegistro.id).where(
            SolicitudRegistro.email == email,
            SolicitudRegistro.estado == "pendiente",
        )
    )
    if (
        usuario_existente is not None
        or socio_existente is not None
        or solicitud_pendiente is not None
    ):
        raise Conflicto("El correo electrónico ya está registrado o tiene una solicitud pendiente")

    solicitud = SolicitudRegistro(
        nombre=datos.nombre,
        email=email,
        telefono=datos.telefono,
        hashed_password=hash_password(datos.password),
        estado="pendiente",
    )
    try:
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto(
            "El correo electrónico ya está registrado o tiene una solicitud pendiente"
        ) from exc
    return SolicitudOut.model_validate(solicitud)


@router.post("/login", response_model=TokenRespuesta)
@limiter.limit("10/minute")
def iniciar_sesion(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenRespuesta:
    _ = request
    email = form_data.username.strip().lower()
    usuario = db.scalar(
        select(Usuario).where(Usuario.email == email).with_for_update()
    )
    if usuario is None:
        raise NoAutenticado("Correo o contraseña incorrectos")
    if not usuario.is_active:
        raise Prohibido("La cuenta está inactiva")

    ahora = datetime.now(timezone.utc)
    if usuario.locked_until is not None:
        if usuario.locked_until > ahora:
            raise CuentaBloqueada()
        usuario.locked_until = None
        usuario.failed_login_attempts = 0

    if not verify_password(form_data.password, usuario.hashed_password):
        usuario.failed_login_attempts += 1
        bloqueada = (
            usuario.failed_login_attempts
            >= get_settings().login_max_failed_attempts
        )
        if bloqueada:
            usuario.locked_until = ahora + timedelta(
                minutes=get_settings().login_lock_minutes
            )
        db.commit()
        if bloqueada:
            raise CuentaBloqueada()
        raise NoAutenticado("Correo o contraseña incorrectos")

    usuario.failed_login_attempts = 0
    usuario.locked_until = None
    tokens = _crear_par_de_tokens(db, usuario)
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenRespuesta)
def refrescar_tokens(
    datos: RefreshSolicitud,
    db: DbSession,
) -> TokenRespuesta:
    claims = _decodificar_token(datos.refresh_token, "refresh")
    usuario_id = int(claims["sub"])
    refresh = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.jti == claims["jti"])
        .with_for_update()
    )
    if (
        refresh is None
        or refresh.revocado
        or refresh.usuario_id != usuario_id
        or refresh.expira_en <= datetime.now(timezone.utc)
    ):
        raise NoAutenticado("Refresh token inválido o revocado")

    usuario = db.scalar(
        select(Usuario).where(Usuario.id == usuario_id).with_for_update()
    )
    if usuario is None:
        raise NoAutenticado()
    if not usuario.is_active:
        raise Prohibido("La cuenta está inactiva")
    if usuario.rol != claims["rol"]:
        raise NoAutenticado("Refresh token inválido o revocado")

    refresh.revocado = True
    tokens = _crear_par_de_tokens(db, usuario)
    db.commit()
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(datos: RefreshSolicitud, db: DbSession) -> Response:
    claims = _decodificar_token(datos.refresh_token, "refresh")
    refresh = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.jti == claims["jti"])
        .with_for_update()
    )
    if refresh is None or refresh.usuario_id != int(claims["sub"]):
        raise NoAutenticado("Refresh token inválido")
    if not refresh.revocado:
        refresh.revocado = True
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UsuarioRespuesta)
def usuario_actual(usuario: CurrentUser) -> UsuarioRespuesta:
    return UsuarioRespuesta.model_validate(usuario)


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cambiar_password(
    datos: CambioPassword,
    usuario: CurrentUser,
    db: DbSession,
) -> Response:
    if not verify_password(datos.password_actual, usuario.hashed_password):
        raise NoAutenticado("La contraseña actual es incorrecta")

    usuario.hashed_password = hash_password(datos.password_nueva)
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.usuario_id == usuario.id,
            RefreshToken.revocado.is_(False),
        )
        .values(revocado=True)
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
