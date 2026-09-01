from pathlib import Path

from src.database.connection import engine


SCHEMA_FILE = Path("sql/schema_raw.sql")


def initialize_database():
    sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with engine.begin() as connection:
        for statement in sql.split(";"):
            statement = statement.strip()

            if statement:
                connection.exec_driver_sql(statement)

    print("Banco de dados inicializado com sucesso.")


if __name__ == "__main__":
    initialize_database()