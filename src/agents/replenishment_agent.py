from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import register_decision


class ReplenishmentAgent:

    name = "Replenishment Agent"

    def analyze(self):

        query = """
            SELECT
                t.task_id,
                t.product_id,
                t.quantity,
                t.priority,
                i.quantity AS current_stock,
                i.reorder_point,
                i.reorder_quantity
            FROM tasks t
            JOIN inventory i
                ON i.product_id = t.product_id
            WHERE
                t.task_type = 'REPLENISHMENT'
                AND t.status = 'PENDING'
            ORDER BY
                CASE t.priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,
                t.created_at
        """

        with engine.connect() as connection:

            tasks = connection.execute(
                text(query)
            ).mappings().all()

        decisions = []

        for task in tasks:

            task_id = task["task_id"]

            product_id = task["product_id"]
                        
            pending_purchase_query = """
                SELECT 1
                FROM purchases
                WHERE
                    product_id = :product_id
                    AND status = 'ORDERED'
                LIMIT 1
            """

            with engine.connect() as connection:

                pending_purchase = connection.execute(
                    text(pending_purchase_query),
                    {
                        "product_id": product_id
                    }
                ).first()

            if pending_purchase:
                continue
            quantity = task["current_stock"]

            reorder_point = task["reorder_point"]

            reorder_quantity = task[
                "reorder_quantity"
            ]

            priority = task["priority"]

            if quantity <= 0:

                priority = "CRITICAL"

            elif quantity <= reorder_point:

                priority = "HIGH"

            else:

                continue

            reasoning = (
                f"Estoque atual ({quantity}) "
                f"está abaixo do reorder point "
                f"({reorder_point}). "
                f"Reposição recomendada: "
                f"{reorder_quantity} unidades."
            )

            decision_data = {
                "task_id": task_id,
                "current_stock": quantity,
                "reorder_point": reorder_point,
                "reorder_quantity": reorder_quantity,
                "priority": priority
            }

            decision_id = register_decision(
                agent_name=self.name,
                product_id=product_id,
                decision_type="REPLENISH",
                reasoning=reasoning,
                decision_data=decision_data,
                is_simulated=True
            )

            decisions.append({
                "decision_id": decision_id,
                "task_id": task_id,
                "product_id": product_id,
                "quantity": reorder_quantity,
                "priority": priority
            })

        return decisions


if __name__ == "__main__":

    agent = ReplenishmentAgent()

    results = agent.analyze()

    print(
        f"Decisões de reposição: "
        f"{len(results)}"
    )