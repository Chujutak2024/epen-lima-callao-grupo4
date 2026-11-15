import csv
import json
import unittest
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from experimento import CLASSES, DATA_PATH, SEED, load_data


class TestEPEN(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y, cls.groups, cls.audit = load_data(DATA_PATH)

    def test_edad_faltante_y_etiquetas(self):
        self.assertEqual(self.audit["age_99_in_domain"], 2)
        self.assertEqual(self.audit["age_above_99_in_domain"], 2)
        self.assertTrue(self.X["C208"].between(14, 98).all())
        self.assertEqual(set(self.y), set(CLASSES))
        np.testing.assert_array_equal(np.bincount(self.y), [6111, 475, 152, 3461])

    def test_hogares_separados(self):
        split = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
        train, test = next(split.split(self.X, self.y, self.groups))
        self.assertFalse(set(self.groups[train]) & set(self.groups[test]))
        self.assertEqual(set(self.y[test]), set(CLASSES))
        self.assertEqual(set(self.y[train]), set(CLASSES))
        inner = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED + 1)
        for fit, valid in inner.split(self.X.iloc[train], self.y[train], self.groups[train]):
            self.assertFalse(set(self.groups[train[fit]]) & set(self.groups[train[valid]]))
            self.assertEqual(set(self.y[train[valid]]), set(CLASSES))

    def test_resultados_agregados(self):
        stored = json.loads(Path("resultados/resultados.json").read_text(encoding="utf-8"))
        np.testing.assert_array_equal(stored["support"]["total"], np.bincount(self.y))
        for model, metrics in stored["test"].items():
            with self.subTest(model=model):
                matrix = np.array(metrics["confusion"])
                support = matrix.sum(axis=1)
                np.testing.assert_array_equal(support, stored["support"]["test"])
                f1 = 2 * matrix.diagonal() / (support + matrix.sum(axis=0))
                self.assertAlmostEqual(metrics["f1_weighted"], np.average(f1, weights=support))
                self.assertAlmostEqual(metrics["f1_macro"], f1.mean())

    def test_diagnosticos_por_clase(self):
        stored = json.loads(Path("resultados/resultados.json").read_text(encoding="utf-8"))
        with Path("resultados/validacion.csv").open(encoding="utf8", newline="") as file:
            candidates = list(csv.DictReader(file))
        self.assertEqual(len(candidates), 38)
        for family, strategies in stored["best_by_balance"].items():
            for strategy in strategies:
                matching = [row for row in candidates if row["model"] == family and
                            row["balance"] == str(strategy["balance"])]
                best = max(matching, key=lambda row: (float(row["cv_weighted"]), float(row["cv_macro"])))
                self.assertAlmostEqual(float(best["cv_weighted"]), strategy["cv_weighted"])
                for k in range(1, 5):
                    key = f"cv_recall_{k}"
                    self.assertAlmostEqual(float(best[key]), strategy[key])
            diagonal = np.diag(stored["test"][family]["confusion"])
            for k, row in enumerate(stored["score_diagnostics"][family]):
                self.assertEqual(row["support"], stored["support"]["test"][k])
                self.assertTrue(diagonal[k] <= row["top2_hits"] <= row["support"])
                self.assertAlmostEqual(sum(row["mean_scores"]), 1, places=6)
