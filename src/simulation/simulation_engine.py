
import threading
import time

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

        self.worker_thread = None

        self.worker_lock = threading.Lock()

        self.last_result = None

        self.last_error = None

    # ========================================================
    # CICLO
    # ========================================================

    def process_cycle(self):

        scenario = get_scenario(
            self.state.scenario
        )

        self.sales_generator.sales_multiplier = (
            scenario["sales_multiplier"]
        )

        self.supplier_simulator.delay_days = (
            scenario["supplier_delay"]
        )

        sales = []

        # ----------------------------------------------------
        # VENDAS
        # ----------------------------------------------------

        for _ in range(self.state.speed):

            # Verifica se foi pausada durante o ciclo.

            if not self.state.running:

                break

            sale = (
                self.sales_generator.generate_sale(
                    self.state.simulated_time
                )
            )

            if sale:

                self.state.register_sale()

                sales.append(sale)

        # ----------------------------------------------------
        # ENTREGAS
        # ----------------------------------------------------

        deliveries = (
            self.supplier_simulator.process_deliveries(
                self.state.simulated_time
            )
        )

        if self.state.running:

            for _ in deliveries:

                self.state.register_delivery()

        # ----------------------------------------------------
        # MONITORAMENTO
        # ----------------------------------------------------

        if self.state.running:

            self.monitor.check_inventory()

        # ----------------------------------------------------
        # REPOSIÇÃO
        # ----------------------------------------------------

        decisions = []

        if self.state.running:

            decisions = self.replenishment.analyze()

        # ----------------------------------------------------
        # COMPRAS
        # ----------------------------------------------------

        purchases = []

        if self.state.running:

            for decision in decisions:

                if not self.state.running:

                    break

                purchase_id = (
                    self.purchase_generator.create_purchase(
                        product_id=decision["product_id"],
                        quantity=decision["quantity"],
                        simulated_time=(
                            self.state.simulated_time
                        ),
                        supplier_delay=(
                            scenario["supplier_delay"]
                        ),
                    )
                )

                if purchase_id:

                    self.state.register_purchase()

                    purchases.append(
                        purchase_id
                    )

        # ----------------------------------------------------
        # TEMPO SIMULADO
        # ----------------------------------------------------

        if self.state.running:

            self.state.simulated_time += (
                self.state.SPEED_TIME[
                    self.state.speed
                ]
            )

        return {
            "sales": sales,
            "deliveries": deliveries,
            "decisions": decisions,
            "purchases": purchases,
            "status": self.state.get_status(),
        }

    # ========================================================
    # WORKER
    # ========================================================

    def _worker(self):

        print(
            "Worker da simulação iniciado."
        )

        self.last_error = None

        while self.state.running:

            try:

                result = self.process_cycle()

                self.last_result = result

                self._print_cycle_summary(
                    result
                )

                # ------------------------------------------------
                # Espera interrompível.
                #
                # Em vez de simplesmente:
                #
                # time.sleep(self.interval)
                #
                # verificamos periodicamente se a simulação
                # ainda está rodando.
                # ------------------------------------------------

                elapsed = 0

                while (
                    elapsed < self.interval
                    and self.state.running
                ):

                    time.sleep(0.1)

                    elapsed += 0.1

            except Exception as error:

                self.last_error = error

                print(
                    f"Simulation error: {error}"
                )

                self.state.stop()

                break

        print(
            "Worker da simulação finalizado."
        )

    # ========================================================
    # INICIAR EM BACKGROUND
    # ========================================================

    def start_background(self):

        with self.worker_lock:

            # Não permite duas threads simultâneas.

            if (
                self.worker_thread is not None
                and self.worker_thread.is_alive()
            ):

                return False

            create_simulation_snapshot()

            self.state.start()

            self.last_error = None

            self.worker_thread = threading.Thread(
                target=self._worker,
                daemon=True,
                name="inventory-simulation-worker",
            )

            self.worker_thread.start()

            return True

    # ========================================================
    # COMPATIBILIDADE
    # ========================================================

    def start(self):

        return self.start_background()

    def run(self):

        return self.start_background()

    # ========================================================
    # PARAR
    # ========================================================

    def stop(self):

        self.state.stop()

        print(
            "Solicitação para parar a simulação."
        )

    # ========================================================
    # STATUS DA THREAD
    # ========================================================

    def is_running(self):

        if not self.state.running:

            return False

        if self.worker_thread is None:

            return False

        return self.worker_thread.is_alive()

    # ========================================================
    # RESUMO
    # ========================================================

    @staticmethod
    def _print_cycle_summary(result):

        sales = result.get(
            "sales",
            []
        )

        deliveries = result.get(
            "deliveries",
            []
        )

        decisions = result.get(
            "decisions",
            []
        )

        purchases = result.get(
            "purchases",
            []
        )

        if sales:

            print(
                f"Venda: {sales}"
            )

        if deliveries:

            print(
                f"Entregas: {len(deliveries)}"
            )

        if decisions:

            print(
                f"Decisões: {len(decisions)}"
            )

        if purchases:

            print(
                f"Compras: {len(purchases)}"
            )


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":

    simulation = SimulationEngine()

    simulation.start_background()

    try:

        while simulation.is_running():

            time.sleep(1)

    except KeyboardInterrupt:

        simulation.stop()

