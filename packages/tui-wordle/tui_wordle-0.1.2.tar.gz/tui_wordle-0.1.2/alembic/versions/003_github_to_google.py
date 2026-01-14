"""Change from GitHub to Google OAuth

Revision ID: 003
Revises: 002
Create Date: 2025-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_id column
    op.add_column("users", sa.Column("google_id", sa.String(255), nullable=True))
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)

    # Drop github_id column and index
    op.drop_index("ix_users_github_id", table_name="users")
    op.drop_column("users", "github_id")


def downgrade() -> None:
    # Add github_id column back
    op.add_column("users", sa.Column("github_id", sa.BigInteger(), nullable=True))
    op.create_index("ix_users_github_id", "users", ["github_id"], unique=True)

    # Drop google_id column
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "google_id")
