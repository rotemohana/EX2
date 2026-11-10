"""Check the receipt gallery uses real results and safely displays order text."""
import unittest
from html.parser import HTMLParser
from bakery import graph
from receipts import render_receipts
from test_bakery import CASES


class ReceiptPageTests(unittest.TestCase):
    def test_all_orders_and_totals(self):
        orders = []
        for label, item, quantity, day, city, *_ in CASES:
            order = dict(item=item, quantity=quantity, day=day, city=city)
            orders.append((label, order, graph.invoke(order)))
        page = render_receipts(orders)
        HTMLParser().feed(page)
        self.assertEqual(page.count('<article class="receipt">'), len(CASES))
        self.assertEqual(page.count('<details>'), len(CASES))
        self.assertIn('173.00₪', page)
        self.assertIn('Nothing to pay', page)
        self.assertIn('babka → sourdough', page)

    def test_escape_customer_text(self):
        order = dict(item='<script>alert(1)</script>', quantity=1, day='Monday', city='')
        page = render_receipts([('<img onerror=alert(1)>', order, graph.invoke(order))])
        self.assertNotIn('<script>', page)
        self.assertNotIn('<img ', page)
        self.assertIn('&lt;script&gt;', page)


if __name__ == '__main__':
    unittest.main()
