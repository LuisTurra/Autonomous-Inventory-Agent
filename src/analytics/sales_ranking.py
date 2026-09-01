import pandas as pd

from src.database.connection import engine


def get_sales_ranking(days=None):

    date_filter = ""

    if days is not None:
        date_filter = f"""
            WHERE sale_timestamp >=
                CURRENT_TIMESTAMP - INTERVAL '{int(days)} days'
        """

    query = f"""
        SELECT
            s.product_id,
            p.product_category_name,
            SUM(s.quantity) AS units_sold,
            SUM(s.quantity * s.unit_price) AS revenue,
            AVG(s.unit_price) AS average_price
        FROM sales s
        JOIN products p
            ON s.product_id = p.product_id
        {date_filter}
        GROUP BY
            s.product_id,
            p.product_category_name
        ORDER BY
            units_sold DESC
    """

    return pd.read_sql(
        query,
        engine
    )


def top_selling_products(limit=10, days=None):

    ranking = get_sales_ranking(days)

    return ranking.head(limit)


def lowest_selling_products(limit=10, days=None):

    ranking = get_sales_ranking(days)

    return ranking.sort_values(
        "units_sold"
    ).head(limit)


def highest_revenue_products(limit=10, days=None):

    ranking = get_sales_ranking(days)

    return ranking.sort_values(
        "revenue",
        ascending=False
    ).head(limit)