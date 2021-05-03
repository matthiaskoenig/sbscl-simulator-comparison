from pathlib import Path
from typing import List
from pprint import pprint

BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

N_REPEAT = 5


def bigg_model_paths() -> List[Path]:
    """Get the Bigg model paths"""
    bigg_path = MODELS_DIR / "bigg-v1.6"
    paths = bigg_path.glob("*.xml.gz")
    paths = sorted(paths, key=lambda x: str(x))
    return list(paths)


def biomodels_model_paths() -> List[Path]:
    """Get the biomodels model paths"""
    bigg_path = MODELS_DIR / "biomodels"
    paths = bigg_path.glob("*.xml")
    paths = sorted(paths, key=lambda x: str(x))
    return list(paths)


BIGG_MODEL_PATHS = bigg_model_paths()
BIOMODELS_MODEL_PATHS = biomodels_model_paths()
# pprint(BIGG_MODEL_PATHS)
# pprint(BIOMODELS_MODEL_PATHS)