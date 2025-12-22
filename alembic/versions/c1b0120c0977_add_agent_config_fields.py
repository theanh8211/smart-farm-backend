"""add agent config fields

Revision ID: c1b0120c0977
Revises: a2957a768918
Create Date: 2025-12-18 13:56:23.101751

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = 'c1b0120c0977'
down_revision = 'a2957a768918'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Step 1: Add columns as nullable
    op.add_column('agent', sa.Column('sensor_interval', sa.Integer(), nullable=True))
    op.add_column('agent', sa.Column('camera_interval', sa.Integer(), nullable=True))
    op.add_column('agent', sa.Column('humidity_threshold', sa.Integer(), nullable=True))
    op.add_column('agent', sa.Column('temperature_threshold', sa.Integer(), nullable=True))
    op.add_column('agent', sa.Column('watering_schedule', sa.String(), nullable=True))
    op.add_column('agent', sa.Column('relay_override', sa.Boolean(), nullable=True))
    op.add_column('agent', sa.Column('deep_sleep_enabled', sa.Boolean(), nullable=True))

    # Step 2: Populate default values for existing rows
    op.execute("UPDATE agent SET sensor_interval = 4 WHERE sensor_interval IS NULL")
    op.execute("UPDATE agent SET camera_interval = 4 WHERE camera_interval IS NULL")
    op.execute("UPDATE agent SET humidity_threshold = 40 WHERE humidity_threshold IS NULL")
    op.execute("UPDATE agent SET temperature_threshold = 32 WHERE temperature_threshold IS NULL")
    op.execute("UPDATE agent SET relay_override = false WHERE relay_override IS NULL")
    op.execute("UPDATE agent SET deep_sleep_enabled = true WHERE deep_sleep_enabled IS NULL")

    # Step 3: Alter columns to non-nullable
    op.alter_column('agent', 'sensor_interval', nullable=False)
    op.alter_column('agent', 'camera_interval', nullable=False)
    op.alter_column('agent', 'humidity_threshold', nullable=False)
    op.alter_column('agent', 'temperature_threshold', nullable=False)
    op.alter_column('agent', 'relay_override', nullable=False)
    op.alter_column('agent', 'deep_sleep_enabled', nullable=False)

def downgrade() -> None:
    op.drop_column('agent', 'deep_sleep_enabled')
    op.drop_column('agent', 'relay_override')
    op.drop_column('agent', 'watering_schedule')
    op.drop_column('agent', 'temperature_threshold')
    op.drop_column('agent', 'humidity_threshold')
    op.drop_column('agent', 'camera_interval')
    op.drop_column('agent', 'sensor_interval')
