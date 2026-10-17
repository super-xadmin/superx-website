# -*- coding: utf-8 -*-
"""Home page (index.html)."""
from core import C, s, items, tri, has, esc, fmt, T, TC, B, Tk, Bk, aria, media, img, href, ic
from schema import TX, S, LINK, BOOL, IMG, ALT, VID, ICON, MODEL, LIST, CHAT, SEL, STEP
from layout import PAGE_FIELDS_CTA, page, cta_band, chat_art, model, mkey, form_model, kv, bgv, head, steps, link_shown

FILE = 'index.html'
DIR = 'pages/home'
LABEL = 'หน้าแรก'
STRIP = LIST('strip', 'แถบพันธมิตรด้านล่าง', [IMG('logo', 'โลโก้ (PNG พื้นใส หรือ SVG) ใส่แล้วจะแสดงเป็นแถบโลโก้เลื่อนไปทางซ้าย'),
                                               TX('label', 'ข้อความนำ (เว้นว่างได้)'), TX('name', 'ชื่อ (ตัวหนา)'), TX('small', 'คำอธิบายเล็ก (เว้นว่างได้)')],
             summary='{label_th} {name_th}')

# Short band right under the film: pilot sites and partners, so visitors see real proof straight away
PROOF = [
    TX('label', 'ข้อความนำ (เช่น โครงการนำร่องและพันธมิตร)'),
    LIST('items', 'รายชื่อโครงการ / พันธมิตร', [
        TX('name', 'ชื่อ (ตัวหนา)'), TX('small', 'คำอธิบายเล็ก (เว้นว่างได้)'),
        IMG('logo', 'โลโก้ (เว้นว่างได้ ถ้าใส่จะแสดงโลโก้แทนชื่อ)'), LINK(),
    ], summary='{name_th}'),
    TX('link_label', 'ข้อความลิงก์ท้ายแถบ'), LINK('link', 'ลิงก์ท้ายแถบ'),
]

