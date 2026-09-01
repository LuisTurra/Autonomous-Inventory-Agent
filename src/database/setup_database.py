from pathlib import Path

from sqlalchemy import text

from src.database.connection import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SQL_DIR = PROJECT_ROOT / "sql"


def execute_sql_file(filename):

    sql_path = SQL_DIR / filename

    if not sql_path.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {sql_path}"
        )

    sql = sql_path.read_text(
        encoding="utf-8"
    )

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    with engine.begin() as connection:

        for statement in statements:

            connection.execute(
                text(statement)
            )


def setup_database():

    print("========================================")
    print("Configurando banco operacional...")
    print("========================================")

    print("1. Criando tabelas...")

    execute_sql_file(
        "schema.sql"
    )

    print("2. Criando views...")

    execute_sql_file(
        "views.sql"
    )

    print("========================================")
    print("Banco operacional configurado.")
    print("========================================")


if __name__ == "__main__":

    setup_database()