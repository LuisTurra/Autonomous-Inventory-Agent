import pandas as pd
from sklearn.linear_model import LinearRegression

from src.database.connection import engine


def forecast_product_demand(
    product_id,
    forecast_days=7,
    history_days=30
):

    query = """
        SELECT
            DATE(sale_timestamp) AS sale_date,
            SUM(quantity) AS units_sold
        FROM sales
        WHERE
            product_id = :product_id
            AND sale_timestamp >=
                CURRENT_TIMESTAMP -
                (:history_days * INTERVAL '1 day')
        GROUP BY DATE(sale_timestamp)
        ORDER BY sale_date
    """

    data = pd.read_sql(
        query,
        engine,
        params={
            "product_id": product_id,
            "history_days": history_days
        }
    )

    if len(data) < 3:
        return {
            "product_id": product_id,
            "forecast_days": forecast_days,
            "predicted_daily_demand": 0.0,
            "predicted_total_demand": 0.0
        }

    data["day"] = range(len(data))

    X = data[["day"]]
    y = data["units_sold"]

    model = LinearRegression()

    model.fit(X, y)

    future_days = pd.DataFrame({
        "day": range(
            len(data),
            len(data) + forecast_days
        )
    })

    predictions = model.predict(
        future_days
    )

    predictions = predictions.clip(
        min=0
    )

    total_demand = predictions.sum()

    daily_demand = (
        total_demand / forecast_days
    )

    return {
        "product_id": product_id,
        "forecast_days": forecast_days,
        "predicted_daily_demand": float(
            daily_demand
        ),
        "predicted_total_demand": float(
            total_demand
        )
    }