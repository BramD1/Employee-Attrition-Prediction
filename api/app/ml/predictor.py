from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "model_best.pkl"

FEATURE_COLUMNS = [
    "Age", "DailyRate", "DistanceFromHome", "MonthlyIncome",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
    "BusinessTravel", "Department", "OverTime",
    "EnvironmentSatisfaction", "JobSatisfaction", "StockOptionLevel",
    "WorkLifeBalance",
]


class AttritionModel:
    def __init__(self, model_path: Path = MODEL_PATH):
        self._pipeline = joblib.load(model_path)

    def predict(self, features: dict) -> tuple[bool, float]:
        row = {col: features[col] for col in FEATURE_COLUMNS}
        df = pd.DataFrame([row])
        probability = float(self._pipeline.predict_proba(df)[0, 1])
        prediction = bool(self._pipeline.predict(df)[0])
        return prediction, probability


@lru_cache
def get_model() -> AttritionModel:
    return AttritionModel()
