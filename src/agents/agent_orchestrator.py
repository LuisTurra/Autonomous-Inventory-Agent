from src.agents.monitor import MonitorAgent
from src.agents.sales_analyst import SalesAnalyst
from src.agents.demand_agent import DemandAgent
from src.agents.replenishment_agent import ReplenishmentAgent
from src.agents.executor import AgentExecutor


class AgentOrchestrator:

    def __init__(self):

        self.monitor = MonitorAgent()
        self.sales = SalesAnalyst()
        self.demand = DemandAgent()
        self.replenishment = ReplenishmentAgent()
        self.executor = AgentExecutor()

    def run_cycle(self):

        monitor_result = (
            self.monitor.check_inventory()
        )

        sales_result = (
            self.sales.analyze(days=30)
        )

        demand_result = (
            self.demand.analyze_products(
                limit=20
            )
        )

        replenishment_result = (
            self.replenishment.analyze()
        )

        execution_result = (
            self.executor.execute_pending_tasks()
        )

        return {
            "monitor": monitor_result,
            "sales": sales_result,
            "demand": demand_result,
            "replenishment": replenishment_result,
            "execution": execution_result
        }