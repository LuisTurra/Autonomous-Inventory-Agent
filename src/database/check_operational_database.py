import pandas as pd

from src.database.connection import engine


TABLES = [
    "products",
    "inventory",
    "suppliers",
    "sales",
    "purchases",
    "inventory_movements",
    "events",
    "tasks",
    "decisions",
    "agent_memory"
]


def check_database():

    print("\n=== OPERATIONAL DATABASE ===\n")

    for table in TABLES:

        try:

            result = pd.read_sql(
                f"SELECT COUNT(*) AS total FROM {table}",
                engine
            )

            total = int(result.iloc[0]["total"])

            print(
                f"{table:<25} {total:>10,} registros"
            )

        except Exception as error:

            print(
                f"{table:<25} ERRO: {error}"
            )


if __name__ == "__main__":
    check_database()