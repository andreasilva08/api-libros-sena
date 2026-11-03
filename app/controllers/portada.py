from io import BytesIO
from typing import Any

import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.utils import cloudinary_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ErrorAplicacion, NoEncontrado
from app.controllers.libro import get_libro_by_id
from app.models.libro import Libro


def actualizar_portada(
    db: Session,
    libro_id: int,
    contenido: bytes,
    nombre_archivo: str,
) -> Libro:
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")

    settings = get_settings()
    cloud_name = settings.cloud_name
    api_key = settings.cloud_api_key
    api_secret = settings.cloud_api_secret
    if not cloud_name or not api_key or not api_secret:
        raise ErrorAplicacion(
            status_code=503,
            detail="El servicio de almacenamiento de imágenes no está configurado",
        )

    archivo = BytesIO(contenido)
    archivo.name = nombre_archivo
    public_id = f"libros/{libro_id}/portada"
    try:
        resultado: dict[str, Any] = cloudinary.uploader.upload(
            archivo,
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            public_id=public_id,
            overwrite=True,
            invalidate=True,
            resource_type="image",
        )
    except CloudinaryError as exc:
        raise ErrorAplicacion(
            status_code=502,
            detail="Cloudinary no pudo guardar la portada",
        ) from exc

    secure_url = resultado.get("secure_url")
    uploaded_public_id = resultado.get("public_id")
    if not isinstance(secure_url, str) or not isinstance(uploaded_public_id, str):
        raise ErrorAplicacion(
            status_code=502,
            detail="Cloudinary devolvió una respuesta de imagen incompleta",
        )

    thumbnail_url, _ = cloudinary_url(
        uploaded_public_id,
        cloud_name=cloud_name,
        version=resultado.get("version"),
        width=200,
        height=300,
        crop="fill",
        quality="auto",
        fetch_format="auto",
        secure=True,
    )
    libro.portada_url = secure_url
    libro.portada_public_id = uploaded_public_id
    libro.portada_thumbnail_url = thumbnail_url
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return get_libro_by_id(db, libro_id)