# Listed in the order they appear on the page (top to bottom), the main business (RoboVan) first
SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพวิดีโอด้านบนสุด', [
        VID('video', 'วิดีโอพื้นหลัง (MP4 สั้นๆ ไม่มีเสียง)'), IMG('poster', 'ภาพก่อนวิดีโอเล่น'),
        TX('eyebrow', 'ข้อความเล็กด้านบน'), TX('title', 'หัวข้อใหญ่ (ขึ้นบรรทัดใหม่ได้)', long=True,
                                                  desc='บอกให้ชัดว่าเราขายอะไร ให้ใคร · ใช้ **คำ** เพื่อทำเป็นสีฟ้า'),
        TX('lead', 'คำอธิบาย', long=True),
        TX('btn1_label', 'ปุ่มที่ 1'), LINK('btn1_link', 'ลิงก์ปุ่มที่ 1'), TX('btn2_label', 'ปุ่มที่ 2'), LINK('btn2_link', 'ลิงก์ปุ่มที่ 2'),
        LIST('facts', 'ตัวเลขเด่นด้านล่าง', [S('value', 'ตัวเลข'), TX('label', 'คำอธิบาย')], summary='{value} {label_th}'),
        TX('caption', 'คำบรรยายวิดีโอ (มุมขวาล่าง)'),
    ]),
    ('proof', '2. แถบโครงการนำร่องและพันธมิตร (ใต้ภาพวิดีโอ)', PROOF),
    ('about', '3. เราทำอะไร', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        LIST('flow', 'กล่อง 3 ขั้น (รถ → ติดตั้ง → ดูแล)', [
            TX('who', 'บรรทัดบน'), TX('name', 'ชื่อ (ตัวใหญ่)'), TX('text', 'คำอธิบาย'), BOOL('highlight', 'เน้นสีกล่องนี้'),
            LIST('bullets', 'รายการเครื่องหมายถูก', [TX('text', 'ข้อความ')]),
        ], summary='{name_th}'),
        LIST('stats', 'ตัวเลขสถิติ', [S('value', 'ตัวเลข'), TX('unit', 'หน่วย (ตัวเล็ก)'), TX('text', 'คำอธิบาย')], summary='{value} {text_th}'),
        TX('note', 'หมายเหตุใต้ตัวเลข', long=True),
    ]),
    ('models', '4. รุ่นรถ RoboVan', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('link_label', 'ข้อความลิงก์มุมขวา'), LINK('link', 'ลิงก์มุมขวา'),
        LIST('cards', 'การ์ดรถที่แสดง (ข้อมูลมาจากเมนู ข้อมูลรถแต่ละรุ่น)', [MODEL()], summary='{model}'),
        TX('others_label', 'ข้อความหน้าปุ่มรุ่นอื่น'),
        LIST('others', 'ปุ่มรุ่นอื่น', [TX('label', 'ข้อความ'), LINK()]),
    ]),
    ('start', '5. ขั้นตอนเริ่มใช้งาน 1-2-3 (ป๊อปอัพใช้ขั้นตอนชุดนี้ด้วย)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True, desc='ใช้ **คำ** เพื่อทำเป็นสีฟ้า'), TX('lead', 'คำอธิบาย', long=True),
        LIST('steps', 'ขั้นตอน (แนะนำ 3 ขั้น ไม่เกิน 4 ขั้น)', STEP, desc='ลบทุกขั้น = ไม่แสดงส่วนนี้ และไม่แสดงขั้นตอนในป๊อปอัพ'),
        TX('btn1_label', 'ปุ่มที่ 1'), LINK('btn1_link', 'ลิงก์ปุ่มที่ 1'),
        TX('btn2_label', 'ปุ่มที่ 2 (เว้นว่าง = ไม่มีปุ่มนี้)'), LINK('btn2_link', 'ลิงก์ปุ่มที่ 2'),
    ]),
    ('scenarios', '6. งานที่ใช้ RoboVan ได้ (การ์ดเลื่อน)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        LIST('tiles', 'ภาพการใช้งาน', [IMG(), ALT(), TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย')]),
    ]),
    ('cases', '7. ผลงานและพันธมิตร', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('link_label', 'ข้อความลิงก์มุมขวา'), LINK('link', 'ลิงก์มุมขวา'),
        LIST('cards', 'การ์ดผลงาน', [
            LINK(), IMG(), ALT(), TX('status', 'ป้ายสถานะ'), TX('location', 'สถานที่'), TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย', long=True),
        ]),
        STRIP, TX('strip_link_label', 'ข้อความลิงก์ท้ายแถบ'), LINK('strip_link', 'ลิงก์ท้ายแถบ'),
    ]),
    ('control', '8. แอปควบคุมฝูงรถ', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
        LIST('items', 'รายการความสามารถ', [ICON(), TX('text', 'ข้อความ')]),
        LIST('phones', 'ภาพหน้าจอแอป', [IMG('image', 'ภาพหน้าจอ (แนวตั้ง)'), ALT(), TX('label', 'คำบรรยาย')]),
    ]),
    ('business', '9. โซลูชันอื่น (การศึกษา / ความปลอดภัย / AI Agent)', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True), TX('more', 'ข้อความลิงก์ในการ์ด'),
        LIST('modules', 'การ์ดโซลูชัน', [
            LINK(), SEL('media_type', 'ภาพประกอบ', [('image', 'รูปภาพ'), ('chat', 'ข้อความแชตตัวอย่าง')]), IMG(), ALT(), CHAT(),
            TX('label', 'ป้ายเล็ก (เช่น 01 · Education)'), TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย', long=True),
        ]),
    ]),
]


