from sqlalchemy import text

from src.database.connection import engine


TABLES = [
    "olist_customers_dataset",
    # "olist_geolocation_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "olist_orders_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "product_category_name_translation",
]


def check_database():
    with engine.connect() as connection:

        for table in TABLES:
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )

            count = result.scalar()

            print(f"{table}: {count:,} registros")


if __name__ == "__main__":
    check_database()