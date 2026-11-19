"""Agregar reseñas y calificaciones de libros."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_resenas_libros"
down_revision: Union[str, None] = "0008_solicitudes_registro"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resenas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("libro_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("calificacion", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "calificacion BETWEEN 1 AND 5",
            name=op.f("ck_resenas_calificacion_valida"),
        ),
        sa.ForeignKeyConstraint(
            ["libro_id"],
            ["libros.id"],
            name=op.f("fk_resenas_libro_id_libros"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name=op.f("fk_resenas_usuario_id_usuarios"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_resenas")),
        sa.UniqueConstraint(
            "libro_id",
            "usuario_id",
            name="uq_resenas_libro_usuario",
        ),
    )
    op.create_index(op.f("ix_resenas_id"), "resenas", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resenas_id"), table_name="resenas")
    op.drop_table("resenas")
