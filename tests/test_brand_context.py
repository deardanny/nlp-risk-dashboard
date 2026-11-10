"""Check context extraction with fictional text, without warehouse access."""
import ast
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ['brand-classification.ipynb', 'brand-classification_en.ipynb']


def context_functions(name):
    notebook = json.loads((ROOT / name).read_text())
    source = next(''.join(cell['source']) for cell in notebook['cells']
                  if cell['cell_type'] == 'code'
                  and 'def find_nearby_sentences(' in ''.join(cell['source']))
    names = {'find_nearby_sentences', 'extract_brand_sentence'}
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {'re': re, 'brand_keywords_list': {'Demo': ['DemoBrand', '데모브랜드']}}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), name, 'exec'), namespace)
    return namespace


class BrandContextTests(unittest.TestCase):
    def test_context_keeps_source_order_and_repeated_sentences(self):
        text = 'Repeat. DEMOBRAND sample. Repeat. Unrelated ending.'
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                extract = context_functions(name)['find_nearby_sentences']
                self.assertEqual(extract(text, ['demobrand'], window=1),
                                 'Repeat. DEMOBRAND sample. Repeat.')

    def test_overlapping_windows_do_not_duplicate_positions(self):
        text = 'Opening. DemoBrand first. Shared. DemoBrand second. Closing.'
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                extract = context_functions(name)['find_nearby_sentences']
                self.assertEqual(extract(text, ['demobrand'], window=1), text)
                self.assertEqual(extract(text, ['absent'], window=1), '')
                self.assertEqual(extract(text, ['demobrand'], window=0),
                                 'DemoBrand first. DemoBrand second.')

    def test_brand_excerpt_matches_case_insensitive_detection(self):
        for name in NOTEBOOKS:
            for mention in ['DEMOBRAND', 'demobrand', 'DemoBrand', '데모브랜드']:
                with self.subTest(notebook=name, mention=mention):
                    extract = context_functions(name)['extract_brand_sentence']
                    row = {'BRAND': 'Demo', 'TITLE': 'Title fallback',
                           'CONTENTS': f'Before;{mention} sample;After;Outside'}
                    self.assertEqual(extract(row), f'Before {mention} sample After')

    def test_no_matching_brand_uses_title(self):
        for name in NOTEBOOKS:
            with self.subTest(notebook=name):
                extract = context_functions(name)['extract_brand_sentence']
                self.assertEqual(extract({'BRAND': 'Demo', 'TITLE': 'Title fallback',
                                          'CONTENTS': 'An unrelated sample.'}), 'Title fallback')


if __name__ == '__main__':
    unittest.main()