def logo_marquee(logos):
    """Partner logos sliding slowly to the left, repeated so the row never runs out."""
    one = ''.join(f'<li><img src="{esc(media(s(e, "logo"), "img"))}" alt="{esc(tri(e, "name")[2] or tri(e, "name")[0])}" loading="lazy"></li>'
                  for e in logos)
    reps = max(1, -(-8 // len(logos)))          # at least 8 logos per half
    hidden = one.replace('<li>', '<li aria-hidden="true">')
    half = one + hidden * (reps - 1)            # repeats are hidden from screen readers and when motion is reduced
    copy = hidden * reps
    return f'<div class="logo-marquee"><ul class="logo-track">{half}{copy}</ul></div>'


def strip(d, key='strip', link_label='strip_link_label', link='strip_link'):
    logos = [e for e in items(d, key) if s(e, 'logo')]
    lines = []
    if logos:
        lines.append(logo_marquee(logos))
    for e in items(d, key):
        if s(e, 'logo'):
            continue
        part = ''
        if has(e, 'label'):
            part += f'<span>{Tk(e, "label")}</span>'
        if has(e, 'name'):
            small = f' <small>{Tk(e, "small")}</small>' if has(e, 'small') else ''
            part += f'<span class="partner-name">{TC(tri(e, "name"))}{small}</span>'
        lines.append(part)
    if s(d, link) and has(d, link_label):
        lines.append(f'<a class="link-arrow" href="{href(s(d, link))}">{Tk(d, link_label)}{ic("arrow")}</a>')
    return '<div class="partner-strip">\n      ' + '\n      '.join(lines) + '\n    </div>'


def proof_band(d):
    """Pilot sites and partners in one row under the film. Nothing listed = no band."""
    rows = [e for e in items(d, 'items') if has(e, 'name') or s(e, 'logo')]
    if not rows:
        return ''

    def one(e):
        logo, name = media(s(e, 'logo'), 'img'), tri(e, 'name')
        inner = f'<img src="{esc(logo)}" alt="{esc(name[2] or name[0])}" loading="lazy">' if logo else f'<b>{TC(name)}</b>'
        small = f'<small>{Tk(e, "small")}</small>' if has(e, 'small') else ''
        if s(e, 'link'):
            return f'<a class="proof-item" href="{href(s(e, "link"))}">{inner}{small}</a>'
        return f'<span class="proof-item">{inner}{small}</span>'
    label = f'<span class="proof-label">{Tk(d, "label")}</span>' if has(d, 'label') else ''
    more = (f'<a class="link-arrow" href="{href(s(d, "link"))}">{Tk(d, "link_label")}{ic("arrow")}</a>'
            if s(d, 'link') and has(d, 'link_label') else '')
    return f'''<section class="proof" id="proof">
  <div class="wrap proof-row">
    {label}
    <div class="proof-list">{''.join(one(e) for e in rows)}</div>
    {more}
  </div>
</section>'''


def start_section(d):
    """How to start using RoboVan, 1-2-3, with buttons. The pop-up (promo.py) shows the same steps.
    No steps listed = no section."""
    rows = [r for r in items(d, 'steps') if has(r, 'title')]
    if not rows:
        return ''
    btns = []
    for lab, lnk, cls, before, after in (('btn1_label', 'btn1_link', 'btn-primary', ic('calendar'), ''),
                                         ('btn2_label', 'btn2_link', 'btn-outline', '', ic('arrow'))):
        if has(d, lab) and s(d, lnk) and link_shown(s(d, lnk)):
            btns.append(f'<a class="btn {cls}" href="{href(s(d, lnk))}">{before}{Tk(d, lab)}{after}</a>')
    cta = f'\n    <div class="btn-row start-cta">{"".join(btns)}</div>' if btns else ''
    return f'''<section class="section section--mist" id="start">
  <div class="wrap">
    {head(d, link=False)}
    {steps(rows, 'goal s4' if len(rows) == 4 else 'goal')}{cta}
  </div>
</section>'''


# Sections that can have a 🎬 background video (the top film has its own video field)
BG_KEYS = ('proof', 'about', 'business', 'models', 'start', 'control', 'scenarios', 'cases')

def render():
    lb = C('site/labels')
    h = C(f'{DIR}/hero')
    facts = '\n        '.join(f'<div class="hero-fact"><b>{fmt(s(f, "value"))}</b><span>{Tk(f, "label")}</span></div>' for f in items(h, 'facts'))
    hero = f'''<section class="hero">
  <div class="hero-media">
    <video autoplay muted loop playsinline preload="auto" poster="{esc(media(s(h, 'poster'), 'img'))}" aria-hidden="true">
      <source src="{esc(media(s(h, 'video'), 'video'))}" type="video/mp4">
    </video>
  </div>
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <span class="eyebrow">{Tk(h, 'eyebrow')}</span>
      <h1 class="h1">{Tk(h, 'title')}</h1>
      {Bk('p', h, 'lead', cls='lead')}
      <div class="btn-row">
        <a class="btn btn-light" href="{href(s(h, 'btn1_link'))}">{ic('calendar')}{Tk(h, 'btn1_label')}</a>
        <a class="btn btn-ghost" href="{href(s(h, 'btn2_link'))}">{Tk(h, 'btn2_label')}{ic('arrow')}</a>
      </div>
    </div>
    <div class="hero-foot">
      <div class="hero-facts">
        {facts}
      </div>
    </div>
  </div>
</section>'''

    a = C(f'{DIR}/about')

    def flow_step(st):
        cls = ' is-us' if st.get('highlight') else ''
        lis = '\n          '.join(f'<li>{ic("check")}{Tk(b, "text")}</li>' for b in items(st, 'bullets'))
        return f'''<div class="flow-step{cls}">
        <span class="flow-who">{Tk(st, 'who')}</span>
        <span class="flow-name">{TC(tri(st, 'name'))}</span>
        {Bk('p', st, 'text')}
        <ul>
          {lis}
        </ul>
      </div>'''
    flow = '\n      '.join(flow_step(st) for st in items(a, 'flow'))
    stats = '\n      '.join(
        f'<div class="stat"><b>{fmt(s(st, "value"))}<small>{TC(tri(st, "unit"))}</small></b>{Bk("p", st, "text")}</div>' for st in items(a, 'stats'))
    positioning = f'''<section class="section" id="about">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">{Tk(a, 'eyebrow')}</span>
      <h2 class="h2">{Tk(a, 'title')}</h2>
      {Bk('p', a, 'lead', cls='lead')}
    </div>
    <div class="flow">
      {flow}
    </div>
    <div class="stats">
      {stats}
    </div>
    {Bk('p', a, 'note', cls='note stats-note')}
  </div>
</section>'''

    b = C(f'{DIR}/business')

    def module(mo):
        if s(mo, 'media_type') == 'chat':
            med = chat_art(items(mo, 'chat'))
        else:
            med = img(mo)
        return f'''<a class="module" href="{href(s(mo, 'link'))}">
  <div class="module-media">{med}</div>
  <div class="module-body"><span class="module-label">{Tk(mo, 'label')}</span><h3>{Tk(mo, 'title')}</h3>{Bk('p', mo, 'text')}<span class="link-arrow">{Tk(b, 'more')}{ic('arrow')}</span></div>
</a>'''
    mod_list = items(b, 'modules')
    mods = '\n      '.join(module(mo) for mo in mod_list)
    mod_cls = 'modules c3' if len(mod_list) == 3 else 'modules'
    modules = f'''<section class="section section--mist" id="business">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">{Tk(b, 'eyebrow')}</span>
      <h2 class="h2">{Tk(b, 'title')}</h2>
      {Bk('p', b, 'lead', cls='lead')}
    </div>
    <div class="{mod_cls}">
      {mods}
    </div>
  </div>
</section>'''

    m = C(f'{DIR}/models')
    refs = [s(x, 'model') for x in items(m, 'cards') if model(s(x, 'model'))]
    tabs, panels = [], []
    for i, ref in enumerate(refs):
        k, mo = esc(mkey(ref)), model(ref)
        on = i == 0
        tabs.append(f'<button class="lineup-tab" type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" '
                    f'aria-selected="{"true" if on else "false"}" tabindex="{0 if on else -1}">{fmt(s(mo, "model_name"))}</button>')
        tag = ''
        if has(mo, 'card_tag'):
            cold = ' cold' if s(mo, 'card_tag_style') == 'cold' else ''
            tag = f'<span class="pcard-tag{cold}">{Tk(mo, "card_tag")}</span>'
        facts = ''.join(f'<div><dt>{Tk(r, "label")}</dt><dd>{fmt(s(r, "value"))}</dd></div>' for r in items(mo, 'card_facts'))
        pdf = media(s(mo, 'pdf'), 'docs')
        if s(mo, 'card_button') == 'pdf' and pdf:
            a1 = f'<a class="btn btn-primary" href="{esc(pdf)}" target="_blank" rel="noopener">{ic("download")}{Tk(lb, "card_pdf")}</a>'
        else:
            a1 = f'<a class="btn btn-primary" href="{href(s(mo, "page"))}">{Tk(lb, "card_details")}</a>'
        a2 = f'<a class="btn btn-outline" href="contact.html?topic=quote&amp;model={esc(form_model(mo))}">{Tk(lb, "card_quote")}</a>'
        hidden = '' if on else ' hidden'
        panels.append(f'''<div class="lineup-panel" role="tabpanel" id="panel-{k}" aria-labelledby="tab-{k}"{hidden}>
      <div class="lineup-stage">{tag}{img(mo, alt=s(mo, 'full_name'), lazy=not on)}</div>
      <div class="lineup-name"><h3>{fmt(s(mo, 'model_name'))}</h3><span>{Tk(mo, 'type')}</span></div>
      <dl class="lineup-facts">{facts}</dl>
      <div class="btn-row">{a1}{a2}</div>
    </div>''')
    others = ''.join(f'<a class="chip" href="{href(s(o, "link"))}">{TC(tri(o, "label"))}</a>' for o in items(m, 'others'))
    more = ''
    if others or (s(m, 'link') and has(m, 'link_label')):
        link = f'<a class="link-arrow" href="{href(s(m, "link"))}">{Tk(m, "link_label")}{ic("arrow")}</a>' if s(m, 'link') and has(m, 'link_label') else ''
        more = f'''
    <div class="more-models"><span>{Tk(m, 'others_label')}</span>
      <div class="chips">{others}</div>{link}</div>'''
    tab_list = '\n        '.join(tabs)
    panel_list = '\n    '.join(panels)
    models = f'''<section class="section lineup" id="models">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">{Tk(m, 'eyebrow')}</span>
      <h2 class="h2">{Tk(m, 'title')}</h2></div>
    <div class="lineup-nav">
      <div class="lineup-tabs" role="tablist"{aria(tri(m, 'title'))}>
        {tab_list}
      </div>
    </div>
    {panel_list}{more}
  </div>
</section>'''

    c = C(f'{DIR}/control')
    lis = '\n        '.join(f'<li>{ic(s(i, "icon"))}{Tk(i, "text")}</li>' for i in items(c, 'items'))
    phones = '\n      '.join(
        f'<div class="phone-card"><div class="phone">{img(p, w=560, h=1212)}</div><span>{Tk(p, "label")}</span></div>' for p in items(c, 'phones'))
    control = f'''<section class="section section--night" id="control">
  <div class="wrap control-grid">
    <div class="stack">
      <span class="eyebrow">{TC(tri(c, 'eyebrow'))}</span>
      <h2 class="h2">{Tk(c, 'title')}</h2>
      {Bk('p', c, 'lead', cls='lead')}
      <ul class="control-list">
        {lis}
      </ul>
    </div>
    <div class="phones">
      {phones}
    </div>
  </div>
</section>'''

    sc = C(f'{DIR}/scenarios')
    cards = '\n      '.join(f'<figure class="rail-card">{img(t)}<figcaption><b>{Tk(t, "title")}</b>{Bk("p", t, "text")}</figcaption></figure>'
                            for t in items(sc, 'tiles'))
    scenarios = f'''<section class="section section--deep" id="scenarios">
  <div class="wrap">
    <div class="section-head is-left"><span class="eyebrow">{Tk(sc, 'eyebrow')}</span>
      <h2 class="h2">{Tk(sc, 'title')}</h2>
      {Bk('p', sc, 'lead', cls='lead')}
    </div>
  </div>
  <div class="rail-box" data-rail>
    <div class="rail" tabindex="0"{aria(tri(sc, 'title'))}>
      {cards}
    </div>
    <div class="wrap rail-nav">
      <button class="rail-btn prev" type="button"{aria(tri(lb, 'prev') if has(lb, 'prev') else ('ก่อนหน้า', '上一个', 'Previous'))}>{ic('arrow')}</button>
      <button class="rail-btn next" type="button"{aria(tri(lb, 'next') if has(lb, 'next') else ('ถัดไป', '下一个', 'Next'))}>{ic('arrow')}</button>
    </div>
  </div>
</section>'''

    cs = C(f'{DIR}/cases')

    def case(k):
        return f'''<a class="case" href="{href(s(k, 'link'))}">{img(k)}
        <div class="case-meta"><span class="status">{Tk(k, 'status')}</span><span>{ic('pin')}{Tk(k, 'location')}</span></div>
        <h3>{TC(tri(k, 'title'))}</h3>
        {Bk('p', k, 'text')}</a>'''
    case_cards = '\n      '.join(case(k) for k in items(cs, 'cards'))
    cases = f'''<section class="section section--mist" id="cases">
  <div class="wrap">
    <div class="section-head split">
      <div><span class="eyebrow">{Tk(cs, 'eyebrow')}</span>
        <h2 class="h2">{Tk(cs, 'title')}</h2></div>
      <a class="link-arrow" href="{href(s(cs, 'link'))}">{Tk(cs, 'link_label')}{ic('arrow')}</a>
    </div>
    <div class="cases">
      {case_cards}
    </div>
    {strip(cs)}
  </div>
</section>'''

    pr = C(f'{DIR}/proof')
    st = C(f'{DIR}/start')
    pg = C(f'{DIR}/page')
    # Main business first: what we sell and proof, the range and how to start, then uses, projects and the app;
    # other solutions last
    body = (hero + bgv(proof_band(pr), pr) + bgv(positioning, a) + bgv(models, m) + bgv(start_section(st), st)
            + bgv(scenarios, sc) + bgv(cases, cs) + bgv(control, c) + bgv(modules, b) + cta_band(pg))
    return page(FILE, pg, body)
