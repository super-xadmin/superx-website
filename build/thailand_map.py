# -*- coding: utf-8 -*-
"""Thailand map for the about page: a tilted 3D board with all 77 provinces, the company base and arcs to each zone.

Province shapes come from apisit/thailand.json (MIT licence), stored in thailand_provinces.json as a flat map
(x = (longitude - 97.2) * 40 * cos 13.5°, y = (20.6 - latitude) * 40). Here the flat map is turned, tilted back
and drawn in perspective, so it looks like a model of the country lying on a table.
"""
import json
import math
import os
import re

from core import esc, s, tri, items, TC, B

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thailand_provinces.json'), encoding='utf-8') as _f:
    PROVINCES = json.load(_f)
for _p in PROVINCES:
    _p['pts'] = [[tuple(float(v) for v in xy.split(',')) for xy in ring.split()] for ring in _p['rings']]

_K, _C, _LON0, _LAT0 = 40, math.cos(math.radians(13.5)), 97.2, 20.6
CX, CY = 168.0, 303.0                      # middle of the flat map
TILT, TURN, FOCAL = math.radians(56), math.radians(-12), 700.0
DEPTH = 9                                  # thickness of the board
PIN, HQ_PIN = 17, 34                       # height of the pins

ALIASES = {'กรุงเทพ': 'กรุงเทพมหานคร', 'กรุงเทพฯ': 'กรุงเทพมหานคร', 'กทม': 'กรุงเทพมหานคร', 'กทม.': 'กรุงเทพมหานคร',
           'bangkok': 'กรุงเทพมหานคร', 'อยุธยา': 'พระนครศรีอยุธยา', 'ayutthaya': 'พระนครศรีอยุธยา', 'โคราช': 'นครราชสีมา',
           'korat': 'นครราชสีมา', 'chonburi': 'ชลบุรี', 'lopburi': 'ลพบุรี', 'buriram': 'บุรีรัมย์', 'phang nga': 'พังงา'}


def _key(name):
    n = re.sub(r'^\s*(จังหวัด|จ\.)\s*', '', (name or '').strip()).strip().lower()
    return ALIASES.get(n, n)


_BY_NAME = {}
for _i, _p in enumerate(PROVINCES):
    _BY_NAME[_p['th']] = _i
    _BY_NAME[_p['en'].lower()] = _i
    _BY_NAME[_p['en'].lower().replace(' ', '')] = _i
_BY_NAME['bangkok metropolis'] = _BY_NAME['กรุงเทพมหานคร']


def find_province(name):
    k = _key(name)
    return _BY_NAME.get(k, _BY_NAME.get(k.replace(' ', '')))


def _inside(pt, ring):
    x, y = pt
    hit = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def province_at(pt):
    """Province under a point; a point just off the coast counts for the nearest province."""
    for i, p in enumerate(PROVINCES):
        if any(_inside(pt, r) for r in p['pts']):
            return i
    best, near = None, 12.0
    for i, p in enumerate(PROVINCES):
        for ring in p['pts']:
            for q in ring:
                dist = math.dist(pt, q)
                if dist < near:
                    best, near = i, dist
    return best


def _num(v, default):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def flat(lat, lng):
    return (lng - _LON0) * _K * _C, (_LAT0 - lat) * _K


def proj(pt, lift=0.0):
    """Flat map point → point on the tilted board (lift raises it above the board)."""
    dx, dy = pt[0] - CX, pt[1] - CY
    rx = dx * math.cos(TURN) - dy * math.sin(TURN)
    ry = dx * math.sin(TURN) + dy * math.cos(TURN)
    k = FOCAL / (FOCAL - ry * math.sin(TILT))
    return rx * k, (ry * math.cos(TILT) - lift) * k


