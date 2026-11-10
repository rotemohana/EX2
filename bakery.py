"""Deterministic Dana's Bakery workflow. Install: pip install -r requirements.txt."""
from decimal import Decimal
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

PRICES = {'challah': 18, 'babka': 45, 'rugelach': 30, 'sourdough': 25}
INITIAL_STOCK = {'challah': 10, 'babka': 0, 'rugelach': 3, 'sourdough': 4}
FALLBACK = {'babka': 'rugelach', 'rugelach': 'sourdough', 'sourdough': 'challah'}


class OrderInput(TypedDict):
    item: str
    quantity: int
    day: str
    city: str


class OrderOutput(TypedDict):
    status: str
    item: str
    delivery: str
    total: float
    message: str
    steps: list[str]


class State(OrderInput, OrderOutput):
    suggestions_count: int
    original_item: str


def build_graph(stock=None):
    """Each invocation checks an unchanged stock snapshot; orders are quotations.

    No stock is consumed between invocations. Pass a stock mapping to model a
    different inventory snapshot. Unavailable candidates count as suggestions;
    the first candidate with enough stock is automatically selected.
    """
    inventory = dict(INITIAL_STOCK if stock is None else stock)
    if set(inventory) != set(PRICES) or any(type(n) is not int or n < 0 for n in inventory.values()):
        raise ValueError('Stock must contain all four active products with nonnegative integer counts.')

    def initialize(s):
        return {'item': s.get('item', ''), 'quantity': s.get('quantity', 0),
                'day': s.get('day', ''), 'city': s.get('city', ''),
                'status': 'accepted', 'delivery': 'pickup', 'total': 0.0,
                'message': '', 'steps': ['initialize: order received'], 'suggestions_count': 0,
                'original_item': ''}

    def validate(s):
        item = s['item'].strip().lower() if isinstance(s['item'], str) else ''
        reason = ''
        if item not in PRICES:
            reason = f"I'm sorry, {item or 'that item'} isn't on our active menu."
        elif type(s['quantity']) is not int or s['quantity'] <= 0:
            reason = "I'm sorry, please order a positive whole-number quantity."
        elif not isinstance(s['day'], str) or s['day'].strip().lower() not in {
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        } or not isinstance(s['city'], str):
            reason = "I'm sorry, please provide a valid weekday and a city as text."
        return {'item': item, 'original_item': item, 'status': 'rejected' if reason else 'accepted',
                'message': reason,
                'steps': s['steps'] + ['validate: ' + (reason or 'valid order')]}

    def delivery(s):
        city = s['city'].strip()
        mode = 'delivery' if city.casefold() == 'jerusalem' else 'pickup'
        note = ("I'm sorry, we only deliver inside Jerusalem, so I've arranged free pickup for you. "
                if city and mode == 'pickup' else '')
        return {'delivery': mode, 'message': note,
                'steps': s['steps'] + [f'delivery: {mode}; fee {20 if mode == "delivery" else 0}₪']}

    def check_stock(s):
        enough = inventory[s['item']] >= s['quantity']
        return {'steps': s['steps'] + [f'stock: {s["item"]}; ' + ('sufficient' if enough else 'insufficient')]}

    def route_stock(s):
        if inventory[s['item']] >= s['quantity']:
            return 'price'
        return 'substitute' if s['suggestions_count'] < 2 and s['item'] in FALLBACK else 'reject'

    def substitute(s):
        candidate = FALLBACK[s['item']]
        count = s['suggestions_count'] + 1
        return {'item': candidate, 'suggestions_count': count,
                'message': s['message'] + f"We're short of {s['item']}; let me try {candidate} for you. ",
                'steps': s['steps'] + [f'substitute: suggestion {count}: {candidate}']}

    def reject(s):
        return {'status': 'rejected', 'total': 0.0,
                'message': s['message'] + "I'm so sorry, we can't fill your full quantity today, so your order is cancelled. We'd love to bake for you another day! — Dana",
                'steps': s['steps'] + ['reject: no fulfillable substitute within two suggestions']}

    def price(s):
        goods = Decimal(PRICES[s['item']]) * s['quantity']
        friday = s['day'].strip().lower() == 'friday'
        discount = goods * Decimal('0.15') if goods > 150 and not friday else Decimal(0)
        fee = 20 if s['delivery'] == 'delivery' else 0
        total = (goods - discount + fee).quantize(Decimal('0.01'))
        receipt = [f"Lovely! Your {s['quantity']} × {s['item']} are reserved for {s['delivery']}."]
        if s['suggestions_count']:
            receipt.append(f"Substitution: {s['original_item']} → {s['item']} (same quantity: {s['quantity']}).")
        receipt.extend(['', f"Baked goods: {s['quantity']} × {PRICES[s['item']]:.2f}₪ = {goods:.2f}₪"])
        if discount:
            receipt.append(f'Your 15% baked-goods discount: −{discount:.2f}₪')
        elif friday:
            receipt.append('Discount: 0.00₪ — discounts take a break on Fridays.')
        else:
            receipt.append('Discount: 0.00₪ — 15% off applies when baked goods exceed 150.00₪.')
        receipt.extend([f'Jerusalem delivery: {fee:.2f}₪' if fee else 'Pickup: 0.00₪',
                        f'Total: {total:.2f}₪', '', 'Thank you for ordering! — Dana'])
        prefix = s['message'].strip()
        return {'total': float(total), 'message': (prefix + '\n\n' if prefix else '') + '\n'.join(receipt),
                'steps': s['steps'] + [f'price: goods={goods}; discount={discount}; delivery={fee}; total={total}']}

    def finish(s):
        return {'steps': s['steps'] + [f'finish: {s["status"]}']}

    builder = StateGraph(State, input_schema=OrderInput, output_schema=OrderOutput)
    for name, node in [('initialize', initialize), ('validate', validate), ('delivery', delivery),
                       ('check_stock', check_stock), ('substitute', substitute),
                       ('reject', reject), ('price', price), ('finish', finish)]:
        builder.add_node(name, node)
    builder.add_edge(START, 'initialize')
    builder.add_edge('initialize', 'validate')
    builder.add_conditional_edges('validate', lambda s: s['status'], {'accepted': 'delivery', 'rejected': 'finish'})
    builder.add_edge('delivery', 'check_stock')
    builder.add_conditional_edges('check_stock', route_stock, {'price': 'price', 'substitute': 'substitute', 'reject': 'reject'})
    builder.add_edge('substitute', 'check_stock')
    builder.add_edge('reject', 'finish')
    builder.add_edge('price', 'finish')
    builder.add_edge('finish', END)
    return builder.compile()


graph = build_graph()


if __name__ == '__main__':
    from pprint import pprint
    pprint(graph.invoke({'item': 'babka', 'quantity': 2, 'day': 'Monday', 'city': 'Jerusalem'}))
