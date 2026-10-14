# -*- coding: utf-8 -*-
"""News page (news.html) and one page per news item that has full text (news-<file name>.html).

Each news item is one file in content/news/ (back office: ข่าวสาร).
"""
import hashlib
import re

from core import C, collection, s, items, tri, has, esc, T, TC, B, Tk, Bk, img, href, is_external, ic, date3, LANGS
from schema import TX, S, LINK, BOOL, DATE, IMG, ALT, VID, SEL, LIST
from layout import PAGE_FIELDS_CTA, PHERO, page, phero, crumbs, cta_band, head, gallery, video_card, trail, bgv

FILE = 'news.html'
DIR = 'pages/news'
LABEL = 'ข่าวสาร'

CATEGORIES = [('company', 'ข่าวบริษัท'), ('partner', 'ข่าวพันธมิตร'), ('project', 'โครงการ / ผลงาน'),
              ('event', 'กิจกรรม / งานแสดงสินค้า'), ('press', 'สื่อมวลชน')]
DATE_SHOW = [('day', 'วัน เดือน ปี (เช่น 14 ก.ย. 2569)'), ('month', 'เดือน ปี (เช่น ก.ย. 2569)'), ('year', 'ปีอย่างเดียว (เช่น 2569)')]

NEWS_FIELDS = [
    TX('title', 'หัวข้อข่าว', req=True),
    DATE('date', 'วันที่ของข่าว', desc='ข่าวเรียงจากวันที่ใหม่ที่สุดก่อน'),
    SEL('date_show', 'แสดงวันที่แบบ', DATE_SHOW),
    SEL('category', 'ประเภทข่าว', CATEGORIES),
    BOOL('featured', 'ข่าวเด่น (แสดงใหญ่ด้านบนสุดของหน้าข่าว)', desc='ถ้าเลือกไว้หลายข่าว จะแสดงข่าวที่วันที่ใหม่ที่สุด'),
    BOOL('hide', 'ซ่อนข่าวนี้ (ยังไม่แสดงบนเว็บ)'),
    TX('summary', 'สรุปข่าวสั้นๆ (แสดงในรายการข่าว)', long=True),
    IMG('image', 'รูปหลักของข่าว'), ALT(),
    TX('body', 'เนื้อหาข่าวฉบับเต็ม (ถ้าใส่ เว็บจะสร้างหน้าอ่านข่าวให้อัตโนมัติ)', rich=True),
    LIST('gallery', 'รูปเพิ่มเติม (แสดงในหน้าอ่านข่าว)', [IMG(), ALT(), TX('caption', 'คำบรรยาย (เว้นว่างได้)')], summary='{alt}'),
    VID('video', 'วิดีโอ (แสดงในหน้าอ่านข่าว) เว้นว่างได้'), IMG('poster', 'ภาพก่อนกดเล่นวิดีโอ'),
    S('source_url', 'ลิงก์ข่าวต้นฉบับ (เว็บไซต์ภายนอก) เว้นว่างได้', desc='เช่น https://www.bangkokbiznews.com/...'),
    TX('source_name', 'ชื่อแหล่งข่าว (เช่น กรุงเทพธุรกิจ)'),
    LINK('link', 'ลิงก์ไปหน้าในเว็บนี้ (เว้นว่างได้)', desc='เช่น cases.html#tcav หรือ products.html'),
    TX('link_label', 'ข้อความลิงก์ในเว็บ (เช่น ดูโครงการ)'),
]

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
    ('list', '2. รายการข่าวและข้อความปุ่ม', [
        TX('eyebrow', 'หัวข้อเล็กเหนือรายการข่าว'), TX('title', 'หัวข้อรายการข่าว', long=True),
        TX('source_button', 'ปุ่มข่าวเด่น: อ่านข่าวต้นฉบับ', desc='{source} จะถูกแทนด้วยชื่อแหล่งข่าว'),
        TX('read_more', 'ปุ่มอ่านข่าวฉบับเต็ม'),
        TX('back', 'หน้าอ่านข่าว: ปุ่มกลับไปหน้าข่าวทั้งหมด'),
        TX('source_label', 'หน้าอ่านข่าว: คำนำหน้าลิงก์ต้นฉบับ (เช่น ที่มา)'),
        TX('empty', 'ข้อความเมื่อยังไม่มีข่าว'),
    ] + [TX(f'cat_{k}', f'ชื่อประเภทข่าว: {v}') for k, v in CATEGORIES]),
]

