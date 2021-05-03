import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.lines import Line2D

from code.comparisonpy import RESULTS_DIR

parameters = {
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "axes.labelsize": 14,
    "axes.labelweight": "bold",
}
plt.rcParams.update(parameters)


def visualize_fba_timings():
    # [1] visualize running time for models
    simulators = [
        "sbscl",
        # "cameo",
        "cobrapy"
    ]
    dfs = []
    for simulator in simulators:
        df = pd.read_csv(RESULTS_DIR / "fba" / f"bigg_{simulator}.tsv", sep="\t")
        df["simulator"] = simulator
        df["total_time"] = df["load_time"] + df["simulate_time"]
        dfs.append(df)

    # concatenate all the timings
    df_data = pd.concat(dfs)
    df_data.sort_values(inplace=True, by=['model'])
    visualize_timings(df_data, dataset="fba")


def visualize_ode_timings():
    simulators = [
        "sbscl",
        "roadrunner",
        # "copasi",
    ]
    dfs = []
    for simulator in simulators:
        df = pd.read_csv(RESULTS_DIR / "ode" / f"biomodels_{simulator}.tsv", sep="\t")
        df["simulator"] = simulator
        df["total_time"] = df["load_time"] + df["simulate_time"]
        dfs.append(df)

    # concatenate all the timings
    df_data = pd.concat(dfs)
    df_data.sort_values(inplace=True, by=['model'])
    visualize_timings(df_data, dataset="ode")


def visualize_timings(df: pd.DataFrame, dataset="fba"):
    """Visualizes the timings comparison."""

    colors = {
        "sbscl": "tab:blue",
        "cobrapy": "tab:orange",
        "cameo": "tab:red",
        "roadrunner": "tab:red",
        "copasi": "tab:green",
    }
    labels = {
        "sbscl": "SBSCL-v1.2",
        "cobrapy": "cobrapy-v0.21.0",
        "cameo": "cameo-v0.13.0",
        "copasi": "COPASI-v4.30.240",
        "roadrunner": "roadrunner-2.0.5",
    }
    simulators = df.simulator.unique()

    for time_key in ["load_time", "simulate_time", "total_time"]:
        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 20), dpi=150)
        # ensure labels are plotted
        fig.subplots_adjust(left=0.3)
        for simulator in simulators:
            df_sim = df[df.simulator == simulator]

            sns.boxplot(
                y="model",
                x=time_key,
                orient="h",
                ax=ax,
                data=df_sim,
                color=colors[simulator],
                saturation=1.0,
                boxprops={'color': colors[simulator]},
                whis=5.0
            )

        ax.set_xscale("log")
        ax.set_xlabel(f"{time_key} [s]")
        ax.set_title(f"{dataset.upper()} {time_key.replace('_', ' ')}")

        print(simulators)
        legend_lines = [Line2D([0], [0], color=colors[sim], marker="s", linestyle="") for
                        sim in simulators]
        sim_labels = [labels[sim] for sim in simulators]

        ax.legend(legend_lines, sim_labels,
                  bbox_to_anchor=(0, 1, 1, 0), loc="lower left")
        # ax.grid()

        plt.savefig(RESULTS_DIR / dataset / f"{time_key}.svg")
        plt.show()


if __name__ == "__main__":
    visualize_fba_timings()
    visualize_ode_timings()
