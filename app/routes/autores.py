from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import Staff, get_db, paginacion
from app.schemas.paginacion import Pagina
from app.schemas.autor import AutorCreate, AutorUpdate, AutorResponse
from app.schemas.libro import LibroResponse
from app.controllers import autor as autor_controller
from app.controllers import libro as libro_controller

router = APIRouter(prefix="/autores", tags=["Autores"])

@router.get("/", response_model=Pagina[AutorResponse])
def listar_autores(
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion),
    nacionalidad: Optional[str] = None,
):
    items, total = autor_controller.get_autores(
        db, pag["skip"], pag["limit"], nacionalidad
    )
    return Pagina(items=items, total=total, **pag)

@router.get("/{id}", response_model=AutorResponse)
def obtener_autor(id: int, db: Session = Depends(get_db)):
    return autor_controller.get_autor_by_id(db, id)

@router.post("/", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
def crear_autor(autor: AutorCreate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return autor_controller.create_autor(db, autor)

@router.patch("/{id}", response_model=AutorResponse)
def actualizar_autor(id: int, autor: AutorUpdate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return autor_controller.update_autor(db, id, autor)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(id: int, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return autor_controller.delete_autor(db, id)

@router.get("/{id}/libros", response_model=Pagina[LibroResponse])
def listar_libros_de_autor(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion)
):
    items, total = libro_controller.get_libros_by_autor(
        db, id, pag["skip"], pag["limit"]
    )
    return Pagina(items=items, total=total, **pag)