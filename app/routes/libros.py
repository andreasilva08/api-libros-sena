from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import Staff, get_db, paginacion
from app.schemas.paginacion import Pagina
from app.schemas.libro import LibroCreate, LibroUpdate, LibroResponse
from app.controllers import libro as libro_controller
from app.controllers.libro import OrdenLibro

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.get("/", response_model=Pagina[LibroResponse])
def listar_libros(
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion),
    buscar: Optional[str] = None,
    autor: Optional[str] = None,
    categoria_id: Optional[int] = None,
    desde: Optional[int] = None,
    hasta: Optional[int] = None,
    orden: Optional[OrdenLibro] = None,
):
    items, total = libro_controller.get_libros(
        db, pag["skip"], pag["limit"], buscar, autor, categoria_id, desde, hasta, orden
    )
    return Pagina(items=items, total=total, **pag)

@router.get("/{id}", response_model=LibroResponse)
def obtener_libro(id: int, db: Session = Depends(get_db)):
    return libro_controller.get_libro_by_id(db, id)

@router.post("/", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
def crear_libro(libro: LibroCreate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return libro_controller.create_libro(db, libro)

@router.patch("/{id}", response_model=LibroResponse)
def actualizar_libro(id: int, libro: LibroUpdate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return libro_controller.update_libro(db, id, libro)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(id: int, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return libro_controller.delete_libro(db, id)

@router.get("/autores/{autor_id}/libros", response_model=Pagina[LibroResponse])
def listar_libros_por_autor(
    autor_id: int,
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion)
):
    items, total = libro_controller.get_libros_by_autor(
        db, autor_id, pag["skip"], pag["limit"]
    )
    return Pagina(items=items, total=total, **pag)