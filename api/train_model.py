"""Regenerates model_best.pkl as a self-contained artifact.

The original pickle (deployment/model_best.pkl) references a FunctionTransformer
whose function was defined in a notebook's __main__ namespace, so it can only be
unpickled by scripts that happen to redefine that function first. This script
rebuilds the exact same pipeline - same preprocessing, same SVC hyperparameters
found by the original GridSearchCV (C=10, gamma=1, kernel='linear'), same
train/test split (test_size=0.15, random_state=2) - but with the reshape
function importable from app.ml.transform, so the dump can be loaded from
anywhere via a plain `joblib.load`.
"""

import argparse
from pathlib import Path

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    MinMaxScaler,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
from sklearn.svm import SVC

from app.ml.transform import array_to_dataframe

FEATURE_COLUMNS = [
    "Age", "DailyRate", "DistanceFromHome", "MonthlyIncome",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
    "BusinessTravel", "Department", "OverTime",
    "EnvironmentSatisfaction", "JobSatisfaction", "StockOptionLevel",
    "WorkLifeBalance",
]

TRANSFORMED_COLUMNS = [
    "num_scaler__Age", "num_scaler__DailyRate", "num_scaler__DistanceFromHome",
    "num_scaler__MonthlyIncome", "num_scaler__TrainingTimesLastYear",
    "num_minmax__TotalWorkingYears", "num_minmax__YearsAtCompany",
    "cat_onehot__Department_Research & Development", "cat_onehot__Department_Sales",
    "cat_onehot__OverTime_Yes", "cat_ordinal__BusinessTravel",
    "passthrough__EnvironmentSatisfaction", "passthrough__JobSatisfaction",
    "passthrough__StockOptionLevel", "passthrough__WorkLifeBalance",
]


def build_pipeline() -> ImbPipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num_scaler", Pipeline([("scaler", StandardScaler())]),
             ["Age", "DailyRate", "DistanceFromHome", "MonthlyIncome", "TrainingTimesLastYear"]),
            ("num_minmax", Pipeline([("minmax", MinMaxScaler())]),
             ["TotalWorkingYears", "YearsAtCompany"]),
            ("cat_onehot", Pipeline([("onehot", OneHotEncoder(drop="first", handle_unknown="ignore"))]),
             ["Department", "OverTime"]),
            ("cat_ordinal", Pipeline([("ordinal", OrdinalEncoder())]),
             ["BusinessTravel"]),
            ("passthrough", "passthrough",
             ["EnvironmentSatisfaction", "JobSatisfaction", "StockOptionLevel", "WorkLifeBalance"]),
        ]
    )

    return ImbPipeline([
        ("transformer", preprocessor),
        ("smote", SMOTE(sampling_strategy="minority", k_neighbors=5, random_state=2)),
        ("to_dataframe", FunctionTransformer(array_to_dataframe, kw_args={"columns": TRANSFORMED_COLUMNS})),
        ("classifier", SVC(C=10, gamma=1, kernel="linear", probability=True, random_state=2)),
    ])


def main(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df["Attrition"].str.replace("Yes", "1").replace("No", "0").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=2)

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(f"Test recall:  {recall_score(y_test, y_pred):.4f}")
    print(f"Test ROC AUC: {roc_auc_score(y_test, y_pred):.4f}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out_path)
    print(f"Saved pipeline to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv", type=Path,
        default=Path(__file__).resolve().parent.parent / "WA_Fn-UseC_-HR-Employee-Attrition.csv",
    )
    parser.add_argument(
        "--out", type=Path,
        default=Path(__file__).resolve().parent / "model_best.pkl",
    )
    args = parser.parse_args()
    main(args.csv, args.out)
