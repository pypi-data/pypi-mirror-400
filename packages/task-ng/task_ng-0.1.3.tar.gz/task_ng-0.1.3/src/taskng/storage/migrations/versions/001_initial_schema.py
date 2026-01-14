"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade to initial schema.

    Note: The initial schema is created by database.initialize()
    using schema.py. This migration establishes the baseline.
    """
    pass


def downgrade() -> None:
    """Downgrade from initial schema.

    Cannot downgrade from initial - would require dropping all tables.
    """
    pass
