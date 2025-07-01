"""add user_mood table

Revision ID: add_user_mood_table
Revises: add_ai_flag_to_quiz_q
Create Date: 2025-06-30 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_mood_table'
down_revision = 'add_ai_flag_to_quiz_q'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user_mood',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mood', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.String(length=32), nullable=False)
    )
    with op.batch_alter_table('reminders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shared_with_partner', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    with op.batch_alter_table('reminders', schema=None) as batch_op:
        batch_op.drop_column('shared_with_partner')
    op.drop_table('user_mood') 