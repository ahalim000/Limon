"""Removed 'nullable=False' from meal_plan_item's 'recipe' attribute

Revision ID: 59e197a18bed
Revises: 85569448052e
Create Date: 2023-03-14 16:40:37.813479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59e197a18bed'
down_revision = '85569448052e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('meal_plan_item', 'servings',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('meal_plan_item', 'servings',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
