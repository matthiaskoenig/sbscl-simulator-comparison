"""
Script for running FBA on all BiGG models.
"""
import os
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import roadrunner
from COPASI import CDataModel

from code.comparisonpy import N_REPEAT, RESULTS_DIR, BIOMODELS_MODEL_PATHS
from code.comparisonpy.copasi_example import run_time_course as run_copasi_time_course
from basico import load_model

import time

START = 0.0
END = 100.0
STEPS = 100
ABSOLUTE_TOLERANCE = 1E-10
RELATIVE_TOLERANCE = 1E-6


def run_models_roadrunner(model_paths: List[Path], output_dir: Path) -> pd.DataFrame:
    """ODE optimization for all given models."""
    results = []
    n_models = len(model_paths)
    for k, path in enumerate(model_paths):
        model_id = path.stem
        try:
            # load model
            start_time = time.time()
            rr: roadrunner.RoadRunner = roadrunner.RoadRunner(str(path))
            load_time = time.time() - start_time  # [s]

            model: roadrunner.ExecutableModel = rr.model
            # set tolerances
            integrator: roadrunner.Integrator = rr.integrator
            integrator.setValue("absolute_tolerance", ABSOLUTE_TOLERANCE)
            integrator.setValue("relative_tolerance", RELATIVE_TOLERANCE)

            # set selections
            rr.selections = ["time"] + model.getFloatingSpeciesIds() + model.getBoundarySpeciesIds()

            # run optimization
            start_time = time.time()
            s = rr.simulate(start=START, end=END, steps=STEPS)
            simulate_time = time.time() - start_time  # [s]

            # filter models with delay
            if model_id in ["BIOMD0000000024", "BIOMD0000000025", "BIOMD0000000034"]:
                raise RuntimeError("delays not supported")
            status = "success"
        except (RuntimeError) as err:
            print(f"ERROR in '{model_id}'", err)
            simulate_time = np.NaN
            status = "failure"

        # store result
        df = pd.DataFrame(s, columns=s.colnames)
        df.to_csv(output_dir / f"{model_id}.tsv", sep="\t",
                  index=False)
        res = (model_id, status, load_time, simulate_time)
        results.append(res)

        print("[{}/{}]".format(k, n_models), res)

    df = pd.DataFrame(data=results, columns=("model", "status", "load_time", "simulate_time"))
    return df


def run_models_copasi(model_paths: List[Path], output_dir: Path) -> pd.DataFrame:
    """ODE optimization for all given models."""
    results = []
    n_models = len(model_paths)
    for k, path in enumerate(model_paths):
        model_id = path.stem
        try:
            # load model
            start_time = time.time()
            model: CDataModel = load_model(str(path))
            load_time = time.time() - start_time  # [s]
            if model is None:
                raise RuntimeError(f"COPASI model could not be loaded: '{model_id}'")

            # run optimization
            start_time = time.time()
            df = run_copasi_time_course(
                model=model,
                start_time=START,
                duration=END-START,
                step_number=STEPS,
                a_tol=ABSOLUTE_TOLERANCE,
                r_tol=RELATIVE_TOLERANCE,
            )
            simulate_time = time.time() - start_time  # [s]
            status = "success"
        except (ValueError, RuntimeError) as err:
            print(f"ERROR in '{model_id}'", err)
            simulate_time = np.NaN
            status = "failure"

        # store result
        df.to_csv(output_dir / f"{model_id}.tsv", sep="\t", index=False)
        res = (model_id, status, load_time, simulate_time)
        results.append(res)

        print("[{}/{}]".format(k, n_models), res)

    df = pd.DataFrame(data=results, columns=("model", "status", "load_time", "simulate_time"))
    return df


def run_models(simulator: str, n_repeat: int):
    """Optimize the models repeatidly."""
    model_paths = BIOMODELS_MODEL_PATHS

    f_dict = {
        "roadrunner": run_models_roadrunner,
        "copasi": run_models_copasi,
    }

    f_run = f_dict[simulator]
    dfs = []
    for k in range(n_repeat):
        df = f_run(model_paths, output_dir=RESULTS_DIR / "ode" / simulator)
        df["repeat"] = k + 1
        dfs.append(df)

    df = pd.concat(dfs)
    df.sort_values(by=["model", "repeat"], inplace=True)
    df.to_csv(
        RESULTS_DIR / "ode" / f"biomodels_{simulator}.tsv",
        sep="\t", index=False
    )


if __name__ == "__main__":
    run_models(simulator="roadrunner", n_repeat=N_REPEAT)
    run_models(simulator="copasi", n_repeat=N_REPEAT)
