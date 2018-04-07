"""Adding `is_active` column to `users`

Revision ID: f9d9b163eaaa
Revises:
Create Date: 2018-03-29 10:31:55.541000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9d9b163eaaa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    '''Add `is_active` to user's table'''
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()))


def downgrade():
    '''Remove `is_active` from `users`'''
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column('is_active')
