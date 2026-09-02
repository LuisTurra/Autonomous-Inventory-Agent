from datetime import datetime, timedelta

from src.simulation.scenarios import get_scenarios
from sqlalchemy import text

from src.database.connection import engine


class SimulationState:

    ALLOWED_SPEEDS = [
        1,
        2,
        5,
        10,
        20,
        50,
        100
    ]

    SPEED_TIME = {

        1: timedelta(hours=1),

        2: timedelta(hours=3),

        5: timedelta(hours=6),

        10: timedelta(hours=12),

        20: timedelta(days=1),

        50: timedelta(days=3),

        100: timedelta(days=7),
    }

    def __init__(self):

        self.running = False

        self.speed = 1

        self.scenario = "Normal"

        self.simulated_time = datetime.now()

        self.events_processed = 0
        self.sales_processed = 0
        self.purchases_processed = 0
        self.deliveries_processed = 0

        self.products_per_cycle = 1

        self.simulation_start_time = None

    # ============================================================
    # CONTROLE
    # ============================================================

    def start(self):

        if self.simulated_time is None:

            last_date = self.get_historical_end()

            if last_date:

                self.simulated_time = (
                    last_date + timedelta(minutes=1)
                )

        self.running = True

    def stop(self):

        self.running = False

    def reset(self):

        self.running = False

        self.speed = 1

        self.scenario = "Normal"

        self.simulated_time = datetime.now()

        self.events_processed = 0
        self.sales_processed = 0
        self.purchases_processed = 0
        self.deliveries_processed = 0

        self.products_per_cycle = 1

        self.simulation_start_time = None

    # ============================================================
    # EVENTOS
    # ============================================================

    def register_sale(self):

        self.sales_processed += 1
        self.events_processed += 1

    def register_purchase(self):

        self.purchases_processed += 1
        self.events_processed += 1

    def register_delivery(self):

        self.deliveries_processed += 1
        self.events_processed += 1

    def register_event(self):

        self.events_processed += 1

    # ============================================================
    # CONFIGURAÇÕES
    # ============================================================

    def set_speed(self, speed):

        if speed not in self.ALLOWED_SPEEDS:

            raise ValueError(
                "Velocidade deve ser 1, 2, 5, 10, 20, 50 ou 100."
            )

        self.speed = speed

    def set_scenario(self, scenario):

        if scenario not in get_scenarios():

            raise ValueError(
                f"Cenário desconhecido: {scenario}"
            )

        self.scenario = scenario

    def set_products_per_cycle(self, quantity):

        if quantity < 1:

            raise ValueError(
                "A quantidade de produtos deve ser maior que zero."
            )

        self.products_per_cycle = quantity

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        return {

            "running": self.running,

            "speed": self.speed,

            "scenario": self.scenario,

            "simulated_time": self.simulated_time,

            "events_processed": self.events_processed,

            "sales_processed": self.sales_processed,

            "purchases_processed": self.purchases_processed,

            "deliveries_processed": self.deliveries_processed,
        }

    # ============================================================
    # HISTÓRICO
    # ============================================================

    def get_historical_end(self):

        query = """
            SELECT MAX(sale_timestamp)
            FROM sales
            WHERE is_simulated = FALSE
        """

        with engine.connect() as connection:

            return connection.execute(
                text(query)
            ).scalar()