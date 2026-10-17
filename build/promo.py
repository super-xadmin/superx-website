# -*- coding: utf-8 -*-
"""Pop-up for new visitors: what we sell, how to start in 3 steps, and the current promotion.

Staff edit it in the back office (📣 ป๊อปอัพ / โปรโมชั่น). Two layers:
  * the main message (picture, title, text, steps, buttons) is always shown while the pop-up is switched on;
  * the 🎁 promotion is optional, has its own start and end dates, and is added as a highlighted box (with its
    own picture and main button if given) only between those dates. After the end date the pop-up goes back
    to the main message by itself, so nothing has to be typed again.
The steps are the ones on the home page (หน้าแรก → 5. ขั้นตอนเริ่มใช้งาน), so they are edited in one place.
Dates are checked in the visitor's browser against the date in Thailand (main.js), so a promotion starts and
ends on time without a new build. Each layer has a key made from its content: change the main message and
everybody sees the pop-up again; start a new promotion and everybody sees it once."""
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone

from core import C, s, items, tri, has, esc, Tk, Bk, aria, img, href, ic
from schema import TX, LINK, NUM, BOOL, DATE, IMG, ALT, SEL, OBJ

REL = 'site/popup'
LABEL = '📣 ป๊อปอัพ / โปรโมชั่น'
HOME = 'index.html'
NEVER = {'contact.html', '404.html'}   # never on the contact form or the error page
STEPS_FROM = 'pages/home/start'
SETTINGS = ('enabled', 'pages', 'delay', 'repeat_days', 'offer')   # not part of the main message's key

FIT = [('cover', 'เต็มกรอบ (เหมาะกับภาพถ่าย ขอบรูปอาจถูกตัดเล็กน้อย)'),
       ('contain', 'แสดงทั้งรูป (เหมาะกับแบนเนอร์ที่มีตัวหนังสือ รูปไม่ถูกตัด)')]

OFFER = [
    BOOL('active', 'แสดงโปรโมชั่น', desc='ไม่ติ๊ก = ซ่อนโปรโมชั่น (ข้อความที่พิมพ์ไว้ยังเก็บไว้ ใช้ครั้งหน้าได้)'),
    DATE('start', 'เริ่มวันที่ (เว้นว่าง = เริ่มทันที)'),
    DATE('end', 'ถึงวันที่ (เว้นว่าง = ไม่มีวันหมด)',
         desc='พ้นวันนี้แล้ว (ตามเวลาประเทศไทย) กล่องโปรโมชั่นจะหายไปเอง ป๊อปอัพกลับเป็นข้อความหลักตามเดิม'),
    TX('label', 'ป้ายเล็ก (เช่น โปรโมชั่น · ถึง 31 ธ.ค.)'),
    TX('title', 'หัวข้อโปรโมชั่น', long=True),
    TX('text', 'รายละเอียด / เงื่อนไข', long=True),
    IMG('image', 'รูปช่วงโปรโมชั่น (เว้นว่าง = ใช้รูปของข้อความหลัก)', desc='แนะนำขนาด 1600×700 px ไม่เกินประมาณ 300 KB'),
    ALT('alt'),
    SEL('image_fit', 'การแสดงรูปโปรโมชั่น', FIT),
    TX('btn_label', 'ปุ่มหลักช่วงโปรโมชั่น (เว้นว่าง = ใช้ปุ่มหลักเดิม)'), LINK('btn_link', 'ลิงก์ปุ่มหลักช่วงโปรโมชั่น'),
]

