from src.analytics.sales_ranking import (
    get_sales_ranking,
    top_selling_products,
    lowest_selling_products,
    highest_revenue_products
)


class SalesAnalyst:

    name = "Sales Analyst"

    def analyze(self, days=30):

        ranking = get_sales_ranking(days)

        return {
            "period_days": days,
            "total_products": len(ranking),
            "total_units": int(
                ranking["units_sold"].sum()
            ) if not ranking.empty else 0,
            "total_revenue": float(
                ranking["revenue"].sum()
            ) if not ranking.empty else 0.0,
            "top_products": top_selling_products(
                limit=10,
                days=days
            ).to_dict("records"),
            "lowest_products": lowest_selling_products(
                limit=10,
                days=days
            ).to_dict("records"),
            "highest_revenue": highest_revenue_products(
                limit=10,
                days=days
            ).to_dict("records")
        }


if __name__ == "__main__":

    agent = SalesAnalyst()

    result = agent.analyze()

    print(
        f"Produtos analisados: "
        f"{result['total_products']}"
    )

    print(
        f"Unidades vendidas: "
        f"{result['total_units']:,}"
    )

    print(
        f"Receita: "
        f"R$ {result['total_revenue']:,.2f}"
    )