
"""
Script for running FBA on all BiGG models.
"""
import os
import cobra
import numpy as np
import pandas as pd
from cobra.io.sbml3 import read_sbml_model
from cobra.util.solver import linear_reaction_coefficients

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
BIGG_VERSION = "v1.5"
BIGG_MODELS_PATH = os.path.join(
    DIRECTORY,
    "models",
    BIGG_VERSION
)
EPS_COMPARISON = 1E-4


def optimize_models(model_dir, results_path):
    """ Loads all models in given path and runs FBA.
    Writes results in TSV.

    :param model_dir: Directory with models (this can be compressed).
    :param results_path: Filename of output CSV/TSV file.
    :return:
    """
    results = []

    model_paths = sorted(os.listdir(model_dir))
    n_models = len(model_paths)

    for k, fname in enumerate(model_paths):
        path = os.path.join(model_dir, fname)

        # load model
        model = read_sbml_model(path)

        # run optimization
        solution = model.optimize()
        obj_value = solution.objective_value

        # get the optimization target (all reactions in the optimization value)
        coeff_dict = linear_reaction_coefficients(model)
        # print(coeff_dict)

        target = ""
        for r, c in coeff_dict.items():
            sign = '+'
            if c < 0:
                sign = '-'
            target += "{}{} {}".format(sign, c, r.id)

        # store result
        res = (k, fname, obj_value, target)
        results.append(res)

        # progress
        print("[{}/{}]".format(k, n_models), res)

    # store results
    df = pd.DataFrame(data=results, columns=("index", "model", "objective_value", "target"))
    df.to_csv(results_path, sep="\t", index=False)


def compare_results(cobrapy_path, sbscl_path, output_path):
    """ Compare the FBA results.

    :param cobrapy_file:
    :param sbscl_file:
    :return:
    """
    df_cobra = pd.read_csv(cobrapy_path, sep="\t")
    df_cobra['mid'] = df_cobra.model.str.split('.').str[0]
    df_sbscl = pd.read_csv(sbscl_path, sep="\t")
    df_sbscl['mid'] = df_sbscl.model.str.split('.').str[0]
    df = pd.merge(left=df_cobra, right=df_sbscl, on=['mid'])
    df['identical'] = np.abs(df.objective_value_x - df.objective_value_y) < EPS_COMPARISON
    del df['target']
    del df['model_x']
    del df['model_y']
    print(df[df.identical == False])
    df.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    # simulation
    cobrapy_path = os.path.join(DIRECTORY, 'results', "bigg-fba-{}_cobrapy.tsv".format(BIGG_VERSION))
    results_path = os.path.join(DIRECTORY, 'results')
    # optimize_models(model_dir=BIGG_MODELS_PATH, results_path=results_path)

    # comparison of results
    sbscl_path = os.path.join(DIRECTORY, 'results', "bigg-fba-{}_sbscl.tsv".format(BIGG_VERSION))
    comparison_path = os.path.join(DIRECTORY, 'results', "bigg-fba-{}_comparison.tsv".format(BIGG_VERSION))
    compare_results(cobrapy_path=cobrapy_path, sbscl_path=sbscl_path, output_path=comparison_path)




