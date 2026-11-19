from datetime import date, datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import bloquear_email_registro, get_db
from app.core.dependencies import Staff, paginacion
from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.core.security import hash_password
from app.models.socio import Socio
from app.models.solicitud_registro import SolicitudRegistro
from app.models.usuario import RolUsuario, Usuario
from app.schemas.paginacion import Pagina
from app.schemas.solicitud import (
    SolicitudCreate,
    SolicitudOut,
    SolicitudRechazoIn,
)


router = APIRouter(tags=["Solicitudes de registro"])
DbSession = Annotated[Session, Depends(get_db)]
EstadoSolicitud = Literal["pendiente", "aprobada", "rechazada"]


@router.get("/solicitudes", response_model=Pagina[SolicitudOut])
def listar_solicitudes(
    _: Staff,
    db: DbSession,
    estado: EstadoSolicitud = "pendiente",
    pag: dict = Depends(paginacion),
) -> Pagina[SolicitudOut]:
    filtro = SolicitudRegistro.estado == estado
    total = db.scalar(
        select(func.count(SolicitudRegistro.id)).where(filtro)
    ) or 0
    items = list(
        db.scalars(
            select(SolicitudRegistro)
            .where(filtro)
            .order_by(SolicitudRegistro.creado_en.desc(), SolicitudRegistro.id.desc())
            .offset(pag["skip"])
            .limit(pag["limit"])
        ).all()
    )
    return Pagina(
        items=items,
        total=total,
        skip=pag["skip"],
        limit=pag["limit"],
    )


def _obtener_solicitud_pendiente(
    db: Session,
    solicitud_id: int,
) -> SolicitudRegistro:
    solicitud = db.scalar(
        select(SolicitudRegistro)
        .where(SolicitudRegistro.id == solicitud_id)
        .with_for_update()
    )
    if solicitud is None:
        raise NoEncontrado("Solicitud no encontrada")
    if solicitud.estado != "pendiente":
        raise Conflicto("La solicitud ya fue revisada")
    return solicitud


@router.post(
    "/solicitudes/{solicitud_id}/aprobar",
    response_model=SolicitudOut,
)
def aprobar_solicitud(
    solicitud_id: int,
    revisor: Staff,
    db: DbSession,
) -> SolicitudOut:
    solicitud = _obtener_solicitud_pendiente(db, solicitud_id)
    if not solicitud.hashed_password:
        raise ReglaNegocio("La solicitud no tiene una contraseña válida")

    bloquear_email_registro(db, solicitud.email)
    usuario_existente = db.scalar(
        select(Usuario.id).where(
            func.lower(Usuario.email) == solicitud.email.lower()
        )
    )
    socio_existente = db.scalar(
        select(Socio.id).where(
            func.lower(Socio.email) == solicitud.email.lower()
        )
    )
    if usuario_existente is not None or socio_existente is not None:
        raise Conflicto("El correo electrónico ya está registrado")

    socio = Socio(
        nombre=solicitud.nombre,
        email=solicitud.email,
        telefono=solicitud.telefono,
        activo=True,
        fecha_alta=date.today(),
    )
    try:
        db.add(socio)
        db.flush()
        db.add(
            Usuario(
                email=solicitud.email,
                nombre=solicitud.nombre,
                hashed_password=solicitud.hashed_password,
                rol=RolUsuario.socio,
                is_active=True,
                socio_id=socio.id,
            )
        )
        solicitud.estado = "aprobada"
        solicitud.revisado_por_id = revisor.id
        solicitud.revisado_en = datetime.now(timezone.utc)
        solicitud.hashed_password = None
        db.commit()
        db.refresh(solicitud)
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto(
            "No se pudo aprobar la solicitud porque el correo ya está registrado"
        ) from exc
    return SolicitudOut.model_validate(solicitud)


@router.post(
    "/solicitudes/{solicitud_id}/rechazar",
    response_model=SolicitudOut,
)
def rechazar_solicitud(
    solicitud_id: int,
    revisor: Staff,
    db: DbSession,
    datos: SolicitudRechazoIn | None = None,
) -> SolicitudOut:
    solicitud = _obtener_solicitud_pendiente(db, solicitud_id)
    solicitud.estado = "rechazada"
    solicitud.motivo_rechazo = datos.motivo_rechazo if datos else None
    solicitud.revisado_por_id = revisor.id
    solicitud.revisado_en = datetime.now(timezone.utc)
    solicitud.hashed_password = None
    db.commit()
    db.refresh(solicitud)
    return SolicitudOut.model_validate(solicitud)


