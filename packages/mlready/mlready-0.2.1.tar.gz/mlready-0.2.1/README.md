# mlready

**mlready** is a lightweight Python library for making tabular datasets **safe and ready for machine-learning pipelines**.

It focuses on **observation → risk detection → safe normalization**, not aggressive automation.

---

## Why mlready?

Real-world datasets fail ML pipelines because of:

Your current list is **good but incomplete** for real-world ML failures.
You should add only **failure modes that `mlready` actually addresses**. No marketing fluff.

Add **exactly these**. Nothing more.

---

## Why mlready?

Real-world datasets fail ML pipelines because of:

* numeric values stored as strings (`"$1,200"`, `"1.2M"`)
* inconsistent booleans (`Yes / no / YES / n`)
* datetime columns stored as text
* mixed types within the same column
* silent missing values (`""`, `"NA"`, `"null"`, `"?"`)
* zero-variance and near-constant columns
* high-cardinality categorical fields
* ID-like columns that leak information
* unseen categories between train and test
* silent target leakage via derived or proxy columns
* schema drift between training and inference data

`mlready` helps you **detect these issues early and fix only what is safe**.

---

## Installation

Base install (data readiness utilities):

```bash
pip install mlready
````

Model reporting (metrics, curves, no plots):

```bash
pip install "mlready[report]"
```

Model reporting with visualizations:

```bash
pip install "mlready[report,viz]"
# or
pip install "mlready[full]"
```

---

## Core API (4 functions)

### 1️⃣ `profile(df)`

**Purpose:** Understand the dataset (read-only).

```python
import mlready as mr

report = mr.profile(df)
```

**What it provides:**

* dataset shape, memory usage, duplicates
* per-column:

  * dtype and inferred logical type
  * missing counts and percentages
  * unique counts and percentages
  * top values
  * pattern hints (currency, boolean, datetime)

No data is modified.

---

### 2️⃣ `audit(df, target=None, reference_df=None)`

**Purpose:** Detect ML risks before training.

```python
audit_report = mr.audit(df, target="label")
```

**What it detects:**

* ID-like columns
* zero-variance columns
* high-cardinality categoricals
* numeric / boolean / datetime stored as strings
* potential target leakage
* ghost categories (train vs test mismatch)
* schema drift

Returns **structured warnings**, not guesses.

---

### 3️⃣ `apply(df, recipe=None)`

**Purpose:** Safely normalize raw data.

```python
clean_df, recipe, report = mr.apply(df)
```

**What it safely applies (v0.1):**

* currency / numeric string → numeric
  (`"$1,200"`, `"(50)"`, `"1.2M"`)
* boolean strings → boolean dtype
  (`Yes / no / YES / n`)
* unambiguous datetime parsing
* safe numeric downcasting (nullable-aware)

**What it does NOT do:**

* no column dropping
* no encoding
* no fuzzy category merging
* no feature engineering

All actions are recorded in a **reproducible recipe**.

Got it. You want **symmetry**, not examples, and **no model-specific implication**.

Below is the **correct, precise, non-misleading** way to add `report()` in the **same style** as your other APIs.

You can paste this directly into your README.

---

### 4️⃣ `report(model, X_train, X_test, y_train, y_test, ...)`

**Purpose:** Evaluate classification models in a structured, pipeline-safe way.

**What it provides:**

* train and test classification reports
* summary metrics:

  * accuracy
  * balanced accuracy
  * precision / recall / F1 (macro, weighted)
* confusion matrix (data + optional plot)
* feature importance (when supported by the model)
* confidence analysis (probability distributions, when available)
* error analysis:

  * top misclassified rows with confidence scores
* model performance curves (optional):

  * ROC and Precision–Recall (binary)
  * calibration curve (probability-based models)
  * macro One-vs-Rest ROC-AUC (multiclass)
  * optional per-class OvR ROC curves (multiclass)

**Model support scope:**

* designed for **sklearn-compatible classifiers**
* requires `predict()`
* uses `predict_proba()` and/or `decision_function()` when available
* supports tree-based, linear, kernel-based, and sklearn-wrapped models

**What it does NOT support:**

* regression models
* clustering / anomaly detection
* multilabel (multi-hot) classification
* raw deep-learning models without sklearn-style APIs

Optional dependencies are required for reporting and visualization.

---

## Design Principles

* **Safety first** – no silent destructive actions
* **Sampling-aware** – fast on large data, reliable on small data
* **Pipeline-friendly** – deterministic behavior via recipes
* **Minimal dependencies** – pure pandas / numpy

---

## When to use mlready

Use `mlready` when:

* ingesting raw CSVs or business data
* validating train vs test consistency
* preparing data before encoding / modeling
* building reproducible ML pipelines

Not intended to replace:

* feature engineering libraries
* AutoML tools
* visualization-heavy EDA tools

---

## Project Status

* Version: **0.2.1**
* Stable core API
* Tests included
* Ready for production pipelines (safe mode)

---

## License

MIT License

---