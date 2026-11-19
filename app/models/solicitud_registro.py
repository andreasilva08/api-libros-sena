from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)

from app.core.database import Base


class SolicitudRegistro(Base):
    __tablename__ = "solicitudes_registro"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'aprobada', 'rechazada')",
            name="estado_valido",
        ),
        Index(
            "uq_solicitudes_registro_email_pendiente",
            text("lower(email)"),
            unique=True,
            postgresql_where=text("estado = 'pendiente'"),
            sqlite_where=text("estado = 'pendiente'"),
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    estado = Column(
        String(20),
        nullable=False,
        default="pendiente",
        server_default="pendiente",
    )
    motivo_rechazo = Column(String(500), nullable=True)
    creado_en = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revisado_en = Column(DateTime(timezone=True), nullable=True)
    revisado_por_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
