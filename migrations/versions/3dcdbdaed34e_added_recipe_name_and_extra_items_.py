"""Added 'recipe_name' and 'extra_items' attributes to grocery_list_item

Revision ID: 3dcdbdaed34e
Revises: 59e197a18bed
Create Date: 2023-03-14 19:15:49.879068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dcdbdaed34e'
down_revision = '59e197a18bed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('grocery_list_item', sa.Column('recipe_name', sa.String(), nullable=False))
    op.add_column('grocery_list_item', sa.Column('extra_items', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('grocery_list_item', 'extra_items')
    op.drop_column('grocery_list_item', 'recipe_name')
    # ### end Alembic commands ###
