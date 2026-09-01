from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


RAW_DIR = Path("data/raw")


FILES = {
    "products": "olist_products_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
}


def load_csv(name):

    path = RAW_DIR / FILES[name]

    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}"
        )

    return pd.read_csv(path)


def clear_olist_data():

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                DELETE FROM inventory_movements;

                DELETE FROM sales;

                DELETE FROM inventory;

                DELETE FROM products;
                """
            )
        )


def load_products():

    products = load_csv("products")
    items = load_csv("order_items")

    prices = (
        items
        .groupby("product_id")["price"]
        .mean()
        .reset_index()
    )

    data = products[
        [
            "product_id",
            "product_category_name"
        ]
    ].merge(
        prices,
        on="product_id",
        how="left"
    )

    data = data.rename(
        columns={
            "price": "unit_price"
        }
    )

    data["unit_price"] = (
        data["unit_price"]
        .fillna(0)
    )

    data = data.drop_duplicates(
        subset=["product_id"]
    )

    data.to_sql(
        "products",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Produtos carregados: {len(data):,}"
    )

def load_sales():

    orders = load_csv("orders")
    items = load_csv("order_items")

    orders = orders[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_status"
        ]
    ]

    data = items.merge(
        orders,
        on="order_id",
        how="inner"
    )

    data = data[
        data["order_status"] == "delivered"
    ]

    sales = data[
        [
            "product_id",
            "price",
            "order_purchase_timestamp"
        ]
    ].copy()

    # Cada linha do order_items representa
    # uma unidade/item vendido.
    sales["quantity"] = 1

    sales = sales.rename(
        columns={
            "price": "unit_price",
            "order_purchase_timestamp":
                "sale_timestamp"
        }
    )

    sales = sales[
        [
            "product_id",
            "quantity",
            "unit_price",
            "sale_timestamp"
        ]
    ]

    sales.to_sql(
        "sales",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Vendas históricas carregadas: "
        f"{len(sales):,}"
    )


def main():

    print(
        "========================================"
    )

    print(
        "Carregando dados da Olist..."
    )

    print(
        "========================================"
    )

    clear_olist_data()

    load_products()

    load_sales()

    print(
        "Carga da Olist concluída."
    )


if __name__ == "__main__":
    main()