# -*- coding: utf-8 -*-
"""Contact page (contact.html): company details and the enquiry form that sends leads to Lark."""
import json

from core import C, s, items, tri, has, esc, fmt, T, Tk, Bk, ph, opt, img, href, ic, LANGS
from schema import TX, S, SEL, LIST, STEP
from layout import PAGE_FIELDS, PHERO, page, phero, trail, steps, SOCIAL_ICON, social_name, bgv

FILE = 'contact.html'
DIR = 'pages/contact'
LABEL = 'ติดต่อเรา'

LARK_COLORS = [('blue', 'น้ำเงิน'), ('wathet', 'ฟ้าอ่อน'), ('turquoise', 'เขียวอมฟ้า'), ('green', 'เขียว'), ('yellow', 'เหลือง'),
               ('orange', 'ส้ม'), ('red', 'แดง'), ('carmine', 'แดงเข้ม'), ('violet', 'ม่วงอ่อน'), ('purple', 'ม่วง'),
               ('indigo', 'คราม'), ('grey', 'เทา')]

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า)', PAGE_FIELDS),
    ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
    ('details', '2. ช่องทางติดต่อ (เบอร์ อีเมล ที่อยู่ แก้ที่ ⚙️ ข้อมูลบริษัท)', [
        TX('eyebrow', 'หัวข้อเล็ก'),
        TX('label_phone', 'ชื่อแถว: โทรศัพท์'), TX('label_email', 'ชื่อแถว: อีเมล'), TX('label_address', 'ชื่อแถว: ที่อยู่'),
        TX('label_website', 'ชื่อแถว: เว็บไซต์'), TX('maps_button', 'ปุ่มเปิดแผนที่'),
        TX('next_title', 'หัวข้อ "หลังจากส่งข้อมูล"'), LIST('next_steps', 'ขั้นตอนหลังส่งข้อมูล', STEP),
    ]),
    ('form', '3. แบบฟอร์ม (ข้อความในช่อง และตัวเลือก)', [
        TX('title', 'หัวข้อแบบฟอร์ม'), TX('lead', 'คำอธิบายใต้หัวข้อ', long=True),
        TX('label_name', 'ช่อง: ชื่อ-นามสกุล'), TX('label_company', 'ช่อง: บริษัท / หน่วยงาน'), TX('label_position', 'ช่อง: ตำแหน่ง'),
        TX('label_phone', 'ช่อง: โทรศัพท์'), TX('label_email', 'ช่อง: อีเมล'), TX('label_line', 'ช่อง: LINE ID'),
        TX('label_interest', 'ช่อง: เรื่องที่สนใจ'), TX('label_model', 'ช่อง: รุ่นที่สนใจ'), TX('label_quantity', 'ช่อง: จำนวนรถ'),
        TX('label_message', 'ช่อง: รายละเอียด'), TX('message_placeholder', 'ตัวอย่างข้อความจางๆ ในช่องรายละเอียด', long=True),
        TX('consent', 'ข้อความยินยอม (PDPA)', long=True), TX('submit', 'ปุ่มส่งข้อมูล'),
        LIST('interests', 'ตัวเลือก "เรื่องที่สนใจ" (แสดงในการ์ด Lark ด้วย)', [
            S('value', 'รหัส (ภาษาอังกฤษ ห้ามซ้ำ ห้ามเว้นวรรค)',
              desc='ใช้กับลิงก์ contact.html?topic=รหัส · รหัส buy = ซื้อขาด และ lease = เช่า จะบันทึกวิธีจัดซื้อลง CRM ให้อัตโนมัติ'),
            TX('label', 'ข้อความที่ลูกค้าเห็น'),
            S('lark_icon', 'อีโมจิบนการ์ด Lark (เช่น 📅)'),
            SEL('lark_color', 'สีหัวการ์ด Lark', LARK_COLORS),
        ], summary='{label_th}'),
        TX('model_none', 'ตัวเลือกแรกของ "รุ่นที่สนใจ" (เช่น ยังไม่ระบุ)'),
        LIST('models', 'ตัวเลือก "รุ่นที่สนใจ"', [
            S('value', 'รหัสรุ่น (ใช้ - แทนช่องว่าง เช่น Z5-Plus)', desc='ต้องตรงกับชื่อรุ่นในเมนู ข้อมูลรถแต่ละรุ่น (เว้นวรรคเปลี่ยนเป็น -) ปุ่มขอราคาในหน้ารุ่นรถจึงเลือกรุ่นให้อัตโนมัติ'),
            S('label', 'ชื่อที่ลูกค้าเห็น (เว้นว่าง = ใช้รหัส)'),
        ], summary='{value}'),
    ]),
    ('messages', '4. ข้อความหลังกดส่งแบบฟอร์ม', [
        TX('sending', 'ระหว่างส่ง'),
        TX('ok_title', 'ส่งสำเร็จ: หัวข้อ'), TX('ok_body', 'ส่งสำเร็จ: ข้อความ', long=True),
        TX('fail_title', 'ส่งไม่สำเร็จ: หัวข้อ'),
        TX('fail_body', 'ส่งไม่สำเร็จ: ข้อความ', long=True, desc='{email} และ {phone} จะถูกแทนด้วยอีเมลและเบอร์โทรของบริษัท'),
        TX('off_title', 'เปิดเว็บแบบออฟไลน์: หัวข้อ'), TX('off_body', 'เปิดเว็บแบบออฟไลน์: ข้อความ', long=True),
        TX('copy_message', 'ปุ่มคัดลอกข้อความ'), TX('open_email', 'ปุ่มเปิดอีเมล'), TX('copied', 'ข้อความหลังกดคัดลอก'),
    ]),
]

