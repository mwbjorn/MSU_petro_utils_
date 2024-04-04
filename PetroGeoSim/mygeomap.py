from collections import defaultdict

from PetroGeoSim.models import Model
from numpy import ndarray, nan_to_num, where, isnan

def send_mygeomap(model: Model) -> dict[str, dict]:
    initial_result = model.get_all_properties("values", include=("inputs", "results"))
    initial_stats = model.get_all_properties("stats", include=("inputs", "results"))

    # Converts all NumPy arrays to lists (to enable serialization)
    final_result = defaultdict(dict)
    for reg, props in initial_result.items():
        # reg имя региона, props значение (словарь)
        # {'Площадь': array([]), ....  's * hef * poro * (1-sw) * (1/fvf)': array([]),
        # 'values_probability': []})
        vals_probability = []
        value = props.get('values_probability')
        if value is not 0 and value is not None and (isinstance(value, ndarray) and len(value) > 0):
            vals_probability = nan_to_num(value, nan=0.)
            vals_probability[vals_probability < 1e-5] = 0
        for prop, vals in props.items():
            if prop != "values_probability" and prop != "probability_stats":
                final_result[reg][prop] = {
                    "values": vals.tolist(),
                    "stats": {
                        "P90": (initial_stats[reg][prop]["P10"], 90),
                        "P50": (initial_stats[reg][prop]["P50"], 50),
                        "P10": (initial_stats[reg][prop]["P90"], 10),
                    },
                }
        final_result[reg]["result_probability"] = {
            "values": vals_probability.tolist(),
             "stats": {
                    "P90": (initial_stats[reg]["probability_stats"]["P10"], 90),
                    "P50": (initial_stats[reg]["probability_stats"]["P50"], 50),
                    "P10": (initial_stats[reg]["probability_stats"]["P90"], 10),
                },
        }


    return dict(final_result)


def receive_mygeomap(setup_config: dict[str, dict]) -> "Model":
    if "config" in setup_config:
        setup_config["regions"] = setup_config.pop("config")

    return Model.deserialize(setup_config)