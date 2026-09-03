import json
from datetime import timedelta
from pathlib import Path

from sqlalchemy import text

from src.database.connection import engine
from src.database.repositories import (
    clear_simulation_data,
    create_simulation_snapshot,
)
from src.simulation.simulation_engine import SimulationEngine

OUTPUT_FILE = Path("data/demo/demo_dataset.json")


def get_historical_end():

    query = """
        SELECT MAX(sale_timestamp)
        FROM sales
        WHERE is_simulated = FALSE
    """

    with engine.connect() as connection:
        return connection.execute(text(query)).scalar()


def prepare_demo_inventory():

    query = """
        SELECT product_id
        FROM inventory
        ORDER BY product_id
        LIMIT 20
    """

    with engine.connect() as connection:
        products = connection.execute(text(query)).mappings().all()

    if not products:
        raise RuntimeError("Nenhum produto encontrado para preparar a Demo.")

    for product in products:

        product_id = product["product_id"]

        with engine.begin() as connection:

            connection.execute(
                text("""
                    UPDATE inventory
                    SET
                        quantity = 5,
                        minimum_stock = 10,
                        reorder_point = 20,
                        reorder_quantity = 50,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = :product_id
                """),
                {"product_id": product_id},
            )

    print(f"Estoque preparado para {len(products)} produtos.")


def collect_demo_data():

    tables = {
        "sales": """
            SELECT
                product_id,
                quantity,
                unit_price,
                sale_timestamp
            FROM sales
            WHERE is_simulated = TRUE
            ORDER BY sale_timestamp
        """,
        "purchases": """
            SELECT
                product_id,
                supplier_id,
                quantity,
                unit_cost,
                status,
                expected_delivery,
                delivered_at
            FROM purchases
            WHERE is_simulated = TRUE
            ORDER BY purchase_id
        """,
        "inventory_movements": """
            SELECT
                product_id,
                movement_type,
                quantity,
                reference_id,
                created_at
            FROM inventory_movements
            WHERE is_simulated = TRUE
            ORDER BY movement_id
        """,
        "events": """
            SELECT
                event_type,
                product_id,
                quantity,
                event_data,
                event_timestamp
            FROM events
            WHERE is_simulated = TRUE
            ORDER BY event_id
        """,
        "tasks": """
            SELECT
                task_type,
                product_id,
                quantity,
                priority,
                status,
                created_at,
                completed_at
            FROM tasks
            WHERE is_simulated = TRUE
            ORDER BY task_id
        """,
        "decisions": """
            SELECT
                agent_name,
                product_id,
                decision_type,
                reasoning,
                decision_data,
                created_at
            FROM decisions
            WHERE is_simulated = TRUE
            ORDER BY decision_id
        """,
    }

    dataset = {}

    with engine.connect() as connection:

        for table, query in tables.items():

            rows = connection.execute(text(query)).mappings().all()

            records = []

            for row in rows:

                record = dict(row)

                for key, value in record.items():

                    if hasattr(value, "isoformat"):
                        record[key] = value.isoformat()

                records.append(record)

            dataset[table] = records

        inventory_rows = connection.execute(text("""
                SELECT
                    product_id,
                    quantity,
                    reserved_quantity,
                    minimum_stock,
                    reorder_point,
                    reorder_quantity
                FROM inventory
                ORDER BY product_id
            """)).mappings().all()

        dataset["inventory"] = [dict(row) for row in inventory_rows]

    return dataset


def run_demo():

    print("=" * 60)
    print("GERADOR DO DEMO DATASET")
    print("=" * 60)

    historical_end = get_historical_end()

    if historical_end is None:

        raise RuntimeError("Não foi encontrada uma data final no histórico.")

    print(f"Fim do histórico: {historical_end}")

    # --------------------------------------------------------
    # LIMPAR DEMO ANTERIOR
    # --------------------------------------------------------

    clear_simulation_data()

    # --------------------------------------------------------
    # GARANTIR SNAPSHOT DO ESTOQUE ORIGINAL
    # --------------------------------------------------------

    create_simulation_snapshot()

    # --------------------------------------------------------
    # PREPARAR ALGUNS PRODUTOS PARA A DEMO
    # --------------------------------------------------------

    prepare_demo_inventory()

    # --------------------------------------------------------
    # CRIAR ENGINE
    # --------------------------------------------------------

    simulation = SimulationEngine(interval=0)

    simulation.state.simulated_time = historical_end + timedelta(minutes=1)

    # --------------------------------------------------------
    # EXECUTAR CENÁRIOS
    # --------------------------------------------------------

    scenarios = [
        ("Normal", 20),
        ("Alta demanda", 20),
        ("Demand Shock", 20),
        ("Ruptura de estoque", 30),
        ("Supplier Delay", 20),
    ]

    for scenario_name, cycles in scenarios:

        print()
        print(f"▶ Cenário: {scenario_name} " f"({cycles} ciclos)")

        simulation.state.set_scenario(scenario_name)

        simulation.state.set_speed(20)

        for cycle in range(cycles):

            result = simulation.process_cycle()

            print(
                f"  ciclo {cycle + 1:03d} | "
                f"vendas={len(result['sales'])} | "
                f"decisões={len(result['decisions'])} | "
                f"compras={len(result['purchases'])} | "
                f"entregas={len(result['deliveries'])}"
            )

    # --------------------------------------------------------
    # COLETAR RESULTADO
    # --------------------------------------------------------

    print()
    print("Coletando dados simulados...")

    dataset = collect_demo_data()

    # --------------------------------------------------------
    # SALVAR JSON
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(dataset, file, ensure_ascii=False, indent=2, default=str)

    print()
    print("=" * 60)
    print("DEMO DATASET GERADO")
    print("=" * 60)

    for table, records in dataset.items():

        print(f"{table}: " f"{len(records)} registros")

    print()
    print(f"Arquivo: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_demo()
