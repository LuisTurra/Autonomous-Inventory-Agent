from src.database.load_olist_data import main as load_olist_data
from src.database.initialize_operational_data import (
    main as initialize_operational_data
)


def main():

    print("=== OLIST → OPERATIONAL DATABASE ===")

    print("\n1. Carregando dados históricos...")
    load_olist_data()

    print("\n2. Inicializando operação...")
    initialize_operational_data()

    print("\nBase operacional pronta.")


if __name__ == "__main__":
    main()