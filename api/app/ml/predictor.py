"""Loads the trained pipeline and turns a validated request into a prediction.

Kept separate from main.py so the model logic can be imported and tested on its
own, without spinning up the web layer.
"""

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

# Resolved relative to this file rather than the working directory, so the app
# behaves the same whether it's started from api/, from the repo root, or from
# /app inside the container.
#   predictor.py -> ml/ -> app/ -> api/model_best.pkl
MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "model_best.pkl"

# The 14 features the pipeline was fitted on, in no particular order - the
# ColumnTransformer selects columns by name, so order doesn't matter, but the
# names and spelling must match the training data exactly.
FEATURE_COLUMNS = [
    "Age", "DailyRate", "DistanceFromHome", "MonthlyIncome",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
    "BusinessTravel", "Department", "OverTime",
    "EnvironmentSatisfaction", "JobSatisfaction", "StockOptionLevel",
    "WorkLifeBalance",
]


class AttritionModel:
    """Thin wrapper around the fitted imblearn Pipeline.

    The pipeline handles all preprocessing internally (scaling, one-hot and
    ordinal encoding), so raw human-readable values go in - no manual encoding
    needed at the call site.
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        # Reads the whole pickle into memory. Done once at startup; see
        # get_model() below.
        self._pipeline = joblib.load(model_path)

    def predict(self, features: dict) -> tuple[bool, float]:
        """Score one employee. Returns (will_leave, probability_of_leaving)."""
        # Rebuild the dict in the trained column order and drop any extra keys.
        # A KeyError here means the caller omitted a required feature, which
        # should be impossible - the Pydantic schema guarantees all 14 exist.
        row = {col: features[col] for col in FEATURE_COLUMNS}

        # scikit-learn expects 2D tabular input; one dict becomes one row.
        df = pd.DataFrame([row])

        # Column 1 is the positive class ("Yes, attrited"), because the model was
        # trained on y where 1 == Yes. Column 0 would give P(stays).
        probability = float(self._pipeline.predict_proba(df)[0, 1])

        # Taken from predict() rather than thresholding the probability at 0.5,
        # so the answer always matches what the SVC itself decides.
        prediction = bool(self._pipeline.predict(df)[0])

        # Cast away numpy types (np.bool_, np.float64) - Pydantic and the JSON
        # serializer want plain Python builtins.
        return prediction, probability


@lru_cache
def get_model() -> AttritionModel:
    """Return the shared model instance, loading it on first call.

    @lru_cache makes this a lazy singleton: every later call returns the same
    object instead of re-reading the pickle from disk on every request.
    """
    return AttritionModel()
