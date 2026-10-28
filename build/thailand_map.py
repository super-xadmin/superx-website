# -*- coding: utf-8 -*-
"""Thailand service map for the about page, drawn like a network console: a dark panel, the country as a
dot matrix, the provinces of each service zone lit up, thin routes from the head office to every zone with
small "packets" travelling along them, and real coordinates (graticule, scale bar, north arrow).

Province shapes come from apisit/thailand.json (MIT licence), stored in thailand_provinces.json as a flat map:
x = (longitude - 97.2) * 40 * cos 13.5°, y = (20.6 - latitude) * 40. Everything here is drawn in those units.
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
STEP = 5.6                                  # distance between dots of the matrix (about 15 km)

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
        f = float(v)
    except (TypeError, ValueError):
        return default
    return f if math.isfinite(f) else default


def flat(lat, lng):
    return (lng - _LON0) * _K * _C, (_LAT0 - lat) * _K


def _f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


# ---------------------------------------------------------------- the dot matrix (same for every build)
def _dots():
    """{(col, row): province index} for a square grid of dots STEP apart, inside the country."""
    out = {}
    for i, p in enumerate(PROVINCES):
        edges = [(a, b) for ring in p['pts'] for a, b in zip(ring, ring[1:] + ring[:1])]
        ys = [q[1] for ring in p['pts'] for q in ring]
        for row in range(math.ceil(min(ys) / STEP), math.floor(max(ys) / STEP) + 1):
            y = row * STEP
            xs = sorted(x1 + (y - y1) * (x2 - x1) / (y2 - y1) for (x1, y1), (x2, y2) in edges if (y1 > y) != (y2 > y))
            for a, b in zip(xs[0::2], xs[1::2]):
                for col in range(math.ceil(a / STEP), math.floor(b / STEP) + 1):
                    out.setdefault((col, row), i)
    return out


DOTS = _dots()


def _simplify(ring, tol=0.7):
    """Fewer points on a province border (Douglas–Peucker), so the page stays light."""
    if len(ring) < 4:
        return ring

    def rdp(pts):
        (x1, y1), (x2, y2) = pts[0], pts[-1]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1e-9
        far, k = 0.0, 0
        for j in range(1, len(pts) - 1):
            d = abs(dy * pts[j][0] - dx * pts[j][1] + x2 * y1 - y2 * x1) / n
            if d > far:
                far, k = d, j
        if far <= tol:
            return [pts[0], pts[-1]]
        return rdp(pts[:k + 1])[:-1] + rdp(pts[k:])
    half = len(ring) // 2
    return rdp(ring[:half + 1])[:-1] + rdp(ring[half:] + ring[:1])[:-1]


def _ring_path(rings):
    out = []
    for ring in rings:
        pts = _simplify(ring)
        if len(pts) < 3:
            continue
        out.append('M' + ' '.join(f'{_f(x)} {_f(y)}' for x, y in pts) + 'Z')
    return ''.join(out)


BORDERS = [_ring_path(p['pts']) for p in PROVINCES]


def _dot_path(cells):
    return ''.join(f'M{c} {r}h.01' for c, r in sorted(cells, key=lambda cr: (cr[1], cr[0])))


def _curve(a, b):
    """Gentle curve from a to b (bends to the left of the way), as a path and its middle control point."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    bend = min(0.18 * dist, 36)
    cx, cy = (x1 + x2) / 2 + dy / dist * bend, (y1 + y2) / 2 - dx / dist * bend
    return f'M{_f(x1)} {_f(y1)}Q{_f(cx)} {_f(cy)} {_f(x2)} {_f(y2)}', (cx, cy), dist


def _box_gap(box, pt):
    (x0, y0, x1, y1), (px, py) = box, pt
    return math.hypot(max(x0 - px, 0, px - x1), max(y0 - py, 0, py - y1))


def _coord(lat, lng):
    return f'{abs(lat):.2f}°{"N" if lat >= 0 else "S"}  {abs(lng):.2f}°{"E" if lng >= 0 else "W"}'


