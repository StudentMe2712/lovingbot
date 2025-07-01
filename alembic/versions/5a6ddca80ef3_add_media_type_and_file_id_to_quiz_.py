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
    with op.batch_alter_table('quiz_questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('media_type', sa.String(length=16), nullable=True, server_default='text'))
        batch_op.add_column(sa.Column('file_id', sa.String(length=128), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('score',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('score',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))

    with op.batch_alter_table('quiz_questions', schema=None) as batch_op:
        batch_op.drop_column('file_id')
        batch_op.drop_column('media_type')
