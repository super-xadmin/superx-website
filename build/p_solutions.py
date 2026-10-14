# -*- coding: utf-8 -*-
"""Solution pages: education.html, security.html, ai-agent.html."""
from core import C, s, items, tri, has, esc, fmt, T, TC, Tk, Bk, img, href, ic
from schema import TX, S, LINK, IMG, ALT, ICON, LIST, CHAT, FEATURE, STEP, BULLET
from layout import (PAGE_FIELDS_CTA, PHERO, page, phero, trail, cta_band, head, features, checks, steps, chips, chat_art, bgv)

BUTTON = [TX('button_label', 'ปุ่ม'), LINK('button_link', 'ลิงก์ปุ่ม')]
CHIP_LINK = [S('anchor', 'ไปที่หัวข้อ (#)'), ICON(), TX('label', 'ข้อความ')]
CHIP = [ICON(), TX('label', 'ข้อความ')]


def section(cls, inner, sid=''):
    i = f' id="{sid}"' if sid else ''
    return f'''<section class="{cls}"{i}>
  <div class="wrap">
    {inner}
  </div>
</section>'''


def btn(d, cls='btn btn-primary'):
    return f'<div class="btn-row"><a class="{cls}" href="{href(s(d, "button_link"))}">{Tk(d, "button_label")}</a></div>'


# ================================================================ EDUCATION
class Education:
    FILE, DIR, LABEL = 'education.html', 'pages/education', 'รถไร้คนขับเพื่อการศึกษา'
    BG_KEYS = ('hero', 'audience', 'topics', 'offer', 'process')
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
        ('hero', '1. ภาพหลักและหัวข้อ', PHERO(BUTTON)),
        ('audience', '2. เหมาะกับใคร', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('items', 'กลุ่มผู้ใช้', FEATURE)]),
        ('topics', '3. หัวข้อการเรียนรู้', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
                                            LIST('items', 'หัวข้อ', FEATURE)]),
        ('offer', '4. สิ่งที่ SuperX AI ส่งมอบ', [
            TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('checks', 'รายการเครื่องหมายถูก', BULLET)] + BUTTON + [
            IMG(), ALT(), TX('caption', 'คำบรรยายใต้รูป', long=True), TX('caption_link_label', 'ข้อความลิงก์ใต้รูป'), LINK('caption_link', 'ลิงก์ใต้รูป')]),
        ('process', '5. ขั้นตอน', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('steps', 'ขั้นตอน', STEP)]),
    ]

    def render(self):
        D = self.DIR
        h = C(f'{D}/hero')
        hero = phero(img(h, lazy=False), 'photo', trail('products', h), h, btn(h))
        au, tp, of, pr = (C(f'{D}/{k}') for k in ('audience', 'topics', 'offer', 'process'))
        who = section('section', f'{head(au)}\n    {features(items(au, "items"), "f4")}')
        topics = section('section section--mist', f'{head(tp)}\n    {features(items(tp, "items"))}')
        offer = f'''<section class="section">
  <div class="wrap split">
    <div class="stack">
      <span class="eyebrow">{Tk(of, 'eyebrow')}</span>
      <h2 class="h2">{Tk(of, 'title')}</h2>
      {checks(items(of, 'checks'))}
      {btn(of)}
    </div>
    <figure class="video-card">{img(of, cls='rounded-img ratio-4-3')}
      <figcaption>{Tk(of, 'caption')}
        <a class="link-arrow" href="{href(s(of, 'caption_link'))}">{Tk(of, 'caption_link_label')}{ic('arrow')}</a></figcaption></figure>
  </div>
</section>'''
        process = section('section section--mist', f'{head(pr)}\n    {steps(items(pr, "steps"))}')
        pg = C(f'{D}/page')
        return page(self.FILE, pg, bgv(hero, h) + bgv(who, au) + bgv(topics, tp) + bgv(offer, of) + bgv(process, pr) + cta_band(pg))