def _arc(a, b, n=30):
    """Route from a to b that bends a little sideways and rises above the board in the middle."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    bend = min(0.12 * dist, 30)
    cx, cy = (x1 + x2) / 2 - dy / dist * bend, (y1 + y2) / 2 + dx / dist * bend
    height = max(12, min(0.35 * dist, 110))
    out = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t * t * x2
        y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2
        out.append(proj((x, y), height * math.sin(math.pi * t)))
    return out


def _f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def thai_map(d, uid='thm'):
    """HTML for the 3D map plus the numbered list of zones. Empty when no zones are set."""
    pts = [p for p in items(d, 'map_points') if s(p, 'lat') != '' and s(p, 'lng') != '']
    if not pts:
        return ''
    o_flat = flat(_num(d.get('map_origin_lat'), 13.52), _num(d.get('map_origin_lng'), 100.66))
    home = province_at(o_flat)

    zones = {}                               # province index → set of zone numbers
    grounds, arcs = [], []
    for i, p in enumerate(pts):
        pf = flat(_num(p.get('lat'), 13.7), _num(p.get('lng'), 100.5))
        names = [n for n in re.split(r'[,،、/·\n]+', s(p, 'provinces')) if n.strip()]
        idx = [k for k in (find_province(n) for n in names) if k is not None] or [province_at(pf)]
        for k in idx:
            if k is not None and k != home:
                zones.setdefault(k, set()).add(i)
        grounds.append(proj(pf))
        arcs.append(_arc(o_flat, pf))
    o = proj(o_flat)
    # pins near the company base stand taller so their heads never cover each other
    heads = [(o[0], o[1] - HQ_PIN), (o[0] + 50, o[1] - HQ_PIN)]     # the HQ head and its name
    tall = [PIN] * len(grounds)
    for i in sorted(range(len(grounds)), key=lambda j: math.dist(grounds[j], o)):
        gx, gy = grounds[i]
        while tall[i] < PIN + 60 and any(math.dist((gx, gy - tall[i]), h) < 21 for h in heads):
            tall[i] += 5
        heads.append((gx, gy - tall[i]))

    shapes = [[[proj(q) for q in ring] for ring in p['pts']] for p in PROVINCES]
    xs = [q[0] for sh in shapes for ring in sh for q in ring] + [q[0] for a in arcs for q in a] + [o[0] + 92]
    ys = [q[1] for sh in shapes for ring in sh for q in ring] + [q[1] for a in arcs for q in a] + \
         [g[1] - t - 12 for g, t in zip(grounds, tall)] + [o[1] - HQ_PIN - 14]
    pad = 12
    ox, oy = pad - min(xs), pad - min(ys)
    W, H = max(xs) + ox + pad, max(ys) + DEPTH + oy + pad

    def P(q):
        return q[0] + ox, q[1] + oy

    def path(rings):
        return ''.join('M' + ' '.join(f'{_f(P(q)[0])} {_f(P(q)[1])}' for q in ring) + 'Z' for ring in rings)

    shape_paths = [path(sh) for sh in shapes]
    group = ''.join(f'<path d="{dd}"/>' for dd in shape_paths)
    sides = ''.join(f'<use href="#{uid}-land" class="thmap-side" transform="translate(0 {k})"/>' for k in range(DEPTH, 0, -2))
    zone_paths = ''.join(f'<path class="thmap-zone" data-pin="{" ".join(str(z) for z in sorted(zs))}" d="{shape_paths[k]}"/>'
                         for k, zs in zones.items())
    home_path = f'<path class="thmap-home" d="{shape_paths[home]}"/>' if home is not None else ''
    base = f'''<svg class="thmap-base" viewBox="0 0 {_f(W)} {_f(H)}" aria-hidden="true" focusable="false">
        <defs><g id="{uid}-land">{group}</g>
          <linearGradient id="{uid}-sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{_f(H)}">
            <stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset=".7" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
        {sides}<use href="#{uid}-land" class="thmap-edge"/><use href="#{uid}-land" class="thmap-top"/>
        {zone_paths}{home_path}<use href="#{uid}-land" class="thmap-sheen" fill="url(#{uid}-sheen)"/>
      </svg>'''

    routes, cars = [], []
    for i, a in enumerate(arcs):
        rid = f'{uid}-r{i}'
        dd = 'M' + ' L'.join(f'{_f(P(q)[0])} {_f(P(q)[1])}' for q in a)
        length = sum(math.dist(a[j], a[j + 1]) for j in range(len(a) - 1))
        routes.append(f'<path id="{rid}" class="thmap-route" d="{dd}" pathLength="1" style="--i:{i}"/>')
        cars.append(f'<circle class="thmap-car" r="2.8"><animateMotion dur="{1.6 + min(length / 110, 3.2):.1f}s" '
                    f'begin="{0.4 + i * 0.4:.1f}s" repeatCount="indefinite"><mpath href="#{rid}"/></animateMotion></circle>')
    pins = []
    for i in sorted(range(len(grounds)), key=lambda j: grounds[j][1]):
        gx, gy = P(grounds[i])
        ph = tall[i]
        pins.append(f'<g class="thmap-pin" data-pin="{i}" style="--i:{i}">'
                    f'<ellipse class="thmap-pin-shadow" cx="{_f(gx)}" cy="{_f(gy)}" rx="5" ry="2"/>'
                    f'<line x1="{_f(gx)}" y1="{_f(gy)}" x2="{_f(gx)}" y2="{_f(gy - ph)}"/>'
                    f'<circle cx="{_f(gx)}" cy="{_f(gy - ph)}" r="8.5"/>'
                    f'<text x="{_f(gx)}" y="{_f(gy - ph + 3.3)}" text-anchor="middle">{i + 1}</text></g>')
    hx, hy = P(o)
    rk = round(math.cos(TILT), 2)
    hq = (f'<g class="thmap-hq"><ellipse class="thmap-ring" cx="{_f(hx)}" cy="{_f(hy)}" rx="8" ry="{_f(8 * rk)}"/>'
          f'<ellipse class="thmap-ring r2" cx="{_f(hx)}" cy="{_f(hy)}" rx="8" ry="{_f(8 * rk)}"/>'
          f'<line x1="{_f(hx)}" y1="{_f(hy)}" x2="{_f(hx)}" y2="{_f(hy - HQ_PIN)}"/>'
          f'<circle cx="{_f(hx)}" cy="{_f(hy - HQ_PIN)}" r="10"/>'
          f'<text class="thmap-hq-in" x="{_f(hx)}" y="{_f(hy - HQ_PIN + 3)}" text-anchor="middle">HQ</text>'
          f'<text class="thmap-hq-name" x="{_f(hx + 15)}" y="{_f(hy - HQ_PIN + 4)}">SuperX AI</text></g>')
    label = esc(tri(d, 'map_title')[2] or 'Service map of Thailand')
    fx = f'''<svg class="thmap-fx" viewBox="0 0 {_f(W)} {_f(H)}" role="img" aria-label="{label}">
        <g class="thmap-routes">{"".join(routes)}</g><g class="thmap-cars">{"".join(cars)}</g>
        {"".join(pins)}{hq}
      </svg>'''

    legend = [f'<li class="is-hq"><span class="thmap-num">HQ</span><span><b>{TC(tri(d, "map_origin"))}</b>{B("small", tri(d, "map_origin_text"))}</span></li>']
    for i, p in enumerate(pts):
        legend.append(f'<li data-pin="{i}"><span class="thmap-num">{i + 1}</span><span><b>{TC(tri(p, "name"))}</b>{B("small", tri(p, "text"))}</span></li>')
    title = B('h3', tri(d, 'map_title'), cls='h3 thmap-title')
    return f'''<div class="thmap" data-thmap>
    <div class="thmap-art">
      {base}
      {fx}
    </div>
    <div class="thmap-side-list">{title}
      <ol class="thmap-legend">{"".join(legend)}</ol>
    </div>
  </div>'''
