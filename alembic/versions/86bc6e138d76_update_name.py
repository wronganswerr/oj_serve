"""update name

Revision ID: 86bc6e138d76
Revises: 62b60c60f48c
Create Date: 2024-11-17 19:24:21.284806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '86bc6e138d76'
down_revision: Union[str, None] = '62b60c60f48c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('codeforces_problem')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('codeforces_problem',
    sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('contest_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('index', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.Column('type', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.Column('rating', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('tags', mysql.JSON(), nullable=False),
    sa.Column('solved_count', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_in_mongodb', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128), nullable=True),
    sa.Column('contest_index', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
