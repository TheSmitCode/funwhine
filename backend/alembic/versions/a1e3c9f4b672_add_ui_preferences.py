"""Add UI preference fields to users table (SQLite safe)

Revision ID: a1e3c9f4b672
Revises: 5335c2bdc93e
Create Date: 2025-12-01 12:00:00
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "a1e3c9f4b672"
down_revision = "5335c2bdc93e"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite-safe: add columns with defaults, do NOT attempt to drop defaults
    op.add_column(
        "users",
        sa.Column("ui_theme", sa.String(length=64), nullable=False, server_default="theme-light"),
    )
    op.add_column(
        "users",
        sa.Column("ui_sidebar", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "users",
        sa.Column("ui_navbar", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "users",
        sa.Column("ui_font_scale", sa.String(length=16), nullable=False, server_default="normal"),
    )
    op.add_column(
        "users",
        sa.Column("ui_simple_mode", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column(
        "users",
        sa.Column("ui_features", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # NOTE:
    # SQLite does not allow "DROP DEFAULT", so we leave the defaults in-place.
    # This does NOT affect application behavior and is completely safe.


def downgrade():
    op.drop_column("users", "ui_features")
    op.drop_column("users", "ui_simple_mode")
    op.drop_column("users", "ui_font_scale")
    op.drop_column("users", "ui_navbar")
    op.drop_column("users", "ui_sidebar")
    op.drop_column("users", "ui_theme")
