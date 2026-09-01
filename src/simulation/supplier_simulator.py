from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import (
    update_inventory,
    register_movement,
    register_event,
)


class SupplierSimulator:

    def process_deliveries(self, simulated_time):

        query = """
            SELECT
                purchase_id,
                product_id,
                quantity,
                expected_delivery
            FROM purchases
            WHERE
                status = 'ORDERED'
                AND expected_delivery <= :simulated_time
            ORDER BY expected_delivery
        """

        with engine.connect() as connection:

            purchases = (
                connection.execute(text(query), {"simulated_time": simulated_time})
                .mappings()
                .all()
            )

        deliveries = []

        for purchase in purchases:

            purchase_id = purchase["purchase_id"]
            product_id = purchase["product_id"]
            quantity = purchase["quantity"]

            update_inventory(product_id, quantity)

            register_movement(
                product_id, "PURCHASE", quantity, purchase_id, is_simulated=True
            )

            register_event(
                event_type="SUPPLIER_DELIVERY",
                product_id=product_id,
                quantity=quantity,
                is_simulated=True,
                event_data={
                    "purchase_id": purchase_id,
                    "simulated_time": (simulated_time.isoformat()),
                },
            )

            with engine.begin() as connection:

                connection.execute(
                    text("""
                        UPDATE purchases
                        SET
                            status = 'DELIVERED',
                            delivered_at = :delivered_at
                        WHERE
                            purchase_id = :purchase_id
                        """),
                    {"purchase_id": purchase_id, "delivered_at": simulated_time},
                )

            deliveries.append(purchase_id)

        return deliveries
