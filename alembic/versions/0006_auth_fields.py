"""Agregar perfil y estado de bloqueo de usuarios."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_auth_fields"
down_revision: Union[str, None] = "0005_auditoria_prestamos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "nombre",
            sa.String(length=100),
            server_default="",
            nullable=False,
        ),
    )
    op.alter_column("usuarios", "nombre", server_default=None)
    op.add_column(
        "usuarios",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.alter_column("usuarios", "failed_login_attempts", server_default=None)
    op.add_column(
        "usuarios",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "creado_en")
    op.drop_column("usuarios", "locked_until")
    op.drop_column("usuarios", "failed_login_attempts")
    op.drop_column("usuarios", "nombre")
