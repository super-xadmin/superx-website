# -*- coding: utf-8 -*-
"""404 page: shown for any address that does not exist. build.py makes its links absolute."""
from core import C, s, items, fmt, Tk, Bk, href
from schema import TX, S, LINK, LIST
from layout import PAGE_FIELDS, page, bgv

FILE = '404.html'
DIR = 'pages/404'
LABEL = 'หน้าไม่พบ (404)'

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า)', PAGE_FIELDS),
    ('content', 'ข้อความและปุ่ม', [
        S('eyebrow', 'ข้อความเล็กด้านบน'), TX('title', 'หัวข้อ'), TX('lead', 'คำอธิบาย', long=True),
        LIST('buttons', 'ปุ่ม (ปุ่มแรกเป็นสีน้ำเงิน)', [TX('label', 'ข้อความ'), LINK()]),
    ]),
]


BG_KEYS = ('content',)

def render():
    d = C(f'{DIR}/content')
    btns = []
    for i, b in enumerate(items(d, 'buttons')):
        cls = 'btn btn-primary' if i == 0 else 'btn btn-outline'
        btns.append(f'<a class="{cls}" href="{href(s(b, "link"))}">{Tk(b, "label")}</a>')
    buttons = '\n      '.join(btns)
    body = f'''<section class="section">
  <div class="wrap" style="max-width:760px;text-align:center;padding-block:48px">
    <span class="eyebrow">{fmt(s(d, 'eyebrow'))}</span>
    <h1 class="h1">{Tk(d, 'title')}</h1>
    {Bk('p', d, 'lead', cls='lead')}
    <div class="btn-row" style="justify-content:center;margin-top:24px">
      {buttons}
    </div>
  </div>
</section>'''
    html = page(FILE, C(f'{DIR}/page'), bgv(body, d))
    return html.replace('<meta name="theme-color"', '<meta name="robots" content="noindex"><meta name="theme-color"', 1)
