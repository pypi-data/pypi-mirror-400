import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from mlready import report

def test_report_returns_expected_keys():
    X, y = load_iris(return_X_y=True)
    Xtr, Xts, ytr, yts = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = DecisionTreeClassifier(random_state=42).fit(Xtr, ytr)

    out = report(model, Xtr, Xts, ytr, yts, plot=False, compute_curves=True, learning_curve_plot=False)

    assert "metrics" in out
    assert "train_report" in out
    assert "test_report" in out
    assert "labels" in out
    assert "confusion_matrix" in out
    assert "top_errors" in out
