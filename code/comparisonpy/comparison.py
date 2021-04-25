EPS_COMPARISON = 1E-4

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


