"""Comparación reproducible de clasificadores con el archivo oficial EPEN."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter
from urllib.request import urlretrieve
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, make_scorer, recall_score
from sklearn.model_selection import ParameterGrid, StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

URL = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/CSV/1029-Modulo76.zip"
SEED = 42
LABELS = ["Ocupado", "Desocupado abierto", "Desocupado oculto", "Inactivo pleno"]
CLASSES = np.arange(4)
HOUSEHOLD = ["CONGLOMERADO", "MUESTRA", "SELVIV", "HOGAR"]
DATA_PATH = Path("datos/1029-Modulo76.zip")
FUNCTIONAL = [f"C375_{i}" for i in range(1, 7)]
CATEGORIES = {
    "C207": (1, 2), "C366": tuple(range(1, 13)),
    **{column: (1, 2) for column in FUNCTIONAL},
    "C376": tuple(range(1, 15)), "C377": tuple(range(1, 9)),
}
FEATURES = ["C208", *CATEGORIES]
FAMILIES = {
    "Logística": (LogisticRegression(max_iter=1500, solver="lbfgs"),
                 {"C": [0.1, 1, 10]}),
    "Random Forest": (RandomForestClassifier(random_state=SEED, n_jobs=2),
                      {"n_estimators": [150, 300], "max_depth": [5, 12],
                       "min_samples_leaf": [5, 15]}),
    "XGBoost": (XGBClassifier(random_state=SEED, n_jobs=2, tree_method="hist",
                             objective="multi:softprob", eval_metric="mlogloss",
                             subsample=0.85, colsample_bytree=0.85, reg_lambda=1),
                {"n_estimators": [100, 200], "max_depth": [2, 4],
                 "learning_rate": [0.05, 0.10]}),
}


def load_data(path):
    with ZipFile(path) as archive:
        member, = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        with archive.open(member) as stream:
            raw = pd.read_csv(stream, dtype=str, encoding="latin1").apply(lambda col: col.str.strip())
    if set(raw["ANIO"]) != {"2026"} or set(raw["MES"]) != {"01", "02", "03"}:
        raise ValueError("Se requiere el archivo oficial del trimestre enero-marzo de 2026.")
    age = pd.to_numeric(raw["C208"], errors="coerce")
    target = pd.to_numeric(raw["OCUP300"], errors="coerce")
    residents = raw["REGION"].eq("1") & raw["RESIDENT"].eq("1")
    scope = residents & age.between(14, 98)
    eligible = scope & target.isin([1, 2, 3, 4])
    records = raw.loc[eligible].reset_index(drop=True)
    keys = records[HOUSEHOLD + ["C201"]]
    if keys.isna().any().any() or keys.eq("").any().any() or keys.duplicated().any():
        raise ValueError("Revise la integridad de las claves de hogar y persona.")
    groups = records.groupby(HOUSEHOLD, sort=False).ngroup().to_numpy()
    predictors = pd.DataFrame({"C208": age.loc[eligible].to_numpy()})
    for column, valid_codes in CATEGORIES.items():
        values = pd.to_numeric(records[column], errors="coerce")
        predictors[column] = values.where(values.isin(valid_codes)).astype(float)
    audit = {"rows_csv": len(raw), "cols_csv": len(raw.columns),
             "age_99_in_domain": int((residents & age.eq(99)).sum()),
             "age_above_99_in_domain": int((residents & age.gt(99)).sum()),
             "residents_age14_region1": int(scope.sum()),
             "invalid_target_in_scope": int((scope & ~eligible).sum()),
             "n": len(records), "households": int(len(np.unique(groups))),
             "missing": predictors.isna().sum().to_dict(),
             "geo_cardinality": raw[["REGION", "ESTRATO"]].nunique().to_dict()}
    return predictors, target.loc[eligible].astype(int).to_numpy() - 1, groups, audit


def make_model(estimator, params):
    prep = ColumnTransformer([
        ("edad", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), ["C208"]),
        ("categorias", make_pipeline(SimpleImputer(strategy="constant", fill_value=-1),
                                    OneHotEncoder(handle_unknown="ignore")), list(CATEGORIES)),
    ])
    return make_pipeline(prep, sklearn.base.clone(estimator).set_params(**params))


def f1(y, predicted, average):
    return f1_score(y, predicted, labels=CLASSES, average=average, zero_division=0)


def fit_model(estimator, params, balance, X, y):
    model = make_model(estimator, params)
    weights = compute_sample_weight("balanced", y) if balance else np.ones(len(y))
    return model.fit(X, y, **{f"{model.steps[-1][0]}__sample_weight": weights})


def metrics(y, prediction):
    return {
        "f1_weighted": f1(y, prediction, "weighted"),
        "f1_macro": f1(y, prediction, "macro"),
        "recall": recall_score(y, prediction, labels=CLASSES, average=None, zero_division=0).tolist(),
        "confusion": confusion_matrix(y, prediction, labels=CLASSES).tolist(),
    }


def grouped_bootstrap(y, predictions, groups):
    """Intervalos descriptivos para las diferencias pareadas en F1 ponderado."""
    unique, group_index = np.unique(groups, return_inverse=True)
    cubes = {}
    for name, predicted in predictions.items():
        counts = np.bincount(group_index * 16 + y * 4 + predicted, minlength=len(unique) * 16)
        cubes[name] = counts.reshape(-1, 4, 4)
    rng = np.random.default_rng(SEED)
    weights = rng.multinomial(len(unique), np.full(len(unique), 1 / len(unique)), size=1000)
    scores = {}
    for name, cube in cubes.items():
        cm = (weights @ cube.reshape(-1, 16)).reshape(-1, 4, 4)
        true_count, predicted_count = cm.sum(axis=2), cm.sum(axis=1)
        tp = np.diagonal(cm, axis1=1, axis2=2)
        denom = true_count + predicted_count
        class_f1 = np.divide(2 * tp, denom, out=np.zeros_like(denom, dtype=float), where=denom > 0)
        scores[name] = (class_f1 * true_count).sum(axis=1) / true_count.sum(axis=1)
    return {name: np.quantile(scores[name] - scores["Logística"], [0.025, 0.975]).tolist()
            for name in ("Random Forest", "XGBoost")}


def plot_confusions(test, out):
    fig, axes = plt.subplots(2, 2, figsize=(7.7, 6.2), layout="constrained")
    fig.supxlabel("Clase predicha")
    fig.supylabel("Clase observada")
    for ax, (name, row) in zip(axes.flat, test.items()):
        counts = np.asarray(row["confusion"])
        proportions = counts / counts.sum(axis=1, keepdims=True)
        ax.imshow(proportions, vmin=0, vmax=1, cmap="Blues")
        ax.set_title(name, fontsize=11)
        ax.set_xticks(range(4), ["1", "2", "3", "4"])
        ax.set_yticks(range(4), ["1", "2", "3", "4"])
        for i, j in np.ndindex(counts.shape):
            ax.text(j, i, str(counts[i, j]), ha="center", va="center",
                    color="white" if proportions[i, j] > 0.65 else "#162934", fontsize=10)
    fig.savefig(out / "matrices.png", dpi=210)
    plt.close(fig)


def evaluate(path, out):
    start = perf_counter()
    X, y, groups, audit = load_data(path)
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train, test = next(outer.split(X, y, groups))
    X_train, y_train, groups_train = X.iloc[train], y[train], groups[train]
    X_test, y_test, groups_test = X.iloc[test], y[test], groups[test]
    folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED + 1)
                 .split(X_train, y_train, groups_train))
    if set(groups_train) & set(groups_test) or any(set(groups_train[a]) & set(groups_train[b])
                                                   for a, b in folds):
        raise ValueError("Se detectó un hogar compartido entre particiones.")
    if any(len(np.unique(y[idx])) != 4 for idx in (train, test)) or any(
            len(np.unique(y_train[idx])) != 4 for fold in folds for idx in fold):
        raise ValueError("Una partición carece de alguna clase.")
    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    predictions = {"Clase mayoritaria": baseline.predict(X_test)}
    test_metrics = {"Clase mayoritaria": metrics(y_test, predictions["Clase mayoritaria"])}
    runs, best_by_balance, trained, score_diagnostics = [], {}, {}, {}
    for name, (estimator, grid) in FAMILIES.items():
        candidates = []
        for params in ParameterGrid(grid):
            for balance in (False, True):
                folds_weighted, folds_macro, folds_recall = [], [], []
                for fit, validation in folds:
                    model = fit_model(estimator, params, balance, X_train.iloc[fit], y_train[fit])
                    val_pred = model.predict(X_train.iloc[validation])
                    folds_weighted.append(f1(y_train[validation], val_pred, "weighted"))
                    folds_macro.append(f1(y_train[validation], val_pred, "macro"))
                    folds_recall.append(recall_score(y_train[validation], val_pred, labels=CLASSES,
                                                     average=None, zero_division=0))
                row = {"model": name, "balance": balance, "params": params,
                       "cv_weighted": float(np.mean(folds_weighted)),
                       "cv_weighted_sd": float(np.std(folds_weighted, ddof=1)),
                       "cv_macro": float(np.mean(folds_macro)),
                       **{f"cv_recall_{k + 1}": float(value)
                          for k, value in enumerate(np.mean(folds_recall, axis=0))}}
                candidates.append(row)
        rank = lambda row: (row["cv_weighted"], row["cv_macro"])
        chosen = max(candidates, key=rank)
        best_by_balance[name] = [max((r for r in candidates if r["balance"] == balance), key=rank)
                                 for balance in (False, True)]
        runs.extend(candidates)
        t0 = perf_counter()
        trained[name] = fit_model(estimator, chosen["params"], chosen["balance"], X_train, y_train)
        elapsed_fit = perf_counter() - t0
        t0 = perf_counter()
        probabilities = trained[name].predict_proba(X_test)
        elapsed_predict = perf_counter() - t0
        if not np.allclose(probabilities.sum(axis=1), 1.0):
            raise ValueError("Probabilidades multiclase inválidas.")
        predictions[name] = trained[name].classes_[probabilities.argmax(axis=1)]
        ranks = np.argsort(-probabilities, axis=1, kind="stable")
        score_diagnostics[name] = [
            {"support": int((y_test == k).sum()),
             "mean_scores": probabilities[y_test == k].mean(axis=0).tolist(),
             "top2_hits": int(np.any(ranks[y_test == k, :2] == k, axis=1).sum())}
            for k in CLASSES
        ]
        test_metrics[name] = dict(metrics(y_test, predictions[name]), **chosen,
                                  fit_seconds=elapsed_fit, prediction_seconds=elapsed_predict)
        print(name, chosen, flush=True)
    chosen_for_audit = max(trained, key=lambda name: test_metrics[name]["cv_weighted"])
    scorer = make_scorer(f1_score, labels=CLASSES, average="weighted", zero_division=0)
    importance = permutation_importance(trained[chosen_for_audit], X_test, y_test,
                                        scoring=scorer, n_repeats=15, random_state=SEED)
    importance_table = pd.DataFrame({"variable": FEATURES, "mean": importance.importances_mean,
                                     "sd": importance.importances_std}).sort_values("mean", ascending=False)
    importance_table.to_csv(out / "importancia.csv", index=False)
    pd.DataFrame(runs).to_csv(out / "validacion.csv", index=False)
    subgroup = {}
    for sex in (1, 2):
        mask = X_test["C207"].eq(sex).to_numpy()
        subgroup[str(sex)] = {"n": int(mask.sum()), "f1_macro": f1(
            y_test[mask], predictions[chosen_for_audit][mask], "macro"),
            "support": np.bincount(y_test[mask], minlength=4).tolist()}
    result = {
        "audit": audit, "labels": LABELS, "seed": SEED, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "support": {name: np.bincount(y[idx], minlength=4).tolist()
                    for name, idx in (("total", np.arange(len(y))), ("train", train), ("test", test))},
        "train_households": len(np.unique(groups_train)), "test_households": len(np.unique(groups_test)),
        "cv_configurations": len(runs), "best_by_balance": best_by_balance, "test": test_metrics,
        "audit_model": chosen_for_audit, "importance": importance_table.to_dict(orient="records"),
        "subgroup": subgroup, "bootstrap": grouped_bootstrap(y_test, predictions, groups_test),
        "score_diagnostics": score_diagnostics,
        "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                        "sklearn": sklearn.__version__, "xgboost": xgboost.__version__,
                        "numpy": np.__version__, "matplotlib": matplotlib.__version__,
                        "platform": platform.platform()},
    }
    plot_confusions(test_metrics, out)
    result["total_seconds"] = perf_counter() - start
    (out / "resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, default=DATA_PATH)
    parser.add_argument("--salida", type=Path, default=Path("resultados"))
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    if not args.archivo.exists():
        args.archivo.parent.mkdir(parents=True, exist_ok=True)
        partial = args.archivo.with_suffix(".descarga")
        urlretrieve(URL, partial)
        with ZipFile(partial) as archive:
            if archive.testzip() is not None:
                raise ValueError("El ZIP descargado tiene un archivo dañado.")
        partial.replace(args.archivo)
    evaluate(args.archivo, args.salida)


if __name__ == "__main__":
    main()
