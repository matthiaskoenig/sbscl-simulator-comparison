"""
Script for running FBA on all BiGG models.
"""
import os
from pathlib import Path
from typing import List

import cobra
import numpy as np
import pandas as pd
from cobra.io.sbml import read_sbml_model
from cameo import fba
from cobra.util.solver import linear_reaction_coefficients


from code.comparisonpy import N_REPEAT, RESULTS_DIR, BIGG_MODEL_PATHS
import time


def optimize_models_cobrapy(model_paths: List[Path]) -> pd.DataFrame:
    """FBA optimization for all given models."""
    results = []
    n_models = len(model_paths)
    for k, path in enumerate(model_paths):
        # load model
        start_time = time.time()
        model = read_sbml_model(str(path))
        load_time = time.time() - start_time  # [s]

        # run optimization
        start_time = time.time()
        solution = model.optimize()
        simulate_time = time.time() - start_time  # [s]

        objective_value = solution.objective_value
        filename = path.name
        model = filename.split(".")[0]
        res = (model, objective_value, load_time, simulate_time)
        results.append(res)

        print("[{}/{}]".format(k, n_models), res)

    return pd.DataFrame(data=results, columns=("model", "objective_value", "load_time", "simulate_time"))


def optimize_models_cameo(model_paths: List[Path]) -> pd.DataFrame:
    """FBA optimization for all given models."""
    results = []
    n_models = len(model_paths)
    for k, path in enumerate(model_paths):
        # load model
        start_time = time.time()
        model = read_sbml_model(str(path))
        load_time = time.time() - start_time  # [s]

        # run optimization
        start_time = time.time()
        result = fba(model)
        simulate_time = time.time() - start_time  # [s]
        objective_value = result.objective_value
        filename = path.name
        model = filename.split(".")[0]
        res = (model, objective_value, load_time, simulate_time)
        results.append(res)

        print("[{}/{}]".format(k, n_models), res)

    return pd.DataFrame(data=results, columns=("model", "objective_value", "load_time", "simulate_time"))


def optimize_models(n_repeat: int=N_REPEAT):
    """Optimize the models repeatidly."""
    model_paths = BIGG_MODEL_PATHS
    print("model_paths", model_paths)
    cobrapy_path = RESULTS_DIR / "fba" / "bigg_cobrapy.tsv"
    cameo_path = RESULTS_DIR / "fba" / "bigg_cameo.tsv"

    dfs_cobrapy = []
    dfs_cameo = []
    for k in range(n_repeat):
        df_cobrapy = optimize_models_cobrapy(model_paths)
        df_cameo = optimize_models_cameo(model_paths)
        for df in df_cobrapy, df_cameo:
            df["repeat"] = k + 1
        dfs_cobrapy.append(df_cobrapy)
        dfs_cameo.append(df_cameo)

    df_cobrapy = pd.concat(dfs_cobrapy)
    df_cameo = pd.concat(dfs_cameo)
    for df in df_cobrapy, df_cameo:
        df.sort_values(by=["model", "repeat"], inplace=True)

    # save dfs
    # cobrapy_path.parent.mkdir(parents=True, exist_ok=True)
    # cameo_path.parent.mkdir(parents=True, exist_ok=True)
    df_cobrapy.to_csv(cobrapy_path, sep="\t", index=False)
    df_cameo.to_csv(cameo_path, sep="\t", index=False)


if __name__ == "__main__":
    optimize_models()
