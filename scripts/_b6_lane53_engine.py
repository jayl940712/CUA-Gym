"""Faithful Python re-implementation of shopping_admin's Sales report pipeline.

Mirrors:
  src/components/reports/reportUtils.js   (periodKey, periodLabel, inRange,
                                           aggregateByPeriod, totalsOf,
                                           scopeRows, applyStatusFilter,
                                           bestsellersRows)
  src/pages/reports/SalesReports.jsx      (OrdersReport, ShippingReport,
                                           BestsellersReport)
  src/utils/formatters.js                 (formatCurrency, formatInt)

Used ONLY at authoring time to derive exact rendered cell strings.
"""
import json, datetime, os, calendar, html

ROOT = "/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_admin_mock"
AGG = json.load(open(os.path.join(ROOT, "src/data/reportAggregates.json")))
AGG_ORDER = json.load(open(os.path.join(ROOT, "src/components/reports/reportAggregatesOrder.json")))
BEST = json.load(open(os.path.join(ROOT, "src/components/reports/bestsellersAggregates.json")))

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def d(y, m, dd):
    return datetime.date(y, m, dd)


def iso(x):
    return x.isoformat()


def period_key(s, period_type):
    s = str(s)[:10]
    if period_type == 'year':
        return s[:4] + '-01-01'
    if period_type == 'month':
        return s[:7] + '-01'
    return s


def period_label(key, period_type):
    y, m, dd = [int(x) for x in key.split('-')]
    if period_type == 'year':
        return str(y)
    if period_type == 'month':
        return "%d/%d" % (m, y)
    return "%s %d, %d" % (MONTHS[m - 1], dd, y)


def in_range(row_period, frm, to):
    p = str(row_period)[:10]
    if frm and p < iso(frm):
        return False
    if to and p > iso(to):
        return False
    return True


def scope_rows(rows, store_id=0):
    return [r for r in rows if int(r['store_id']) == store_id]


def apply_status(rows, show='0', statuses=None, exclude_canceled=True):
    if str(show) == '1' and statuses:
        s = set(statuses)
        return [r for r in rows if r.get('order_status') in s]
    if not exclude_canceled:
        return rows
    return [r for r in rows if r.get('order_status') != 'canceled']


def sql_sum(acc, v):
    if v is None or v == '':
        return acc
    return (0 if acc is None else acc) + (float(v) or 0.0)


def aggregate_by_period(rows, period_type, sum_fields, extra_key=None, first_fields=()):
    buckets = {}
    order = []
    for r in rows:
        key = period_key(r['period'], period_type)
        sub = (key, extra_key(r)) if extra_key else key
        b = buckets.get(sub)
        if b is None:
            b = {'__period': key}
            for f in first_fields:
                b[f] = r.get(f)
            for f in sum_fields:
                b[f] = None
            buckets[sub] = b
            order.append(sub)
        for f in sum_fields:
            b[f] = sql_sum(b[f], r.get(f))
    out = [buckets[k] for k in order]
    out.sort(key=lambda r: r['__period'])
    return out


def totals_of(rows, fields):
    out = {}
    for f in fields:
        acc = None
        for r in rows:
            acc = sql_sum(acc, r.get(f))
        out[f] = acc
    return out


def fmt_currency(v):
    if v is None:
        return ''
    n = float(v)
    a = "%.2f" % abs(n)
    i, dec = a.split('.')
    grouped = "{:,}".format(int(i))
    return ("-" if n < 0 else "") + "$" + grouped + "." + dec


def fmt_int(v):
    if v is None:
        return ''
    return "{:,}".format(int(round(float(v))))


# --------------------------------------------------------------- reports

ORDERS_MEASURES = ['orders_count', 'total_qty_ordered', 'total_income_amount',
                   'total_invoiced_amount', 'total_refunded_amount', 'total_tax_amount',
                   'total_shipping_amount', 'total_discount_amount', 'total_canceled_amount']
ORDERS_LABELS = {'orders_count': 'Orders', 'total_qty_ordered': 'Sales Items',
                 'total_income_amount': 'Sales Total', 'total_invoiced_amount': 'Invoiced',
                 'total_refunded_amount': 'Refunded', 'total_tax_amount': 'Sales Tax',
                 'total_shipping_amount': 'Sales Shipping',
                 'total_discount_amount': 'Sales Discount', 'total_canceled_amount': 'Canceled'}
