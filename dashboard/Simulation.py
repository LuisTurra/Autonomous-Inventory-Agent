
import streamlit as st

from src.simulation.simulation_engine import SimulationEngine
from src.simulation.scenarios import SCENARIOS
from src.database.repositories import (
    clear_simulation_data,
    create_simulation_snapshot,
)


st.title("⚙️ Simulação")


# ============================================================
# INICIALIZAÇÃO
# ============================================================

if "simulation_engine" not in st.session_state:

    st.session_state.simulation_engine = SimulationEngine(
        interval=5
    )


engine = st.session_state.simulation_engine
state = engine.state


if "simulation_running" not in st.session_state:

    st.session_state.simulation_running = False


if "simulation_result" not in st.session_state:

    st.session_state.simulation_result = None


# ============================================================
# CONTROLES
# ============================================================

st.subheader("🎮 Controles")

col1, col2, col3, col4 = st.columns(4)


# ============================================================
# INICIAR
# ============================================================

with col1:

    if st.button(
        "▶️ Iniciar",
        use_container_width=True,
    ):

        create_simulation_snapshot()

        state.start()

        st.session_state.simulation_running = True

        st.rerun()


# ============================================================
# PAUSAR
# ============================================================

with col2:

    if st.button(
        "⏸️ Pausar",
        use_container_width=True,
    ):

        state.stop()

        st.session_state.simulation_running = False

        st.rerun()


# ============================================================
# REINICIAR
# ============================================================

with col3:

    if st.button(
        "↻ Reiniciar",
        use_container_width=True,
    ):

        state.reset()

        st.session_state.simulation_running = False

        st.session_state.simulation_result = None

        st.rerun()


# ============================================================
# VELOCIDADE
# ============================================================

with col4:

    speed = st.selectbox(
        "Velocidade",
        state.ALLOWED_SPEEDS,
        index=state.ALLOWED_SPEEDS.index(
            state.speed
        ),
        format_func=lambda x: (
            f"{x}x — {x}h simuladas/ciclo"
        ),
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
    ),
)

if scenario != state.scenario:

    state.set_scenario(scenario)


# ============================================================
# FRAGMENTO DA SIMULAÇÃO
# ============================================================
#
# IMPORTANTE:
#
# Tudo que muda durante a simulação está dentro deste
# fragmento.
#
# Isso inclui:
#
# - execução do ciclo
# - status
# - eventos
# - vendas
# - compras
# - entregas
# - tempo simulado
# - último ciclo
#
# O fragmento é atualizado automaticamente a cada segundo.
#
# ============================================================

@st.fragment(run_every=1)
def simulation_view():

    # ========================================================
    # EXECUTAR CICLO
    # ========================================================

    if st.session_state.simulation_running:

        try:

            result = engine.process_cycle()

            st.session_state.simulation_result = result

        except Exception as error:

            state.stop()

            st.session_state.simulation_running = False

            st.session_state.simulation_result = None

            st.error(
                f"❌ Erro na simulação: {error}"
            )

            return


    # ========================================================
    # STATUS
    # ========================================================

    st.divider()

    st.subheader("📡 Estado da Simulação")

    status = state.get_status()


    if status["running"]:

        st.success(
            "🟢 Simulação em execução"
        )

    else:

        st.warning(
            "🔴 Simulação pausada"
        )


    # ========================================================
    # MÉTRICAS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Eventos",
            status["events_processed"],
        )


    with col2:

        st.metric(
            "Vendas",
            status["sales_processed"],
        )


    with col3:

        st.metric(
            "Compras",
            status["purchases_processed"],
        )


    with col4:

        st.metric(
            "Entregas",
            status["deliveries_processed"],
        )


    # ========================================================
    # INFORMAÇÕES DA SIMULAÇÃO
    # ========================================================

    st.divider()

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Cenário",
            status["scenario"],
        )


    with col2:

        st.metric(
            "Velocidade",
            f'{status["speed"]}x',
        )


    with col3:

        simulated_time = status["simulated_time"]

        st.metric(
            "Tempo simulado",
            simulated_time.strftime(
                "%d/%m/%Y %H:%M"
            ),
        )


    # ========================================================
    # RESULTADO DO ÚLTIMO CICLO
    # ========================================================

    result = st.session_state.simulation_result


    if result:

        st.divider()

        st.subheader("📊 Último ciclo")


        sales = result.get(
            "sales",
            [],
        )


        deliveries = result.get(
            "deliveries",
            [],
        )


        decisions = result.get(
            "decisions",
            [],
        )


        purchases = result.get(
            "purchases",
            [],
        )


        # ----------------------------------------------------
        # MÉTRICAS DO CICLO
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Vendas",
                "Sim" if sales else "Não",
            )


        with col2:

            st.metric(
                "Entregas",
                len(deliveries),
            )


        with col3:

            st.metric(
                "Decisões",
                len(decisions),
            )


        with col4:

            st.metric(
                "Compras",
                len(purchases),
            )


        # ----------------------------------------------------
        # DETALHES
        # ----------------------------------------------------

        if sales:

            st.success(
                f"🛒 Venda gerada: {sales}"
            )


        if deliveries:

            st.info(
                f"📦 {len(deliveries)} "
                "entrega(s) processada(s)."
            )


        if decisions:

            st.warning(
                f"🤖 {len(decisions)} "
                "decisão(ões) de reposição."
            )


        if purchases:

            st.success(
                f"🚚 {len(purchases)} "
                "compra(s) criada(s)."
            )


# ============================================================
# EXECUTAR INTERFACE DINÂMICA
# ============================================================

simulation_view()


# ============================================================
# DADOS DA SIMULAÇÃO
# ============================================================

st.divider()

st.subheader("🗑️ Dados da simulação")


if st.button(
    "🗑️ Limpar dados da simulação",
    use_container_width=True,
):

    state.stop()

    clear_simulation_data()

    state.reset()

    st.session_state.simulation_running = False

    st.session_state.simulation_result = None

    st.success(
        "Dados da simulação removidos."
    )

    st.rerun()

