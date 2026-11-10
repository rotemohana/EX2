"""Build an offline HTML receipt gallery from actual graph results."""
from html import escape
from pathlib import Path


def render_receipts(orders):
    """orders contains (label, input dictionary, graph output dictionary) tuples."""
    cards = []
    accepted = sum(result['status'] == 'accepted' for _, _, result in orders)
    for number, (label, order, result) in enumerate(orders, 1):
        ok = result['status'] == 'accepted'
        status = 'Accepted' if ok else 'Cancelled'
        diary = ''.join(f'<li>{escape(step)}</li>' for step in result['steps'])
        message = ''.join(f'<div class="line{ " total-line" if line.startswith("Total:") else ""}">{escape(line) or "&nbsp;"}</div>'
                          for line in result['message'].splitlines())
        cards.append(f'''<article class="receipt">
          <div class="card-top"><span>ORDER {number:03d}</span><span class="badge {'ok' if ok else 'cancelled'}">{status}</span></div>
          <h2>{escape(str(label)).title()}</h2>
          <p class="meta">Requested: {escape(str(order['quantity']))} × {escape(str(order['item']))}<br>
          {escape(str(order['day']))} · {escape(str(order['city'])) or 'Pickup at the bakery'}</p>
          <div class="message">{message}</div>
          <div class="amount"><span>{'Amount to pay' if ok else 'Nothing to pay'}</span><strong>{result['total']:.2f}₪</strong></div>
          <details><summary>How we processed this order</summary><ol>{diary}</ol></details>
          </article>''')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Dana's Bakery · Your receipts</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f7f1e8;color:#35251e;font-family:Arial,sans-serif}
    header{background:#3e2923;color:#fff5e5;padding:42px max(24px,calc((100% - 1180px)/2))}
    .eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:3px;color:#edc49a}
    h1{font-family:Georgia,serif;font-size:clamp(32px,5vw,54px);margin:12px 0}header p{color:#edd9c9;line-height:1.6}
    main{max-width:1228px;margin:auto;padding:28px 24px}.summary{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:26px}
    .summary span{background:#ede1d2;padding:12px 18px;border-radius:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:24px;align-items:start}
    .receipt{background:#fffdf8;border:1px solid #e4d7c6;border-radius:18px;padding:26px;box-shadow:0 7px 22px #4630240a}
    .card-top{display:flex;justify-content:space-between;align-items:center;gap:10px;color:#806a5b;font-size:11px;letter-spacing:1px}
    .badge{padding:7px 10px;border-radius:20px;font-weight:bold;letter-spacing:0}.ok{background:#e3eee0;color:#335a34}.cancelled{background:#f7e2dc;color:#903f30}
    h2{font-family:Georgia,serif;font-size:27px;margin:22px 0 10px}.meta{color:#806a5b;font-size:13px;line-height:1.8;padding-bottom:18px;border-bottom:1px dashed #d6c4b0}
    .message{font-size:14px;line-height:1.7;overflow-wrap:anywhere}.total-line{font-weight:bold}.amount{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:22px;padding:18px 0;border-top:1px dashed #d6c4b0}.amount span{color:#806a5b;font-size:13px}.amount strong{font-size:27px}
    details{border-top:1px solid #eee3d5;padding-top:16px;font-size:12px;color:#806a5b}summary{cursor:pointer}li{margin:9px 0;overflow-wrap:anywhere}
    footer{text-align:center;padding:32px;color:#806a5b;font-size:12px}
    @media print{body{background:white}header{background:white;color:#35251e}header p,.eyebrow{color:#806a5b}.summary{display:none}.grid{display:block}.receipt{break-inside:avoid;margin-bottom:20px;box-shadow:none}details{display:none}}
    </style></head><body><header><div class="eyebrow">Freshly baked · Made with care</div>
    <h1>Dana's Bakery</h1><p>Your orders, beautifully wrapped up.<br>Every total explained, every substitution shown.</p></header><main>
    <div class="summary">''' + f'<span>{len(orders)} orders</span><span>{accepted} accepted</span><span>{len(orders)-accepted} cancelled</span>' + '''</div>
    <section class="grid" aria-label="Order receipts">''' + ''.join(cards) + '''</section></main>
    <footer>With love, Dana · Independent quotes against the initial inventory · Print or save this page for your records.</footer></body></html>'''


def save_receipts(orders, filename='bakery_receipts.html'):
    path = Path(filename)
    path.write_text(render_receipts(orders), encoding='utf-8')
    return path


if __name__ == '__main__':
    from bakery import graph
    from test_bakery import CASES
    orders = []
    for label, item, quantity, day, city, *_ in CASES:
        order = dict(item=item, quantity=quantity, day=day, city=city)
        orders.append((label, order, graph.invoke(order)))
    print(save_receipts(orders).resolve())