ORDERS_MONEY = set(ORDERS_MEASURES) - {'orders_count', 'total_qty_ordered'}


def orders_report(frm, to, period_type='day', show='0', statuses=None):
    src = [r for r in scope_rows(AGG['orders_aggregated_created']) if in_range(r['period'], frm, to)]
    src = apply_status(src, show, statuses, True)
    rows = aggregate_by_period(src, period_type, ORDERS_MEASURES)
    return rows, totals_of(rows, ORDERS_MEASURES)


SHIP_MEASURES = ['orders_count', 'total_shipping', 'total_shipping_actual']


def shipping_report(frm, to, period_type='day', show='0', statuses=None):
    src = [r for r in scope_rows(AGG_ORDER['shipping_aggregated_order']) if in_range(r['period'], frm, to)]
    src = apply_status(src, show, statuses, False)
    rows = aggregate_by_period(src, period_type, SHIP_MEASURES,
                               extra_key=lambda r: r['shipping_description'],
                               first_fields=('shipping_description',))
    return rows, totals_of(rows, SHIP_MEASURES)


def _table_for(base, pt):
    return "%s_%s" % (base, 'yearly' if pt == 'year' else 'monthly' if pt == 'month' else 'daily')


def bestsellers_report(frm, to, period_type='day', store_id=1, limit=5):
    daily = scope_rows(BEST.get('bestsellers_daily', []), store_id)
    main = scope_rows(BEST.get(_table_for('bestsellers', period_type), []), store_id)

    def collect(rows, label):
        by = {}
        order = []
        for r in rows:
            pid = r['product_id']
            if pid in by:
                by[pid]['qty_ordered'] += float(r['qty_ordered'] or 0)
            else:
                by[pid] = {'__period': label, 'product_id': pid, 'product_name': r['product_name'],
                           'product_price': r['product_price'], 'qty_ordered': float(r['qty_ordered'] or 0)}
                order.append(pid)
        return [by[p] for p in order]

    def boundary(bfrm, bto):
        rows = [r for r in daily if in_range(r['period'], bfrm, bto)]
        label = period_key(iso(bfrm), period_type)
        out = collect(rows, label)
        out.sort(key=lambda r: (-r['qty_ordered'], r['product_id']))
        return out[:limit]

    unions = []
    main_from, main_to, main_disabled = frm, to, False
    if period_type == 'year':
        if frm and (frm.month != 1 or frm.day != 1):
            dt_to = d(frm.year, 12, 31)
            if (not to) or dt_to < to:
                unions.append(boundary(frm, dt_to))
                main_from = d(frm.year + 1, 1, 1)
        if to and (to.month != 12 or to.day != 31):
            dt_from = d(to.year, 1, 1)
            if (not frm) or dt_from > frm:
                unions.append(boundary(dt_from, to))
                main_to = d(to.year - 1, 12, 31)
        if frm and to and frm.year == to.year:
            unions.append(boundary(frm, to))
            main_disabled = True
    elif period_type == 'month':
        if frm and frm.day != 1:
            dt_to = d(frm.year, frm.month, calendar.monthrange(frm.year, frm.month)[1])
            if (not to) or dt_to < to:
                unions.append(boundary(frm, dt_to))
                nm = d(frm.year + (frm.month // 12), (frm.month % 12) + 1, 1)
                main_from = nm
        if to and to.day != calendar.monthrange(to.year, to.month)[1]:
            dt_from = d(to.year, to.month, 1)
            if (not frm) or dt_from > frm:
                unions.append(boundary(dt_from, to))
                pm = dt_from - datetime.timedelta(days=1)
                main_to = pm
        if frm and to and frm.year == to.year and frm.month == to.month:
            unions.append(boundary(frm, to))
            main_disabled = True

    out = []
    if not main_disabled:
        rows = [r for r in main if float(r['rating_pos']) <= limit and in_range(r['period'], main_from, main_to)]
        by_period = {}
        order = []
        for r in rows:
            k = period_key(r['period'], period_type)
            by_period.setdefault(k, [])
            if k not in order:
                order.append(k)
            by_period[k].append(r)
        for k in order:
            out.extend(collect(by_period[k], k))
    for u in unions:
        out.extend(u)
    out.sort(key=lambda r: (r['__period'], -r['qty_ordered'], r['product_id']))
    return out, totals_of(out, ['qty_ordered'])


def decode_entities(s):
    return html.unescape(str(s))
