from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import (
    register_event,
    create_task
)


class MonitorAgent:

    name = "Monitor Agent"

    def check_inventory(self):

        query = """
            SELECT
                i.product_id,
                i.quantity,
                i.minimum_stock,
                i.reorder_point,
                i.reorder_quantity
            FROM inventory i
            WHERE i.quantity <= i.reorder_point
        """

        with engine.connect() as connection:

            products = connection.execute(
                text(query)
            ).mappings().all()

        monitored_products = []

        for product in products:

            product_id = product["product_id"]

            if self._has_pending_replenishment(
                product_id
            ):
                continue

            register_event(
                event_type="LOW_STOCK",
                product_id=product_id,
                quantity=product["quantity"],
                event_data={
                    "reorder_point":
                        product["reorder_point"],
                    "minimum_stock":
                        product["minimum_stock"],
                    "reorder_quantity":
                        product["reorder_quantity"]
                },
                is_simulated=True,
            )

            create_task(
    task_type="REPLENISHMENT",
    product_id=product_id,
    quantity=product["reorder_quantity"],
    priority="HIGH",
    is_simulated=True
)

            monitored_products.append(
                product
            )

        return monitored_products

    def _has_pending_replenishment(
        self,
        product_id
    ):

        query = """
            SELECT EXISTS (
                SELECT 1
                FROM tasks
                WHERE
                    product_id = :product_id
                    AND task_type = 'REPLENISHMENT'
                    AND status = 'PENDING'
            )
            OR EXISTS (
                SELECT 1
                FROM purchases
                WHERE
                    product_id = :product_id
                    AND status = 'ORDERED'
            )
        """

        with engine.connect() as connection:

            return connection.execute(
                text(query),
                {
                    "product_id": product_id
                }
            ).scalar()

    def has_pending_replenishment(
        self,
        product_id
    ):

        return self._has_pending_replenishment(
            product_id
        )


if __name__ == "__main__":

    agent = MonitorAgent()

    results = agent.check_inventory()

    print(
        "Monitor Agent: "
        f"{len(results)} produtos precisam "
        "de atenção."
    )