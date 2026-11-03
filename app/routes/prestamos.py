from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers import prestamo as prestamo_controller
from app.core.dependencies import CurrentUser, Staff, get_db, paginacion
from app.core.exceptions import NoEncontrado
from app.schemas.paginacion import Pagina
from app.schemas.prestamo import (
    DevolucionCreate,
    PrestamoCreate,
    PrestamoResponse,
)


router = APIRouter(prefix="/prestamos", tags=["Préstamos"])
EstadoPrestamo = Literal["activo", "vencido", "devuelto"]


@router.get("/", response_model=Pagina[PrestamoResponse])
def listar_prestamos(
    usuario: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    estado: EstadoPrestamo | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None,
    pag: dict = Depends(paginacion),
):
    socio_propietario = (
        usuario.socio_id
        if usuario.rol == "socio"
        else socio_id
    )
    if usuario.rol == "socio" and socio_propietario is None:
        raise NoEncontrado("Perfil de socio no encontrado")
    prestamos, total = prestamo_controller.get_prestamos(
        db,
        pag["skip"],
        pag["limit"],
        estado,
        socio_propietario,
        libro_id,
    )
    return Pagina(
        items=prestamos,
        total=total,
        skip=pag["skip"],
        limit=pag["limit"],
    )


@router.get("/{id}", response_model=PrestamoResponse)
def obtener_prestamo(id: int, usuario: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    socio_propietario = usuario.socio_id if usuario.rol == "socio" else None
    if usuario.rol == "socio" and socio_propietario is None:
        raise NoEncontrado("Préstamo no encontrado")
    return prestamo_controller.get_prestamo_by_id(
        db, id, socio_id=socio_propietario
    )


@router.post(
    "/",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_prestamo(
    prestamo: PrestamoCreate,
    usuario: Staff,
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.rol == "socio":
        if usuario.socio_id is None:
            raise NoEncontrado("Perfil de socio no encontrado")
        prestamo = prestamo.model_copy(
            update={"socio_id": usuario.socio_id}
        )
    return prestamo_controller.create_prestamo(
        db, prestamo, registrado_por_id=usuario.id
    )


@router.post("/{id}/devolucion", response_model=PrestamoResponse)
def devolver_prestamo(
    id: int,
    devolucion: DevolucionCreate,
    _: Staff,
    db: Annotated[Session, Depends(get_db)],
):
    return prestamo_controller.registrar_devolucion(db, id, devolucion)
