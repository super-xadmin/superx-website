# -*- coding: utf-8 -*-
"""Live chat box (💬 bottom right of every page). Visitors write here; the sales team answers in Lark.

The texts and office hours are edited in the back office (💬 แชทบนเว็บ). The chat itself runs in chat.js on
Cloudflare; it needs the Lark bot set up first (README 8.1), so the box stays hidden until "เปิดใช้แชท" is ticked."""
import json

from core import C, s, tri, has, esc, T, Tk, Bk, aria, ph, ic, LANGS
from schema import TX, NUM, BOOL

REL = 'site/chat'
LABEL = '💬 แชทบนเว็บ (ตอบผ่าน Lark)'
NEVER = {'404.html'}

FIELDS = [
    BOOL('enabled', 'เปิดใช้แชทบนเว็บ', desc='ติ๊กหลังจากตั้งค่าบอท Lark เสร็จแล้วเท่านั้น (ดู README ข้อ 8.1) ไม่อย่างนั้นลูกค้าจะส่งข้อความไม่ได้'),
    TX('button', 'ข้อความบนปุ่มแชท'),
    TX('title', 'หัวข้อกล่องแชท'),
    TX('intro', 'ข้อความต้อนรับ', long=True),
    TX('online', 'สถานะในเวลาทำการ (เช่น ทีมงานพร้อมตอบ)'),
    TX('offline', 'สถานะนอกเวลาทำการ', desc='เช่น นอกเวลาทำการ ทิ้งข้อความไว้ได้ เราจะติดต่อกลับ'),
    TX('hours', 'เวลาทำการ (ข้อความที่ลูกค้าเห็น เช่น จ.–ศ. 9:00–18:00 น.)'),
    NUM('open_from', 'เวลาเริ่มตอบ (ชั่วโมง 0–23 เช่น 9)', desc='ใช้คำนวณว่าตอนนี้อยู่ในเวลาทำการหรือไม่ (เวลาประเทศไทย)'),
    NUM('open_until', 'เวลาเลิกตอบ (ชั่วโมง 1–24 เช่น 18)'),
    BOOL('saturday', 'ตอบวันเสาร์ด้วย'),
    BOOL('sunday', 'ตอบวันอาทิตย์ด้วย'),
    TX('name_label', 'ช่องชื่อ'),
    TX('phone_label', 'ช่องเบอร์โทร'),
    TX('message_label', 'ช่องข้อความแรก'),
    TX('consent', 'ข้อความยินยอม PDPA (ช่องติ๊ก)', long=True),
    TX('start', 'ปุ่มเริ่มแชท'),
    TX('placeholder', 'ข้อความจางในช่องพิมพ์'),
    TX('send', 'ปุ่มส่ง (คำอ่านสำหรับโปรแกรมอ่านหน้าจอ)'),
    TX('sent', 'ข้อความหลังเริ่มแชท', long=True),
    TX('staff', 'ชื่อที่แสดงตอนทีมงานตอบ'),
    TX('me', 'ชื่อที่แสดงข้อความของลูกค้า (เช่น คุณ)'),
    TX('error', 'ข้อความเมื่อส่งไม่สำเร็จ', long=True),
    TX('too_many', 'ข้อความเมื่อส่งถี่เกินไป'),
    TX('new_chat', 'ปุ่มเริ่มแชทใหม่'),
    TX('close', 'คำอ่านปุ่มปิด (สำหรับโปรแกรมอ่านหน้าจอ)'),
]

_FALLBACK = {'close': ('ปิด', '关闭', 'Close'), 'send': ('ส่ง', '发送', 'Send')}


def _t3(d, k):
    return tri(d, k) if has(d, k) else _FALLBACK.get(k, ('', '', ''))


def _hour(v, default):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    return min(max(f, 0), 24) if f == f else default


def render(fname):
    """The chat box for one page, or '' when switched off."""
    d = C(REL)
    if not d.get('enabled') or fname in NEVER:
        return ''
    texts = {k: dict(zip([c for c, _ in LANGS], _t3(d, k))) for k in ('sent', 'error', 'too_many', 'staff', 'me', 'offline', 'online')}
    hours = {'from': _hour(d.get('open_from'), 9), 'until': _hour(d.get('open_until'), 18),
             'sat': bool(d.get('saturday')), 'sun': bool(d.get('sunday'))}
    data = json.dumps({'t': texts, 'hours': hours}, ensure_ascii=False).replace('<', '\\u003c')
    hours_note = f'<p class="chat-hours">{ic("clock")}{Tk(d, "hours")}</p>' if has(d, 'hours') else ''
    return f'''
<div class="chat" id="chat">
  <button class="chat-fab" type="button" aria-expanded="false" aria-controls="chat-panel">{ic('chat')}<span class="chat-fab-label">{Tk(d, 'button')}</span><span class="chat-unread" hidden></span></button>
  <section class="chat-panel" id="chat-panel" aria-labelledby="chat-title" hidden>
    <header class="chat-head">
      <div class="chat-who"><b id="chat-title">{Tk(d, 'title')}</b><span class="chat-status"><i aria-hidden="true"></i><span class="chat-online">{Tk(d, 'online')}</span><span class="chat-offline" hidden>{Tk(d, 'offline')}</span></span></div>
      <button class="chat-x" type="button"{aria(_t3(d, 'close'))}>{ic('close')}</button>
    </header>
    <div class="chat-log" aria-live="polite">
      <div class="chat-msg staff chat-intro">{Bk('p', d, 'intro')}</div>
    </div>
    <form class="chat-start" novalidate>
      <label><span>{Tk(d, 'name_label')}</span><input name="name" autocomplete="name" maxlength="80" required></label>
      <label><span>{Tk(d, 'phone_label')}</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="30" required></label>
      <label><span>{Tk(d, 'message_label')}</span><textarea name="text" rows="2" maxlength="1000" required></textarea></label>
      <label class="chat-consent"><input type="checkbox" name="consent" required><span>{Tk(d, 'consent')}</span></label>
      <label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
      <button class="btn btn-primary" type="submit">{Tk(d, 'start')}</button>
      {hours_note}
      <p class="chat-error" role="alert" hidden></p>
    </form>
    <form class="chat-form" hidden>
      <textarea name="text" rows="1" maxlength="1000"{ph(tri(d, 'placeholder'))}{aria(tri(d, 'placeholder'))}></textarea>
      <button class="chat-send" type="submit"{aria(_t3(d, 'send'))}>{ic('arrow')}</button>
    </form>
    <p class="chat-error chat-error2" role="alert" hidden></p>
    <button class="chat-new" type="button" hidden>{Tk(d, 'new_chat')}</button>
  </section>
  <script type="application/json" id="chat-data">{data}</script>
</div>'''
