from pathlib import Path

import pandas as pd

from src.database.connection import engine


DATA_DIR = Path("data/raw")


FILES = {
    "olist_customers_dataset": "olist_customers_dataset.csv",
    # "olist_geolocation_dataset": "olist_geolocation_dataset.csv",
    "olist_products_dataset": "olist_products_dataset.csv",
    "olist_sellers_dataset": "olist_sellers_dataset.csv",
    "olist_orders_dataset": "olist_orders_dataset.csv",
    "olist_order_items_dataset": "olist_order_items_dataset.csv",
    "olist_order_payments_dataset": "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset": "olist_order_reviews_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}


def load_olist_data():
    for table_name, filename in FILES.items():

        file_path = DATA_DIR / filename

        if not file_path.exists():
            print(f"[ERRO] Arquivo não encontrado: {filename}")
            continue

        print(f"[LOAD] {filename}")

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        print(f"[OK] {len(df):,} registros carregados")


if __name__ == "__main__":
    load_olist_data()
    print("\nCarga da Olist concluída.")