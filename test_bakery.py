"""Run with: python -m unittest -v"""
import unittest
from bakery import build_graph, graph


# label, item, quantity, day, city, status, final item, delivery, total, attempts
CASES = [
    ('delivery', 'challah', 2, 'Monday', 'Jerusalem', 'accepted', 'challah', 'delivery', 56, 0),
    ('pickup', 'sourdough', 2, 'Thursday', '', 'accepted', 'sourdough', 'pickup', 50, 0),
    ('discount', 'challah', 10, 'Monday', 'Jerusalem', 'accepted', 'challah', 'delivery', 173, 0),
    ('Friday', 'challah', 10, 'Friday', 'Jerusalem', 'accepted', 'challah', 'delivery', 200, 0),
    ('outside', 'challah', 2, 'Monday', 'Tel Aviv', 'accepted', 'challah', 'pickup', 36, 0),
    ('first substitute', 'babka', 2, 'Monday', '', 'accepted', 'rugelach', 'pickup', 60, 1),
    ('second substitute', 'babka', 4, 'Monday', '', 'accepted', 'sourdough', 'pickup', 100, 2),
    ('limit', 'babka', 5, 'Monday', '', 'rejected', 'sourdough', 'pickup', 0, 2),
    ('challah fallback', 'sourdough', 9, 'Monday', '', 'accepted', 'challah', 'pickup', 137.7, 1),
    ('no fallback', 'challah', 11, 'Monday', '', 'rejected', 'challah', 'pickup', 0, 0),
    ('discontinued', 'croissants', 1, 'Monday', '', 'rejected', 'croissants', 'pickup', 0, 0),
    ('unknown', 'pizza', 1, 'Monday', '', 'rejected', 'pizza', 'pickup', 0, 0),
    ('zero', 'challah', 0, 'Monday', '', 'rejected', 'challah', 'pickup', 0, 0),
    ('negative', 'challah', -2, 'Monday', '', 'rejected', 'challah', 'pickup', 0, 0),
]


class BakeryTests(unittest.TestCase):
    def test_orders(self):
        for label, item, quantity, day, city, status, final, mode, total, attempts in CASES:
            with self.subTest(label=label):
                result = graph.invoke(dict(item=item, quantity=quantity, day=day, city=city))
                self.assertEqual(set(result), {'status', 'item', 'delivery', 'total', 'message', 'steps'})
                self.assertEqual((result['status'], result['item'], result['delivery']), (status, final, mode))
                self.assertAlmostEqual(result['total'], total)
                self.assertEqual(sum(step.startswith('substitute:') for step in result['steps']), attempts)
                self.assertTrue(result['message'])
                self.assertEqual(result['steps'][-1], f'finish: {status}')
                if label == 'outside':
                    self.assertIn('only deliver inside Jerusalem', result['message'])

    def test_exact_discount_boundary(self):
        # Six sourdough loaves require a custom snapshot: initial stock is four.
        custom = build_graph({'challah': 10, 'babka': 0, 'rugelach': 3, 'sourdough': 7})
        for qty, expected in [(6, 170), (7, 168.75)]:
            result = custom.invoke(dict(item='sourdough', quantity=qty, day='Monday', city='Jerusalem'))
            self.assertEqual(result['total'], expected)

    def test_repeatable_and_malformed(self):
        order = dict(item=' CHALLAH ', quantity=10, day=' friday ', city=' jerusalem ')
        self.assertEqual(graph.invoke(order), graph.invoke(order))
        self.assertEqual(graph.invoke(order)['total'], 200)
        for qty in [True, 1.5, '2', None]:
            self.assertEqual(graph.invoke({**order, 'quantity': qty})['status'], 'rejected')

    def test_receipts(self):
        for label, item, quantity, day, city, status, final, mode, total, attempts in CASES:
            with self.subTest(label=label):
                message = graph.invoke(dict(item=item, quantity=quantity, day=day, city=city))['message']
                if status == 'rejected':
                    self.assertNotIn('Baked goods:', message)
                    self.assertNotIn('Total:', message)
                    continue
                self.assertIn(f'Total: {total:.2f}₪', message)
                self.assertIn('Jerusalem delivery: 20.00₪' if mode == 'delivery' else 'Pickup: 0.00₪', message)
                if attempts:
                    self.assertIn(f'Substitution: {item} → {final} (same quantity: {quantity}).', message)
                else:
                    self.assertNotIn('Substitution:', message)
                if label == 'discount':
                    self.assertIn('Baked goods: 10 × 18.00₪ = 180.00₪', message)
                    self.assertIn('Your 15% baked-goods discount: −27.00₪', message)
                elif label == 'Friday':
                    self.assertIn('Discount: 0.00₪ — discounts take a break on Fridays.', message)
                    self.assertNotIn('−27.00₪', message)
                elif label == 'pickup':
                    self.assertIn('baked goods exceed 150.00₪', message)


if __name__ == '__main__':
    unittest.main()
