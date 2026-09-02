import time

import streamlit as st

from src.simulation.simulation_worker import simulation_worker
from src.simulation.scenarios import SCENARIOS

from src.database.repositories import (
    clear_simulation_data,
    create_simulation_snapshot
)


st.title("⚙️ Simulação")


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

    if st.button(
        "▶️ Iniciar",
        width="stretch"
    ):

        create_simulation_snapshot()

        worker.start()

        st.rerun()


# ------------------------------------------------------------
# PAUSAR
# ------------------------------------------------------------

with col2:

    if st.button(
        "⏸️ Pausar",
        width="stretch"
    ):

        worker.stop()

        st.rerun()


# ------------------------------------------------------------
# REINICIAR
# ------------------------------------------------------------

with col3:

    if st.button(
        "↻ Reiniciar",
        width="stretch"
    ):

        worker.reset()

        st.rerun()


# ------------------------------------------------------------
# VELOCIDADE
# ------------------------------------------------------------

with col4:

    speed = st.selectbox(
        "Velocidade",
        state.ALLOWED_SPEEDS,
        index=state.ALLOWED_SPEEDS.index(
            state.speed
        ),
        format_func=lambda x: (
            f"{x}x — {x}h simuladas/ciclo"
        )
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
    index=list(SCENARIOS.keys()).index(
        state.scenario
    )
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

col1.metric(
    "Eventos",
    status["events_processed"]
)

col2.metric(
    "Vendas",
    status["sales_processed"]
)

col3.metric(
    "Compras",
    status["purchases_processed"]
)

col4.metric(
    "Entregas",
    status["deliveries_processed"]
)


# ============================================================
# INFORMAÇÕES
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Cenário",
        status["scenario"]
    )


with col2:

    st.metric(
        "Velocidade",
        f'{status["speed"]}x'
    )


with col3:

    simulated_time = status["simulated_time"]

    st.metric(
        "Tempo simulado",
        simulated_time.strftime(
            "%d/%m/%Y %H:%M"
        )
    )


# ============================================================
# ERRO DO WORKER
# ============================================================

error = worker.get_error()

if error:

    st.error(
        f"❌ Erro na simulação: {error}"
    )


# ============================================================
# ÚLTIMO CICLO
# ============================================================

result = worker.get_last_result()


if result:

    st.divider()

    st.subheader("📊 Último ciclo")

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


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Vendas no ciclo",
        len(sales)
    )

    col2.metric(
        "Entregas no ciclo",
        len(deliveries)
    )

    col3.metric(
        "Decisões",
        len(decisions)
    )

    col4.metric(
        "Compras",
        len(purchases)
    )


# ============================================================
# DADOS DA SIMULAÇÃO
# ============================================================

st.divider()

st.subheader("🗑️ Dados da simulação")


if st.button(
    "🗑️ Limpar dados da simulação",
    width="stretch"
):

    worker.reset()

    clear_simulation_data()

    st.success(
        "Dados da simulação removidos."
    )

    st.rerun()


# ============================================================
# ATUALIZAÇÃO DA INTERFACE
# ============================================================

if status["running"]:

    # IMPORTANTE:
    #
    # Este sleep NÃO executa a simulação.
    #
    # Ele apenas controla a frequência com que
    # esta página atualiza os números na tela.
    #
    # A simulação está sendo executada pela thread
    # SimulationWorker.

    time.sleep(1)

    st.rerun()