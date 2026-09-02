import threading
import time

from src.simulation.simulation_engine import SimulationEngine


class SimulationWorker:
    """
    Worker global da simulação.

    A thread permanece ativa enquanto o processo do Streamlit estiver ativo.
    A página do Streamlit apenas controla e consulta o worker.
    """

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        self.engine = SimulationEngine(interval=5)
        self.state = self.engine.state

        self._thread = None
        self._thread_lock = threading.Lock()
        self._cycle_lock = threading.Lock()

        self._last_result = None
        self._error = None

    # ============================================================
    # THREAD
    # ============================================================

    def ensure_running(self):
        """
        Garante que exista uma única thread de execução.
        """

        with self._thread_lock:

            if self._thread is not None and self._thread.is_alive():
                return

            self._thread = threading.Thread(
                target=self._run,
                name="simulation-worker",
                daemon=True
            )

            self._thread.start()

    def _run(self):
        """
        Loop da simulação.

        IMPORTANTE:
        Esta função não depende da renderização do Streamlit.
        """

        while True:

            try:

                if self.state.running:

                    with self._cycle_lock:

                        result = self.engine.process_cycle()

                        self._last_result = result
                        self._error = None

                    time.sleep(
    max(
        0.1,
        self.engine.interval / max(self.state.speed, 1)
    )
)

                else:

                    # Worker permanece vivo, mas não executa ciclos
                    time.sleep(0.2)

            except Exception as error:

                self._error = error
                self.state.stop()

                time.sleep(1)

    # ============================================================
    # CONTROLE
    # ============================================================

    def start(self):

        self.ensure_running()

        self.state.start()

    def stop(self):

        self.state.stop()

    def reset(self):

        self.state.stop()

        with self._cycle_lock:
            self.state.reset()
            self._last_result = None
            self._error = None

    # ============================================================
    # CONSULTA
    # ============================================================

    def get_status(self):

        return self.state.get_status()

    def get_last_result(self):

        return self._last_result

    def get_error(self):

        return self._error


# ============================================================
# WORKER GLOBAL
# ============================================================

simulation_worker = SimulationWorker()