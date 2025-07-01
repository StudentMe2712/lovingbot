"""add memories table

Revision ID: add_memories_table
Revises: add_user_mood_table
Create Date: 2025-06-30 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_memories_table'
down_revision = 'add_user_mood_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'memories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.String(length=128), nullable=True),
        sa.Column('emotion', sa.String(length=16), nullable=True),
        sa.Column('media_type', sa.String(length=16), nullable=False, server_default='text'),
        sa.Column('file_id', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.String(length=32), nullable=False)
    )
    op.add_column('memories', sa.Column('tags', sa.String(length=128), nullable=True))
    op.add_column('memories', sa.Column('emotion', sa.String(length=16), nullable=True))
    op.create_table(
        'blocked_partners',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('blocked_id', sa.Integer(), nullable=False)
    )
    op.create_table(
        'wishlists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item', sa.String(length=256), nullable=False),
        sa.Column('done', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.String(length=32), nullable=False)
    )
    op.create_table(
        'answer_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('answer', sa.String(length=128), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('timestamp', sa.String(length=32), nullable=False)
    )

def downgrade():
    op.drop_table('memories')
    op.drop_column('memories', 'tags')
    op.drop_column('memories', 'emotion')
    op.drop_table('blocked_partners')
    op.drop_table('wishlists')
    op.drop_table('answer_history') 