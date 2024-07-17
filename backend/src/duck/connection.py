from db.config import settings


def connect_to_postgres(duckdb_con):
    duckdb_con.execute("INSTALL postgres;")
    duckdb_con.execute("LOAD postgres;")
    duckdb_con.execute(
        "ATTACH 'dbname={} user={} password={} host=db port={}' AS db (TYPE POSTGRES);".format(
            settings.POSTGRES_DB,
            settings.POSTGRES_DB_USER,
            settings.POSTGRES_DB_PASSWORD,
            settings.POSTGRES_DB_HOST_PORT,
        )
    )


def connect_to_md(duckdb_con, motherduck_token):
    duckdb_con.sql(f"INSTALL md;")
    duckdb_con.sql(f"LOAD md;")
    duckdb_con.sql(f"SET motherduck_token='{motherduck_token}';")
    duckdb_con.sql(f"ATTACH 'md:'")
