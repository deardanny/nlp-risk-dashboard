"""Run brand expansion and features on fictional posts without database calls."""
import ast
import json
from pathlib import Path
import re
import unittest
from unittest.mock import Mock

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ['brand-classification.ipynb', 'brand-classification_en.ipynb']


def read_posts(name, rows):
    notebook = json.loads((ROOT / name).read_text())
    source = next(''.join(c['source']) for c in notebook['cells']
                  if c['cell_type'] == 'code' and 'content_query = ' in ''.join(c['source']))
    cursor = Mock()
    cursor.execute.return_value = iter(rows)
    namespace = {'pd': pd, 'cur': cursor, 'five_days_ago': '2026-01-01',
                 'five_days_ago_str': '2026-01-01'}
    exec(compile(source, name, 'exec'), namespace)
    return namespace['content']


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
    def test_empty_query_result_reaches_brand_processing(self):
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                posts = read_posts(name, [])
                self.assertTrue(posts.empty)
                self.assertEqual(len(posts.columns), 16)
                self.assertTrue({'CONTENTS', 'TITLE', 'YEAR', 'MONTH'} <= set(posts.columns))
                result = expand_posts(name, posts)
                self.assertTrue(result.empty)
                self.assertTrue({'BRAND', 'UNIQUE_ID', 'RISK_YN'} <= set(result.columns))

    def test_nonempty_query_preserves_fields_and_date_features(self):
        row = (7, 'demo-7', 'Demo board', 'Demo community', 'Huggies example',
               None, None, 'Demo author', 'https://example.com/post/7',
               '2026-01-03', '2026-01-04', 10, 2, 1)
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                posts = read_posts(name, [row])
                self.assertEqual(posts.loc[0, 'CONTENTS'], '')
                self.assertEqual(posts.loc[0, 'WDATE'], '2026-01-03')
                self.assertEqual(posts.loc[0, 'RDATE'], '2026-01-04')
                self.assertEqual(posts.loc[0, 'YEAR'], 2026)
                self.assertEqual(posts.loc[0, 'MONTH'], 1)
                self.assertEqual(posts.loc[0, 'VIEWS'], 10)
                result = expand_posts(name, posts)
                self.assertEqual(result['UNIQUE_ID'].tolist(), ['7-Huggies'])

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
