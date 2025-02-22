"""empty message

Revision ID: 986a4ba6fab6
Revises: 0ab12efbb188
Create Date: 2024-07-28 16:27:07.208276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '986a4ba6fab6'
down_revision = '0ab12efbb188'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('accounts_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=15), nullable=True),
    sa.Column('last_name', sa.String(length=25), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('accounts_id')
    )
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accounts_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'accounts', ['accounts_id'], ['accounts_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('accounts_id')

    op.drop_table('accounts')
    # ### end Alembic commands ###
