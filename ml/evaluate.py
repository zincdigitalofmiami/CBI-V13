import numpy as np
import pandas as pd


def rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def permutation_importance_placeholder() -> dict:
    return {"note": "Permutation importance to be implemented once full model/data are in place."}
