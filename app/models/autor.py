from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    nacionalidad = Column(String(60), nullable=True)
    anio_naci = Column(Integer, nullable=True)

    libros = relationship("Libro", back_populates="autor")