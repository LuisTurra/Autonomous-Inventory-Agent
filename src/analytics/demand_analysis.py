import pandas as pd

from src.database.connection import engine


def get_demand_analysis(days=30):

    query = """
        SELECT
            product_id,
            SUM(quantity) AS units_sold,
            COUNT(DISTINCT DATE(sale_timestamp)) AS active_days
        FROM sales
        WHERE sale_timestamp >=
            CURRENT_TIMESTAMP - (:days * INTERVAL '1 day')
        GROUP BY product_id
    """

    data = pd.read_sql(
        query,
        engine,
        params={"days": days}
    )

    if data.empty:
        return data

    data["sales_per_day"] = (
        data["units_sold"] /
        data["active_days"].clip(lower=1)
    )

    return data


def get_product_demand(product_id, days=30):

    data = get_demand_analysis(days)

    if data.empty:
        return None

    result = data[
        data["product_id"] == product_id
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def calculate_demand_trend(product_id):

    query = """
        SELECT
            CASE
                WHEN sale_timestamp >=
                    CURRENT_TIMESTAMP - INTERVAL '15 days'
                THEN 'recent'
                ELSE 'previous'
            END AS period,
            SUM(quantity) AS units_sold
        FROM sales
        WHERE
            product_id = :product_id
            AND sale_timestamp >=
                CURRENT_TIMESTAMP - INTERVAL '30 days'
        GROUP BY period
    """

    data = pd.read_sql(
        query,
        engine,
        params={"product_id": product_id}
    )

    if data.empty:
        return 0.0

    recent = data.loc[
        data["period"] == "recent",
        "units_sold"
    ].sum()

    previous = data.loc[
        data["period"] == "previous",
        "units_sold"
    ].sum()

    if previous == 0:
        return 1.0 if recent > 0 else 0.0

    return float(
        (recent - previous) / previous
    )