# Dana's Bakery

A deterministic Python order-processing system built with LangGraph. It validates
orders, handles delivery and substitutions, and calculates discounts without LLM
calls or API keys.

## Run in Google Colab

Open `danas_bakery.ipynb` in Google Colab and choose **Runtime → Run all**.
It contains the full implementation, diagram rendering, 14 example orders,
and automated assertions, including discount boundary checks.
The final cells display a designed receipt gallery for all example orders. Click
**Download receipt page**, then open `bakery_receipts.html` in your browser for
a separate page. Accepted and cancelled orders appear with explanations, totals,
and expandable processing diaries. Add your own orders to the final cell's list.

## Run locally

With Python 3.10+:

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python bakery.py
python receipts.py
```

## Project files

| File | Purpose |
| --- | --- |
| `prompt.md` | Original technical specification |
| `danas_bakery.ipynb` | Standalone Colab notebook, diagram, examples, and checks |
| `bakery.py` | Graph implementation and example invocation |
| `test_bakery.py` | Business-rule and output-contract tests |
| `make_notebook.py` | Regenerates the notebook from the Python sources |
| `requirements.txt` | Python dependencies |
| `receipts.py` | Offline HTML receipt gallery generator |

Locally, open the generated `bakery_receipts.html` in any browser. The page is
self-contained and can be printed or saved as PDF using the browser print menu.

## Behavior and assumptions

`prompt.md` preserves the supplied specification. `bakery.py` exposes the compiled
`graph` and `build_graph(stock=None)`. Each invocation returns exactly the six
specified output keys. No language model or API key is used.

Orders are independent quotes against the initial inventory: no stock depletion
occurs across invocations. Empty city means pickup. Outside cities are converted
to pickup with an explanation. Each next product checked counts as one suggestion;
the first available candidate is selected automatically, with a maximum of two.
On rejection, `item` is the last attempted item and `total` is zero.

Accepted orders include an itemized receipt in `message`: quantity and unit price,
baked-goods subtotal, discount or eligibility explanation, delivery or free pickup,
and final total. Substitutions show the original and final products. This bonus
preserves the six output keys and explains Friday's discount exclusion.

The notebook calls `draw_mermaid_png()`; its default renderer uses an external
Mermaid rendering service. If unavailable, Mermaid text is displayed instead.

Regenerate the notebook after source edits using `python make_notebook.py`.

LangGraph API references:
[StateGraph and output schemas](https://reference.langchain.com/python/langgraph/graph/state/StateGraph)
and [draw_mermaid_png](https://reference.langchain.com/python/langchain-core/runnables/graph/Graph/draw_mermaid_png).
