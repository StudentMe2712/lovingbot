"""add media_type and file_id to quiz_questions

Revision ID: 5a6ddca80ef3
Revises: add_score_to_user
Create Date: 2025-06-26 12:33:58.350950

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5a6ddca80ef3'
down_revision = 'add_score_to_user'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('quiz_questions', sa.Column('media_type', sa.String(length=16), nullable=True, server_default='text'))
    op.add_column('quiz_questions', sa.Column('file_id', sa.String(length=128), nullable=True))
    op.alter_column('users', 'score',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))

def downgrade():
    op.alter_column('users', 'score',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.drop_column('quiz_questions', 'file_id')
    op.drop_column('quiz_questions', 'media_type')
