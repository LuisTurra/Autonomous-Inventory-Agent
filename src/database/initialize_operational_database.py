from pathlib import Path

from src.database.connection import engine


SCHEMA_FILE = Path("sql/operational_schema.sql")


def initialize_operational_database():
    sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with engine.begin() as connection:
        for statement in sql.split(";"):
            statement = statement.strip()

            if statement:
                connection.exec_driver_sql(statement)

    print("Banco operacional inicializado com sucesso.")


if __name__ == "__main__":
    initialize_operational_database()