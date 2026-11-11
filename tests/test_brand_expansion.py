"""Run brand expansion and features on fictional posts without database calls."""
import ast
import json
from pathlib import Path
import re
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ['brand-classification.ipynb', 'brand-classification_en.ipynb']


def expand_posts(name, posts):
    notebook = json.loads((ROOT / name).read_text())
    sources = [''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code']
    namespace = {'pd': pd, 're': re, 'content': posts}
    # Read the notebook's own keyword constants, excluding imports and I/O.
    for source in sources:
        if 'BRAND_KEYWORDS = ' not in source:
            continue
        constants = [node for node in ast.parse(source).body if isinstance(node, ast.Assign)
                     and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id in {'BRAND_KEYWORDS', 'TARGET_BRANDS', 'LEAKAGE_KEYWORDS', 'RISK_KEYWORDS'}]
        exec(compile(ast.Module(body=constants, type_ignores=[]), name, 'exec'), namespace)
    for marker in ['def detect_brands(', 'def check_leakage(']:
        source = next(s for s in sources if marker in s)
        exec(compile(source, name, 'exec'), namespace)
    return namespace['expanded_content']


class BrandExpansionTests(unittest.TestCase):
    def test_no_brand_matches_keeps_an_empty_valid_schema(self):
        posts = pd.DataFrame([{'SEQ': 1, 'TITLE': 'Fictional daily note',
                               'CONTENTS': 'A quiet afternoon.', 'MEDIA': None}])
        for name in NOTEBOOKS:
            for content in [posts, posts.iloc[:0]]:
                with self.subTest(notebook=name, posts=len(content)):
                    result = expand_posts(name, content)
                    self.assertTrue(result.empty)
                    self.assertTrue(set(posts.columns) | {'BRAND', 'UNIQUE_ID', 'CONTENTS_S',
                                    'LEAKAGE_YN', 'MEDIA_YN', 'RISK_YN', 'RISK_KEYWORD'} <= set(result.columns))

    def test_multiple_brand_matches_still_expand_one_post(self):
        posts = pd.DataFrame([{'SEQ': 7, 'TITLE': 'Fictional comparison',
                               'CONTENTS': 'Huggies sample and Pampers sample.', 'MEDIA': None}])
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                result = expand_posts(name, posts)
                # The Korean dictionary uses Korean aliases for Pampers.
                expected = {'Huggies'} if name == 'brand-classification.ipynb' else {'Huggies', 'Pampers'}
                self.assertEqual(set(result['BRAND']), expected)
                self.assertEqual(set(result['UNIQUE_ID']), {'7-' + brand for brand in expected})
                self.assertTrue(result['CONTENTS'].eq(posts.iloc[0]['CONTENTS']).all())


if __name__ == '__main__':
    unittest.main()
