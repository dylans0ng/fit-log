"""empty message

Revision ID: 38fbf901f5bd
Revises: 1885e42a518f
Create Date: 2024-07-31 23:13:38.760029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38fbf901f5bd'
down_revision = '1885e42a518f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['account_email'])

    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accounts_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'accounts', ['accounts_id'], ['accounts_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('accounts_id')

    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
