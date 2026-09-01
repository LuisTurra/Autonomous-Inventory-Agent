SCENARIOS = {
    "Normal": {
        "sales_multiplier": 1.0,
        "supplier_delay": 0,
    },
    "Alta demanda": {
        "sales_multiplier": 2.0,
        "supplier_delay": 0,
    },
    "Baixa demanda": {
        "sales_multiplier": 0.5,
        "supplier_delay": 0,
    },
    "Demand Shock": {
        "sales_multiplier": 3.0,
        "supplier_delay": 0,
    },
    "Supplier Delay": {
        "sales_multiplier": 1.0,
        "supplier_delay": 3,
    },
    "Ruptura de estoque": {
        "sales_multiplier": 4.0,
        "supplier_delay": 5,
    },
}


def get_scenario(name):

    if name not in SCENARIOS:

        raise ValueError(f"Cenário desconhecido: {name}")

    return SCENARIOS[name].copy()


def get_scenarios():

    return list(SCENARIOS.keys())
