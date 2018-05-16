
"""
Script for running FBA on all BiGG models.
"""
import os
import cobra
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


if __name__ == "__main__":
    results_path = os.path.join(DIRECTORY, "bigg-fba-{}.tsv".format(BIGG_VERSION))
    optimize_models(model_dir=BIGG_MODELS_PATH,
                    results_path=results_path)


