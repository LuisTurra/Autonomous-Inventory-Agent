import json

from sqlalchemy import text

from src.database.connection import engine


def get_inventory():

    query = """
        SELECT
            i.product_id,
            p.product_category_name,
            i.quantity,
            i.reserved_quantity,
            i.minimum_stock,
            i.reorder_point,
            i.reorder_quantity,
            i.updated_at
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        ORDER BY i.product_id
    """

    with engine.connect() as connection:

        return connection.execute(text(query)).mappings().all()


def get_product_inventory(product_id):

    query = """
        SELECT
            i.product_id,
            i.quantity,
            i.reserved_quantity,
            i.minimum_stock,
            i.reorder_point,
            i.reorder_quantity,
            i.updated_at
        FROM inventory i
        WHERE i.product_id = :product_id
    """

    with engine.connect() as connection:

        return (
            connection.execute(text(query), {"product_id": product_id})
            .mappings()
            .first()
        )


def update_inventory(product_id, quantity_change):

    query = """
        UPDATE inventory
        SET
            quantity = quantity + :quantity_change,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = :product_id
        RETURNING
            product_id,
            quantity,
            updated_at
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query), {"product_id": product_id, "quantity_change": quantity_change}
        )

        return result.mappings().first()


def register_movement(
    product_id, movement_type, quantity, reference_id=None, is_simulated=False
):

    query = """
        INSERT INTO inventory_movements (
            product_id,
            movement_type,
            quantity,
            reference_id,
            is_simulated
        )
        VALUES (
            :product_id,
            :movement_type,
            :quantity,
            :reference_id,
            :is_simulated
        )
        RETURNING movement_id
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query),
            {
                "product_id": product_id,
                "movement_type": movement_type,
                "quantity": quantity,
                "reference_id": reference_id,
                "is_simulated": is_simulated,
            },
        )

        return result.scalar()


def register_event(
    event_type, product_id=None, quantity=None, event_data=None, is_simulated=False
):

    query = """
        INSERT INTO events (
            event_type,
            product_id,
            quantity,
            event_data,
            "is_simulated"
        )
        VALUES (
            :event_type,
            :product_id,
            :quantity,
            CAST(:event_data AS JSONB),
            :is_simulated
        )
        RETURNING event_id
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query),
            {
                "event_type": event_type,
                "product_id": product_id,
                "quantity": quantity,
                "event_data": json.dumps(event_data or {}, ensure_ascii=False),
                "is_simulated": is_simulated,
            },
        )

        return result.scalar()


def create_task(task_type, product_id, quantity, priority="MEDIUM"):

    query = """
        INSERT INTO tasks (
            task_type,
            product_id,
            quantity,
            priority,
            status
        )
        VALUES (
            :task_type,
            :product_id,
            :quantity,
            :priority,
            'PENDING'
        )
        RETURNING task_id
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query),
            {
                "task_type": task_type,
                "product_id": product_id,
                "quantity": quantity,
                "priority": priority,
            },
        )

        return result.scalar()


def register_decision(
    agent_name, product_id, decision_type, reasoning, decision_data, is_simulated=False
):

    query = """
        INSERT INTO decisions (
            agent_name,
            product_id,
            decision_type,
            reasoning,
            decision_data,
            is_simulated
        )
        VALUES (
            :agent_name,
            :product_id,
            :decision_type,
            :reasoning,
            CAST(:decision_data AS JSONB),
            :is_simulated
        )
        RETURNING decision_id
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query),
            {
                "agent_name": agent_name,
                "product_id": product_id,
                "decision_type": decision_type,
                "reasoning": reasoning,
                "decision_data": json.dumps(decision_data or {}, ensure_ascii=False),
                "is_simulated": is_simulated,
            },
        )

        return result.scalar()


def get_pending_purchases():

    query = """
        SELECT
            purchase_id,
            product_id,
            supplier_id,
            quantity,
            unit_cost,
            status,
            expected_delivery
        FROM purchases
        WHERE status = 'ORDERED'
        ORDER BY expected_delivery
    """

    with engine.connect() as connection:

        return connection.execute(text(query)).mappings().all()


def create_purchase(product_id, supplier_id, quantity, unit_cost, expected_delivery):

    query = """
        INSERT INTO purchases (
            product_id,
            supplier_id,
            quantity,
            unit_cost,
            status,
            expected_delivery
        )
        VALUES (
            :product_id,
            :supplier_id,
            :quantity,
            :unit_cost,
            'ORDERED',
            :expected_delivery
        )
        RETURNING purchase_id
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(query),
            {
                "product_id": product_id,
                "supplier_id": supplier_id,
                "quantity": quantity,
                "unit_cost": unit_cost,
                "expected_delivery": expected_delivery,
            },
        )

        return result.scalar()


def mark_purchase_delivered(purchase_id):

    query = """
        UPDATE purchases
        SET
            status = 'DELIVERED',
            delivered_at = CURRENT_TIMESTAMP
        WHERE purchase_id = :purchase_id
        RETURNING purchase_id
    """

    with engine.begin() as connection:

        result = connection.execute(text(query), {"purchase_id": purchase_id})

        return result.scalar()


def get_available_supplier():

    query = """
        SELECT
            supplier_id,
            supplier_name,
            lead_time_days,
            reliability
        FROM suppliers
        ORDER BY reliability DESC
        LIMIT 1
    """

    with engine.connect() as connection:

        return connection.execute(text(query)).mappings().first()


def create_simulation_snapshot():

    with engine.begin() as connection:

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS simulation_inventory_snapshot (

                product_id VARCHAR(50) PRIMARY KEY
                    REFERENCES products(product_id),

                quantity INTEGER NOT NULL,

                reserved_quantity INTEGER NOT NULL,

                minimum_stock INTEGER NOT NULL,

                reorder_point INTEGER NOT NULL,

                reorder_quantity INTEGER NOT NULL
            )
        """))

        # Só cria o snapshot se estiver vazio
        snapshot_exists = connection.execute(text("""
            SELECT EXISTS (
                SELECT 1
                FROM simulation_inventory_snapshot
            )
        """)).scalar()

        if not snapshot_exists:

            connection.execute(text("""
                INSERT INTO simulation_inventory_snapshot (
                    product_id,
                    quantity,
                    reserved_quantity,
                    minimum_stock,
                    reorder_point,
                    reorder_quantity
                )
                SELECT
                    product_id,
                    quantity,
                    reserved_quantity,
                    minimum_stock,
                    reorder_point,
                    reorder_quantity
                FROM inventory
            """))


def clear_simulation_data():

    with engine.begin() as connection:

        # ====================================================
        # RESTAURAR ESTOQUE ORIGINAL
        # ====================================================

        connection.execute(text("""
            UPDATE inventory
            SET
                quantity = 50,
                reserved_quantity = 0,
                minimum_stock = 10,
                reorder_point = 20,
                reorder_quantity = 50,
                updated_at = CURRENT_TIMESTAMP
        """))

        # ====================================================
        # REMOVER DADOS GERADOS PELA SIMULAÇÃO
        # ====================================================

        connection.execute(text("""
            DELETE FROM sales
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM events
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM inventory_movements
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM purchases
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM tasks
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM decisions
            WHERE is_simulated = TRUE
        """))

        connection.execute(text("""
            DELETE FROM simulation_inventory_snapshot
        """))
