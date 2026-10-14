# -*- coding: utf-8 -*-
"""Projects page (cases.html). Each project is one file in content/cases/ (back office: ผลงาน / โครงการ)."""
import re

from core import C, collection, s, items, tri, has, esc, T, TC, Tk, Bk, img, ic
from schema import TX, S, NUM, BOOL, IMG, ALT, VID, SEL, LIST
from layout import PAGE_FIELDS_CTA, PHERO, page, phero, trail, cta_band, head, video_card, bgv

FILE = 'cases.html'
DIR = 'pages/cases'
LABEL = 'ผลงาน'

GROUPS = [('thailand', 'โครงการในประเทศไทย (แบบละเอียด มีรูปหลายรูป)'), ('asia', 'ภูมิภาคเอเชีย (การ์ดเล็ก)')]
CASE_FIELDS = [
    S('anchor', 'รหัสโครงการ (ภาษาอังกฤษตัวเล็ก ไม่เว้นวรรค เช่น tcav)', req=True,
      desc='ใช้เป็นชื่อไฟล์และลิงก์ตรงไปที่โครงการนี้ เช่น cases.html#tcav'),
    SEL('group', 'แสดงในส่วน', GROUPS),
    NUM('order', 'ลำดับการแสดง (เลขน้อยแสดงก่อน)'),
    BOOL('hide', 'ซ่อนโครงการนี้ (ยังไม่แสดงบนเว็บ)'),
    TX('eyebrow', 'หัวข้อเล็ก (เช่น โครงการนำร่อง · ระยอง)'),
    TX('title', 'ชื่อโครงการ', req=True),
    LIST('paragraphs', 'ย่อหน้า (ใช้ **ข้อความ** เพื่อทำตัวหนา)', [TX('text', 'ข้อความ', long=True)]),
    TX('place', 'สถานที่ / ประเทศ'),
    TX('scope', 'ขอบเขตงาน'),
    TX('vehicles', 'รถที่ใช้'),
    TX('status', 'สถานะ (เช่น โครงการนำร่อง / พันธมิตรเทคโนโลยี)'),
    LIST('gallery', 'รูปภาพ (รูปแรกแสดงใหญ่)', [IMG(), ALT()], summary='{alt}'),
    VID('video', 'วิดีโอ (MP4) เว้นว่างได้'), IMG('poster', 'ภาพก่อนกดเล่นวิดีโอ'), TX('video_caption', 'คำบรรยายวิดีโอ'),
    SEL('video_position', 'ตำแหน่งวิดีโอ', [('text', 'ใต้ข้อความ'), ('media', 'เหนือรูปภาพ')]),
]

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
    ('thailand', '2. หัวข้อส่วนโครงการในประเทศไทย', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย (เว้นว่างได้)', long=True),
        TX('label_place', 'ชื่อแถว: สถานที่'), TX('label_scope', 'ชื่อแถว: ขอบเขตงาน'),
        TX('label_vehicles', 'ชื่อแถว: รถที่ใช้'), TX('label_status', 'ชื่อแถว: สถานะ'),
    ]),
    ('asia', '3. หัวข้อส่วนภูมิภาคเอเชีย', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True)]),
]

COLLECTIONS = [('cases', '📁 ผลงาน / โครงการ (หน้า ผลงาน)', 'cases', CASE_FIELDS,
                {'fields': ['title_th', 'group', 'order', 'hide'], 'primary': 'title_th', 'sort': ['order', 'title_th'],
                 'default': {'sort': 'order', 'order': 'asc'}})]


def _order(c):
    try:
        return float(c.get('order'))
    except (TypeError, ValueError):
        return 9999.0


def anchor(c, slug=''):
    """Safe id for cases.html#id (letters, numbers and dashes)."""
    a = re.sub(r'[^a-z0-9_-]+', '-', s(c, 'anchor').lower()).strip('-')
    return a or re.sub(r'[^a-z0-9_-]+', '-', slug.lower()).strip('-') or 'case'


def cases(group):
    rows = [(slug, c) for slug, c in collection('cases') if not c.get('hide') and (s(c, 'group') or 'thailand') == group]
    rows.sort(key=lambda x: (_order(x[1]), x[0]))
    return [dict(c, _id=anchor(c, slug)) for slug, c in rows]


def _video(c):
    if not s(c, 'video'):
        return ''
    th, zh, en = tri(c, 'video_caption')
    return video_card({'video': s(c, 'video'), 'poster': s(c, 'poster'), 'caption_th': th, 'caption_zh': zh, 'caption_en': en})


def detail(c, lab):
    gal = '<div class="gallery">' + ''.join(img(g) for g in items(c, 'gallery')) + '</div>'
    vid = _video(c)
    at_media = vid and s(c, 'video_position') == 'media'
    media_col = f'<div class="stack">{vid}\n    {gal}</div>' if at_media else gal
    facts = [(tri(lab, f'label_{k}'), tri(c, k)) for k in ('place', 'scope', 'vehicles', 'status') if has(c, k)]
    lines = [f'<span class="eyebrow">{Tk(c, "eyebrow")}</span>', f'<h2 class="h2">{TC(tri(c, "title"))}</h2>']
    lines += [Bk('p', p, 'text') for p in items(c, 'paragraphs')]
    if facts:
        lines.append('<dl class="facts">' + ''.join(f'<div><dt>{T(k)}</dt><dd>{T(v)}</dd></div>' for k, v in facts) + '</dl>')
    if vid and not at_media:
        lines.append(vid)
    body = '\n    '.join(lines)
    return f'''<article class="case-detail" id="{esc(c['_id'])}">
  {media_col}
  <div class="stack">
    {body}
  </div>
</article>'''


def card(c):
    first = (items(c, 'gallery') or [{}])[0]
    paras = ''.join(Bk('p', p, 'text') for p in items(c, 'paragraphs'))
    status = f'<span class="status partner">{Tk(c, "status")}</span>' if has(c, 'status') else ''
    return f'''<article class="case">{img(first)}<div class="case-meta">{status}<span>{ic('pin')}{Tk(c, 'place')}</span></div>
  <h3>{TC(tri(c, 'title'))}</h3>{paras}</article>'''


BG_KEYS = ('hero', 'thailand', 'asia')

def render():
    h = C(f'{DIR}/hero')
    hero = phero(img(h, lazy=False), 'photo', trail('about', h), h)
    th, asia = C(f'{DIR}/thailand'), C(f'{DIR}/asia')
    local = ''.join(detail(c, th) for c in cases('thailand'))
    thailand = f'''<section class="section">
  <div class="wrap">
    {head(th)}
    {local}
  </div>
</section>'''
    cards = '\n      '.join(card(c) for c in cases('asia'))
    regional = f'''<section class="section section--mist">
  <div class="wrap">
    {head(asia)}
    <div class="cases">
      {cards}
    </div>
  </div>
</section>''' if cards else ''
    pg = C(f'{DIR}/page')
    return page(FILE, pg, bgv(hero, h) + bgv(thailand, th) + bgv(regional, asia) + cta_band(pg))
