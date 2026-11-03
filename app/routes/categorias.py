from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import Staff, get_db, paginacion
from app.schemas.paginacion import Pagina
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.controllers import categoria as categoria_controller

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.get("/", response_model=Pagina[CategoriaResponse])
def listar_categorias(
    db: Annotated[Session, Depends(get_db)],
    pag: dict = Depends(paginacion),
):
    items, total = categoria_controller.get_categorias(
        db, pag["skip"], pag["limit"]
    )
    return Pagina(items=items, total=total, **pag)

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return categoria_controller.create_categoria(db, categoria)

@router.patch("/{id}", response_model=CategoriaResponse)
def actualizar_categoria(id: int, categoria: CategoriaUpdate, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return categoria_controller.update_categoria(db, id, categoria)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id: int, _: Staff, db: Annotated[Session, Depends(get_db)]):
    return categoria_controller.delete_categoria(db, id)