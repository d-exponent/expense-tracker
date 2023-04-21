from alembic import op
import sqlalchemy as sa


def execute_raw_sql(sql_query):
    conn = op.get_bind()
    conn.execute(sa.sql.text(sql_query))
