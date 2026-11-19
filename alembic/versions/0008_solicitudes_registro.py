"""Crear solicitudes de registro de socios pendientes de aprobación."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_solicitudes_registro"
down_revision: Union[str, None] = "0007_portadas_libros"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "solicitudes_registro",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column(
            "estado",
            sa.String(length=20),
            server_default="pendiente",
            nullable=False,
        ),
        sa.Column("motivo_rechazo", sa.String(length=500), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("revisado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revisado_por_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'aprobada', 'rechazada')",
            name=op.f("ck_solicitudes_registro_estado_valido"),
        ),
        sa.ForeignKeyConstraint(
            ["revisado_por_id"],
            ["usuarios.id"],
            name=op.f("fk_solicitudes_registro_revisado_por_id_usuarios"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_solicitudes_registro")),
    )
    op.create_index(
        op.f("ix_solicitudes_registro_id"),
        "solicitudes_registro",
        ["id"],
        unique=False,
    )
    op.create_index(
        "uq_solicitudes_registro_email_pendiente",
        "solicitudes_registro",
        [sa.text("lower(email)")],
        unique=True,
        postgresql_where=sa.text("estado = 'pendiente'"),
        sqlite_where=sa.text("estado = 'pendiente'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_solicitudes_registro_email_pendiente",
        table_name="solicitudes_registro",
    )
    op.drop_index(
        op.f("ix_solicitudes_registro_id"),
        table_name="solicitudes_registro",
    )
    op.drop_table("solicitudes_registro")
