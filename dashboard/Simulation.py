import streamlit as st

from src.simulation.scenarios import SCENARIOS
from src.database.repositories import clear_simulation_data
from src.database.demo_loader import load_demo
# ============================================================
# CONFIGURAÇÃO DO AMBIENTE
# ============================================================

try:
    APP_MODE = st.secrets["APP_MODE"]
except Exception:
    APP_MODE = "desktop"

IS_CLOUD = APP_MODE == "cloud"

st.title("⚙️ Simulação")


# ============================================================
# MODO CLOUD — DEMO ESTÁTICO
# ============================================================

if IS_CLOUD:

    st.info(
        "☁️ **Demo Mode** — esta versão utiliza um dataset "
        "pré-gerado para demonstrar o funcionamento do agente."
    )

    # --------------------------------------------------------
    # CONTROLES
    # --------------------------------------------------------

    st.subheader("🎮 Simulação")

    st.warning(
        "A simulação contínua está desativada no Streamlit Cloud. "
        "O ambiente utiliza dados simulados pré-gerados."
    )

    # --------------------------------------------------------
    # ESTADO ATUAL DO BANCO
    # --------------------------------------------------------

    st.divider()

    st.subheader("📡 Estado da Simulação")

    from sqlalchemy import text
    from src.database.connection import engine

    summary = {}

    with engine.connect() as connection:

        summary["sales"] = connection.execute(text("""
                SELECT COUNT(*)
                FROM sales
                WHERE is_simulated = TRUE
            """)).scalar()

        summary["purchases"] = connection.execute(text("""
                SELECT COUNT(*)
                FROM purchases
                WHERE is_simulated = TRUE
            """)).scalar()

        summary["events"] = connection.execute(text("""
                SELECT COUNT(*)
                FROM events
                WHERE is_simulated = TRUE
            """)).scalar()

        summary["decisions"] = connection.execute(text("""
                SELECT COUNT(*)
                FROM decisions
                WHERE is_simulated = TRUE
            """)).scalar()

        simulated_time = connection.execute(text("""
                SELECT MAX(event_timestamp)
                FROM events
                WHERE is_simulated = TRUE
            """)).scalar()

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Eventos", summary["events"])

    col2.metric("Vendas", summary["sales"])

    col3.metric("Compras", summary["purchases"])

    col4.metric("Decisões", summary["decisions"])

    # --------------------------------------------------------
    # INFORMAÇÕES
    # --------------------------------------------------------

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric("Modo", "Demo")

    with col2:

        st.metric("Status", "Dados pré-gerados")

    with col3:

        if simulated_time:

            st.metric("Tempo simulado", simulated_time.strftime("%d/%m/%Y %H:%M"))

        else:

            st.metric("Tempo simulado", "—")

    # --------------------------------------------------------
    # ÚLTIMOS EVENTOS
    # --------------------------------------------------------

    st.divider()

    st.subheader("⚡ Últimos eventos")

    import pandas as pd

    events = pd.read_sql(
        """
        SELECT
            event_type,
            product_id,
            quantity,
            event_timestamp
        FROM events
        WHERE is_simulated = TRUE
        ORDER BY event_timestamp DESC
        LIMIT 15
        """,
        engine,
    )

    if events.empty:

        st.info("Nenhum evento simulado encontrado.")

    else:

        st.dataframe(events, use_container_width=True, hide_index=True)

    # --------------------------------------------------------
    # DADOS DA SIMULAÇÃO
    # --------------------------------------------------------

    st.divider()

    

    st.subheader("🗑️ Dados da simulação")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "🗑️ Limpar dados da simulação",
        width="stretch"
    ):

        clear_simulation_data()

        st.success(
            "Dados da simulação removidos."
        )

        st.rerun()


with col2:

    if st.button(
        "🔄 Restaurar Demo Dataset",
        width="stretch"
    ):

        load_demo()

        st.success(
            "Demo Dataset restaurado."
        )

        st.rerun()

    # --------------------------------------------------------
    # ENCERRA O MODO CLOUD
    # --------------------------------------------------------

    st.stop()


