import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import (
    clear_simulation_data,
    create_simulation_snapshot,
)

DEMO_FILE = Path("data/demo/demo_dataset.json")


def _parse_datetime(value):

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value)


def _load_json():

    if not DEMO_FILE.exists():

        raise FileNotFoundError(f"Demo Dataset não encontrado: {DEMO_FILE}")

    with open(DEMO_FILE, "r", encoding="utf-8") as file:

        return json.load(file)


def _load_inventory(dataset):

    rows = dataset.get("inventory", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            connection.execute(
                text("""
                    UPDATE inventory
                    SET
                        quantity = :quantity,
                        reserved_quantity = :reserved_quantity,
                        minimum_stock = :minimum_stock,
                        reorder_point = :reorder_point,
                        reorder_quantity = :reorder_quantity,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = :product_id
                """),
                {
                    "product_id": row["product_id"],
                    "quantity": row["quantity"],
                    "reserved_quantity": row["reserved_quantity"],
                    "minimum_stock": row["minimum_stock"],
                    "reorder_point": row["reorder_point"],
                    "reorder_quantity": row["reorder_quantity"],
                },
            )


def _load_sales(dataset):

    rows = dataset.get("sales", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

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
                    "product_id": row["product_id"],
                    "quantity": row["quantity"],
                    "unit_price": row["unit_price"],
                    "sale_timestamp": _parse_datetime(row["sale_timestamp"]),
                },
            )


def _load_purchases(dataset):

    rows = dataset.get("purchases", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            connection.execute(
                text("""
                    INSERT INTO purchases (
                        product_id,
                        supplier_id,
                        quantity,
                        unit_cost,
                        status,
                        expected_delivery,
                        delivered_at,
                        is_simulated
                    )
                    VALUES (
                        :product_id,
                        :supplier_id,
                        :quantity,
                        :unit_cost,
                        :status,
                        :expected_delivery,
                        :delivered_at,
                        TRUE
                    )
                """),
                {
                    "product_id": row["product_id"],
                    "supplier_id": row["supplier_id"],
                    "quantity": row["quantity"],
                    "unit_cost": row["unit_cost"],
                    "status": row["status"],
                    "expected_delivery": _parse_datetime(row["expected_delivery"]),
                    "delivered_at": _parse_datetime(row["delivered_at"]),
                },
            )


def _load_movements(dataset):

    rows = dataset.get("inventory_movements", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            connection.execute(
                text("""
                    INSERT INTO inventory_movements (
                        product_id,
                        movement_type,
                        quantity,
                        reference_id,
                        created_at,
                        is_simulated
                    )
                    VALUES (
                        :product_id,
                        :movement_type,
                        :quantity,
                        NULL,
                        :created_at,
                        TRUE
                    )
                """),
                {
                    "product_id": row["product_id"],
                    "movement_type": row["movement_type"],
                    "quantity": row["quantity"],
                    "created_at": _parse_datetime(row["created_at"]),
                },
            )


def _load_events(dataset):

    rows = dataset.get("events", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            event_data = row.get("event_data")

            if event_data is None:
                event_data = {}

            # IDs do Dataset original não são reutilizados no Cloud.
            # Mantemos apenas os dados sem referências físicas antigas.
            event_data = dict(event_data)

            event_data.pop("purchase_id", None)
            event_data.pop("task_id", None)

            connection.execute(
                text("""
                    INSERT INTO events (
                        event_type,
                        product_id,
                        quantity,
                        event_data,
                        event_timestamp,
                        is_simulated
                    )
                    VALUES (
                        :event_type,
                        :product_id,
                        :quantity,
                        CAST(:event_data AS JSONB),
                        :event_timestamp,
                        TRUE
                    )
                """),
                {
                    "event_type": row["event_type"],
                    "product_id": row["product_id"],
                    "quantity": row["quantity"],
                    "event_data": json.dumps(event_data, ensure_ascii=False),
                    "event_timestamp": _parse_datetime(row["event_timestamp"]),
                },
            )


def _load_tasks(dataset):

    rows = dataset.get("tasks", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            connection.execute(
                text("""
                    INSERT INTO tasks (
                        task_type,
                        product_id,
                        quantity,
                        priority,
                        status,
                        created_at,
                        completed_at,
                        is_simulated
                    )
                    VALUES (
                        :task_type,
                        :product_id,
                        :quantity,
                        :priority,
                        :status,
                        :created_at,
                        :completed_at,
                        TRUE
                    )
                """),
                {
                    "task_type": row["task_type"],
                    "product_id": row["product_id"],
                    "quantity": row["quantity"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "created_at": _parse_datetime(row["created_at"]),
                    "completed_at": _parse_datetime(row["completed_at"]),
                },
            )


def _load_decisions(dataset):

    rows = dataset.get("decisions", [])

    if not rows:
        return

    with engine.begin() as connection:

        for row in rows:

            decision_data = row.get("decision_data")

            if decision_data is None:
                decision_data = {}

            decision_data = dict(decision_data)

            decision_data.pop("task_id", None)

            connection.execute(
                text("""
                    INSERT INTO decisions (
                        agent_name,
                        product_id,
                        decision_type,
                        reasoning,
                        decision_data,
                        created_at,
                        is_simulated
                    )
                    VALUES (
                        :agent_name,
                        :product_id,
                        :decision_type,
                        :reasoning,
                        CAST(:decision_data AS JSONB),
                        :created_at,
                        TRUE
                    )
                """),
                {
                    "agent_name": row["agent_name"],
                    "product_id": row["product_id"],
                    "decision_type": row["decision_type"],
                    "reasoning": row["reasoning"],
                    "decision_data": json.dumps(decision_data, ensure_ascii=False),
                    "created_at": _parse_datetime(row["created_at"]),
                },
            )


def load_demo():

    dataset = _load_json()

    # --------------------------------------------------------
    # GARANTIR SNAPSHOT DO ESTADO ORIGINAL
    # --------------------------------------------------------

    create_simulation_snapshot()

    # --------------------------------------------------------
    # LIMPAR DEMO ANTERIOR
    # --------------------------------------------------------

    clear_simulation_data()

    # --------------------------------------------------------
    # CARREGAR DADOS
    # --------------------------------------------------------

    _load_sales(dataset)
    _load_purchases(dataset)
    _load_movements(dataset)
    _load_events(dataset)
    _load_tasks(dataset)
    _load_decisions(dataset)

    # --------------------------------------------------------
    # APLICAR ESTADO FINAL DO ESTOQUE
    # --------------------------------------------------------

    _load_inventory(dataset)

    return {
        "sales": len(dataset.get("sales", [])),
        "purchases": len(dataset.get("purchases", [])),
        "inventory_movements": len(dataset.get("inventory_movements", [])),
        "events": len(dataset.get("events", [])),
        "tasks": len(dataset.get("tasks", [])),
        "decisions": len(dataset.get("decisions", [])),
        "inventory": len(dataset.get("inventory", [])),
    }


if __name__ == "__main__":

    result = load_demo()

    print("=" * 60)
    print("DEMO CARREGADA")
    print("=" * 60)

    for table, count in result.items():

        print(f"{table}: {count} registros")
