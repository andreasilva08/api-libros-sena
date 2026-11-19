from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import Conflicto, NoEncontrado, Prohibido
from app.models.libro import Libro
from app.models.prestamo import Prestamo
from app.models.resena import Resena
from app.models.usuario import Usuario
from app.schemas.resena import ResenaResponse, ResenasLibroResponse, ResenaIn


def _resena_response(resena: Resena, usuario_id: int) -> ResenaResponse:
    return ResenaResponse(
        id=resena.id,
        libro_id=resena.libro_id,
        autor_nombre=resena.usuario.nombre,
        calificacion=resena.calificacion,
        comentario=resena.comentario,
        creado_en=resena.creado_en,
        actualizado_en=resena.actualizado_en,
        es_mia=resena.usuario_id == usuario_id,
    )


def _puede_opinar(db: Session, libro_id: int, usuario: Usuario) -> bool:
    if usuario.rol != "socio" or usuario.socio_id is None:
        return False
    return (
        db.query(Prestamo.id)
        .filter(
            Prestamo.socio_id == usuario.socio_id,
            Prestamo.libro_id == libro_id,
            Prestamo.fecha_devolucion.is_not(None),
        )
        .first()
        is not None
    )


def _validar_permiso_opinar(db: Session, libro_id: int, usuario: Usuario) -> None:
    if not _puede_opinar(db, libro_id, usuario):
        raise Prohibido(
            "Solo puedes calificar y opinar sobre libros que ya hayas devuelto"
        )


def get_resenas(
    db: Session,
    libro_id: int,
    usuario: Usuario,
) -> ResenasLibroResponse:
    if db.get(Libro, libro_id) is None:
        raise NoEncontrado("Libro no encontrado")

    estadisticas = (
        db.query(func.avg(Resena.calificacion), func.count(Resena.id))
        .filter(Resena.libro_id == libro_id)
        .one()
    )
    resenas = (
        db.query(Resena)
        .options(joinedload(Resena.usuario))
        .filter(Resena.libro_id == libro_id)
        .order_by(Resena.creado_en.desc(), Resena.id.desc())
        .all()
    )
    items = [_resena_response(resena, usuario.id) for resena in resenas]
    return ResenasLibroResponse(
        items=items,
        promedio=round(float(estadisticas[0] or 0), 1),
        total=int(estadisticas[1] or 0),
        mi_resena=next((item for item in items if item.es_mia), None),
        puede_opinar=_puede_opinar(db, libro_id, usuario),
    )


def create_resena(
    db: Session,
    libro_id: int,
    usuario: Usuario,
    datos: ResenaIn,
) -> ResenasLibroResponse:
    if db.get(Libro, libro_id) is None:
        raise NoEncontrado("Libro no encontrado")
    _validar_permiso_opinar(db, libro_id, usuario)

    existente = db.query(Resena.id).filter(
        Resena.libro_id == libro_id,
        Resena.usuario_id == usuario.id,
    ).first()
    if existente is not None:
        raise Conflicto("Ya tienes una opinión para este libro; actualízala")

    return _guardar_resena(db, libro_id, usuario, datos)


def upsert_resena(
    db: Session,
    libro_id: int,
    usuario: Usuario,
    datos: ResenaIn,
) -> ResenasLibroResponse:
    if db.get(Libro, libro_id) is None:
        raise NoEncontrado("Libro no encontrado")
    _validar_permiso_opinar(db, libro_id, usuario)

    resena = (
        db.query(Resena)
        .filter(
            Resena.libro_id == libro_id,
            Resena.usuario_id == usuario.id,
        )
        .first()
    )
    if resena is None:
        resena = Resena(
            libro_id=libro_id,
            usuario_id=usuario.id,
            calificacion=datos.calificacion,
            comentario=datos.comentario,
        )
        db.add(resena)
    else:
        resena.calificacion = datos.calificacion
        resena.comentario = datos.comentario

    return _guardar_resena(db, libro_id, usuario, datos, resena)


def _guardar_resena(
    db: Session,
    libro_id: int,
    usuario: Usuario,
    datos: ResenaIn,
    resena: Resena | None = None,
) -> ResenasLibroResponse:
    if resena is None:
        resena = Resena(
            libro_id=libro_id,
            usuario_id=usuario.id,
            calificacion=datos.calificacion,
            comentario=datos.comentario,
        )
        db.add(resena)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto("Ya existe una opinión para este libro") from exc

    return get_resenas(db, libro_id, usuario)


def delete_resena(
    db: Session,
    libro_id: int,
    resena_id: int,
    usuario: Usuario,
) -> ResenasLibroResponse:
    resena = db.query(Resena).filter(
        Resena.id == resena_id,
        Resena.libro_id == libro_id,
    ).first()
    if resena is None:
        raise NoEncontrado("Reseña no encontrada")
    if resena.usuario_id != usuario.id and usuario.rol != "admin":
        raise Prohibido("Solo puedes eliminar tu propia reseña")

    db.delete(resena)
    db.commit()
    return get_resenas(db, libro_id, usuario)
