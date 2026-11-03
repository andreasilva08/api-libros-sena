from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
    true,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RolUsuario(StrEnum):
    admin = "admin"
    bibliotecario = "bibliotecario"
    socio = "socio"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(
        Boolean, default=True, nullable=False, server_default=true()
    )
    failed_login_attempts = Column(
        Integer, default=0, nullable=False, server_default="0"
    )
    locked_until = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    rol = Column(
        Enum(RolUsuario, name="rolusuario"),
        default=RolUsuario.socio,
        nullable=False,
        server_default="socio",
    )
    socio_id = Column(
        Integer,
        ForeignKey("socios.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )

    socio = relationship("Socio", back_populates="usuario", uselist=False)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    prestamos_registrados = relationship(
        "Prestamo", back_populates="registrado_por"
    )

    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"

    @property
    def activo(self) -> bool:
        return self.is_active