import json

import pandas as pd
import streamlit as st

from src.database.connection import engine


st.title("📄 Relatórios")

st.caption(
    "Relatórios operacionais e históricos do Autonomous Inventory Agent."
)


def load_data():

    inventory = pd.read_sql(
        """
        SELECT
            COUNT(*) AS products,
            COALESCE(SUM(quantity), 0) AS total_stock,
            COALESCE(
                SUM(
                    CASE
                        WHEN quantity <= reorder_point
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS low_stock,
            COALESCE(
                SUM(
                    CASE
                        WHEN quantity <= 0
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS out_of_stock
        FROM inventory
        """,
        engine
    )

    sales = pd.read_sql(
        """
        SELECT
            COALESCE(SUM(quantity), 0) AS units_sold,
            COALESCE(
                SUM(quantity * unit_price),
                0
            ) AS revenue
        FROM sales
        """,
        engine
    )

    purchases = pd.read_sql(
        """
        SELECT
            COUNT(*) AS orders,
            COALESCE(SUM(quantity), 0) AS units
        FROM purchases
        """,
        engine
    )

    events = pd.read_sql(
        """
        SELECT
            event_type,
            COUNT(*) AS total
        FROM events
        GROUP BY event_type
        ORDER BY total DESC
        """,
        engine
    )

    decisions = pd.read_sql(
        """
        SELECT
            agent_name,
            COUNT(*) AS total
        FROM decisions
        GROUP BY agent_name
        ORDER BY total DESC
        """,
        engine
    )

    return (
        inventory,
        sales,
        purchases,
        events,
        decisions
    )


(
    inventory,
    sales,
    purchases,
    events,
    decisions
) = load_data()


if inventory.empty:

    st.info(
        "Ainda não existem dados suficientes "
        "para gerar o relatório."
    )

else:

    inventory_row = inventory.iloc[0]
    sales_row = sales.iloc[0]
    purchases_row = purchases.iloc[0]

    report = {
        "inventory": {
            "products": int(
                inventory_row["products"]
            ),
            "total_stock": int(
                inventory_row["total_stock"]
            ),
            "low_stock": int(
                inventory_row["low_stock"]
            ),
            "out_of_stock": int(
                inventory_row["out_of_stock"]
            )
        },
        "sales": {
            "units_sold": int(
                sales_row["units_sold"]
            ),
            "revenue": float(
                sales_row["revenue"]
            )
        },
        "purchases": {
            "orders": int(
                purchases_row["orders"]
            ),
            "units": int(
                purchases_row["units"]
            )
        },
        "events": events.to_dict(
            orient="records"
        ),
        "agent_decisions": decisions.to_dict(
            orient="records"
        )
    }

    st.subheader(
        "📊 Resumo executivo"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Produtos",
        f"{report['inventory']['products']:,}"
    )

    col2.metric(
        "Estoque",
        f"{report['inventory']['total_stock']:,}"
    )

    col3.metric(
        "Vendas",
        f"{report['sales']['units_sold']:,}"
    )

    col4.metric(
        "Receita",
        f"R$ {report['sales']['revenue']:,.2f}"
    )

    st.divider()

    st.subheader(
        "⚠️ Alertas"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Estoque baixo",
        f"{report['inventory']['low_stock']:,}"
    )

    col2.metric(
        "Sem estoque",
        f"{report['inventory']['out_of_stock']:,}"
    )

    st.divider()

    st.subheader(
        "🤖 Atividade dos agentes"
    )

    if decisions.empty:

        st.info(
            "Nenhuma decisão registrada."
        )

    else:

        st.dataframe(
            decisions,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader(
        "📡 Eventos"
    )

    if events.empty:

        st.info(
            "Nenhum evento registrado."
        )

    else:

        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader(
        "⬇️ Exportar relatório"
    )

    json_data = json.dumps(
        report,
        ensure_ascii=False,
        indent=2
    )

    st.download_button(
        label="Baixar JSON",
        data=json_data,
        file_name="inventory_report.json",
        mime="application/json"
    )