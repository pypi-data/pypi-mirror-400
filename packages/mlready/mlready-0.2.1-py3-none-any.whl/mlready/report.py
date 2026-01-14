# mlready/report.py
from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple, Literal


def report(
    model: Any,
    X_train: Any,
    X_test: Any,
    y_train: Any,
    y_test: Any,
    *,
    average_options: Tuple[str, ...] = ("weighted", "macro"),
    compute_curves: bool = True,
    multiclass_curves: Literal["off", "ovr"] = "off",
    learning_curve_plot: bool = False,
    cv: int = 5,
    stratified_cv: bool = True,
    plot: bool = True,
    plot_style: Literal["simple", "enhanced"] = "enhanced",
    top_n_errors: int = 10,
    label_order: Optional[Sequence[Any]] = None,
    title_prefix: str = "",
) -> Dict[str, Any]:
    """
    Sklearn-focused classification report utility.

    Returns a dict with:
      - metrics (accuracy, balanced accuracy, precision/recall/f1 for averages)
      - text reports (train/test classification_report strings)
      - confusion matrix (np.ndarray)
      - optional curves data (binary: roc, pr, calibration; multiclass: ovr roc_auc + optional ovr ROC curves)
      - optional error analysis dataframe (top_errors)
      - optional feature importance series (pd.Series) when supported

    Supports:
      - sklearn-like classifiers with predict()
      - optional predict_proba() and/or decision_function()
      - pandas / numpy / scipy sparse (kept sparse)

    Notes:
      - If y is one-hot encoded multiclass, it is converted via argmax.
      - Multilabel (multi-hot) is NOT supported (argmax would be wrong).
      - Binary ROC/PR curves are computed using probabilities if available, else decision_function.
      - Multiclass curves: always computes ROC-AUC OvR macro when proba is available;
        optional per-class OvR ROC curves when multiclass_curves="ovr".
    """
    import numpy as np
    import pandas as pd

    # --- Optional plotting import ---
    if plot:
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            raise ImportError(
                "Plotting requires matplotlib. Install with: pip install mlready[viz]"
            ) from e
    else:
        plt = None  # type: ignore

    # --- Required sklearn deps (report depends on sklearn) ---
    try:
        from sklearn.base import is_classifier
        from sklearn.calibration import calibration_curve
        from sklearn.metrics import (
            accuracy_score,
            balanced_accuracy_score,
            classification_report,
            confusion_matrix,
            precision_recall_fscore_support,
            roc_curve,
            auc,
            precision_recall_curve,
            average_precision_score,
            roc_auc_score,
        )
        from sklearn.model_selection import learning_curve, StratifiedKFold, KFold
    except Exception as e:
        raise ImportError(
            "mlready.report requires scikit-learn. Install with: pip install mlready[report]"
        ) from e

    # --- Optional sparse support (no hard dependency) ---
    try:
        from scipy import sparse  # type: ignore
        is_sparse = sparse.issparse
    except Exception:
        def is_sparse(_: Any) -> bool:
            return False

    # ---------------- helpers ----------------
    def _to_1d_y(y: Any) -> np.ndarray:
        y_arr = np.asarray(y)
        if y_arr.ndim > 1:
            return y_arr.argmax(axis=1)
        return y_arr

    def _get_feature_names(X: Any) -> Sequence[str]:
        if hasattr(X, "columns"):
            return list(X.columns)
        n = X.shape[1]
        return [f"Feature {i}" for i in range(n)]

    def _as_model_input(X: Any) -> Any:
        # keep sparse sparse; keep pandas as-is
        return X

    def _safe_predict(m: Any, X: Any) -> np.ndarray:
        return np.asarray(m.predict(X))

    def _get_scores_for_curves(m: Any, X: Any) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[str]]:
        proba = None
        scores = None
        mode = None

        if hasattr(m, "predict_proba"):
            try:
                proba = m.predict_proba(X)
                mode = "proba"
            except Exception:
                proba = None
                mode = None

        if mode is None and hasattr(m, "decision_function"):
            try:
                scores = m.decision_function(X)
                mode = "decision"
            except Exception:
                scores = None
                mode = None

        return proba, scores, mode

    def _infer_labels(y_true: np.ndarray, y_pred: np.ndarray, label_order_: Optional[Sequence[Any]]) -> Sequence[Any]:
        if label_order_ is not None:
            return list(label_order_)
        labs = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
        return list(labs)

    def _maybe_print_header(title: str) -> None:
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)

    def _plot_roc_enhanced(fpr: np.ndarray, tpr: np.ndarray, roc_auc: float, title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(7, 5))
        plt.fill_between(fpr, tpr, alpha=0.25, label="AUC Area")
        plt.plot(
            fpr, tpr,
            lw=2,
            marker="o",
            markersize=4,
            markerfacecolor="white",
            label=f"ROC (AUC = {roc_auc:.3f})"
        )
        plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="Random")
        plt.title(title)
        plt.xlabel("False Positive Rate (1 - Specificity)")
        plt.ylabel("True Positive Rate (Sensitivity/Recall)")
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _plot_pr_enhanced(recall: np.ndarray, precision: np.ndarray, ap: float, title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(7, 5))
        plt.fill_between(recall, precision, alpha=0.25, label="AP Area")
        plt.plot(
            recall, precision,
            lw=2,
            marker="o",
            markersize=4,
            markerfacecolor="white",
            label=f"PR (AP = {ap:.3f})"
        )
        plt.title(title)
        plt.xlabel("Recall (True Positive Rate)")
        plt.ylabel("Precision")
        plt.legend(loc="lower left")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _plot_calibration(mean_pred: np.ndarray, frac_pos: np.ndarray, title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(7, 5))
        plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1)
        plt.plot(mean_pred, frac_pos, marker="o", lw=2)
        plt.title(title)
        plt.xlabel("Mean predicted probability")
        plt.ylabel("Fraction of positives")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _plot_cm(cm: np.ndarray, labels_: Sequence[Any], title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(7, 5))
        plt.imshow(cm, interpolation="nearest")
        plt.title(title)
        plt.xticks(range(len(labels_)), labels_, rotation=45, ha="right")
        plt.yticks(range(len(labels_)), labels_)
        plt.colorbar()
        thresh = cm.max() / 2.0 if cm.size else 0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(
                    j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                )
        plt.tight_layout()
        plt.show()

    def _plot_feature_importance(fi: pd.Series, title: str) -> None:
        assert plt is not None
        topk = fi.head(10).sort_values()
        plt.figure(figsize=(7, 5))
        plt.barh(topk.index, topk.values)
        plt.title(title)
        plt.tight_layout()
        plt.show()

    def _plot_confidence_hist(proba_: np.ndarray, labels_: Sequence[Any], title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(7, 5))
        if proba_.shape[1] == 2:
            plt.hist(proba_[:, 1], bins=20, alpha=0.7)
            plt.title(f"{title} (P(class={labels_[1]}))")
            plt.xlabel("Probability")
        else:
            maxp = np.max(proba_, axis=1)
            plt.hist(maxp, bins=20, alpha=0.7)
            plt.title(f"{title} (max class probability)")
            plt.xlabel("Max probability")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _plot_multiclass_ovr_roc(ovr_roc: Dict[Any, Dict[str, Any]], title: str) -> None:
        assert plt is not None
        plt.figure(figsize=(8, 6))
        # Avoid hardcoding specific colors; matplotlib will cycle defaults
        for class_label, data in ovr_roc.items():
            plt.plot(
                data["fpr"],
                data["tpr"],
                lw=2,
                label=f"Class {class_label} (AUC = {float(data['auc']):.2f})",
            )
        plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="Random")
        plt.title(title)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # ---------------- main ----------------
    if not is_classifier(model) and not hasattr(model, "predict"):
        raise TypeError("model must be a sklearn-like classifier with predict().")

    Xtr = _as_model_input(X_train)
    Xts = _as_model_input(X_test)
    ytr = _to_1d_y(y_train)
    yts = _to_1d_y(y_test)

    feature_names = _get_feature_names(X_train)

    ytr_pred = _safe_predict(model, Xtr)
    yts_pred = _safe_predict(model, Xts)

    labels = _infer_labels(yts, yts_pred, label_order)

    # Metrics
    metrics: Dict[str, Any] = {}
    metrics["train_accuracy"] = float(accuracy_score(ytr, ytr_pred))
    metrics["test_accuracy"] = float(accuracy_score(yts, yts_pred))
    metrics["test_balanced_accuracy"] = float(balanced_accuracy_score(yts, yts_pred))

    for avg in average_options:
        p, r, f1, _ = precision_recall_fscore_support(yts, yts_pred, average=avg, zero_division=0)
        metrics[f"test_precision_{avg}"] = float(p)
        metrics[f"test_recall_{avg}"] = float(r)
        metrics[f"test_f1_{avg}"] = float(f1)

    train_report = classification_report(ytr, ytr_pred, zero_division=0)
    test_report = classification_report(yts, yts_pred, zero_division=0)

    cm = confusion_matrix(yts, yts_pred, labels=labels)

    # Feature importance
    feat_importance: Optional[pd.Series] = None
    try:
        if hasattr(model, "feature_importances_"):
            imp = np.asarray(getattr(model, "feature_importances_")).ravel()
            feat_importance = pd.Series(imp, index=feature_names).sort_values(ascending=False)
        elif hasattr(model, "coef_"):
            coef = np.asarray(getattr(model, "coef_"))
            if coef.ndim == 1:
                agg = np.abs(coef)
            elif coef.ndim == 2:
                agg = np.mean(np.abs(coef), axis=0)
            else:
                agg = None
            if agg is not None:
                feat_importance = pd.Series(agg, index=feature_names).sort_values(ascending=False)
    except Exception:
        feat_importance = None

    # Curves
    curves: Dict[str, Any] = {}
    proba, scores, mode = (None, None, None)

    if compute_curves:
        proba, scores, mode = _get_scores_for_curves(model, Xts)
        n_classes = len(labels)

        if n_classes == 2:
            if proba is not None:
                pos_score = proba[:, 1]
                curves["mode"] = "proba"
            elif scores is not None:
                s = np.asarray(scores)
                pos_score = s if s.ndim == 1 else s[:, 1]
                curves["mode"] = "decision"
            else:
                pos_score = None
                curves["mode"] = None

            if pos_score is not None:
                fpr, tpr, _ = roc_curve(yts, pos_score, pos_label=labels[1])
                curves["roc"] = {"fpr": fpr, "tpr": tpr, "auc": float(auc(fpr, tpr))}

                prec, rec, _ = precision_recall_curve(yts, pos_score, pos_label=labels[1])
                curves["pr"] = {
                    "precision": prec,
                    "recall": rec,
                    "ap": float(average_precision_score(yts, pos_score, pos_label=labels[1])),
                }

                if proba is not None:
                    frac_pos, mean_pred = calibration_curve(
                        (np.asarray(yts) == labels[1]).astype(int),
                        proba[:, 1],
                        n_bins=10,
                        strategy="uniform",
                    )
                    curves["calibration"] = {"mean_pred": mean_pred, "frac_pos": frac_pos}
        else:
            if proba is not None:
                # scalar multiclass ROC-AUC OvR macro
                try:
                    label_to_idx = {lab: i for i, lab in enumerate(labels)}
                    y_idx = np.vectorize(label_to_idx.get)(np.asarray(yts))
                    auc_ovr_macro = roc_auc_score(y_idx, proba, multi_class="ovr", average="macro")
                    metrics["test_roc_auc_ovr_macro"] = float(auc_ovr_macro)
                except Exception:
                    pass

                # optional per-class OvR ROC curve data + plot
                if multiclass_curves == "ovr":
                    try:
                        from sklearn.preprocessing import label_binarize
                        y_bin = label_binarize(yts, classes=labels)
                        curves["ovr_roc"] = {}
                        for i, class_label in enumerate(labels):
                            fpr_i, tpr_i, _ = roc_curve(y_bin[:, i], proba[:, i])
                            curves["ovr_roc"][class_label] = {
                                "fpr": fpr_i,
                                "tpr": tpr_i,
                                "auc": float(auc(fpr_i, tpr_i)),
                            }
                    except Exception:
                        pass

    # Error analysis
    errors_df = None
    try:
        wrong = (yts_pred != yts)
        if np.any(wrong):
            idx = np.arange(len(yts))[wrong]
            conf = None
            if proba is not None:
                conf = np.max(proba, axis=1)[wrong]

            errors_df = pd.DataFrame(
                {
                    "row_index": idx,
                    "y_true": np.asarray(yts)[wrong],
                    "y_pred": np.asarray(yts_pred)[wrong],
                    "confidence": conf if conf is not None else np.nan,
                }
            )
            if errors_df["confidence"].notna().any():
                errors_df = errors_df.sort_values("confidence", ascending=True)
            errors_df = errors_df.head(int(top_n_errors))
    except Exception:
        errors_df = None

    # Printing
    _maybe_print_header(f"{title_prefix}STEP 1: CLASSIFICATION REPORTS")
    print("\n>>> TRAIN:\n", train_report)
    print("\n>>> TEST:\n", test_report)

    _maybe_print_header(f"{title_prefix}STEP 2: SUMMARY METRICS (TEST)")
    for k in sorted(metrics.keys()):
        v = metrics[k]
        print(f"{k:>28s}: {v:.4f}" if isinstance(v, float) else f"{k:>28s}: {v}")

    # Plotting
    if plot and plt is not None:
        _plot_cm(cm, labels, f"{title_prefix}Confusion Matrix")

        if feat_importance is not None:
            _plot_feature_importance(feat_importance, f"{title_prefix}Top Feature Drivers (aggregated)")

        if proba is not None:
            _plot_confidence_hist(proba, labels, f"{title_prefix}Confidence")

        # Binary curves
        if compute_curves and len(labels) == 2 and curves.get("mode") is not None:
            if "roc" in curves:
                if plot_style == "enhanced":
                    _plot_roc_enhanced(curves["roc"]["fpr"], curves["roc"]["tpr"], curves["roc"]["auc"],
                                       f"{title_prefix}Enhanced ROC Analysis")
                else:
                    _plot_roc_enhanced(curves["roc"]["fpr"], curves["roc"]["tpr"], curves["roc"]["auc"],
                                       f"{title_prefix}ROC Curve")  # uses same renderer; still fine

            if "pr" in curves:
                if plot_style == "enhanced":
                    _plot_pr_enhanced(curves["pr"]["recall"], curves["pr"]["precision"], curves["pr"]["ap"],
                                      f"{title_prefix}Enhanced Precision-Recall Analysis")
                else:
                    _plot_pr_enhanced(curves["pr"]["recall"], curves["pr"]["precision"], curves["pr"]["ap"],
                                      f"{title_prefix}Precision-Recall Curve")

            if "calibration" in curves:
                _plot_calibration(curves["calibration"]["mean_pred"], curves["calibration"]["frac_pos"],
                                  f"{title_prefix}Calibration Curve")

        # Multiclass OvR ROC plot (optional)
        if multiclass_curves == "ovr" and "ovr_roc" in curves:
            _plot_multiclass_ovr_roc(curves["ovr_roc"], f"{title_prefix}Multiclass One-vs-Rest ROC")

        # Learning curve (optional)
        if learning_curve_plot:
            splitter = (
                StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
                if stratified_cv
                else KFold(n_splits=cv, shuffle=True, random_state=42)
            )
            plt.figure(figsize=(7, 5))
            sizes, tr_s, ts_s = learning_curve(model, Xtr, ytr, cv=splitter, n_jobs=None)
            plt.plot(sizes, np.mean(tr_s, axis=1), "o-", label="Train")
            plt.plot(sizes, np.mean(ts_s, axis=1), "o-", label="CV")
            plt.title(f"{title_prefix}Learning Curve")
            plt.xlabel("Training examples")
            plt.ylabel("Score")
            plt.legend()
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.show()

    return {
        "metrics": metrics,
        "train_report": train_report,
        "test_report": test_report,
        "labels": labels,
        "confusion_matrix": cm,
        "feature_importance": feat_importance,
        "curves": curves,
        "top_errors": errors_df,
    }