FIELD_ROWS = [  # id, name, label key, input html, full width, required
    ('f-name', 'label_name', '<input id="f-name" name="name" type="text" autocomplete="name" required>', False, True),
    ('f-company', 'label_company', '<input id="f-company" name="company" type="text" autocomplete="organization" required>', False, True),
    ('f-position', 'label_position', '<input id="f-position" name="position" type="text" autocomplete="organization-title">', False, False),
    ('f-phone', 'label_phone', '<input id="f-phone" name="phone" type="tel" autocomplete="tel" required>', False, True),
    ('f-email', 'label_email', '<input id="f-email" name="email" type="email" autocomplete="email" required>', False, True),
    ('f-line', 'label_line', '<input id="f-line" name="line" type="text">', False, False),
]


def form_options():
    f = C(f'{DIR}/form')
    interests = ''.join(opt(s(o, 'value'), tri(o, 'label')) for o in items(f, 'interests') if s(o, 'value'))
    models = opt('', tri(f, 'model_none'), True)
    for o in items(f, 'models'):
        v = s(o, 'value')
        if v:
            lab = s(o, 'label') or v.replace('-', ' ')
            models += opt(v, (lab, lab, lab))
    return interests, models


def field(fid, lab3, inp, full=False, req=False):
    r = ' <span class="req">*</span>' if req else ''
    return f'<div class="field{" full" if full else ""}"><label for="{fid}">{T(lab3)}{r}</label>{inp}</div>'


def form_card():
    f = C(f'{DIR}/form')
    interests, models = form_options()
    rows = [field(fid, tri(f, key), inp, full, req) for fid, key, inp, full, req in FIELD_ROWS]
    rows += [
        field('f-interest', tri(f, 'label_interest'), f'<select id="f-interest" name="interest">{interests}</select>'),
        field('f-model', tri(f, 'label_model'), f'<select id="f-model" name="model">{models}</select>'),
        field('f-qty', tri(f, 'label_quantity'), '<input id="f-qty" name="quantity" type="number" min="1" inputmode="numeric">'),
        field('f-message', tri(f, 'label_message'), '<textarea id="f-message" name="message"' + ph(tri(f, 'message_placeholder')) + '></textarea>', full=True),
        f'<label class="consent"><input id="f-consent" name="consent" type="checkbox" value="yes" required><span>{Tk(f, "consent")} <span class="req">*</span></span></label>',
        f'<div class="form-actions"><button class="btn btn-primary" type="submit">{Tk(f, "submit")}{ic("arrow")}</button><span class="status-line" id="form-status" aria-live="polite"></span></div>',
    ]
    grid = '\n      '.join(rows)
    return f'''<div class="form-card">
  <h2 class="h3" style="margin-bottom:6px">{Tk(f, 'title')}</h2>
  {Bk('p', f, 'lead', cls='small')}
  <form id="contact-form" name="contact" method="POST" action="/api/lead" data-netlify="true" netlify-honeypot="bot-field" novalidate style="margin-top:18px">
    <input type="hidden" name="form-name" value="contact">
    <p class="hp"><label>Leave empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
    <div class="form-grid">
      {grid}
    </div>
  </form>
  <div class="form-result" id="form-result" hidden aria-live="polite"></div>
</div>'''


