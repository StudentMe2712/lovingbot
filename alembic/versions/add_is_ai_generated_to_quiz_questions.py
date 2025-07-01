"""add is_ai_generated to quiz_questions

Revision ID: add_ai_flag_to_quiz_q
Revises: change_tg_id_to_bigint
Create Date: 2025-06-30 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_ai_flag_to_quiz_q'
down_revision = 'change_tg_id_to_bigint'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('quiz_questions', sa.Column('is_ai_generated', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    op.drop_column('quiz_questions', 'is_ai_generated') 