def thai_map(d, uid='thm'):
    """HTML for the map panel and the numbered list of zones. Empty when no zones are set."""
    pts = [p for p in items(d, 'map_points') if s(p, 'lat') != '' and s(p, 'lng') != '']
    if not pts:
        return ''
    lat0, lng0 = _num(d.get('map_origin_lat'), 13.52), _num(d.get('map_origin_lng'), 100.66)
    hq = flat(lat0, lng0)
    home = province_at(hq)

    zones = {}                                   # province index → set of zone numbers
    ends = []
    for i, p in enumerate(pts):
        pf = flat(_num(p.get('lat'), 13.7), _num(p.get('lng'), 100.5))
        names = [n for n in re.split(r'[,،、/·\n]+', s(p, 'provinces')) if n.strip()]
        idx = [k for k in (find_province(n) for n in names) if k is not None] or [province_at(pf)]
        for k in idx:
            if k is not None and k != home:
                zones.setdefault(k, set()).add(i)
        ends.append(pf)

    # frame: the country with some sea around it, then everything else must fit inside
    X0, Y0, X1, Y1 = -14.0, -10.0, 344.0, 614.0
    W, H = X1 - X0, Y1 - Y0

    # dots, grouped by what they show: other provinces, the head office's province, each zone's provinces
    groups = {}
    for cell, k in DOTS.items():
        if k == home:
            key = 'home'
        elif k in zones:
            key = ' '.join(str(z) for z in sorted(zones[k]))
        else:
            key = ''
        groups.setdefault(key, []).append(cell)
    dots = [f'<path class="thmap-dots" d="{_dot_path(groups.pop("", []))}"/>']
    for key, cells in groups.items():
        if key == 'home':
            dots.append(f'<path class="thmap-dots is-home" d="{_dot_path(cells)}"/>')
        else:
            dots.append(f'<path class="thmap-dots is-zone" data-pin="{key}" d="{_dot_path(cells)}"/>')
    lattice = f'<g class="thmap-matrix" transform="scale({STEP})">{"".join(dots)}</g>'

    borders = ''.join(BORDERS)
    lit = ''.join(f'<path class="thmap-zone-edge" data-pin="{" ".join(str(z) for z in sorted(zs))}" d="{BORDERS[k]}"/>'
                  for k, zs in zones.items())
    home_edge = f'<path class="thmap-home-edge" d="{BORDERS[home]}"/>' if home is not None else ''

    # graticule every 2°, labelled on the left and bottom edges
    grid, glab = [], []
    for lat in range(6, 21, 2):
        y = flat(lat, 100)[1]
        grid.append(f'M{_f(X0)} {_f(y)}H{_f(X1)}')
        glab.append(f'<text x="{_f(X0 + 4)}" y="{_f(y - 3)}">{lat}°N</text>')
    for lng in range(98, 106, 2):
        x = flat(14, lng)[0]
        grid.append(f'M{_f(x)} {_f(Y0)}V{_f(Y1)}')
        glab.append(f'<text x="{_f(x + 3)}" y="{_f(Y1 - 5)}">{lng}°E</text>')

    # scale bar (200 km) and north arrow, in the empty sea and over Laos
    km200 = 200 / 111.2 * _K
    sx, sy = 16.0, 566.0
    scale = (f'<g class="thmap-scale"><path d="M{_f(sx)} {_f(sy - 3)}V{_f(sy)}H{_f(sx + km200)}V{_f(sy - 3)}'
             f'M{_f(sx + km200 / 2)} {_f(sy - 2)}V{_f(sy)}"/>'
             f'<text x="{_f(sx)}" y="{_f(sy - 7)}">0</text><text x="{_f(sx + km200)}" y="{_f(sy - 7)}" text-anchor="end">200 km</text></g>')
    north = (f'<g class="thmap-north" transform="translate(318 26)"><path d="M0 -12L5 6L0 2.5L-5 6Z"/>'
             f'<text x="0" y="17" text-anchor="middle">N</text></g>')

    # routes from the head office to each zone, with small packets travelling along them
    routes, packets, defs = [], [], []
    mids = []
    for i, e in enumerate(ends):
        dd, mid, dist = _curve(hq, e)
        mids.append(mid)
        gid = f'{uid}-g{i}'
        defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{_f(hq[0])}" y1="{_f(hq[1])}" '
                    f'x2="{_f(e[0])}" y2="{_f(e[1])}"><stop offset="0" stop-color="#4FC8E9" stop-opacity=".2"/>'
                    f'<stop offset="1" stop-color="#4FC8E9" stop-opacity=".95"/></linearGradient>')
        rid = f'{uid}-r{i}'
        routes.append(f'<path id="{rid}" class="thmap-route" data-pin="{i}" d="{dd}" stroke="url(#{gid})" pathLength="1" style="--i:{i}"/>')
        packets.append(f'<circle class="thmap-packet" data-pin="{i}" r="1.7"><animateMotion dur="{2.2 + min(dist / 90, 3.5):.1f}s" '
                       f'begin="{0.3 + i * 0.55:.2f}s" repeatCount="indefinite"><mpath href="#{rid}"/></animateMotion></circle>')

    nodes = []
    for i, (x, y) in enumerate(ends):
        nodes.append(f'<g class="thmap-node" data-pin="{i}" style="--i:{i}" transform="translate({_f(x)} {_f(y)})">'
                     f'<circle class="thmap-node-halo" r="13"/><circle class="thmap-node-ring" r="8.4"/>'
                     f'<text y="2.5" text-anchor="middle">{i + 1:02d}</text></g>')

    # the head office: a reticle with pulsing rings; its name goes where it covers least of the map
    hx, hy = hq
    name = 'SUPERX AI'
    coord = _coord(lat0, lng0)
    bw, bh = 66.0, 21.0
    others = list(ends) + mids + [((hx + e[0]) / 2, (hy + e[1]) / 2) for e in ends]
    best, best_score = None, -1e9
    for ang in range(0, 360, 30):
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        cx, cy = hx + ux * 20, hy + uy * 20
        bx = cx if ux > 0.3 else (cx - bw if ux < -0.3 else cx - bw / 2)
        by = cy if uy > 0.3 else (cy - bh if uy < -0.3 else cy - bh / 2)
        box = (bx, by, bx + bw, by + bh)
        if box[0] < X0 + 2 or box[2] > X1 - 2 or box[1] < Y0 + 2 or box[3] > Y1 - 2:
            continue
        score = min(_box_gap(box, q) for q in others) if others else 99
        if score > best_score:
            best, best_score = box, score
    bx, by = best[0], best[1]
    hq_html = (f'<g class="thmap-hq" transform="translate({_f(hx)} {_f(hy)})">'
               f'<circle class="thmap-pulse" r="6"/><circle class="thmap-pulse p2" r="6"/>'
               f'<circle class="thmap-hq-ring" r="6.5"/><circle class="thmap-hq-core" r="2.4"/>'
               f'<path class="thmap-hq-ticks" d="M0 -9.5V-13M0 9.5V13M-9.5 0H-13M9.5 0H13"/></g>'
               f'<g class="thmap-hq-tag" transform="translate({_f(bx)} {_f(by)})">'
               f'<rect width="{_f(bw)}" height="{_f(bh)}" rx="3"/>'
               f'<text class="thmap-hq-name" x="6" y="8.6">{name}<tspan class="thmap-hq-badge" dx="4">HQ</tspan></text>'
               f'<text class="thmap-hq-coord" x="6" y="16.4">{esc(coord)}</text></g>')

    label = esc(tri(d, 'map_title')[2] or 'Service map of Thailand')
    svg = f'''<svg class="thmap-svg" viewBox="{_f(X0)} {_f(Y0)} {_f(W)} {_f(H)}" role="img" aria-label="{label}">
        <defs>{"".join(defs)}
          <radialGradient id="{uid}-glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#4FC8E9" stop-opacity=".22"/><stop offset="1" stop-color="#4FC8E9" stop-opacity="0"/></radialGradient>
          <filter id="{uid}-blur" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>
        <circle class="thmap-aura" cx="{_f(hx)}" cy="{_f(hy)}" r="120" fill="url(#{uid}-glow)"/>
        <path class="thmap-grid" d="{"".join(grid)}"/><g class="thmap-grid-labels">{"".join(glab)}</g>
        {lattice}
        <path class="thmap-borders" d="{borders}"/>{lit}{home_edge}
        <g class="thmap-routes">{"".join(routes)}</g>
        <g class="thmap-packets"><g filter="url(#{uid}-blur)">{"".join(packets)}</g>{"".join(packets)}</g>
        {"".join(nodes)}{hq_html}{scale}{north}
      </svg>'''

    legend = [f'<li class="is-hq"><span class="thmap-num">HQ</span><span><b>{TC(tri(d, "map_origin"))}</b>{B("small", tri(d, "map_origin_text"))}</span></li>']
    for i, p in enumerate(pts):
        legend.append(f'<li data-pin="{i}"><span class="thmap-num">{i + 1:02d}</span><span><b>{TC(tri(p, "name"))}</b>{B("small", tri(p, "text"))}</span></li>')
    title = B('h3', tri(d, 'map_title'), cls='h3 thmap-title')
    return f'''<div class="thmap" data-thmap>
    <div class="thmap-art">
      {svg}
      <span class="thmap-scan" aria-hidden="true"></span>
    </div>
    <div class="thmap-info">{title}
      <ol class="thmap-legend">{"".join(legend)}</ol>
    </div>
  </div>'''
