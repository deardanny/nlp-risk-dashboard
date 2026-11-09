"""Exercise the review batch cells with synthetic rows, without API/warehouse calls."""
import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ['internal-review-analysis.ipynb', 'internal-review-analysis_en.ipynb.ipynb']


def run_batch(name, reviews):
    notebook = json.loads((ROOT / name).read_text())
    source = next(''.join(cell['source']) for cell in notebook['cells']
                  if cell['cell_type'] == 'code' and 'col_sub, col_word, col_sentiment, col_date = ' in ''.join(cell['source']))
    calls, errors = [], []

    def extract_keywords(batch, brand):
        calls.append((brand, batch.tolist()))
        return "{'satisfied': ['soft'], 'unsatisfied': ['stiff']}"

    namespace = {'pd': pd, 'ast': ast, 'review': reviews,
                 'TARGET_SUBBRANDS': ['DemoA', 'DemoB', 'Absent'],
                 'start': '2026-01-01', 'end': '2026-01-02',
                 'extract_keywords': extract_keywords,
                 'time': SimpleNamespace(sleep=lambda seconds: errors.append(seconds))}
    with redirect_stdout(io.StringIO()):
        exec(compile(source, name, 'exec'), namespace)
    return calls, errors, namespace['output']


class ReviewBatchTests(unittest.TestCase):
    def test_batches_use_the_loaded_review_column_and_keep_all_rows(self):
        reviews = pd.DataFrame({
            'DATE': ['20260101'] * 5 + ['20260102'],
            'BRAND': ['Demo'] * 6,
            'SUBBRAND': ['DemoA', 'DemoB', 'DemoA', 'DemoA', 'DemoA', 'DemoA'],
            'REVIEW': [f'Fictional review {i}' for i in range(6)],
        }, index=[2, 8, 15, 30, 41, 70])
        expected_calls = [
            ('DemoA', ['Fictional review 0', 'Fictional review 2', 'Fictional review 3']),
            ('DemoA', ['Fictional review 4']),
            ('DemoA', ['Fictional review 5']),
            ('DemoB', ['Fictional review 1']),
        ]
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                calls, errors, output = run_batch(name, reviews)
                self.assertEqual(calls, expected_calls)
                self.assertEqual(errors, [])
                self.assertEqual(len(output), 8)
                self.assertEqual(output['SUBBRAND'].tolist(), ['DemoA'] * 6 + ['DemoB'] * 2)
                self.assertEqual(output['DATE'].tolist(), ['2026-01-01'] * 4 + ['2026-01-02'] * 2 + ['2026-01-01'] * 2)
                self.assertEqual(output['KEYWORD'].tolist(), ['soft', 'stiff'] * 4)

    def test_empty_review_table_makes_no_model_calls(self):
        reviews = pd.DataFrame(columns=['DATE', 'BRAND', 'SUBBRAND', 'REVIEW'])
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                calls, errors, output = run_batch(name, reviews)
                self.assertEqual(calls, [])
                self.assertEqual(errors, [])
                self.assertTrue(output.empty)
                self.assertEqual(list(output.columns), ['DATE', 'START_DT', 'END_DT', 'SUBBRAND', 'KEYWORD', 'SENTIMENT'])


if __name__ == '__main__':
    unittest.main()
