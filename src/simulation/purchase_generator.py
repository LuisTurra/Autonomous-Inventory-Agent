from datetime import timedelta

import pandas as pd
from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import register_event


class PurchaseGenerator:

    def create_purchase(self, product_id, quantity, simulated_time, supplier_delay=0):

        supplier = self._get_supplier(product_id)

        if supplier is None:
            return None

        expected_delivery = simulated_time + timedelta(
            days=(supplier["lead_time_days"] + supplier_delay)
        )

        query = """
    INSERT INTO purchases (
        product_id,
        supplier_id,
        quantity,
        unit_cost,
        status,
        expected_delivery,
        is_simulated
    )
    VALUES (
        :product_id,
        :supplier_id,
        :quantity,
        :unit_cost,
        'ORDERED',
        :expected_delivery,
        TRUE
    )
    RETURNING purchase_id
"""

        with engine.begin() as connection:

            purchase_id = connection.execute(
                text(query),
                {
                    "product_id": product_id,
                    "supplier_id": supplier["supplier_id"],
                    "quantity": quantity,
                    "unit_cost": supplier["unit_cost"],
                    "expected_delivery": expected_delivery,
                },
            ).scalar()

        register_event(
            event_type="PURCHASE_CREATED",
            product_id=product_id,
            quantity=quantity,
            event_data={
                "purchase_id": purchase_id,
                "supplier_id": supplier["supplier_id"],
                "lead_time_days": supplier["lead_time_days"],
                "supplier_delay_days": supplier_delay,
                "expected_delivery": (expected_delivery.isoformat()),
            },
            is_simulated=True,
        )

        return purchase_id

    def _get_supplier(self, product_id):

        query = """
            SELECT
                s.supplier_id,
                s.lead_time_days,
                s.reliability,
                COALESCE(
                    p.unit_price,
                    0
                ) AS unit_cost
            FROM suppliers s
            CROSS JOIN products p
            WHERE p.product_id = :product_id
            ORDER BY
                s.reliability DESC,
                s.lead_time_days ASC
            LIMIT 1
        """

        data = pd.read_sql(text(query), engine, params={"product_id": product_id})

        if data.empty:
            return None

        return data.iloc[0].to_dict()


if __name__ == "__main__":

    generator = PurchaseGenerator()

    print("Purchase Generator pronto.")
