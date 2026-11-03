"""Agregar el estado de pago de la multa."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_multa_pagada"
down_revision: Union[str, None] = "a580fae86188"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "prestamos",
        sa.Column(
            "multa_pagada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.execute("UPDATE prestamos SET multa_pagada = true WHERE multa = 0")


def downgrade() -> None:
    op.drop_column("prestamos", "multa_pagada")
