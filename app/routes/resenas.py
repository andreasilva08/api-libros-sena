from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import resena as resena_controller
from app.core.dependencies import CurrentUser, SocioActual, get_db
from app.schemas.resena import ResenaIn, ResenasLibroResponse


router = APIRouter(prefix="/libros", tags=["Opiniones"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{libro_id}/opiniones", response_model=ResenasLibroResponse)
def listar_opiniones(
    libro_id: int,
    usuario: CurrentUser,
    db: DbSession,
):
    return resena_controller.get_resenas(db, libro_id, usuario)


@router.post(
    "/{libro_id}/opiniones",
    response_model=ResenasLibroResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_opinion(
    libro_id: int,
    datos: ResenaIn,
    usuario: SocioActual,
    db: DbSession,
):
    return resena_controller.create_resena(db, libro_id, usuario, datos)


@router.put(
    "/{libro_id}/opiniones",
    response_model=ResenasLibroResponse,
)
def actualizar_opinion(
    libro_id: int,
    datos: ResenaIn,
    usuario: SocioActual,
    db: DbSession,
):
    return resena_controller.upsert_resena(db, libro_id, usuario, datos)


@router.delete(
    "/{libro_id}/opiniones/{opinion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_opinion(
    libro_id: int,
    opinion_id: int,
    usuario: CurrentUser,
    db: DbSession,
):
    resena_controller.delete_resena(db, libro_id, opinion_id, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
