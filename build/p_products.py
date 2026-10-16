# -*- coding: utf-8 -*-
"""Product centre (products.html)."""
from core import C, s, items, tri, has, esc, fmt, T, TC, B, Tk, Bk, media, img, href, ic
from schema import TX, S, LINK, IMG, ALT, DOC, ICON, MODEL, LIST, CHAT, SEL, BULLET
from layout import (PAGE_FIELDS_CTA, PHERO, page, phero, trail, cta_band, product_card, chat_art, chips, checks, downloads,
                    spec_table, model, form_model, mkey, bgv, head)

FILE = 'products.html'
DIR = 'pages/products'
LABEL = 'RoboVan ทุกรุ่น (ผลิตภัณฑ์ทั้งหมด)'
CHIP = [S('anchor', 'ไปที่หัวข้อ (#)', desc='เช่น robovan, z20, services, technology, solutions'), ICON(), TX('label', 'ข้อความ')]

# Listed in the order they appear on the page: the RoboVan range first, other solutions last
SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพหลักและหัวข้อ', PHERO([LIST('chips', 'ปุ่มลัดไปยังหัวข้อ', CHIP)])),
    ('robovan', '2. RoboVan ทุกรุ่น (การ์ดรถ)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        LIST('row1', 'การ์ดรถแถวที่ 1', [MODEL()], summary='{model}'),
        LIST('row2', 'การ์ดรถแถวที่ 2', [MODEL()], summary='{model}'),
        TX('compare_title', 'หัวข้อตารางเปรียบเทียบ'),
    ]),
    ('compare', '3. ตารางเปรียบเทียบทุกรุ่น', [
        TX('col_model', 'หัวคอลัมน์: รุ่น'), TX('col_volume', 'หัวคอลัมน์: ปริมาตร'), TX('col_payload', 'หัวคอลัมน์: บรรทุก'),
        TX('col_range', 'หัวคอลัมน์: ระยะวิ่ง'), TX('col_battery', 'หัวคอลัมน์: แบตเตอรี่'), TX('col_cold', 'หัวคอลัมน์: ห้องเย็น'),
        TX('col_speed', 'หัวคอลัมน์: ความเร็ว'), TX('col_dims', 'หัวคอลัมน์: ขนาด'),
        LIST('models', 'รุ่นในตาราง (ค่าแต่ละช่องแก้ที่เมนู ข้อมูลรถแต่ละรุ่น)', [MODEL()], summary='{model}'),
        LIST('notes', 'หมายเหตุใต้ตาราง', [TX('text', 'ข้อความ', long=True)]),
    ]),
    ('others', '4. รุ่นอื่น (Multi-Locker / Z20)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('used_label', 'คำว่า การใช้งาน'), TX('ask_label', 'ปุ่มสอบถาม'), TX('download_label', 'ปุ่มดาวน์โหลดสเปก'),
        LIST('items', 'รุ่น', [MODEL(), S('anchor', 'รหัสหัวข้อ (#)'), TX('lead', 'คำอธิบาย', long=True), TX('uses', 'การใช้งาน', long=True)], summary='{anchor}'),
    ]),
    ('services', '5. ซื้อหรือเช่า และบริการ', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True),
        LIST('plans', 'รูปแบบการซื้อ / เช่า', [ICON(), TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย', long=True)]),
        LIST('services', 'บริการ', [ICON(), TX('label', 'ข้อความ')]),
    ]),
    ('technology', '6. ชุดระบบขับขี่อัตโนมัติ L4', [
        IMG(), ALT(), TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('text', 'คำอธิบาย', long=True),
        LIST('specs', 'รายการอุปกรณ์', [TX('label', 'ชื่อ'), S('value', 'จำนวน / ค่า')], summary='{label_th} {value}'),
        LIST('downloads', 'เอกสารดาวน์โหลด', [DOC(), S('title', 'ชื่อเอกสาร')], summary='{title}'),
    ]),
    ('lines', '7. โซลูชันอื่น (การศึกษา / ความปลอดภัย / AI Agent)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        LIST('items', 'กลุ่มโซลูชัน', [
            S('anchor', 'รหัสหัวข้อ (#)'), SEL('media_type', 'ภาพประกอบ', [('image', 'รูปภาพ'), ('chat', 'ข้อความแชตตัวอย่าง')]), IMG(), ALT(), CHAT(),
            TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'), TX('lead', 'คำอธิบาย', long=True),
            LIST('bullets', 'รายการเครื่องหมายถูก', BULLET), TX('button_label', 'ปุ่ม'), LINK('button_link', 'ลิงก์ปุ่ม'),
        ]),
    ]),
]


