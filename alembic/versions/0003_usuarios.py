"""Crear usuarios, roles y la relación opcional con socios."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_usuarios"
down_revision: Union[str, None] = "0002_multa_pagada"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    rolusuario = postgresql.ENUM(
        "admin",
        "bibliotecario",
        "socio",
        name="rolusuario",
        create_type=False,
    )
    rolusuario.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "rol",
            rolusuario,
            server_default="socio",
            nullable=False,
        ),
        sa.Column("socio_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["socio_id"],
            ["socios.id"],
            name=op.f("fk_usuarios_socio_id_socios"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("socio_id", name=op.f("uq_usuarios_socio_id")),
    )
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)
    op.create_index(
        op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_table("usuarios")
    sa.Enum(name="rolusuario").drop(op.get_bind())