# ============================================================
# MODO DESKTOP — SIMULAÇÃO REAL
# ============================================================

from src.simulation.simulation_worker import simulation_worker
from src.database.repositories import create_simulation_snapshot

# ============================================================
# WORKER
# ============================================================

worker = simulation_worker

# Garante que a thread exista.
# Isso NÃO inicia a simulação.
worker.ensure_running()

state = worker.state


# ============================================================
# CONTROLES
# ============================================================

st.subheader("🎮 Controles")

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# INICIAR
# ------------------------------------------------------------

with col1:

    if st.button("▶️ Iniciar", width="stretch"):

        create_simulation_snapshot()

        worker.start()

        st.rerun()


# ------------------------------------------------------------
# PAUSAR
# ------------------------------------------------------------

with col2:

    if st.button("⏸️ Pausar", width="stretch"):

        worker.stop()

        st.rerun()


# ------------------------------------------------------------
# REINICIAR
# ------------------------------------------------------------

with col3:

    if st.button("↻ Reiniciar", width="stretch"):

        worker.reset()

        st.rerun()


# ------------------------------------------------------------
# VELOCIDADE
# ------------------------------------------------------------

with col4:

    speed = st.selectbox(
        "Velocidade",
        state.ALLOWED_SPEEDS,
        index=state.ALLOWED_SPEEDS.index(state.speed),
        format_func=lambda x: (f"{x}x — {x}h simuladas/ciclo"),
    )

    if speed != state.speed:

        state.set_speed(speed)


# ============================================================
# CENÁRIO
# ============================================================

st.divider()

st.subheader("🎯 Cenário")

scenario = st.selectbox(
    "Escolha o cenário",
    list(SCENARIOS.keys()),
    index=list(SCENARIOS.keys()).index(state.scenario),
)

if scenario != state.scenario:

    state.set_scenario(scenario)


# ============================================================
# STATUS
# ============================================================

st.divider()

st.subheader("📡 Estado da Simulação")

status = worker.get_status()


if status["running"]:

    st.success("🟢 Simulação em execução")

else:

    st.warning("🔴 Simulação pausada")


# ============================================================
# MÉTRICAS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Eventos", status["events_processed"])

col2.metric("Vendas", status["sales_processed"])

col3.metric("Compras", status["purchases_processed"])

col4.metric("Entregas", status["deliveries_processed"])


# ============================================================
# INFORMAÇÕES
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)


with col1:

    st.metric("Cenário", status["scenario"])


with col2:

    st.metric("Velocidade", f'{status["speed"]}x')


with col3:

    simulated_time = status["simulated_time"]

    st.metric("Tempo simulado", simulated_time.strftime("%d/%m/%Y %H:%M"))


# ============================================================
# ERRO DO WORKER
# ============================================================

error = worker.get_error()

if error:

    st.error(f"❌ Erro na simulação: {error}")


# ============================================================
# ÚLTIMO CICLO
# ============================================================

result = worker.get_last_result()


if result:

    st.divider()

    st.subheader("📊 Último ciclo")

    sales = result.get("sales", [])

    deliveries = result.get("deliveries", [])

    decisions = result.get("decisions", [])

    purchases = result.get("purchases", [])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Vendas no ciclo", len(sales))

    col2.metric("Entregas no ciclo", len(deliveries))

    col3.metric("Decisões", len(decisions))

    col4.metric("Compras", len(purchases))


# ============================================================
# DADOS DA SIMULAÇÃO
# ============================================================

st.divider()

st.subheader("🗑️ Dados da simulação")


if st.button("🗑️ Limpar dados da simulação", width="stretch"):

    worker.reset()

    clear_simulation_data()

    st.success("Dados da simulação removidos.")

    st.rerun()


# ============================================================
# ATUALIZAÇÃO DA INTERFACE
# ============================================================

if status["running"]:

    import time

    time.sleep(1)

    st.rerun()
