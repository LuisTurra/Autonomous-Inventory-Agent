from datetime import datetime
import streamlit as st

from src.database.repositories import clear_simulation_data, create_simulation_snapshot
from src.simulation.scenarios import SCENARIOS
from src.simulation.simulation_engine import SimulationEngine

st.title("⚙️ Simulação")

# ============================================================
# INICIALIZAÇÃO
# ============================================================

if "simulation_engine" not in st.session_state:
    st.session_state.simulation_engine = SimulationEngine(interval=5)

engine = st.session_state.simulation_engine
state = engine.state

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

# ============================================================
# CONTROLES & EVENTOS GLOBAL
# ============================================================

st.subheader("🎮 Controles")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Iniciar", use_container_width=True, disabled=st.session_state.simulation_running):
        create_simulation_snapshot()
        state.start()
        st.session_state.simulation_running = True
        st.rerun()

with col2:
    if st.button("⏸️ Pausar", use_container_width=True, disabled=not st.session_state.simulation_running):
        state.stop()
        st.session_state.simulation_running = False
        st.rerun()

with col3:
    if st.button("↻ Reiniciar", use_container_width=True):
        state.reset()
        st.session_state.simulation_running = False
        st.session_state.simulation_result = None
        st.rerun()

with col4:
    speed = st.selectbox(
        "Velocidade",
        state.ALLOWED_SPEEDS,
        index=state.ALLOWED_SPEEDS.index(state.speed),
        format_func=lambda x: f"{x}x — {x}h simuladas/ciclo",
    )
    state.set_speed(speed)

st.divider()
st.subheader("🎯 Cenário")

scenario = st.selectbox(
    "Escolha o cenário",
    list(SCENARIOS.keys()),
    index=list(SCENARIOS.keys()).index(state.scenario),
)
state.set_scenario(scenario)

st.divider()

# ============================================================
# CICLO DA SIMULAÇÃO (ISOLADO COM FRAGMENT)
# ============================================================

# Define dynamic interval based on speed: interval / speed (minimum 0.5s for stability)
refresh_interval = max(0.5, engine.interval / max(state.speed, 1))

@st.fragment(run_every=refresh_interval if st.session_state.simulation_running else None)
def render_simulation_loop():
    # Process cycle inside the fragment if running
    if st.session_state.simulation_running:
        try:
            result = engine.process_cycle()
            st.session_state.simulation_result = result
        except Exception as error:
            state.stop()
            st.session_state.simulation_running = False
            st.error(f"❌ Erro na simulação: {error}")
            return

    status = state.get_status()

    # 1. Status Indicator
    st.subheader("📡 Estado da Simulação")
    if status["running"]:
        st.success("🟢 Simulação em execução")
    else:
        st.warning("🔴 Simulação pausada")

    # 2. Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eventos", status["events_processed"])
    m2.metric("Vendas", status["sales_processed"])
    m3.metric("Compras", status["purchases_processed"])
    m4.metric("Entregas", status["deliveries_processed"])

    # 3. Simulation Info
    i1, i2, i3 = st.columns(3)
    i1.metric("Cenário", status["scenario"])
    i2.metric("Velocidade", f'{status["speed"]}x')
    
    simulated_time = status["simulated_time"]
    time_str = simulated_time.strftime("%d/%m/%Y %H:%M") if simulated_time else "N/A"
    i3.metric("Tempo simulado", time_str)

    # 4. Last Cycle Results
    result = st.session_state.simulation_result
    if result:
        st.divider()
        st.subheader("📊 Último ciclo")

        sales = result.get("sales")
        deliveries = result.get("deliveries", [])
        decisions = result.get("decisions", [])
        purchases = result.get("purchases", [])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Vendas", "Sim" if sales else "Não")
        c2.metric("Entregas", len(deliveries))
        c3.metric("Decisões", len(decisions))
        c4.metric("Compras", len(purchases))

        if sales:
            st.success(f"🛒 Venda gerada: {sales}")
        if deliveries:
            st.info(f"📦 {len(deliveries)} entrega(s) processada(s).")
        if decisions:
            st.warning(f"🤖 {len(decisions)} decisão(ões) de reposição.")
        if purchases:
            st.success(f"🚚 {len(purchases)} compra(s) criada(s).")

# Render isolated simulation component
render_simulation_loop()

# ============================================================
# LIMPEZA DE DADOS
# ============================================================

st.divider()
st.subheader("🗑️ Dados da simulação")

if st.button("🗑️ Limpar dados da simulação", use_container_width=True):
    state.stop()
    clear_simulation_data()
    state.reset()
    st.session_state.simulation_running = False
    st.session_state.simulation_result = None
    st.success("Dados da simulação removidos.")
    st.rerun()