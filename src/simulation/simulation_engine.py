import time
from datetime import timedelta

from src.agents.monitor import MonitorAgent
from src.agents.replenishment_agent import ReplenishmentAgent
from src.simulation.purchase_generator import PurchaseGenerator
from src.simulation.sales_generator import SalesGenerator
from src.simulation.simulation_state import SimulationState
from src.simulation.supplier_simulator import SupplierSimulator
from src.simulation.scenarios import get_scenario
from src.database.repositories import create_simulation_snapshot


class SimulationEngine:

    def __init__(self, interval=5):

        self.interval = interval

        self.state = SimulationState()

        self.sales_generator = SalesGenerator()
        self.supplier_simulator = SupplierSimulator()

        self.monitor = MonitorAgent()
        self.replenishment = ReplenishmentAgent()

        self.purchase_generator = PurchaseGenerator()

    # ============================================================
    # UM CICLO DA SIMULAÇÃO
    # ============================================================

    def process_cycle(self):

        scenario = get_scenario(self.state.scenario)

        self.sales_generator.sales_multiplier = (
            scenario["sales_multiplier"]
        )

        self.supplier_simulator.delay_days = (
            scenario["supplier_delay"]
        )

        # --------------------------------------------------------
        # VENDAS
        # --------------------------------------------------------

        sales = []

        for _ in range(self.state.speed):

            sale = self.sales_generator.generate_sale(
                self.state.simulated_time
            )

            if sale:

                self.state.register_sale()

                sales.append(sale)

        # --------------------------------------------------------
        # ENTREGAS
        # --------------------------------------------------------

        deliveries = self.supplier_simulator.process_deliveries(
            self.state.simulated_time
        )

        for _ in deliveries:

            self.state.register_delivery()

        # --------------------------------------------------------
        # MONITORAMENTO
        # --------------------------------------------------------

        self.monitor.check_inventory()

        # --------------------------------------------------------
        # REABASTECIMENTO
        # --------------------------------------------------------

        decisions = self.replenishment.analyze()

        # --------------------------------------------------------
        # COMPRAS
        # --------------------------------------------------------

        purchases = []

        for decision in decisions:

            purchase_id = self.purchase_generator.create_purchase(
                product_id=decision["product_id"],
                quantity=decision["quantity"],
                simulated_time=self.state.simulated_time,
                supplier_delay=scenario["supplier_delay"]
            )

            if purchase_id:

                self.state.register_purchase()

                purchases.append(purchase_id)

        # --------------------------------------------------------
        # AVANÇA TEMPO SIMULADO
        # --------------------------------------------------------

        self.state.simulated_time += (
            self.state.SPEED_TIME[self.state.speed]
        )

        # --------------------------------------------------------
        # RESULTADO
        # --------------------------------------------------------

        return {
            "sales": sales,
            "deliveries": deliveries,
            "decisions": decisions,
            "purchases": purchases,
            "status": self.state.get_status()
        }

    # ============================================================
    # EXECUÇÃO MANUAL / CLI
    # ============================================================

    def start(self):

        create_simulation_snapshot()

        self.state.start()

        print("Simulação iniciada.")
        print("Pressione Ctrl+C para parar.")

        while self.state.running:

            try:

                result = self.process_cycle()

                self._print_cycle_summary(result)

                time.sleep(self.interval)

            except KeyboardInterrupt:

                print("\nParando simulação...")

                self.stop()

            except Exception as error:

                print(f"Simulation error: {error}")

                time.sleep(self.interval)

    def run(self):

        self.start()

    def stop(self):

        self.state.stop()

        print("Simulação parada.")

    @staticmethod
    def _print_cycle_summary(result):

        sales = result["sales"]

        if sales:
            print(f"Venda: {sales}")

        if result["deliveries"]:
            print(
                f"Entregas: {len(result['deliveries'])}"
            )

        if result["decisions"]:
            print(
                f"Decisões: {len(result['decisions'])}"
            )

        if result["purchases"]:
            print(
                f"Compras: {len(result['purchases'])}"
            )


if __name__ == "__main__":

    simulation = SimulationEngine()

    simulation.start()