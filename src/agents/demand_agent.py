from src.analytics.demand_analysis import (
    get_product_demand,
    calculate_demand_trend
)

from src.analytics.forecasting import (
    forecast_product_demand
)

from src.database.connection import engine
from sqlalchemy import text


class DemandAgent:

    name = "Demand Agent"

    def analyze_product(
        self,
        product_id,
        forecast_days=7
    ):

        demand = get_product_demand(
            product_id
        )

        trend = calculate_demand_trend(
            product_id
        )

        forecast = forecast_product_demand(
            product_id,
            forecast_days
        )

        if demand is None:

            return {
                "product_id": product_id,
                "sales_per_day": 0.0,
                "trend": 0.0,
                "forecast": forecast,
                "risk": "UNKNOWN"
            }

        sales_per_day = demand[
            "sales_per_day"
        ]

        with engine.connect() as connection:

            stock = connection.execute(
                text("""
                    SELECT quantity
                    FROM inventory
                    WHERE product_id = :product_id
                """),
                {
                    "product_id": product_id
                }
            ).scalar()

        stock = stock or 0

        if sales_per_day <= 0:

            days_remaining = None

        else:

            days_remaining = (
                stock / sales_per_day
            )

        if days_remaining is None:

            risk = "LOW"

        elif days_remaining <= 3:

            risk = "HIGH"

        elif days_remaining <= 7:

            risk = "MEDIUM"

        else:

            risk = "LOW"

        return {
            "product_id": product_id,
            "sales_per_day": float(
                sales_per_day
            ),
            "trend": float(trend),
            "days_remaining": (
                float(days_remaining)
                if days_remaining is not None
                else None
            ),
            "forecast": forecast,
            "risk": risk
        }


    def analyze_products(
        self,
        limit=100
    ):

        with engine.connect() as connection:

            products = connection.execute(
                text("""
                    SELECT product_id
                    FROM inventory
                    LIMIT :limit
                """),
                {
                    "limit": limit
                }
            ).scalars().all()

        return [
            self.analyze_product(product_id)
            for product_id in products
        ]


if __name__ == "__main__":

    agent = DemandAgent()

    results = agent.analyze_products(
        limit=10
    )

    for result in results:

        print(
            result["product_id"],
            result["risk"]
        )