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
Accepted messages include itemized receipts, discount explanations, and any
original-to-final product substitution, keeping the same six output keys.

The diagram cell uses `draw_mermaid_png()`, whose default renderer requires
network access to Mermaid's rendering service. Order processing runs locally.
"""
tests = (root / 'test_bakery.py').read_text(encoding='utf-8').replace(
    'from bakery import build_graph, graph\n', '').replace(
    "if __name__ == '__main__':\n    unittest.main()", 
    "suite = unittest.defaultTestLoader.loadTestsFromTestCase(BakeryTests)\nresult = unittest.TextTestRunner(verbosity=2).run(suite)\nassert result.wasSuccessful()")
source = (root / 'bakery.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
receipt_source = (root / 'receipts.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
gallery = '''from IPython.display import HTML, display
orders = []
for label, item, quantity, day, city, *_ in CASES:
    order = dict(item=item, quantity=quantity, day=day, city=city)
    orders.append((label, order, graph.invoke(order)))

# Add your own orders here before saving the page:
# order = dict(item='challah', quantity=10, day='Monday', city='Jerusalem')
# orders.append(('My order', order, graph.invoke(order)))

receipt_path = save_receipts(orders)
page = render_receipts(orders)
display(HTML('<iframe title="Dana bakery receipts" style="width:100%;height:1000px;border:0;border-radius:16px" srcdoc="' + escape(page, quote=True) + '"></iframe>'))

try:
    from google.colab import files
    import ipywidgets as widgets
    download = widgets.Button(description='Download receipt page', icon='download', layout=widgets.Layout(width='240px'))
    download.on_click(lambda _: files.download(str(receipt_path)))
    display(download)
    print('Click Download receipt page, then open bakery_receipts.html in your browser for a full page view.')
except ImportError:
    from IPython.display import FileLink
    display(FileLink(str(receipt_path)))
'''
notebook = {'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'colab': {'name': 'danas_bakery.ipynb'},
                         'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}},
            'cells': [cell('markdown', intro), cell('code', '%pip install -q "langgraph>=1.0,<2.0"'),
                      cell('code', source),
                      cell('code', 'from IPython.display import Image, display\ntry:\n    display(Image(graph.get_graph().draw_mermaid_png()))\nexcept Exception as exc:\n    print(f"PNG renderer unavailable: {exc}")\n    print(graph.get_graph().draw_mermaid())'),
                      cell('markdown', '## Example orders and automated checks'),
                      cell('code', tests),
                      cell('markdown', '## Your receipt page\nRun the following cells to see every order as a designed receipt. Click **Download receipt page**, then open the downloaded HTML file for a full browser page. Edit the orders list to include your own orders.'),
                      cell('code', receipt_source), cell('code', gallery)]}
for index, entry in enumerate(notebook['cells']):
    entry['id'] = f'bakery-{index}'
(root / 'danas_bakery.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')
