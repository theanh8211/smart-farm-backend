"""add relay control fields

Revision ID: 3994063519dc
Revises: c1b0120c0977
Create Date: 2025-12-18 14:39:24.095765

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = '3994063519dc'
down_revision = 'c1b0120c0977'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Step 1: Add columns as nullable
    op.add_column('agent', sa.Column('pump_relay', sa.Boolean(), nullable=True))
    op.add_column('agent', sa.Column('light_relay', sa.Boolean(), nullable=True))
    op.add_column('agent', sa.Column('fan_relay', sa.Boolean(), nullable=True))

    # Step 2: Populate default values (false) for existing rows
    op.execute("UPDATE agent SET pump_relay = false WHERE pump_relay IS NULL")
    op.execute("UPDATE agent SET light_relay = false WHERE light_relay IS NULL")
    op.execute("UPDATE agent SET fan_relay = false WHERE fan_relay IS NULL")

    # Step 3: Alter columns to non-nullable
    op.alter_column('agent', 'pump_relay', nullable=False)
    op.alter_column('agent', 'light_relay', nullable=False)
    op.alter_column('agent', 'fan_relay', nullable=False)

def downgrade() -> None:
    op.drop_column('agent', 'fan_relay')
    op.drop_column('agent', 'light_relay')
    op.drop_column('agent', 'pump_relay')
