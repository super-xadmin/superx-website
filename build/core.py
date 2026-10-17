# -*- coding: utf-8 -*-
"""Shared helpers for the SUPERX AI site builder.

All visible text lives in content/*.json (edited in the back office, Pages CMS).
Text that exists in three languages is stored as  <name>_th, <name>_zh, <name>_en.
"""
import html as _h
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
ASSETS = os.path.join(ROOT, 'assets')
LANGS = (('th', 'th'), ('zh', 'zh-CN'), ('en', 'en'))
_cache = {}


# ---------------------------------------------------------------- content
def C(rel):
    """Content file as a dict, e.g. C('pages/home/hero'). Missing files give {}."""
    path = os.path.join(CONTENT, rel + '.json')
    if path not in _cache:
        try:
            with open(path, encoding='utf-8') as f:
                _cache[path] = json.load(f) or {}
        except FileNotFoundError:
            _cache[path] = {}
    return _cache[path]


def collection(name):
    """All entries of a collection folder as [(slug, data)], sorted by file name."""
    folder = os.path.join(CONTENT, name)
    out = []
    if os.path.isdir(folder):
        for fn in sorted(os.listdir(folder)):
            if fn.endswith('.json'):
                with open(os.path.join(folder, fn), encoding='utf-8') as f:
                    out.append((fn[:-5], json.load(f) or {}))
    return out


def s(d, key, default=''):
    """A single (language-neutral) value as text."""
    v = (d or {}).get(key)
    if v is None:
        return default
    return str(v).strip() if not isinstance(v, bool) else v


def items(d, key):
    v = (d or {}).get(key)
    return [x for x in v if x is not None] if isinstance(v, list) else []


def strs(d, key):
    """A list of text values (several images or models in one field). A single value counts as a list of one."""
    v = (d or {}).get(key)
    if isinstance(v, str):
        v = [v]
    return [str(x).strip() for x in v if x and str(x).strip()] if isinstance(v, list) else []


def tri(d, key):
    """(th, zh, en) for a three-language field. Empty languages fall back: zh→en→th, en→th, th→en→zh."""
    d = d or {}
    th = str(d.get(key + '_th') or '').strip()
    zh = str(d.get(key + '_zh') or '').strip()
    en = str(d.get(key + '_en') or '').strip()
    return (th or en or zh, zh or en or th, en or th or zh)


def has(d, key):
    return any(tri(d, key))


# ---------------------------------------------------------------- text output
def esc(v):
    return _h.escape(str(v), quote=True)


_BOLD = re.compile(r'\*\*(.+?)\*\*', re.S)


def fmt(v):
    """Editor text to HTML: escape, **bold**, and line breaks."""
    t = _h.escape(str(v), quote=False)
    t = _BOLD.sub(r'<strong>\1</strong>', t)
    return t.replace('\r\n', '\n').replace('\n', '<br>')


def T(t3):
    """Inline text in three languages (only the visitor's language shows)."""
    return ''.join(f'<span data-l="{k}" lang="{lg}">{fmt(x)}</span>' for (k, lg), x in zip(LANGS, t3))


def TC(t3):
    """Like T(), but plain text when all three languages are the same (names, brands)."""
    if t3[0] == t3[1] == t3[2]:
        return fmt(t3[0])
    return T(t3)


def B(tag, t3, cls=None, attrs=''):
    """Block element repeated per language, e.g. B('p', ...)."""
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<{tag}{c} data-l="{k}" lang="{lg}"{attrs}>{fmt(x)}</{tag}>' for (k, lg), x in zip(LANGS, t3))


def Tk(d, key):
    return T(tri(d, key))


def Bk(tag, d, key, cls=None):
    return B(tag, tri(d, key), cls)


def ph(t3):
    th, zh, en = (esc(x) for x in t3)
    return f' placeholder="{th}" data-ph-th="{th}" data-ph-zh="{zh}" data-ph-en="{en}"'


def aria(t3):
    th, zh, en = (esc(x) for x in t3)
    return f' aria-label="{th}" data-aria-th="{th}" data-aria-zh="{zh}" data-aria-en="{en}"'


