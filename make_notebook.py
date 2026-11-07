"""Regenerate the standalone Colab notebook from the Python sources."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent


def cell(kind, source):
    result = {'cell_type': kind, 'metadata': {}, 'source': source.splitlines(keepends=True)}
    if kind == 'code':
        result.update(execution_count=None, outputs=[])
    return result


intro = """# Dana's Bakery — deterministic LangGraph
Run all cells in Google Colab. No API keys or LLM calls are used.

Each order uses an unchanged inventory snapshot (no stock depletion between
invocations). Empty city means pickup; another city triggers a friendly pickup
conversion. Substitution is automatic: each next candidate counts as one attempt,
including unavailable candidates, and at most two candidates are checked.
On rejection, `item` records the last attempted product and `total` is zero.
Prices use Decimal arithmetic; the output total is a float in shekels.

The diagram cell uses `draw_mermaid_png()`, whose default renderer requires
network access to Mermaid's rendering service. Order processing runs locally.
"""
tests = (root / 'test_bakery.py').read_text(encoding='utf-8').replace(
    'from bakery import build_graph, graph\n', '').replace(
    "if __name__ == '__main__':\n    unittest.main()", 
    "suite = unittest.defaultTestLoader.loadTestsFromTestCase(BakeryTests)\nresult = unittest.TextTestRunner(verbosity=2).run(suite)\nassert result.wasSuccessful()")
source = (root / 'bakery.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
notebook = {'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'colab': {'name': 'danas_bakery.ipynb'},
                         'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}},
            'cells': [cell('markdown', intro), cell('code', '%pip install -q "langgraph>=1.0,<2.0"'),
                      cell('code', source),
                      cell('code', 'from IPython.display import Image, display\ntry:\n    display(Image(graph.get_graph().draw_mermaid_png()))\nexcept Exception as exc:\n    print(f"PNG renderer unavailable: {exc}")\n    print(graph.get_graph().draw_mermaid())'),
                      cell('markdown', '## Example orders and automated checks'),
                      cell('code', tests),
                      cell('code', 'from pprint import pprint\nfor label, item, quantity, day, city, *_ in CASES:\n    print(label)\n    pprint(graph.invoke(dict(item=item, quantity=quantity, day=day, city=city)))')]}
for index, entry in enumerate(notebook['cells']):
    entry['id'] = f'bakery-{index}'
(root / 'danas_bakery.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')