# ================================================================ SECURITY
ROBOT_SVG = '''<svg viewBox="0 0 520 300" role="img" aria-label="Tracked unmanned ground vehicle with camera mast">
  <defs><linearGradient id="aurfill" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#25326C"/><stop offset=".55" stop-color="#4FC8E9"/><stop offset="1" stop-color="#8EC96D"/></linearGradient></defs>
  <path class="r-beam" d="M318 70 L500 18 L500 128 Z"/>
  <path class="r-line" d="M20 262 H500"/>
  <rect class="r-track" x="70" y="196" width="330" height="62" rx="31"/>
  <circle class="r-wheel" cx="102" cy="227" r="22"/><circle class="r-wheel" cx="170" cy="232" r="15"/><circle class="r-wheel" cx="235" cy="232" r="15"/><circle class="r-wheel" cx="300" cy="232" r="15"/><circle class="r-wheel" cx="368" cy="227" r="22"/>
  <path class="r-body" d="M92 196 V150 Q92 132 110 132 H352 Q378 132 386 150 L396 196 Z"/>
  <rect class="r-accent" x="110" y="176" width="150" height="6" rx="3"/>
  <rect class="r-dark" x="300" y="148" width="66" height="22" rx="6"/>
  <rect class="r-body" x="270" y="104" width="16" height="30" rx="4"/>
  <rect class="r-body" x="244" y="74" width="80" height="34" rx="10"/>
  <circle class="r-dark" cx="306" cy="91" r="9"/><circle cx="306" cy="91" r="3.5" fill="#4FC8E9"/>
  <rect class="r-dark" x="252" y="84" width="30" height="14" rx="4"/>
  <path class="r-body" d="M130 132 V112 M130 112 h18" />
  <circle class="r-dark" cx="150" cy="112" r="5"/>
</svg>'''


class Security:
    FILE, DIR, LABEL = 'security.html', 'pages/security', 'หุ่นยนต์ความปลอดภัยและงานพิเศษ'
    BG_KEYS = ('hero', 'tracked', 'special', 'why')
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
        ('hero', '1. ภาพหลักและหัวข้อ', PHERO([LIST('chips', 'ปุ่มลัดไปยังหัวข้อ', CHIP_LINK)])),
        ('tracked', '2. รถตีนตะขาบไร้คนขับ', [
            IMG('image', 'รูปประกอบ (เว้นว่าง = ใช้ภาพวาดรถตีนตะขาบ)'), ALT(),
            TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
            LIST('checks', 'รายการเครื่องหมายถูก', BULLET), TX('note', 'หมายเหตุ', long=True)] + BUTTON),
        ('special', '3. ยานยนต์งานพิเศษ', [
            TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
            LIST('units', 'รุ่น / งาน', [IMG(), ALT(), TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย', long=True)]),
            TX('unit_link_label', 'ข้อความลิงก์ใต้การ์ด'), LINK('unit_link', 'ลิงก์ใต้การ์ด')]),
        ('why', '4. ทำไมต้องหุ่นยนต์', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('items', 'เหตุผล', FEATURE)]),
    ]

    def render(self):
        D = self.DIR
        h = C(f'{D}/hero')
        hero = phero(img(h, lazy=False), 'photo', trail('products', h), h, '<div class="chips">' + ''.join(chips(items(h, 'chips'))) + '</div>')
        tr, sp, wy = (C(f'{D}/{k}') for k in ('tracked', 'special', 'why'))
        art = img(tr) if s(tr, 'image') else ROBOT_SVG
        tracked = f'''<section class="section" id="tracked">
  <div class="wrap split">
    <div class="robot-art">{art}</div>
    <div class="stack">
      <span class="eyebrow">{Tk(tr, 'eyebrow')}</span>
      <h2 class="h2">{Tk(tr, 'title')}</h2>
      {Bk('p', tr, 'lead', cls='lead')}
      {checks(items(tr, 'checks'))}
      {Bk('p', tr, 'note', cls='note')}
      {btn(tr)}
    </div>
  </div>
</section>'''

        def unit(u):
            return f'''<article class="case">{img(u)}<h3>{Tk(u, 'title')}</h3>{Bk('p', u, 'text')}
  <a class="link-arrow" href="{href(s(sp, 'unit_link'))}">{Tk(sp, 'unit_link_label')}{ic('arrow')}</a></article>'''
        units = '\n      '.join(unit(u) for u in items(sp, 'units'))
        special = f'''<section class="section section--mist" id="special">
  <div class="wrap">
    {head(sp)}
    <div class="grid-2">
      {units}
    </div>
  </div>
</section>'''
        why = section('section section--night', f'{head(wy)}\n    {features(items(wy, "items"), "f4")}')
        pg = C(f'{D}/page')
        return page(self.FILE, pg, bgv(hero, h) + bgv(tracked, tr) + bgv(special, sp) + bgv(why, wy) + cta_band(pg))