def opt(value, t3, selected=False):
    sel = ' selected' if selected else ''
    th, zh, en = (esc(x) for x in t3)
    return f'<option value="{esc(value)}" data-th="{th}" data-zh="{zh}" data-en="{en}"{sel}>{th}</option>'


# ---------------------------------------------------------------- media and links
def media(v, folder):
    """Normalise a stored media value ('/assets/img/x.webp', 'assets/img/x.webp' or 'x.webp') to a page-relative URL."""
    v = (v or '').strip()
    if not v:
        return ''
    if re.match(r'^(https?:)?//', v):
        return v
    v = v.lstrip('/')
    if v.startswith('assets/'):
        return v
    return f'assets/{folder}/{v}'


def asset_path(url):
    """Local file for a page-relative asset URL (used for file sizes)."""
    return os.path.join(ROOT, url) if url.startswith('assets/') else ''


def img(d, key='image', alt_key='alt', cls=None, w=None, h=None, lazy=True, extra='', alt=None):
    src = media(s(d, key), 'img')
    if not src:
        return ''
    a = alt if alt is not None else s(d, alt_key)
    c = f' class="{cls}"' if cls else ''
    wh = f' width="{w}" height="{h}"' if w and h else ''
    lz = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    return f'<img src="{esc(src)}" alt="{esc(a)}"{c}{wh}{lz}{extra}>'


def href(v):
    return esc((v or '').strip() or '#')


def is_external(url):
    return bool(re.match(r'^https?://', (url or '').strip()))


def file_size(url):
    p = asset_path(url)
    try:
        n = os.path.getsize(p)
    except OSError:
        return ''
    return f'{n / 1000000:.1f} MB'


def ic(name, cls='ic'):
    name = (name or '').strip() or 'check'
    if name not in ICONS:
        name = 'spark'
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


