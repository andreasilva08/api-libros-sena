"""Agregar metadatos de portadas Cloudinary a libros."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_portadas_libros"
down_revision: Union[str, None] = "0006_auth_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "libros",
        sa.Column("portada_url", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "libros",
        sa.Column("portada_public_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "libros",
        sa.Column(
            "portada_thumbnail_url",
            sa.String(length=512),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("libros", "portada_thumbnail_url")
    op.drop_column("libros", "portada_public_id")
    op.drop_column("libros", "portada_url")