# ================================================================ AI AGENT
class AiAgent:
    FILE, DIR, LABEL = 'ai-agent.html', 'pages/ai-agent', 'AI Agent'
    BG_KEYS = ('hero', 'channels', 'capabilities', 'getting_started', 'industries')
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
        ('hero', '1. ภาพแชตและหัวข้อ', [CHAT('chat', 'ข้อความแชตตัวอย่าง (แทนรูปภาพ)'), TX('crumb', 'ชื่อหน้าในแถบเส้นทาง'),
                                        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อใหญ่', long=True), TX('lead', 'คำอธิบาย', long=True)] + BUTTON),
        ('channels', '2. ช่องทางที่เชื่อมต่อ', [TX('label', 'ข้อความนำ'), LIST('chips', 'ช่องทาง', CHIP)]),
        ('capabilities', '3. ทำอะไรได้บ้าง', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('items', 'ความสามารถ', FEATURE)]),
        ('getting_started', '4. ขั้นตอนเริ่มใช้งาน', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), LIST('steps', 'ขั้นตอน', STEP)]),
        ('industries', '5. เหมาะกับธุรกิจ', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
                                             LIST('chips', 'ประเภทธุรกิจ', CHIP)]),
    ]

    def render(self):
        D = self.DIR
        h = C(f'{D}/hero')
        rows = items(h, 'chat')
        ai_name = next((tri(r, 'who') for r in rows if s(r, 'side') != 'me' and any(tri(r, 'who'))), ('AI Agent',) * 3)
        art = f'''<div class="chat-phone"><div class="chat-phone-screen">
      <div class="chat-phone-top"><span class="chat-avatar">AI</span><span class="chat-title"><b>{TC(ai_name)}</b><small>{TC(('ออนไลน์', '在线', 'Online'))}</small></span></div>
      {chat_art(rows)}
      <div class="chat-phone-input"><span>{TC(('พิมพ์ข้อความ…', '输入消息…', 'Type a message…'))}</span>{ic('arrow')}</div>
    </div></div>'''
        hero = phero(art, 'chat', trail('products', h), h, btn(h))
        ch, ca, gs, ind = (C(f'{D}/{k}') for k in ('channels', 'capabilities', 'getting_started', 'industries'))
        channels = f'''<section class="section-tight">
  <div class="wrap">
    <div class="more-models" style="margin-top:0"><span>{Tk(ch, 'label')}</span>
      <div class="chips">{''.join(chips(items(ch, 'chips'), link=False))}</div></div>
  </div>
</section>'''
        what = section('section section--mist', f'{head(ca)}\n    {features(items(ca, "items"))}')
        how = section('section', f'{head(gs)}\n    {steps(items(gs, "steps"), "s4")}')
        cs = chips(items(ind, 'chips'), link=False)
        pairs = '\n      '.join(''.join(cs[i:i + 2]) for i in range(0, len(cs), 2))
        fit = f'''<section class="section section--mist">
  <div class="wrap split">
    <div class="stack"><span class="eyebrow">{Tk(ind, 'eyebrow')}</span>
      <h2 class="h2">{Tk(ind, 'title')}</h2>
      {Bk('p', ind, 'lead', cls='lead')}
    </div>
    <div class="chips">{pairs}</div>
  </div>
</section>'''
        pg = C(f'{D}/page')
        return page(self.FILE, pg, bgv(hero, h) + bgv(channels, ch) + bgv(what, ca) + bgv(how, gs) + bgv(fit, ind) + cta_band(pg))


MODULES = [Education(), Security(), AiAgent()]
