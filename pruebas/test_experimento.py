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
