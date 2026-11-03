from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import Staff, get_db, paginacion
from app.schemas.paginacion import Pagina
from app.schemas.libro import LibroCreate, LibroUpdate, LibroResponse
from app.controllers import libro as libro_controller
from app.controllers import portada as portada_controller
from app.controllers.libro import OrdenLibro

router = APIRouter(prefix="/libros", tags=["Libros"])
MAX_PORTADA_BYTES = 5 * 1024 * 1024
PORTADA_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

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


@router.put("/{id}/portada", response_model=LibroResponse)
async def subir_o_actualizar_portada(
    id: int,
    _: Staff,
    db: Annotated[Session, Depends(get_db)],
    archivo: UploadFile = File(...),
):
    if archivo.content_type not in PORTADA_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="La portada debe ser JPEG, PNG o WebP",
        )

    contenido = await archivo.read(MAX_PORTADA_BYTES + 1)
    if len(contenido) > MAX_PORTADA_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La portada no puede superar 5 MB",
        )
    if not contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo de portada está vacío",
        )

    return portada_controller.actualizar_portada(
        db,
        id,
        contenido,
        archivo.filename or "portada",
    )

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