# ---------------------------------------------------------------- icons
ICONS = {
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'chev': '<path d="M6 9l6 6 6-6"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'download': '<path d="M12 4v11M7 10l5 5 5-5"/><path d="M5 19.5h14"/>',
    'play': '<path d="M8.5 5.8v12.4L18.5 12z"/>',
    'pause': '<path d="M9 5.5v13M15 5.5v13"/>',
    'ext': '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.4a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.6" r="2.5"/>',
    'phone': '<path d="M5.2 3.8h3.6l1.9 4.8-2.4 1.5a11 11 0 0 0 5.4 5.4l1.5-2.4 4.8 1.9v3.6a1.4 1.4 0 0 1-1.5 1.4A16.6 16.6 0 0 1 3.8 5.3a1.4 1.4 0 0 1 1.4-1.5z"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    'copy': '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2"/><path d="M15.5 8.5V5.2a1.2 1.2 0 0 0-1.2-1.2H5.2A1.2 1.2 0 0 0 4 5.2v9.1a1.2 1.2 0 0 0 1.2 1.2h3.3"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'close': '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    'gift': '<rect x="3.5" y="8.5" width="17" height="4" rx="1"/><path d="M5 12.5V20h14v-7.5M12 8.5V20"/><path d="M12 8.5C10.6 5.2 6.8 4.6 6.8 6.9c0 1.4 2.3 1.6 5.2 1.6zM12 8.5c1.4-3.3 5.2-3.9 5.2-1.6 0 1.4-2.3 1.6-5.2 1.6z"/>',
    'van': '<path d="M2.5 6.5h11v9.5h-11z"/><path d="M13.5 9.5h4l3.5 3.5v3h-7.5"/><circle cx="6.5" cy="17.5" r="1.9"/><circle cx="17" cy="17.5" r="1.9"/>',
    'box': '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    'weight': '<path d="M6.5 8h11l2 12h-15z"/><circle cx="12" cy="5.5" r="2.2"/>',
    'route': '<circle cx="6" cy="5.5" r="2"/><circle cx="18" cy="18.5" r="2"/><path d="M8 5.5h7a3.2 3.2 0 0 1 0 6.4H9a3.2 3.2 0 0 0 0 6.4h7"/>',
    'battery': '<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M21 10.5v3"/><path d="M6.5 10v4M10 10v4"/>',
    'bolt': '<path d="M13 3L5 13.5h6L10 21l8-10.5h-6z"/>',
    'gauge': '<path d="M4.5 16a8 8 0 1 1 15 0"/><path d="M12 13.5l4-4"/><circle cx="12" cy="13.5" r="1.2"/>',
    'thermo': '<path d="M10 4.5a2 2 0 0 1 4 0v9.3a4 4 0 1 1-4 0z"/><path d="M12 9v6"/>',
    'snow': '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/><path d="M9.5 4.5L12 6.5l2.5-2M9.5 19.5L12 17.5l2.5 2"/>',
    'shield': '<path d="M12 3l7 3v5.2c0 4.4-3 8.3-7 9.8-4-1.5-7-5.4-7-9.8V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    'radar': '<circle cx="12" cy="12" r="2"/><path d="M12 3a9 9 0 0 1 9 9M12 6.5a5.5 5.5 0 0 1 5.5 5.5"/><path d="M3 12a9 9 0 0 0 9 9"/>',
    'camera': '<rect x="3" y="7" width="18" height="12" rx="2"/><circle cx="12" cy="13" r="3.2"/><path d="M8.5 7l1.5-2.5h4L15.5 7"/>',
    'chip': '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3.5V7M14 3.5V7M10 17v3.5M14 17v3.5M3.5 10H7M3.5 14H7M17 10h3.5M17 14h3.5"/>',
    'signal': '<path d="M3.5 9a12 12 0 0 1 17 0"/><path d="M6.8 12.6a7.4 7.4 0 0 1 10.4 0"/><path d="M10 16.1a2.9 2.9 0 0 1 4 0"/><circle cx="12" cy="19.2" r=".7"/>',
    'monitor': '<rect x="3" y="4" width="18" height="12.5" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/><path d="M6.5 10.5h3l1.6-2.6 2 5 1.6-2.4h2.8"/>',
    'headset': '<path d="M4.5 14v-2.2a7.5 7.5 0 0 1 15 0V14"/><rect x="3.5" y="13.5" width="4" height="6" rx="1.5"/><rect x="16.5" y="13.5" width="4" height="6" rx="1.5"/>',
    'gear': '<circle cx="12" cy="12" r="3.2"/><path d="M12 3v2.6M12 18.4V21M3 12h2.6M18.4 12H21M5.6 5.6l1.9 1.9M16.5 16.5l1.9 1.9M5.6 18.4l1.9-1.9M16.5 7.5l1.9-1.9"/>',
    'wrench': '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.1L4 16.8V20h3.2l5.2-5.2a4 4 0 0 0 5.1-5.3l-2.5 2.5-2.3-.6-.6-2.3z"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14h3M8 17h6"/>',
    'grad': '<path d="M2.5 9.5L12 5l9.5 4.5L12 14z"/><path d="M6.5 11.5v4.2c1.5 1.4 3.4 2.1 5.5 2.1s4-.7 5.5-2.1v-4.2"/><path d="M21.5 9.5v5"/>',
    'robot': '<rect x="5" y="8" width="14" height="10" rx="2.5"/><path d="M12 4.5V8"/><circle cx="12" cy="3.6" r="1"/><circle cx="9.3" cy="12.6" r="1.1"/><circle cx="14.7" cy="12.6" r="1.1"/><path d="M3 12v3M21 12v3"/>',
    'chat': '<path d="M4 4.5h16v11.5H10l-6 4.5z"/><circle cx="9" cy="10.3" r=".6"/><circle cx="12" cy="10.3" r=".6"/><circle cx="15" cy="10.3" r=".6"/>',
    'users': '<circle cx="9" cy="8" r="3"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><path d="M16 5.5a3 3 0 0 1 0 5.5M17.5 19a5.5 5.5 0 0 0-2.5-4.6"/>',
    'factory': '<path d="M3 20V10l5 3V10l5 3V7l8 4v9z"/><path d="M7 16.5h2M12 16.5h2M17 16.5h1"/>',
    'warehouse': '<path d="M3 20V9l9-5 9 5v11"/><path d="M7 20v-7h10v7M7 16h10"/>',
    'cart': '<path d="M3.5 5h2l2.2 10.5h10l2-7.5H7"/><circle cx="9.5" cy="19" r="1.3"/><circle cx="16.5" cy="19" r="1.3"/>',
    'pill': '<path d="M8.6 15.4l6.8-6.8a3.4 3.4 0 0 1 4.8 4.8l-6.8 6.8a3.4 3.4 0 0 1-4.8-4.8z"/><path d="M12 12l4.8 4.8"/><path d="M4 9.5h5M6.5 7v5"/>',
    'plane': '<path d="M21 15.5l-8-5V4.8a1.3 1.3 0 0 0-2.6 0v5.7l-8 5v2l8-2.5v4l-2 1.5V22l3.3-1 3.3 1v-1.5l-2-1.5v-4l8 2.5z"/>',
    'leaf': '<path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15"/><path d="M5 19l7-7"/>',
    'eye': '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    'rain': '<path d="M7 15.5a4.5 4.5 0 1 1 1-8.9 5.5 5.5 0 0 1 10.4 2.4A3.5 3.5 0 0 1 17.5 15.5z"/><path d="M8.5 18.5l-1 2M12.5 18.5l-1 2M16.5 18.5l-1 2"/>',
    'moon': '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    'lock': '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    'app': '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
    'map': '<path d="M3 6.5l6-2.5 6 2.5 6-2.5v13.5l-6 2.5-6-2.5-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
    'bell': '<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    'sign': '<path d="M3 17c3-1 4-6 6-6s1 6 3 6 3-3 4-3 2 2 3 2"/><path d="M3 20.5h18"/>',
    'api': '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 5l-3 14"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    'fire': '<path d="M12 21a6.5 6.5 0 0 0 6.5-6.5c0-4-3-6-4-9.5-1.5 2-2 3.5-2 5-1.2-.8-2-2.2-2.2-3.5C8 8.5 5.5 11 5.5 14.5A6.5 6.5 0 0 0 12 21z"/>',
    'broom': '<path d="M15 3l-3.5 8"/><path d="M6.5 11h10l1.5 9.5H5z"/><path d="M9 15v5.5M12 15v5.5M15 15v5.5"/>',
    'tracks': '<rect x="3" y="13" width="18" height="6.5" rx="3.25"/><circle cx="7" cy="16.25" r="1.4"/><circle cx="12" cy="16.25" r="1.4"/><circle cx="17" cy="16.25" r="1.4"/><path d="M7 13V9h10v4M12 9V5.5h3.5"/>',
    'ruler': '<path d="M3 16.5L16.5 3 21 7.5 7.5 21z"/><path d="M7 12.5l2 2M10 9.5l2 2M13 6.5l2 2"/>',
    'doc': '<path d="M6.5 3h8l4 4v14h-12z"/><path d="M14.5 3v4h4M9 12h6M9 15.5h6"/>',
    'spark': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.3 6.3l2.5 2.5M15.2 15.2l2.5 2.5M6.3 17.7l2.5-2.5M15.2 8.8l2.5-2.5"/>',
    'link': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    'tiktok': '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.5 2.5 2.5 4.5 5 4.5"/>',
    'handshake': '<path d="M2.5 11.5l4-4.5 4.5 2 3-2 7.5 5.5-4.5 4.5"/><path d="M6.5 14.5l3 3M9.5 12.5l3.5 3.5M12.5 11l3 3"/>',
    'layers': '<path d="M12 3.5l9 4.5-9 4.5-9-4.5z"/><path d="M3 12.5l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/>',
    'target': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
    'parcel': '<rect x="4" y="4" width="16" height="16" rx="1.5"/><path d="M4 9.5h16M9.5 4v16M14.5 4v16M4 15h16"/>',
    'leasing': '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M8 15l2.5 2.5L16 12.5"/>',
}

