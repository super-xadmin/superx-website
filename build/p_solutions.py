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
        hero = phero(img(h, lazy=False), 'photo', trail('solutions', h), h, btn(h))
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
class Security:
    FILE, DIR, LABEL = 'security.html', 'pages/security', 'หุ่นยนต์ความปลอดภัยและงานพิเศษ'
    BG_KEYS = ('hero', 'tracked', 'special', 'why')
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
        ('hero', '1. ภาพหลักและหัวข้อ', PHERO([LIST('chips', 'ปุ่มลัดไปยังหัวข้อ', CHIP_LINK)])),
        # file name stays "tracked" so the back office keeps its history; the section is now the featured unit
        ('tracked', '2. รุ่นเด่น (รูปซ้าย ข้อความขวา)', [
            IMG('image', 'รูปหลัก (เว้นว่าง = แสดงเฉพาะข้อความ)'), ALT(),
            LIST('gallery', 'รูปเล็กใต้รูปหลัก (เว้นว่างได้)', [IMG(), ALT()], summary='{alt}'),
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
        hero = phero(img(h, lazy=False), 'photo', trail('solutions', h), h, '<div class="chips">' + ''.join(chips(items(h, 'chips'))) + '</div>')
        tr, sp, wy = (C(f'{D}/{k}') for k in ('tracked', 'special', 'why'))
        art = ''
        if s(tr, 'image'):
            thumbs = ''.join(img(g) for g in items(tr, 'gallery') if s(g, 'image'))
            thumbs = f'<div class="feature-thumbs">{thumbs}</div>' if thumbs else ''
            art = f'<div class="feature-media">{img(tr)}{thumbs}</div>'
        copy = f'''<div class="stack">
      <span class="eyebrow">{Tk(tr, 'eyebrow')}</span>
      <h2 class="h2">{Tk(tr, 'title')}</h2>
      {Bk('p', tr, 'lead', cls='lead')}
      {checks(items(tr, 'checks'))}
      {Bk('p', tr, 'note', cls='note')}
      {btn(tr)}
    </div>'''
        inner = f'<div class="wrap split">\n    {art}\n    {copy}\n  </div>' if art else f'<div class="wrap" style="max-width:56rem">\n    {copy}\n  </div>'
        featured = f'''<section class="section" id="featured">
  {inner}
</section>'''

        def unit(u):
            return f'''<article class="case">{img(u)}<h3>{Tk(u, 'title')}</h3>{Bk('p', u, 'text')}
  <a class="link-arrow" href="{href(s(sp, 'unit_link'))}">{Tk(sp, 'unit_link_label')}{ic('arrow')}</a></article>'''
        unit_list = items(sp, 'units')
        units = '\n      '.join(unit(u) for u in unit_list)
        grid = 'grid-3' if len(unit_list) == 3 else 'grid-2'
        special = f'''<section class="section section--mist" id="special">
  <div class="wrap">
    {head(sp)}
    <div class="{grid}">
      {units}
    </div>
  </div>
</section>'''
        why = section('section section--night', f'{head(wy)}\n    {features(items(wy, "items"), "f4")}')
        pg = C(f'{D}/page')
        return page(self.FILE, pg, bgv(hero, h) + bgv(featured, tr) + bgv(special, sp) + bgv(why, wy) + cta_band(pg))


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
        hero = phero(art, 'chat', trail('solutions', h), h, btn(h))
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
