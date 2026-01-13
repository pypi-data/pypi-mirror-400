"""Add recorded_until + legacy metadata columns to datafile

Revision ID: a1b2c3d4e5f6
Revises: 839d46550586
Create Date: 2025-11-28 08:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "839d46550586"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add recorded_until, legacy_image_id and mime_type columns."""

    op.add_column("datafile", sa.Column("recorded_until", sa.DateTime(), nullable=True))
    op.add_column("datafile", sa.Column("legacy_image_id", sa.Integer(), nullable=True))
    op.add_column("datafile", sa.Column("mime_type", sa.String(), nullable=True))


def downgrade() -> None:
    """Remove recorded_until, legacy_image_id and mime_type columns."""

    op.drop_column("datafile", "mime_type")
    op.drop_column("datafile", "legacy_image_id")
    op.drop_column("datafile", "recorded_until")
