"""add totp columns

Revision ID: 2e862ca9d159
Revises: 64f6a347f887
Create Date: 2018-04-05 12:08:35.371000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = '2e862ca9d159'
down_revision = '64f6a347f887'
branch_labels = None
depends_on = None


Base = declarative_base()


# NOTE: We only need the primary key and the columns we need to change.
class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    totp_secret = sa.Column(sa.String(16))


def upgrade():
    op.add_column('users', sa.Column('totp_enabled', sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column('users', sa.Column('totp_secret', sa.String(length=16), nullable=True))
    op.add_column('users', sa.Column('is_authenticated', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column('totp_secret')
        batch_op.drop_column('totp_enabled')
        batch_op.drop_column('is_authenticated')
