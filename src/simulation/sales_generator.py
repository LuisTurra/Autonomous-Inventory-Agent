import random

import pandas as pd
from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import (
    update_inventory,
    register_movement,
    register_event,
)


class SalesGenerator:

    def __init__(self):

        self.products = self._load_products()

        self.sales_multiplier = 1.0

        self.average_daily_sales = self._get_average_daily_sales()

    def _load_products(self):

        query = """
            SELECT
                s.product_id,
                SUM(s.quantity) AS total_sales
            FROM sales s
WHERE s.is_simulated = FALSE
GROUP BY s.product_id
        """

        data = pd.read_sql(text(query), engine)

        if data.empty:
            return []

        total_sales = data["total_sales"].sum()

        if total_sales <= 0:
            return []

        data["weight"] = data["total_sales"] / total_sales

        return data.to_dict("records")

    def _get_average_daily_sales(self):

        query = """
            SELECT
                AVG(daily_sales)
            FROM (
                SELECT
                    DATE(sale_timestamp) AS sale_date,
                    SUM(quantity) AS daily_sales
                FROM sales
                WHERE is_simulated = FALSE
                GROUP BY DATE(sale_timestamp)
            ) daily
        """

        with engine.connect() as connection:

            result = connection.execute(text(query)).scalar()

        if result is None:

            return 0

        return float(result)

    def generate_sale(self, simulated_time):

        if not self.products:

            return None

        probability = min(1.0, 0.25 * self.sales_multiplier)

        if random.random() > probability:

            return None

        product = random.choices(
            self.products, weights=[product["weight"] for product in self.products], k=1
        )[0]

        product_id = product["product_id"]

        query = """
            SELECT
                i.quantity,
                p.unit_price
            FROM inventory i
            JOIN products p
                ON p.product_id = i.product_id
            WHERE i.product_id = :product_id
        """

        data = pd.read_sql(text(query), engine, params={"product_id": product_id})

        if data.empty:

            return None

        current_stock = int(data.iloc[0]["quantity"])

        unit_price = float(data.iloc[0]["unit_price"] or 0)

        if current_stock <= 0:

            register_event(
    event_type="OUT_OF_STOCK",
    product_id=product_id,
    quantity=0,
    event_data={"simulated_time": simulated_time.isoformat()},
    is_simulated=True,
)

            return {"product_id": product_id, "quantity": 0, "status": "OUT_OF_STOCK"}

        quantity = 1

        update_inventory(product_id, -quantity)

        register_movement(product_id, "SALE", -quantity, is_simulated=True)

        with engine.begin() as connection:

            connection.execute(
                text("""
                    INSERT INTO sales (
                        product_id,
                        quantity,
                        unit_price,
                        sale_timestamp,
                        is_simulated
                    )
                    VALUES (
                        :product_id,
                        :quantity,
                        :unit_price,
                        :sale_timestamp,
                        TRUE
                    )
                """),
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "sale_timestamp": simulated_time,
                },
            )

        register_event(
            event_type="SALE",
            product_id=product_id,
            quantity=quantity,
            event_data={
                "unit_price": unit_price,
                "simulated_time": simulated_time.isoformat(),
            },
            is_simulated=True,
        )

        return {
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "status": "SOLD",
        }


if __name__ == "__main__":

    generator = SalesGenerator()

    from datetime import datetime

    result = generator.generate_sale(datetime.now())

    print(result)
