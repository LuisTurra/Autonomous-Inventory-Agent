import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


SUPPLIERS = [
    {
        "supplier_name": "Supplier Alpha",
        "lead_time_days": 2,
        "reliability": 0.95
    },
    {
        "supplier_name": "Supplier Beta",
        "lead_time_days": 4,
        "reliability": 0.90
    },
    {
        "supplier_name": "Supplier Gamma",
        "lead_time_days": 7,
        "reliability": 0.85
    }
]


def initialize_suppliers():

    with engine.begin() as connection:

        existing = connection.execute(
            text(
                """
                SELECT supplier_name
                FROM suppliers
                """
            )
        ).scalars().all()

    existing = set(existing)

    new_suppliers = [
        supplier
        for supplier in SUPPLIERS
        if supplier["supplier_name"] not in existing
    ]

    if not new_suppliers:

        print(
            "Fornecedores já inicializados."
        )

        return

    suppliers = pd.DataFrame(
        new_suppliers
    )

    suppliers.to_sql(
        "suppliers",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Fornecedores criados: "
        f"{len(suppliers)}"
    )


def initialize_inventory():

    products = pd.read_sql(
        """
        SELECT
            product_id
        FROM products
        """,
        engine
    )

    if products.empty:

        print(
            "Nenhum produto encontrado."
        )

        return

    existing = pd.read_sql(
        """
        SELECT
            product_id
        FROM inventory
        """,
        engine
    )

    existing_ids = set(
        existing["product_id"]
    )

    products = products[
        ~products["product_id"].isin(
            existing_ids
        )
    ]

    if products.empty:

        print(
            "Estoque já inicializado."
        )

        return

    inventory = pd.DataFrame({
        "product_id":
            products["product_id"],

        "quantity": 50,

        "reserved_quantity": 0,

        "minimum_stock": 10,

        "reorder_point": 20,

        "reorder_quantity": 50
    })

    inventory.to_sql(
        "inventory",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Estoque inicializado: "
        f"{len(inventory):,} produtos"
    )


def main():

    print(
        "========================================"
    )

    print(
        "Inicializando dados operacionais..."
    )

    print(
        "========================================"
    )

    initialize_suppliers()

    initialize_inventory()

    print(
        "========================================"
    )

    print(
        "Banco operacional inicializado."
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()