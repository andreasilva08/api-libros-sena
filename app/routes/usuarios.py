from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import bloquear_email_registro, get_db
from app.core.dependencies import Admin
from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.core.security import hash_password
from app.models.socio import Socio
from app.models.solicitud_registro import SolicitudRegistro
from app.models.usuario import RolUsuario, Usuario
from app.schemas.paginacion import Pagina
from app.schemas.usuario import (
    UsuarioActivoActualizar,
    UsuarioAdminCreate,
    UsuarioRespuesta,
    UsuarioRolActualizar,
)
from app.core.dependencies import paginacion


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=Pagina[UsuarioRespuesta])
def listar_usuarios(
    _: Admin,
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion),
):
    total = db.scalar(select(func.count(Usuario.id))) or 0
    usuarios = db.scalars(
        select(Usuario)
        .order_by(Usuario.id)
        .offset(pag["skip"])
        .limit(pag["limit"])
    ).all()
    return Pagina(
        items=list(usuarios),
        total=total,
        skip=pag["skip"],
        limit=pag["limit"],
    )


@router.post(
    "/",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_usuario(
    datos: UsuarioAdminCreate,
    _: Admin,
    db: Annotated[Session, Depends(get_db)],
):
    bloquear_email_registro(db, str(datos.email))
    if db.scalar(select(Usuario.id).where(Usuario.email == str(datos.email))):
        raise Conflicto("El correo electrónico ya está registrado")
    if db.scalar(
        select(SolicitudRegistro.id).where(
            func.lower(SolicitudRegistro.email) == str(datos.email).lower(),
            SolicitudRegistro.estado == "pendiente",
        )
    ):
        raise Conflicto("El correo electrónico tiene una solicitud pendiente")
    if datos.rol == RolUsuario.socio and datos.socio_id is None:
        raise ReglaNegocio("Los usuarios con rol socio requieren socio_id")
    if datos.socio_id is not None:
        socio = db.get(Socio, datos.socio_id)
        if socio is None:
            raise NoEncontrado("Socio no encontrado")
        if socio.email.lower() != str(datos.email).lower():
            raise ReglaNegocio(
                "El correo del usuario debe coincidir con el del socio vinculado"
            )
        socio_asignado = db.scalar(
            select(Usuario.id).where(Usuario.socio_id == datos.socio_id)
        )
        if socio_asignado is not None:
            raise Conflicto("El socio ya está vinculado a otro usuario")

    nuevo_usuario = Usuario(
        email=str(datos.email),
        nombre=datos.nombre,
        hashed_password=hash_password(datos.password),
        rol=datos.rol,
        socio_id=datos.socio_id,
        is_active=True,
    )
    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto("No se pudo crear el usuario con esos datos") from exc
    return nuevo_usuario


def _administradores_activos_bloqueados(db: Session) -> list[Usuario]:
    return list(
        db.scalars(
            select(Usuario)
            .where(
                Usuario.rol == RolUsuario.admin,
                Usuario.is_active.is_(True),
            )
            .order_by(Usuario.id)
            .with_for_update()
        ).all()
    )


def _obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.scalar(
        select(Usuario)
        .where(Usuario.id == usuario_id)
        .with_for_update()
    )
    if usuario is None:
        raise NoEncontrado("Usuario no encontrado")
    return usuario


@router.patch("/{id}/rol", response_model=UsuarioRespuesta)
def actualizar_rol_usuario(
    id: int,
    datos: UsuarioRolActualizar,
    usuario_actual: Admin,
    db: Annotated[Session, Depends(get_db)],
):
    administradores = _administradores_activos_bloqueados(db)
    usuario = _obtener_usuario(db, id)
    if (
        usuario.id == usuario_actual.id
        and usuario.is_active
        and usuario.rol == RolUsuario.admin
        and datos.rol != RolUsuario.admin
        and len(administradores) <= 1
    ):
        raise Conflicto(
            "No puedes quitarte el rol de último administrador activo"
        )
    if datos.rol == RolUsuario.socio and usuario.socio_id is None:
        raise ReglaNegocio(
            "Los usuarios con rol socio requieren un perfil de socio vinculado"
        )
    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{id}/activo", response_model=UsuarioRespuesta)
def actualizar_estado_usuario(
    id: int,
    datos: UsuarioActivoActualizar,
    usuario_actual: Admin,
    db: Annotated[Session, Depends(get_db)],
):
    administradores = _administradores_activos_bloqueados(db)
    usuario = _obtener_usuario(db, id)
    if (
        usuario.id == usuario_actual.id
        and usuario.is_active
        and usuario.rol == RolUsuario.admin
        and not datos.activo
        and len(administradores) <= 1
    ):
        raise Conflicto(
            "No puedes desactivarte como último administrador activo"
        )
    usuario.is_active = datos.activo
    db.commit()
    db.refresh(usuario)
    return usuario