FIELDS = [
    BOOL('enabled', 'เปิดใช้ป๊อปอัพ', desc='ไม่ติ๊ก = ไม่แสดงป๊อปอัพเลย'),
    SEL('pages', 'แสดงที่หน้า', [('home', 'หน้าแรกเท่านั้น (แนะนำ)'), ('all', 'ทุกหน้า (ยกเว้นหน้าติดต่อเรา)')]),
    NUM('delay', 'แสดงหลังเปิดหน้าเว็บกี่วินาที', desc='แนะนำ 3 วินาที (ให้ลูกค้าเห็นหน้าเว็บก่อน) · 0 = แสดงทันที'),
    NUM('repeat_days', 'ลูกค้าคนเดิมจะเห็นซ้ำอีกครั้งหลังจากกี่วัน',
        desc='แนะนำ 7 วัน · 0 = เห็นทุกครั้งที่เปิดเว็บใหม่ · เมื่อแก้ข้อความหลัก หรือเริ่มโปรโมชั่นใหม่ ลูกค้าทุกคนจะเห็นป๊อปอัพอีกครั้ง'),
    IMG('image', 'รูปด้านบน (แนวนอน ไม่ใส่ก็ได้)', desc='แนะนำขนาด 1600×700 px ไม่เกินประมาณ 300 KB เช่น รูปรถกำลังทำงาน'),
    ALT(),
    SEL('image_fit', 'การแสดงรูป', FIT),
    TX('badge', 'ป้ายเล็กเหนือหัวข้อ'),
    TX('title', 'หัวข้อ (ข้อความหลัก แสดงตลอด)', long=True,
       desc='บอกให้ชัดว่าเราขายอะไร ให้ใคร · ใช้ **คำ** เพื่อทำเป็นสีฟ้า · ถ้าจะลงโปรโมชั่น ใช้กลุ่ม 🎁 โปรโมชั่น ด้านล่าง ไม่ต้องแก้ตรงนี้'),
    TX('text', 'รายละเอียด', long=True),
    BOOL('show_steps', 'แสดงขั้นตอนเริ่มใช้งาน 1-2-3',
         desc='ขั้นตอนดึงมาจาก 📄 หน้าเว็บ → หน้าแรก → 5. ขั้นตอนเริ่มใช้งาน (แก้ที่นั่นที่เดียว เปลี่ยนทั้งหน้าแรกและป๊อปอัพ)'),
    TX('steps_title', 'หัวข้อเหนือขั้นตอน', desc='ถ้าเพิ่มหรือลดจำนวนขั้นตอน อย่าลืมแก้ตัวเลขในหัวข้อนี้'),
    TX('btn1_label', 'ปุ่มหลัก'), LINK('btn1_link', 'ลิงก์ปุ่มหลัก'),
    TX('btn2_label', 'ปุ่มรอง (เว้นว่าง = ไม่มีปุ่มนี้)'), LINK('btn2_link', 'ลิงก์ปุ่มรอง'),
    TX('note', 'หมายเหตุตัวเล็กใต้ปุ่ม', long=True),
    OBJ('offer', '🎁 โปรโมชั่น (ไม่ใส่ก็ได้)', OFFER,
        desc='ใส่เมื่อมีโปรโมชั่น: จะขึ้นเป็นกล่องเด่นในป๊อปอัพ เฉพาะช่วงวันที่ที่ตั้งไว้ ข้อความหลักด้านบนยังอยู่ครบ'),
    TX('close', 'คำอ่านปุ่มปิด (สำหรับโปรแกรมอ่านหน้าจอ)'),
]


def _date(v):
    m = re.match(r'^\s*(\d{4}-\d{2}-\d{2})', str(v or ''))
    return m.group(1) if m else ''


def _num(v, default, low, high):
    if v in (None, '') or isinstance(v, bool):
        return default
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(f):
        return default
    f = min(max(f, low), high)
    return int(f) if f == int(f) else round(f, 2)


def _today():
    """Today in Thailand (the build runs on a server in another time zone)."""
    return datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d')


def _key(*parts):
    raw = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()[:10]


def steps():
    """The home page steps (title and text), used by the pop-up."""
    return [r for r in items(C(STEPS_FROM), 'steps') if has(r, 'title')]


def _button(d, label, link, cls, icon='', when=''):
    from layout import link_shown
    url = s(d, link)
    if not (has(d, label) and url and link_shown(url)):
        return ''
    w = f' data-when="{when}"' + (' hidden' if when == 'offer' else '') if when else ''
    return f'<a class="btn {cls}" href="{href(url)}"{w}>{Tk(d, label)}{icon}</a>'


def _media(d, when=''):
    pic = img(d)
    if not pic:
        return ''
    fit = 'contain' if s(d, 'image_fit') == 'contain' else 'cover'
    w = f' data-when="{when}"' + (' hidden' if when == 'offer' else '') if when else ''
    return f'\n    <div class="promo-media fit-{fit}"{w}>{pic}</div>'


def live_offer(d):
    """The promotion block when it is switched on, has something to show and has not ended yet; else {}."""
    off = d.get('offer') if isinstance(d.get('offer'), dict) else {}
    if not off.get('active') or not (has(off, 'title') or has(off, 'text') or s(off, 'image')):
        return {}
    end = _date(s(off, 'end'))
    if end and end < _today():
        return {}                      # promotion over: leave it out of the page
    return off