def compare_table(cm):
    heads = ['col_model', 'col_volume', 'col_payload', 'col_range', 'col_battery', 'col_cold', 'col_speed', 'col_dims']
    th = [f'<th scope="col">{Tk(cm, h)}</th>' for h in heads]
    rows = []
    for r in items(cm, 'models'):
        m = model(s(r, 'model'))
        cold = s(m, 'cmp_cold')
        cold_html = f'<span class="cold">{fmt(cold)}</span>' if cold and cold != '—' else '—'
        rows.append(f'<tr><th scope="row"><a href="{href(s(m, "page"))}">{fmt(s(m, "model_name"))}</a><span>{Tk(m, "type")}</span></th>'
                    f'<td>{TC(tri(m, "cmp_volume"))}</td><td>{fmt(s(m, "cmp_payload"))}</td><td>{fmt(s(m, "cmp_range"))}</td>'
                    f'<td>{fmt(s(m, "cmp_battery"))}</td><td>{cold_html}</td><td>{fmt(s(m, "cmp_speed"))}</td><td>{fmt(s(m, "cmp_dims"))}</td></tr>')
    notes = ''.join(Bk('p', n, 'text', cls='note') for n in items(cm, 'notes'))
    return f'''<div class="spec-wrap"><table class="compare">
  <thead><tr>{th[0]}{th[1]}{th[2]}
  {th[3]}{th[4]}{th[5]}
  {th[6]}{th[7]}</tr></thead>
  <tbody>{"".join(rows)}</tbody></table></div>
  <div class="spec-foot">{notes}</div>'''


def other_block(ot, it):
    m = model(s(it, 'model'))
    pdf = media(s(m, 'pdf'), 'docs')
    dl = (f'\n      <a class="btn btn-outline" href="{esc(pdf)}" target="_blank" rel="noopener">{ic("download")}{Tk(ot, "download_label")}</a>'
          if pdf else '')
    return f'''<div class="line" id="{esc(s(it, 'anchor'))}">
  <div class="line-media studio" style="aspect-ratio:16/10">{img(m, alt=s(m, 'full_name'))}</div>
  <div class="stack">
    <span class="eyebrow">{Tk(ot, 'eyebrow')}</span>
    <h3 class="h2">{fmt(s(m, 'full_name'))}</h3>
    {Bk('p', it, 'lead', cls='lead')}
    <p class="small"><b style="color:var(--ink)">{Tk(ot, 'used_label')}:</b> {Tk(it, 'uses')}</p>
    {spec_table([s(it, 'model')])}
    <div class="btn-row"><a class="btn btn-primary" href="contact.html?topic=quote&amp;model={esc(form_model(m))}">{Tk(ot, 'ask_label')}</a>{dl}</div>
  </div>
</div>'''


def line_block(ln):
    if s(ln, 'media_type') == 'chat':
        med = chat_art(items(ln, 'chat'))
    else:
        med = img(ln)
    return f'''<div class="line" id="{esc(s(ln, 'anchor'))}">
  <div class="line-media">{med}</div>
  <div class="stack"><span class="eyebrow">{Tk(ln, 'eyebrow')}</span><h3 class="h2">{Tk(ln, 'title')}</h3>{Bk('p', ln, 'lead', cls='lead')}
    {checks(items(ln, 'bullets'))}
    <div class="btn-row"><a class="btn btn-primary" href="{href(s(ln, 'button_link'))}">{Tk(ln, 'button_label')}{ic('arrow')}</a></div></div>
</div>'''


