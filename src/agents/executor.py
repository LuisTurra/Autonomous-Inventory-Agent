from src.database.connection import engine
from src.database.repositories import register_event
from src.simulation.purchase_generator import PurchaseGenerator

from sqlalchemy import text


class AgentExecutor:

    def __init__(self):

        self.purchase_generator = PurchaseGenerator()

    def execute_pending_tasks(self):

        query = """
            SELECT
                task_id,
                product_id,
                quantity,
                priority
            FROM tasks
            WHERE
                task_type = 'REPLENISHMENT'
                AND status = 'PENDING'
            ORDER BY
                CASE priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    ELSE 4
                END,
                created_at
        """

        with engine.connect() as connection:

            tasks = connection.execute(
                text(query)
            ).mappings().all()

        executed = []

        for task in tasks:

            purchase_id = (
                self.purchase_generator
                .create_purchase(
                    product_id=task["product_id"],
                    quantity=task["quantity"]
                )
            )

            if not purchase_id:
                continue

            with engine.begin() as connection:

                connection.execute(
                    text("""
                        UPDATE tasks
                        SET
                            status = 'IN_PROGRESS'
                        WHERE task_id = :task_id
                    """),
                    {
                        "task_id": task["task_id"]
                    }
                )

            register_event(
                event_type="REPLENISHMENT_EXECUTED",
                product_id=task["product_id"],
                quantity=task["quantity"],
                event_data={
                    "task_id": task["task_id"],
                    "purchase_id": purchase_id
                }
            )

            executed.append({
                "task_id": task["task_id"],
                "purchase_id": purchase_id,
                "product_id": task["product_id"],
                "quantity": task["quantity"]
            })

        return executed


if __name__ == "__main__":

    executor = AgentExecutor()

    results = executor.execute_pending_tasks()

    print(
        f"Tarefas executadas: {len(results)}"
    )