def render(fname):
    """The pop-up for one page, or '' when it is switched off or not meant for this page."""
    d = C(REL)
    if not d.get('enabled'):
        return ''
    if fname in NEVER or (s(d, 'pages') != 'all' and fname != HOME):
        return ''
    off = live_offer(d)
    rows = steps() if d.get('show_steps') else []
    if not (has(d, 'title') or has(d, 'text') or s(d, 'image') or rows or off):
        return ''

    # picture: the promotion's own picture replaces the main one while the promotion runs
    off_media = _media(off, 'offer') if off else ''
    media = _media(d, 'base' if off_media else '') + off_media
    badge = f'<span class="promo-badge">{Tk(d, "badge")}</span>' if has(d, 'badge') else ''
    title = f'<h2 class="promo-title" id="promo-title">{Tk(d, "title")}</h2>' if has(d, 'title') else ''
    text = Bk('p', d, 'text', cls='promo-text') if has(d, 'text') else ''
    box = ''
    if off:
        lab = f'<span class="promo-offer-label">{ic("gift")}{Tk(off, "label")}</span>' if has(off, 'label') else ''
        ttl = f'<b class="promo-offer-title">{Tk(off, "title")}</b>' if has(off, 'title') else ''
        txt = Bk('p', off, 'text', cls='promo-offer-text') if has(off, 'text') else ''
        if lab or ttl or txt:
            box = f'<div class="promo-offer" data-when="offer" hidden>{lab}{ttl}{txt}</div>'
    # main button: the promotion's own button replaces it while the promotion runs
    off_btn = _button(off, 'btn_label', 'btn_link', 'btn-primary', when='offer') if off else ''
    btns = (_button(d, 'btn1_label', 'btn1_link', 'btn-primary', when='base' if off_btn else '') + off_btn
            + _button(d, 'btn2_label', 'btn2_link', 'btn-outline', ic('arrow')))
    btn_row = f'<div class="btn-row promo-btns">{btns}</div>' if btns else ''
    note = Bk('p', d, 'note', cls='promo-note') if has(d, 'note') else ''
    side = ''
    if rows:
        lis = ''.join(f'<li><span class="pin">{n}</span><div><b>{Tk(r, "title")}</b>{Bk("p", r, "text", cls="ps-text")}</div></li>'
                      for n, r in enumerate(rows, 1))
        st = f'<h3 class="promo-steps-title">{Tk(d, "steps_title")}</h3>' if has(d, 'steps_title') else ''
        side = f'''
      <div class="promo-side">{st}<ol class="promo-steps">{lis}</ol></div>'''
    foot = f'''
      <div class="promo-foot">{btn_row}{note}</div>''' if (btn_row or note) else ''
    close3 = tri(d, 'close') if has(d, 'close') else ('ปิด', '关闭', 'Close')

    inner = f'''
  <button class="promo-x" type="button" data-promo-close{aria(close3)}>{ic('close')}</button>
  <div class="promo-card">{media}
    <div class="promo-body">
      <div class="promo-head">{badge}{title}{text}{box}</div>{side}{foot}
    </div>
  </div>
'''
    repeat = _num(d.get('repeat_days'), 7, 0, 365)
    delay = _num(d.get('delay'), 3, 0, 120)
    main = {k: v for k, v in d.items() if k not in SETTINGS}
    key = _key(main, rows)
    cls = 'promo' + (' has-img' if s(d, 'image') else '') + (' has-steps' if rows else '')
    if title:
        label = ' aria-labelledby="promo-title"'
    elif badge:
        label = aria(tri(d, 'badge'))
    else:
        label = aria(tri(off, 'title') if has(off, 'title') else ('โปรโมชั่น', '促销', 'Promotion'))
    extra = ''
    if off:
        extra = (f' data-offer-key="{_key(off)}" data-offer-start="{esc(_date(s(off, "start")))}"'
                 f' data-offer-end="{esc(_date(s(off, "end")))}"')
    return (f'\n<dialog class="{cls}" id="promo" tabindex="-1"{label} data-key="{key}" data-delay="{delay}" '
            f'data-repeat="{repeat}"{extra}>{inner}</dialog>')