BG_KEYS = ('hero', 'robovan', 'others', 'technology', 'lines', 'services')

def render():
    h = C(f'{DIR}/hero')
    hero = phero(img(h, lazy=False), 'photo', trail(None, h), h, '<div class="chips">' + ''.join(chips(items(h, 'chips'))) + '</div>')

    rv, cm, ot = C(f'{DIR}/robovan'), C(f'{DIR}/compare'), C(f'{DIR}/others')
    row1 = ''.join(product_card(s(r, 'model')) for r in items(rv, 'row1'))
    row2 = ''.join(product_card(s(r, 'model')) for r in items(rv, 'row2'))
    others = ''.join(other_block(ot, it) for it in items(ot, 'items'))
    robovan = f'''<section class="section" id="robovan">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">{TC(tri(rv, 'eyebrow'))}</span>
      <h2 class="h2">{Tk(rv, 'title')}</h2>
      {Bk('p', rv, 'lead', cls='lead')}
    </div>
    <div class="pcards c3">{row1}</div>
    <div class="pcards c3" style="margin-top:20px">{row2}</div>
    <h3 class="h3" style="margin:48px 0 16px">{Tk(rv, 'compare_title')}</h3>
    {compare_table(cm)}
  </div>
</section>
<section class="section section--mist">
  <div class="wrap">{others}</div>
</section>'''

    tc = C(f'{DIR}/technology')
    kv = '\n        '.join(f'<div><dt>{Tk(r, "label")}</dt><dd>{fmt(s(r, "value"))}</dd></div>' for r in items(tc, 'specs'))
    suite = f'''<section class="section" id="technology">
  <div class="wrap split wide-right">
    <div class="studio" style="border-radius:var(--r);padding:20px">{img(tc, w=1050, h=999)}</div>
    <div class="stack">
      <span class="eyebrow">{Tk(tc, 'eyebrow')}</span>
      <h2 class="h2">{Tk(tc, 'title')}</h2>
      {Bk('p', tc, 'text')}
      <dl class="kv">
        {kv}
      </dl>
      <div class="btn-row">{downloads(items(tc, 'downloads'))}</div>
    </div>
  </div>
</section>'''

    ln = C(f'{DIR}/lines')
    lines_html = '\n    '.join(line_block(x) for x in items(ln, 'items'))
    lines_head = head(ln, link=False) if has(ln, 'title') else ''
    lines = f'''<section class="section section--mist" id="solutions">
  <div class="wrap">
    {lines_head}
    {lines_html}
  </div>
</section>'''

    sv = C(f'{DIR}/services')
    plans = '\n      '.join(f'<div class="model-card">{ic(s(p, "icon"))}<h3>{Tk(p, "title")}</h3>{Bk("p", p, "text")}</div>' for p in items(sv, 'plans'))
    servs = '\n      '.join(f'<div class="service">{ic(s(x, "icon"))}{Tk(x, "label")}</div>' for x in items(sv, 'services'))
    services = f'''<section class="section" id="services">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">{Tk(sv, 'eyebrow')}</span>
      <h2 class="h2">{Tk(sv, 'title')}</h2></div>
    <div class="models2">
      {plans}
    </div>
    <div class="services">
      {servs}
    </div>
  </div>
</section>'''

    pg = C(f'{DIR}/page')
    # RoboVan range → other models → how to buy → technology → other solutions
    body = (bgv(hero, h) + bgv(bgv(robovan, rv), ot, nth=1) + bgv(services, sv) + bgv(suite, tc) + bgv(lines, ln)
            + cta_band(pg))
    return page(FILE, pg, body)
