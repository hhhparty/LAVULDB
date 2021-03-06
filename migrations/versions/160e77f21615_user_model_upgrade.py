"""User model upgrade

Revision ID: 160e77f21615
Revises: 72be901c9e2f
Create Date: 2017-01-08 14:06:35.424949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '160e77f21615'
down_revision = '72be901c9e2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('permissions', sa.Integer(), nullable=True))
    op.add_column('roles', sa.Column('role_default', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_roles_role_default'), 'roles', ['role_default'], unique=False)
    op.add_column('users', sa.Column('user_confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'user_confirmed')
    op.drop_index(op.f('ix_roles_role_default'), table_name='roles')
    op.drop_column('roles', 'role_default')
    op.drop_column('roles', 'permissions')
    # ### end Alembic commands ###
