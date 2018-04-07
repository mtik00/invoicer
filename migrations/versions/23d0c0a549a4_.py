"""Remove `is_authenticated`

Revision ID: 23d0c0a549a4
Revises: 2e862ca9d159
Create Date: 2018-04-07 08:53:28.116000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23d0c0a549a4'
down_revision = '2e862ca9d159'
branch_labels = None
depends_on = None


def upgrade():
    '''Remove `is_authenticated` from `users`'''
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column('is_authenticated')


def downgrade():
    op.add_column('users', sa.Column('is_authenticated', sa.BOOLEAN(), nullable=True, server_default=sa.false()))
