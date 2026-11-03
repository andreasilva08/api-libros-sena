from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, false
from sqlalchemy.orm import relationship

from app.core.database import Base


class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    socio_id = Column(Integer, ForeignKey("socios.id"), nullable=False)
    fecha_prestamo = Column(Date, nullable=False)
    fecha_limite = Column(Date, nullable=False)
    fecha_devolucion = Column(Date, nullable=True)
    multa = Column(Float, default=0.0)
    multa_pagada = Column(
        Boolean, default=False, nullable=False, server_default=false()
    )
    registrado_por_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    libro = relationship("Libro", back_populates="prestamos")
    socio = relationship("Socio", back_populates="prestamos")
    registrado_por = relationship(
        "Usuario", back_populates="prestamos_registrados"
    )