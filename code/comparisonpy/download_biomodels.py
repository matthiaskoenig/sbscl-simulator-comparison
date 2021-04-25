import logging
from pathlib import Path

import requests
from typing import List
import math

from code.comparisonpy import MODELS_DIR

logger = logging.getLogger(__name__)


def query_curated_biomodels() -> List[str]:
    """Query curated biomodels.

    :return List of biomodel identifiers
    """
    # query number of matches
    url = "https://www.ebi.ac.uk/biomodels/search?query=curationstatus%3A%22Manually%20curated%22&numResults=1&format=json"
    response = requests.get(url)
    response.raise_for_status()
    json = response.json()
    matches = json["matches"]

    # query all SBML files
    pages = math.ceil(matches/100)
    num_results = 100
    biomodel_ids = []
    for k in range(pages):
        offset = k * num_results
        url = f"https://www.ebi.ac.uk/biomodels/search?query=curationstatus%3A%22Manually%20curated%22&numResults=100&offset={offset}&format=json"
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        json = response.json()
        ids = [model["id"] for model in json["models"]]
        biomodel_ids.extend(ids)

    return sorted(biomodel_ids)


def download_biomodel_sbml(mid: str, model_path: Path):
    """Get SBML string from given BioModels identifier."""
    # query file information
    print(f"... download '{mid}' ...")
    url = f"https://www.ebi.ac.uk/biomodels/{mid}?format=json"
    r = requests.get(url)
    r.raise_for_status()

    # query main file
    json = r.json()
    try:
        filename = json["files"]["main"][0]["name"]
        url = (
            f"https://www.ebi.ac.uk/biomodels/model/download/{mid}?filename={filename}"
        )
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        model_str = response.content

        # bytes array in py3
        with open(model_path, "w") as f_out:
            sbml_str = model_str.decode("utf-8")
            f_out.write(sbml_str)

    except (TypeError, KeyError) as err:
        logger.error(
            f"Filename of 'main' file could not be resolved from response: " f"'{json}'"
        )
        raise err


if __name__ == "__main__":
    biomodel_ids = query_curated_biomodels()
    from pprint import pprint
    pprint(biomodel_ids)
    pprint(len(biomodel_ids))

    for mid in biomodel_ids:
        download_biomodel_sbml(
            mid=mid,
            model_path=MODELS_DIR / "biomodels" / f"{mid}.xml"
        )