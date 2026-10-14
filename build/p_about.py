# -*- coding: utf-8 -*-
"""About page (about.html)."""
from core import C, s, items, fmt, Tk, Bk, img, ic
from schema import TX, S, LINK, BOOL, NUM, IMG, ALT, ICON, LIST, STEP
from layout import PAGE_FIELDS_CTA, PHERO, page, phero, trail, cta_band, head, steps, bgv
from p_home import STRIP, strip
from thailand_map import thai_map

FILE = 'about.html'
DIR = 'pages/about'
LABEL = 'เกี่ยวกับ SuperX'

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
    ('story', '2. เรื่องราวของเรา', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True),
        LIST('paragraphs', 'ย่อหน้า (ใช้ **ข้อความ** เพื่อทำตัวหนา)', [TX('text', 'ข้อความ', long=True)]),
        IMG(), ALT(),
    ]),
    ('vision', '3. วิสัยทัศน์และพันธกิจ', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True),
        LIST('items', 'กล่องข้อความ', [TX('title', 'หัวข้อกล่อง (เช่น วิสัยทัศน์)'), TX('text', 'ข้อความ', long=True)]),
    ]),
    ('group', '4. เครือบริษัท', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        S('parent_name', 'บริษัทแม่ (กล่องบน) ชื่อ'), TX('parent_text', 'บริษัทแม่ คำอธิบาย'),
        LIST('members', 'บริษัทในเครือ (กล่องล่าง)', [S('name', 'ชื่อ'), TX('text', 'คำอธิบาย'), BOOL('is_us', 'เน้นกรอบ (บริษัทเรา)')],
             summary='{name}'),
        IMG(), ALT(),
    ]),
    ('approach', '5. รูปแบบความร่วมมือ', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('steps', 'ขั้นตอน', STEP)]),
    ('roadmap', '6. แผนงานในประเทศไทย', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('steps', 'ขั้นตอน', STEP),
        S('target_number', 'ตัวเลขเป้าหมาย (ตัวใหญ่)'), TX('target_text', 'คำอธิบายเป้าหมาย', long=True),
        TX('map_title', 'แผนที่: หัวข้อเหนือรายชื่อโซน'),
        TX('map_origin', 'แผนที่: ชื่อที่ตั้งบริษัท (จุด HQ)'), TX('map_origin_text', 'แผนที่: คำอธิบายที่ตั้งบริษัท'),
        NUM('map_origin_lat', 'แผนที่: ละติจูดของที่ตั้งบริษัท', desc='หาได้จาก Google Maps: คลิกขวาที่จุด แล้วกดตัวเลขบรรทัดแรก ตัวแรกคือละติจูด ตัวหลังคือลองจิจูด'),
        NUM('map_origin_lng', 'แผนที่: ลองจิจูดของที่ตั้งบริษัท'),
        LIST('map_points', 'แผนที่: โซนปลายทาง (มีเส้นทางวิ่งจากที่ตั้งบริษัท) ลบหมด = ไม่แสดงแผนที่', [
            TX('name', 'ชื่อโซน'), TX('text', 'คำอธิบายสั้น'),
            NUM('lat', 'ละติจูด', desc='หาได้จาก Google Maps: คลิกขวาที่จุด แล้วกดตัวเลขบรรทัดแรก'), NUM('lng', 'ลองจิจูด'),
        ], summary='{name_th}'),
    ]),
    ('partners', '7. พันธมิตร', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True),
        LIST('items', 'การ์ดพันธมิตร', [ICON(), TX('role', 'ป้ายเล็ก (เช่น พันธมิตรเทคโนโลยี)'), S('name', 'ชื่อ'), TX('text', 'คำอธิบาย', long=True)],
             summary='{name}'),
        STRIP, TX('strip_link_label', 'ข้อความลิงก์ท้ายแถบ'), LINK('strip_link', 'ลิงก์ท้ายแถบ'),
    ]),
]


BG_KEYS = ('hero', 'story', 'vision', 'group', 'approach', 'roadmap', 'partners')

def render():
    h = C(f'{DIR}/hero')
    hero = phero(img(h, lazy=False), 'photo', trail(None, h), h)

    st = C(f'{DIR}/story')
    paras = '\n      '.join(Bk('p', p, 'text') for p in items(st, 'paragraphs'))
    story = f'''<section class="section">
  <div class="wrap split wide-left">
    <div class="prose">
      <span class="eyebrow">{Tk(st, 'eyebrow')}</span>
      <h2 class="h2">{Tk(st, 'title')}</h2>
      {paras}
    </div>
    {img(st, cls='rounded-img ratio-4-3')}
  </div>
</section>'''

    vm = C(f'{DIR}/vision')
    boxes = '\n      '.join(f'<div><dt>{Tk(x, "title")}</dt><dd>{Tk(x, "text")}</dd></div>' for x in items(vm, 'items'))
    vision = f'''<section class="section section--mist">
  <div class="wrap">
    {head(vm)}
    <dl class="vm">
      {boxes}
    </dl>
  </div>
</section>'''

    gr = C(f'{DIR}/group')
    members = '\n        '.join(
        f'<div class="eco-node{" is-us" if x.get("is_us") else ""}"><b>{fmt(s(x, "name"))}</b><span>{Tk(x, "text")}</span></div>'
        for x in items(gr, 'members'))
    group = f'''<section class="section">
  <div class="wrap split">
    <div class="stack">
      <span class="eyebrow">{Tk(gr, 'eyebrow')}</span>
      <h2 class="h2">{Tk(gr, 'title')}</h2>
      {Bk('p', gr, 'lead', cls='lead')}
    </div>
    <div class="eco">
      <div class="eco-node"><b>{fmt(s(gr, 'parent_name'))}</b><span>{Tk(gr, 'parent_text')}</span></div>
      <div class="eco-row">
        {members}
      </div>
      {img(gr, cls='rounded-img ratio-16-10', extra=' style="margin-top:20px"')}
    </div>
  </div>
</section>'''

    ap = C(f'{DIR}/approach')
    approach = f'''<section class="section section--mist">
  <div class="wrap">
    {head(ap)}
    {steps(items(ap, 'steps'), 'goal')}
  </div>
</section>'''

    rm = C(f'{DIR}/roadmap')
    target = ''
    if s(rm, 'target_number'):
        target = f'\n    <div class="target"><b>{fmt(s(rm, "target_number"))}</b>{Bk("p", rm, "target_text", cls="lead")}</div>'
    roadmap = f'''<section class="section">
  <div class="wrap">
    {head(rm)}
    {thai_map(rm)}
    {steps(items(rm, 'steps'), 's4 goal')}{target}
  </div>
</section>'''

    pt = C(f'{DIR}/partners')
    cards = '\n      '.join(
        f'<div class="model-card">{ic(s(x, "icon"))}<span class="module-label">{Tk(x, "role")}</span><h3>{fmt(s(x, "name"))}</h3>{Bk("p", x, "text")}</div>'
        for x in items(pt, 'items'))
    partners = f'''<section class="section section--mist" id="partners">
  <div class="wrap">
    {head(pt)}
    <div class="grid-3">
      {cards}
    </div>
    {strip(pt)}
  </div>
</section>'''

    pg = C(f'{DIR}/page')
    return page(FILE, pg, bgv(hero, h) + bgv(story, st) + bgv(vision, vm) + bgv(group, gr) + bgv(approach, ap) + bgv(roadmap, rm)
                + bgv(partners, pt) + cta_band(pg))
