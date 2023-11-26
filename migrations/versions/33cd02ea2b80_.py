"""empty message

Revision ID: 33cd02ea2b80
Revises: ebc171823624
Create Date: 2023-11-26 16:05:40.131841

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '33cd02ea2b80'
down_revision = 'ebc171823624'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_time', sa.DateTime(), nullable=False))
        batch_op.drop_column('order_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_id', mysql.DATETIME(), nullable=False))
        batch_op.drop_column('order_time')

    # ### end Alembic commands ###
