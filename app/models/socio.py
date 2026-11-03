from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

class Socio(Base):
    __tablename__ = "socios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)
    fecha_alta = Column(Date)

    # Relación con la tabla prestamos
    prestamos = relationship("Prestamo", back_populates="socio")
    usuario = relationship("Usuario", back_populates="socio", uselist=False)