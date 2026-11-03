from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.categoria import libro_categoria

class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    isbn = Column(String(50), unique=True, index=True, nullable=False)
    anio_publicacion = Column(Integer, nullable=False)
    ejemplares = Column(Integer, default=1)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)

    autor = relationship("Autor", back_populates="libros")
    categorias = relationship(
        "Categoria",
        secondary=libro_categoria,
        back_populates="libros"
    )
    prestamos = relationship("Prestamo", back_populates="libro")