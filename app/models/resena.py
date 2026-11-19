from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resena(Base):
    __tablename__ = "resenas"
    __table_args__ = (
        CheckConstraint(
            "calificacion BETWEEN 1 AND 5",
            name="calificacion_valida",
        ),
        UniqueConstraint(
            "libro_id",
            "usuario_id",
            name="uq_resenas_libro_usuario",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(
        Integer, ForeignKey("libros.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    calificacion = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    creado_en = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    libro = relationship("Libro", back_populates="resenas")
    usuario = relationship("Usuario", back_populates="resenas")