def details_block():
    d, co, lb = C(f'{DIR}/details'), C('site/company'), C('site/labels')
    copy_lbl = f'<span class="copy-label">{Tk(lb, "copy")}</span>'

    def copy_btn(value):
        return f'<button class="copy-btn" type="button" data-copy="{esc(value)}">{ic("copy")}{copy_lbl}</button>'
    lis = []
    if s(co, 'phone'):
        lis.append(f'<li>{ic("phone")}<span><span class="label">{Tk(d, "label_phone")}</span><span class="value num">{fmt(s(co, "phone"))}</span></span>{copy_btn(s(co, "phone"))}</li>')
    if s(co, 'email'):
        lis.append(f'<li>{ic("mail")}<span><span class="label">{Tk(d, "label_email")}</span><span class="value">{fmt(s(co, "email"))}</span></span>{copy_btn(s(co, "email"))}</li>')
    if has(co, 'address'):
        lis.append(f'<li>{ic("pin")}<span><span class="label">{Tk(d, "label_address")}</span><span class="value">{Tk(co, "address")}</span></span>{copy_btn(tri(co, "address")[0])}</li>')
    if s(co, 'website'):
        lis.append(f'<li>{ic("globe")}<span><span class="label">{Tk(d, "label_website")}</span><span class="value">{fmt(s(co, "website"))}</span></span></li>')
    for x in items(co, 'socials'):
        if s(x, 'url'):
            lis.append(f'<li>{ic(SOCIAL_ICON.get(s(x, "network"), "link"))}<span><span class="label">{fmt(social_name(x))}</span>'
                       f'<a class="value" href="{href(s(x, "url"))}" target="_blank" rel="noopener">{fmt(s(x, "handle") or s(x, "url"))}</a></span></li>')
    maps = ''
    if s(co, 'maps_url'):
        maps = f'\n  <a class="btn btn-outline" href="{href(s(co, "maps_url"))}" target="_blank" rel="noopener">{ic("map")}{Tk(d, "maps_button")}</a>'
    nxt = ''
    if items(d, 'next_steps'):
        nxt = f'''
  <div style="margin-top:18px">
    <h3 class="h3" style="margin-bottom:12px">{Tk(d, 'next_title')}</h3>
    {steps(items(d, 'next_steps'))}
  </div>'''
    lis_html = '\n    '.join(lis)
    return f'''<div class="stack">
  <span class="eyebrow">{Tk(d, 'eyebrow')}</span>
  <h2 class="h2">{Tk(co, 'company_name')}</h2>
  <ul class="details">
    {lis_html}
  </ul>{maps}{nxt}
</div>'''


MSG_KEYS = [('sending', 'sending'), ('okTitle', 'ok_title'), ('okBody', 'ok_body'), ('offTitle', 'off_title'), ('offBody', 'off_body'),
            ('failTitle', 'fail_title'), ('failBody', 'fail_body'), ('copy', 'copy_message'), ('mail', 'open_email'), ('copied', 'copied')]


def messages_json():
    """Texts the page script (assets/js/main.js) shows after the form is sent."""
    m, co = C(f'{DIR}/messages'), C('site/company')
    out = {}
    for js_key, key in MSG_KEYS:
        if has(m, key):
            out[js_key] = {k: x.replace('{email}', s(co, 'email')).replace('{phone}', s(co, 'phone'))
                           for (k, _lg), x in zip(LANGS, tri(m, key))}
    if s(co, 'email'):
        out['email'] = s(co, 'email')
    text = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    return text.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


BG_KEYS = ('hero',)

def render():
    h = C(f'{DIR}/hero')
    hero = bgv(phero(img(h, lazy=False), 'photo', trail(None, h), h), h)
    body = hero + f'<section class="section"><div class="wrap contact-grid">{details_block()}{form_card()}</div></section>'
    body += f'\n<script type="application/json" id="form-msgs">{messages_json()}</script>'
    return page(FILE, C(f'{DIR}/page'), body)