COLLECTIONS = [('news', '📰 ข่าวสาร (เพิ่มข่าวใหม่ที่นี่)', 'news', NEWS_FIELDS,
                {'fields': ['title_th', 'date', 'featured', 'hide'], 'primary': 'title_th', 'sort': ['date', 'title_th'],
                 'default': {'sort': 'date', 'order': 'desc'}})]


# ---------------------------------------------------------------- data
def _article_name(slug):
    safe = re.sub(r'[^a-z0-9-]+', '-', slug.lower()).strip('-')
    if not re.search(r'[a-z0-9]', safe):
        safe = hashlib.sha1(slug.encode('utf-8')).hexdigest()[:10]
    return f'news-{safe}.html'


def has_body(n):
    return any(re.sub(r'<[^>]+>|&nbsp;|\s', '', x) for x in tri(n, 'body')) or bool(items(n, 'gallery')) or bool(s(n, 'video'))


def all_news():
    """Visible news, newest first. Each item gets _page (its own page, or '') and _date (three languages)."""
    out = []
    for slug, n in collection('news'):
        if n.get('hide') or not has(n, 'title'):
            continue
        n = dict(n, _slug=slug, _page=_article_name(slug) if has_body(n) else '',
                 _date=date3(s(n, 'date'), s(n, 'date_show') or 'day'))
        out.append(n)
    out.sort(key=lambda n: (s(n, 'date'), n['_slug']), reverse=True)
    return out


def featured_and_rest(news):
    feat = next((n for n in news if n.get('featured')), None)
    return feat, [n for n in news if n is not feat]


def _source_button(lst, n):
    tpl, src = tri(lst, 'source_button'), tri(n, 'source_name')
    return tuple(t.replace('{source}', x) if '{source}' in t else t for t, x in zip(tpl, src))


# ---------------------------------------------------------------- news.html
def featured_block(n, lst):
    buttons = []
    if n['_page']:
        buttons.append(f'<a class="btn btn-primary" href="{esc(n["_page"])}">{Tk(lst, "read_more")}</a>')
    if s(n, 'source_url'):
        buttons.append(f'<a class="btn btn-outline" href="{href(s(n, "source_url"))}" target="_blank" rel="noopener">{T(_source_button(lst, n))}{ic("ext")}</a>')
    if s(n, 'link') and has(n, 'link_label'):
        cls = 'btn btn-outline' if n['_page'] else 'btn btn-primary'
        buttons.append(f'<a class="{cls}" href="{href(s(n, "link"))}">{Tk(n, "link_label")}</a>')
    row = ('\n      <div class="btn-row">' + '\n        '.join(buttons) + '</div>') if buttons else ''
    return f'''<section class="section">
  <div class="wrap news-feature">
    {img(n)}
    <div class="stack">
      <span class="kicker num">{T(n['_date'])}</span>
      <h2 class="h2">{Tk(n, 'title')}</h2>
      {Bk('p', n, 'summary', cls='lead')}{row}
    </div>
  </div>
</section>'''


def list_item(n, lst):
    if n['_page']:
        link = f'<a class="news-src" href="{esc(n["_page"])}">{Tk(lst, "read_more")}{ic("arrow")}</a>'
    elif s(n, 'source_url'):
        link = f'<a class="news-src" href="{href(s(n, "source_url"))}" target="_blank" rel="noopener">{TC(tri(n, "source_name"))}{ic("ext")}</a>'
    elif s(n, 'link') and has(n, 'link_label'):
        ext = is_external(s(n, 'link'))
        tgt = ' target="_blank" rel="noopener"' if ext else ''
        link = f'<a class="news-src" href="{href(s(n, "link"))}"{tgt}>{Tk(n, "link_label")}{ic("ext" if ext else "arrow")}</a>'
    else:
        link = ''
    cat = tri(lst, f'cat_{s(n, "category") or "company"}')
    return (f'<article class="news-item"><span class="news-date">{T(n["_date"])}</span><div><span class="kicker">{T(cat)}</span>'
            f'<h3>{Tk(n, "title")}</h3>{Bk("p", n, "summary")}</div>{link}</article>')


