import pandas as pd


def array_to_dataframe(X, columns):
    """Reshape step used inside the trained pipeline's ColumnTransformer output.

    Must stay importable at this exact module path (app.ml.transform) -
    joblib pickles a reference to it, not its code, so moving or renaming
    this function breaks unpickling of model_best.pkl.
    """
    return pd.DataFrame(X, columns=columns)
