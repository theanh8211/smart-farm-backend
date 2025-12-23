"""add stream_url and agent_id to camera

Revision ID: b7a1c3d9e4f2
Revises: efacf88c0286
Create Date: 2025-12-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7a1c3d9e4f2'
down_revision = 'efacf88c0286'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nullable columns first
    op.add_column('camera', sa.Column('stream_url', sa.String(), nullable=True))
    op.add_column('camera', sa.Column('agent_id', sa.Integer(), nullable=True))

    # Optionally add FK to agent.id if agent table exists and uses integer primary key
    try:
        op.create_foreign_key('fk_camera_agent', 'camera', 'agent', ['agent_id'], ['id'])
    except Exception:
        # If FK creation fails (e.g., naming or engine), skip to avoid blocking migration
        pass


def downgrade() -> None:
    try:
        op.drop_constraint('fk_camera_agent', 'camera', type_='foreignkey')
    except Exception:
        pass
    op.drop_column('camera', 'agent_id')
    op.drop_column('camera', 'stream_url')
