# Dana's Bakery

A deterministic Python order-processing system built with LangGraph. It validates
orders, handles delivery and substitutions, and calculates discounts without LLM
calls or API keys.

## Run in Google Colab

Open `danas_bakery.ipynb` in Google Colab and choose **Runtime → Run all**.
It contains the full implementation, diagram rendering, 14 example orders,
and automated assertions, including discount boundary checks.

## Run locally

With Python 3.10+:

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python bakery.py
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

## Behavior and assumptions

`prompt.md` preserves the supplied specification. `bakery.py` exposes the compiled
`graph` and `build_graph(stock=None)`. Each invocation returns exactly the six
specified output keys. No language model or API key is used.

Orders are independent quotes against the initial inventory: no stock depletion
occurs across invocations. Empty city means pickup. Outside cities are converted
to pickup with an explanation. Each next product checked counts as one suggestion;
the first available candidate is selected automatically, with a maximum of two.
On rejection, `item` is the last attempted item and `total` is zero.

The notebook calls `draw_mermaid_png()`; its default renderer uses an external
Mermaid rendering service. If unavailable, Mermaid text is displayed instead.

Regenerate the notebook after source edits using `python make_notebook.py`.

LangGraph API references:
[StateGraph and output schemas](https://reference.langchain.com/python/langgraph/graph/state/StateGraph)
and [draw_mermaid_png](https://reference.langchain.com/python/langchain-core/runnables/graph/Graph/draw_mermaid_png).
