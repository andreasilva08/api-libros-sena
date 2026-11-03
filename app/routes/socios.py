from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.controllers.libro import enriq_libro
from app.controllers import socio as socio_controller
from app.core.dependencies import (
    Admin,
    CurrentUser,
    SocioActual,
    Staff,
    get_db,
    paginacion,
)
from app.core.exceptions import NoEncontrado
from app.models.prestamo import Prestamo
from app.models.libro import Libro
from app.models.socio import Socio
from app.models.usuario import Usuario
from app.schemas.multas import SocioMultasResponse
from app.schemas.paginacion import Pagina
from app.schemas.prestamo import PrestamoResponse
from app.schemas.socio import (
    SocioActualizarPropio,
    SocioCreate,
    SocioResponse,
    SocioUpdate,
)


router = APIRouter(prefix="/socios", tags=["Socios"])
EstadoPrestamo = Literal["activo", "vencido", "devuelto"]
DbSession = Annotated[Session, Depends(get_db)]


def _obtener_socio_propietario(db: Session, usuario: Usuario) -> Socio:
    if usuario.socio_id is None:
        raise NoEncontrado("Perfil de socio no encontrado")
    socio = db.get(Socio, usuario.socio_id)
    if socio is None:
        raise NoEncontrado("Perfil de socio no encontrado")
    return socio


@router.get("/me", response_model=SocioResponse)
def mi_perfil(usuario: SocioActual, db: DbSession):
    return _obtener_socio_propietario(db, usuario)


@router.patch("/me", response_model=SocioResponse)
def actualizar_mi_perfil(
    datos: SocioActualizarPropio,
    usuario: SocioActual,
    db: DbSession,
):
    socio = _obtener_socio_propietario(db, usuario)
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    if "nombre" in cambios:
        usuario.nombre = cambios["nombre"]
    db.commit()
    db.refresh(socio)
    return socio


@router.get("/me/prestamos", response_model=Pagina[PrestamoResponse])
def mis_prestamos(
    usuario: SocioActual,
    db: DbSession,
    estado: EstadoPrestamo | None = None,
    pag: dict = Depends(paginacion),
):
    socio = _obtener_socio_propietario(db, usuario)
    prestamos, total = socio_controller.get_prestamos_by_socio(
        db, socio.id, estado, pag["skip"], pag["limit"]
    )
    return Pagina(
        items=prestamos,
        total=total,
        skip=pag["skip"],
        limit=pag["limit"],
    )


@router.get("/me/multas", response_model=SocioMultasResponse)
def mis_multas(
    usuario: SocioActual,
    db: DbSession,
    pag: dict = Depends(paginacion),
):
    socio = _obtener_socio_propietario(db, usuario)
    base_query = select(Prestamo).where(
        Prestamo.socio_id == socio.id,
        Prestamo.multa > 0,
        Prestamo.multa_pagada.is_(False),
    )
    total_adeudado = db.scalar(
        select(func.coalesce(func.sum(Prestamo.multa), 0.0)).where(
            Prestamo.socio_id == socio.id,
            Prestamo.multa > 0,
            Prestamo.multa_pagada.is_(False),
        )
    )
    items = list(
        db.scalars(
            base_query.options(
                selectinload(Prestamo.libro).selectinload(Libro.autor),
                selectinload(Prestamo.libro).selectinload(Libro.categorias),
                selectinload(Prestamo.socio),
            )
            .offset(pag["skip"])
            .limit(pag["limit"])
        ).all()
    )
    for prestamo in items:
        if prestamo.libro:
            enriq_libro(db, prestamo.libro)
    return SocioMultasResponse(
        items=items,
        total_adeudado=float(total_adeudado or 0),
        skip=pag["skip"],
        limit=pag["limit"],
    )


@router.get("/", response_model=Pagina[SocioResponse])
def listar_socios(
    _: Staff,
    db: DbSession,
    activo: bool | None = None,
    pag: dict = Depends(paginacion),
):
    query = db.query(Socio)
    if activo is not None:
        query = query.filter(Socio.activo == activo)
    total = query.count()
    items = query.offset(pag["skip"]).limit(pag["limit"]).all()
    return Pagina(items=items, total=total, **pag)


@router.get("/{id}", response_model=SocioResponse)
def obtener_socio(
    id: int,
    usuario: CurrentUser,
    db: DbSession,
):
    if usuario.rol == "socio" and usuario.socio_id != id:
        raise NoEncontrado("Socio no encontrado")
    return socio_controller.get_socio_by_id(db, id)


@router.post(
    "/",
    response_model=SocioResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_socio(
    socio: SocioCreate,
    _: Staff,
    db: DbSession,
):
    return socio_controller.create_socio(db, socio)


@router.patch("/{id}", response_model=SocioResponse)
def actualizar_socio(
    id: int,
    socio: SocioUpdate,
    _: Staff,
    db: DbSession,
):
    return socio_controller.update_socio(db, id, socio)


@router.delete("/{id}")
def eliminar_socio(
    id: int,
    _: Admin,
    db: DbSession,
):
    resultado = socio_controller.delete_socio(db, id)
    if resultado is None:
        return {"mensaje": "Socio eliminado exitosamente"}
    return resultado


@router.get("/{id}/prestamos", response_model=Pagina[PrestamoResponse])
def listar_prestamos_socio(
    id: int,
    usuario: CurrentUser,
    db: DbSession,
    estado: EstadoPrestamo | None = None,
    pag: dict = Depends(paginacion),
):
    if usuario.rol == "socio" and usuario.socio_id != id:
        raise NoEncontrado("Socio no encontrado")
    socio_controller.get_socio_by_id(db, id)
    prestamos, total = socio_controller.get_prestamos_by_socio(
        db, id, estado, pag["skip"], pag["limit"]
    )
    return Pagina(
        items=prestamos,
        total=total,
        skip=pag["skip"],
        limit=pag["limit"],
    )
