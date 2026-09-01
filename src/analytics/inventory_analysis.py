import pandas as pd

from src.database.connection import engine


def get_inventory_analysis():

    query = """
        SELECT
            i.product_id,
            p.product_category_name,
            i.quantity,
            i.reserved_quantity,
            i.minimum_stock,
            i.reorder_point,
            i.reorder_quantity,

            COALESCE(
                SUM(s.quantity),
                0
            ) AS total_units_sold

        FROM inventory i

        JOIN products p
            ON i.product_id = p.product_id

        LEFT JOIN sales s
            ON i.product_id = s.product_id

        GROUP BY
            i.product_id,
            p.product_category_name,
            i.quantity,
            i.reserved_quantity,
            i.minimum_stock,
            i.reorder_point,
            i.reorder_quantity
    """

    data = pd.read_sql(
        query,
        engine
    )

    if data.empty:
        return data

    data["sales_per_day"] = (
        data["total_units_sold"] / 30
    )

    data["days_of_inventory"] = (
        data["quantity"] /
        data["sales_per_day"].replace(0, pd.NA)
    )

    data["status"] = "HEALTHY"

    data.loc[
        data["quantity"] <= data["reorder_point"],
        "status"
    ] = "LOW_STOCK"

    data.loc[
        data["quantity"] <= data["minimum_stock"],
        "status"
    ] = "CRITICAL"

    data.loc[
        data["quantity"] <= 0,
        "status"
    ] = "OUT_OF_STOCK"

    return data


def get_low_stock_products():

    data = get_inventory_analysis()

    if data.empty:
        return data

    return data[
        data["quantity"] <= data["reorder_point"]
    ].sort_values(
        "days_of_inventory"
    )


def get_out_of_stock_products():

    data = get_inventory_analysis()

    if data.empty:
        return data

    return data[
        data["quantity"] <= 0
    ]


def get_fast_moving_products(limit=20):

    data = get_inventory_analysis()

    if data.empty:
        return data

    return data.sort_values(
        "sales_per_day",
        ascending=False
    ).head(limit)


def get_slow_moving_products(limit=20):

    data = get_inventory_analysis()

    if data.empty:
        return data

    return data.sort_values(
        "sales_per_day"
    ).head(limit)