BG_KEYS = ('hero', 'list')

def render():
    h = C(f'{DIR}/hero')
    lst = C(f'{DIR}/list')
    hero = phero(img(h, lazy=False), 'photo', trail('about', h), h)
    feat, rest = featured_and_rest(all_news())
    featured = featured_block(feat, lst) if feat else ''
    if rest:
        inner = '<div class="news-list">\n      ' + '\n      '.join(list_item(n, lst) for n in rest) + '\n    </div>'
    else:
        inner = Bk('p', lst, 'empty', cls='lead')
    listing = f'''<section class="section section--mist">
  <div class="wrap">
    {head(lst, lead=False, link=False)}
    {inner}
  </div>
</section>'''
    pg = C(f'{DIR}/page')
    return page(FILE, pg, bgv(hero, h) + featured + bgv(listing, lst) + cta_band(pg))


# ---------------------------------------------------------------- one page per news item
def _body_html(n):
    """Full text from the rich-text editor (HTML), one block per language."""
    out = []
    for (k, lg), html in zip(LANGS, tri(n, 'body')):
        html = re.sub(r'<script\b.*?</script>', '', html, flags=re.S | re.I)
        out.append(f'<div class="article-body" data-l="{k}" lang="{lg}">{html}</div>')
    return '\n      '.join(out)


def article(n):
    lb, h, lst = C('site/labels'), C(f'{DIR}/hero'), C(f'{DIR}/list')
    cat = tri(lst, f'cat_{s(n, "category") or "company"}')
    eyebrow = tuple(f'{c} · {d}' if c and d else (c or d) for c, d in zip(cat, n['_date']))
    hero_d = {}
    for i, (k, _lg) in enumerate(LANGS):
        hero_d[f'eyebrow_{k}'] = eyebrow[i]
        hero_d[f'title_{k}'] = tri(n, 'title')[i]
        hero_d[f'lead_{k}'] = tri(n, 'summary')[i]
    pic = img(n, lazy=False) or img(h, lazy=False)
    trail_ = [('index.html', tri(lb, 'crumb_home')), ('news.html', tri(h, 'crumb')), (None, tri(n, 'title'))]
    hero = phero(pic, 'photo', trail_, hero_d)

    parts = []
    if any(re.sub(r'<[^>]+>|&nbsp;|\s', '', x) for x in tri(n, 'body')):
        parts.append(_body_html(n))
    if items(n, 'gallery'):
        parts.append(gallery([dict(g, size='g-half') for g in items(n, 'gallery')]))
    if s(n, 'video'):
        parts.append(video_card(n))
    if s(n, 'source_url'):
        src = TC(tri(n, 'source_name')) if has(n, 'source_name') else esc(s(n, 'source_url'))
        parts.append(f'<p class="article-meta">{Tk(lst, "source_label")} <a href="{href(s(n, "source_url"))}" target="_blank" rel="noopener">{src}{ic("ext")}</a></p>')
    btns = [f'<a class="btn btn-outline" href="news.html">{ic("arrow", "ic ic-back")}{Tk(lst, "back")}</a>']
    if s(n, 'link') and has(n, 'link_label'):
        btns.append(f'<a class="btn btn-primary" href="{href(s(n, "link"))}">{Tk(n, "link_label")}</a>')
    parts.append('<div class="btn-row">' + ''.join(btns) + '</div>')
    body = f'''<section class="section">
  <div class="wrap">
    <div class="article">
      {chr(10).join('      ' + p if i else p for i, p in enumerate(parts))}
    </div>
  </div>
</section>'''
    seo = {}
    for i, (k, _lg) in enumerate(LANGS):
        seo[f'seo_title_{k}'] = f'{tri(n, "title")[i]} — SUPERX AI'
        seo[f'seo_desc_{k}'] = tri(n, 'summary')[i]
    pg = C(f'{DIR}/page')
    return page(n['_page'], seo, hero + body + cta_band(pg), current=FILE, share=s(n, 'image') or None)


def extra_pages():
    return [(n['_page'], article(n)) for n in all_news() if n['_page']]