# Thai names shown in the back office icon picker
ICON_NAMES = {
    'van': 'รถตู้', 'box': 'กล่องสินค้า', 'parcel': 'พัสดุ', 'weight': 'น้ำหนัก', 'route': 'เส้นทาง', 'map': 'แผนที่',
    'pin': 'หมุดตำแหน่ง', 'battery': 'แบตเตอรี่', 'bolt': 'ชาร์จไฟ / สายฟ้า', 'gauge': 'มาตรวัด', 'thermo': 'อุณหภูมิ',
    'snow': 'ห้องเย็น / หิมะ', 'shield': 'ความปลอดภัย', 'radar': 'เซนเซอร์ / เรดาร์', 'camera': 'กล้อง', 'chip': 'ชิป / AI',
    'signal': 'สัญญาณ', 'monitor': 'จอเฝ้าระวัง', 'headset': 'ทีมดูแล / หูฟัง', 'gear': 'เฟือง', 'wrench': 'ประแจ / ซ่อมบำรุง',
    'calendar': 'ปฏิทิน / นัดหมาย', 'clock': 'นาฬิกา', 'grad': 'การศึกษา', 'robot': 'หุ่นยนต์', 'tracks': 'รถตีนตะขาบ',
    'chat': 'แชต', 'users': 'คน / ทีม', 'factory': 'โรงงาน', 'warehouse': 'คลังสินค้า', 'cart': 'รถเข็น / ค้าปลีก',
    'pill': 'ยา / เวชภัณฑ์', 'plane': 'เครื่องบิน', 'leaf': 'ใบไม้ / พลังงานสะอาด', 'eye': 'ดวงตา', 'rain': 'ฝน / สภาพอากาศ',
    'moon': 'กลางคืน', 'lock': 'กุญแจล็อก', 'app': 'แอปมือถือ', 'bell': 'กระดิ่งแจ้งเตือน', 'sign': 'ลายเซ็น',
    'api': 'โค้ด / API', 'fire': 'ไฟ / ดับเพลิง', 'broom': 'ไม้กวาด / ทำความสะอาด', 'ruler': 'ไม้บรรทัด', 'doc': 'เอกสาร',
    'spark': 'ประกาย', 'link': 'ลิงก์', 'handshake': 'จับมือ / พันธมิตร', 'layers': 'ชั้น / ระบบ', 'target': 'เป้าหมาย',
    'leasing': 'สัญญาเช่า', 'gift': 'ของขวัญ / โปรโมชั่น', 'globe': 'ลูกโลก / เว็บไซต์', 'phone': 'โทรศัพท์', 'mail': 'อีเมล', 'tiktok': 'TikTok',
    'check': 'เครื่องหมายถูก', 'arrow': 'ลูกศร', 'download': 'ดาวน์โหลด', 'ext': 'ลิงก์ภายนอก',
}


def sprite():
    syms = ''.join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            '<linearGradient id="aur" gradientUnits="userSpaceOnUse" x1="2" y1="22" x2="22" y2="2">'
            '<stop offset="0" stop-color="#25326C"/><stop offset=".55" stop-color="#4FC8E9"/><stop offset="1" stop-color="#8EC96D"/></linearGradient>'
            f'</defs>{syms}</svg>')


# ---------------------------------------------------------------- dates (news)
TH_MON = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
EN_MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def date3(value, precision='day'):
    """'2026-09-14' → ('14 ก.ย. 2569', '2026年9月14日', '14 Sep 2026'); precision: day, month or year."""
    m = re.match(r'^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?', str(value or ''))
    if not m:
        return ('', '', '')
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
    if precision == 'year':
        return (f'{y + 543}', f'{y}年', f'{y}')
    if precision == 'month':
        return (f'{TH_MON[mo - 1]} {y + 543}', f'{y}年{mo}月', f'{EN_MON[mo - 1]} {y}')
    return (f'{d} {TH_MON[mo - 1]} {y + 543}', f'{y}年{mo}月{d}日', f'{d} {EN_MON[mo - 1]} {y}')
