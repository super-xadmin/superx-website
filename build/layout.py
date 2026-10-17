# -*- coding: utf-8 -*-
"""Site-wide parts: header, footer, page shell, and building blocks used by several pages."""
import re

from core import (C, collection, s, items, tri, has, esc, fmt, T, TC, B, Tk, Bk, aria, media, img, href, is_external,
                  file_size, ic, sprite)
from schema import (TX, S, LINK, NUM, BOOL, IMG, ALT, DOC, SEL, ICON, LIST, SLIST, OBJ, IMGS, FILE3D, BG)
from core import strs

# ================================================================ back-office definitions (site-wide files)
NETWORKS = [('tiktok', 'TikTok'), ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('line', 'LINE'),
            ('linkedin', 'LinkedIn'), ('youtube', 'YouTube'), ('x', 'X (Twitter)'), ('other', 'อื่นๆ')]

SITE_FILES = [
    ('site/company', 'ข้อมูลบริษัทและช่องทางติดต่อ', [
        TX('company_name', 'ชื่อบริษัท'),
        S('site_name', 'ชื่อเว็บไซต์ (ใช้ตอนแชร์ลิงก์)'),
        S('tagline', 'สโลแกน (ใต้โลโก้ด้านล่างเว็บ)'),
        TX('footer_about', 'คำแนะนำบริษัท (ด้านล่างเว็บ)', long=True),
        S('phone', 'เบอร์โทรศัพท์'),
        S('email', 'อีเมล'),
        S('website', 'ชื่อเว็บไซต์ที่แสดง'),
        TX('address', 'ที่อยู่', long=True),
        S('maps_url', 'ลิงก์ Google Maps'),
        LIST('socials', 'โซเชียลมีเดีย', [
            SEL('network', 'ช่องทาง', NETWORKS), S('handle', 'ชื่อบัญชี (เช่น @superxai_official)'), S('url', 'ลิงก์'),
        ], summary='{network} {handle}'),
        IMG('logo', 'โลโก้ (พื้นขาว)'),
        IMG('logo_white', 'โลโก้สีขาว (ใช้บนภาพหรือวิดีโอ เช่น เมนูด้านบนของหน้าแรก)'),
        IMG('favicon', 'ไอคอนแท็บเบราว์เซอร์'),
        IMG('apple_icon', 'ไอคอนเมื่อบันทึกลงหน้าจอมือถือ'),
        IMG('share_image', 'รูปตอนแชร์ลิงก์ (LINE / Facebook)'),
        S('copyright_year', 'ปีลิขสิทธิ์'),
        S('copyright_name', 'ชื่อเจ้าของลิขสิทธิ์'),
        TX('rights', 'ข้อความสงวนลิขสิทธิ์'),
        TX('footer_note', 'หมายเหตุท้ายเว็บ'),
    ]),
    ('site/menu', 'เมนูด้านบนและด้านล่างเว็บ', [
        TX('nav_home', 'เมนู: หน้าแรก'),
        TX('nav_products', 'เมนูกลุ่มที่ 1: ธุรกิจหลัก (RoboVan)'),
        TX('nav_solutions', 'เมนูกลุ่มที่ 2: โซลูชันอื่น'),
        TX('nav_about', 'เมนูกลุ่มที่ 3: เกี่ยวกับ'),
        TX('nav_contact', 'เมนู: ติดต่อเรา'),
        TX('nav_demo', 'ปุ่มมุมขวาบน'),
        LINK('nav_demo_link', 'ลิงก์ปุ่มมุมขวาบน'),
        LIST('products_menu', 'รายการในเมนูกลุ่มที่ 1 (RoboVan)', [
            LINK(), TX('title', 'ชื่อ'), TX('hint', 'คำอธิบายสั้น'), BOOL('divider_before', 'มีเส้นคั่นก่อนรายการนี้'),
        ]),
        LIST('solutions_menu', 'รายการในเมนูกลุ่มที่ 2 (โซลูชันอื่น)', [
            LINK(), TX('title', 'ชื่อ'), TX('hint', 'คำอธิบายสั้น'), BOOL('divider_before', 'มีเส้นคั่นก่อนรายการนี้'),
        ], desc='ลบทุกรายการ = ไม่แสดงเมนูนี้'),
        LIST('about_menu', 'รายการในเมนูกลุ่มที่ 3 (เกี่ยวกับ)', [
            LINK(), TX('title', 'ชื่อ'), TX('hint', 'คำอธิบายสั้น'), BOOL('divider_before', 'มีเส้นคั่นก่อนรายการนี้'),
        ]),
        TX('footer_products_title', 'หัวคอลัมน์ที่ 1 ด้านล่างเว็บ (RoboVan)'),
        LIST('footer_products', 'ลิงก์คอลัมน์ที่ 1', [LINK(), TX('label', 'ข้อความ')]),
        TX('footer_solutions_title', 'หัวคอลัมน์ที่ 2 ด้านล่างเว็บ (โซลูชันอื่น)'),
        LIST('footer_solutions', 'ลิงก์คอลัมน์ที่ 2 (ลบทุกรายการ = ไม่แสดงคอลัมน์นี้)', [LINK(), TX('label', 'ข้อความ')]),
        TX('footer_company_title', 'หัวคอลัมน์บริษัท (ด้านล่างเว็บ)'),
        LIST('footer_company', 'ลิงก์คอลัมน์บริษัท', [LINK(), TX('label', 'ข้อความ')]),
        TX('footer_contact_title', 'หัวคอลัมน์ติดต่อ (ด้านล่างเว็บ)'),
        TX('home_aria', 'คำอ่านโลโก้ (สำหรับโปรแกรมอ่านหน้าจอ)'),
        TX('menu_aria', 'คำอ่านเมนูหลัก'),
        TX('open_menu_aria', 'คำอ่านปุ่มเปิดเมนูบนมือถือ'),
        TX('lang_aria', 'คำอ่านปุ่มเลือกภาษา'),
        TX('skip', 'ลิงก์ข้ามไปยังเนื้อหา (สำหรับคีย์บอร์ด)'),
    ]),
    ('site/labels', 'ข้อความปุ่มและป้ายที่ใช้หลายหน้า', [
        TX('crumb_home', 'แถบเส้นทาง: หน้าแรก'),
        TX('crumb_products', 'แถบเส้นทาง: หน้ารวม RoboVan ทุกรุ่น'),
        TX('crumb_solutions', 'แถบเส้นทาง: โซลูชันอื่น'),
        TX('crumb_about', 'แถบเส้นทาง: เกี่ยวกับ'),
        TX('crumb_aria', 'คำอ่านแถบเส้นทาง'),
        TX('cta_title', 'แถบปิดท้ายหน้า: หัวข้อมาตรฐาน', long=True),
        TX('cta_lead', 'แถบปิดท้ายหน้า: คำอธิบายมาตรฐาน', long=True),
        TX('cta_demo', 'แถบปิดท้ายหน้า: ปุ่มนัดสาธิต'),
        TX('cta_quote', 'แถบปิดท้ายหน้า: ปุ่มขอใบเสนอราคา'),
        LINK('cta_quote_link', 'แถบปิดท้ายหน้า: ลิงก์ปุ่มขอใบเสนอราคา'),
        TX('card_details', 'การ์ดรถ: ปุ่มดูรายละเอียด'),
        TX('card_pdf', 'การ์ดรถ: ปุ่มสเปก PDF'),
        TX('card_quote', 'การ์ดรถ: ปุ่มขอใบเสนอราคา'),
        TX('model_quote', 'หน้ารุ่นรถ: ปุ่มขอใบเสนอราคา'),
        TX('model_demo', 'หน้ารุ่นรถ: ปุ่มนัดหมายสาธิต'),
        LIST('model_nav', 'หน้ารุ่นรถ: เมนูย่อยใต้ภาพหลัก', [
            SEL('section', 'ไปที่หัวข้อ', [('media', 'ภาพและวิดีโอ'), ('overview', 'ตำแหน่งผลิตภัณฑ์'), ('uses', 'การใช้งาน'),
                                          ('features', 'จุดเด่น'), ('specs', 'ข้อมูลจำเพาะ'), ('options', 'ตัวเลือก'), ('downloads', 'ดาวน์โหลด')]),
            TX('label', 'ข้อความ'),
        ]),
        TX('video_toggle', 'คำอ่านปุ่มหยุด/เล่นวิดีโอ'),
        TX('prev', 'คำอ่านปุ่มเลื่อนการ์ดไปทางซ้าย (ก่อนหน้า)'),
        TX('next', 'คำอ่านปุ่มเลื่อนการ์ดไปทางขวา (ถัดไป)'),
        TX('copy', 'ปุ่มคัดลอก'),
    ]),
    ('site/settings', 'ลูกเล่นและการแสดงผล (โหมดมืด / ปุ่มลอยบนมือถือ / ภาพ 360°)', [
        BOOL('dark_mode', 'เปลี่ยนเว็บเป็นพื้นเข้มอัตโนมัติ เมื่อเครื่องลูกค้าตั้งโหมดมืดไว้'),
        BOOL('quick_bar', 'แสดงปุ่มติดต่อด่วนลอยด้านล่างจอมือถือ'),
        TX('quick_line', 'ปุ่มลอย: ข้อความปุ่ม LINE', desc='ลิงก์ LINE ใช้จาก ข้อมูลบริษัท → โซเชียลมีเดีย (ช่องทาง LINE) ถ้าไม่มี ปุ่มนี้จะไม่แสดง'),
        TX('quick_call', 'ปุ่มลอย: ข้อความปุ่มโทร'),
        TX('quick_demo', 'ปุ่มลอย: ข้อความปุ่มนัดสาธิต'),
        LINK('quick_demo_link', 'ปุ่มลอย: ลิงก์ปุ่มนัดสาธิต'),
        TX('quick_aria', 'คำอ่านแถบปุ่มลอย (สำหรับโปรแกรมอ่านหน้าจอ)'),
        TX('spin_hint', 'ข้อความบนภาพ 360° (เช่น ลากเพื่อหมุนดูรอบคัน)'),
    ]),
    ('site/specs', 'ตารางสเปกรถ (หัวข้อแถวและหมายเหตุ)', [
        TX('item_header', 'หัวคอลัมน์แรกของตาราง'),
        LIST('rows', 'แถวในตารางสเปก', [S('key', 'รหัสแถว (ห้ามแก้)', readonly=True), TX('label', 'ชื่อแถว')]),
        LIST('groups', 'กลุ่มแถว', [TX('title', 'ชื่อกลุ่ม'), SLIST('keys', 'รหัสแถวในกลุ่มนี้')]),
        TX('charge_note', 'หมายเหตุใต้ตาราง 1', long=True),
        TX('rights_note', 'หมายเหตุใต้ตาราง 2', long=True),
        TX('drawing_caption', 'คำอธิบายภาพลายเส้นขนาดรถ ({model} = ชื่อรุ่น)'),
        LIST('swatches', 'สีตัวรถ (วงกลมสี)', [S('name', 'ชื่อสี'), S('color', 'รหัสสี (เช่น #F4F6F8)')]),
    ]),
]

MODEL_FIELDS = [
    S('model_name', 'ชื่อรุ่น (เช่น Z5)', req=True),
    S('full_name', 'ชื่อเต็ม (เช่น Z5 Logistics RoboVan)'),
    TX('type', 'ประเภทรถ (บรรทัดใต้ชื่อรุ่น)'),
    IMG('image', 'รูปรถ (พื้นหลังโปร่งใส)'),
    DOC('pdf', 'สเปกชีท PDF'),
    LINK('page', 'หน้ารายละเอียดของรุ่นนี้', desc='เช่น z5.html หรือ products.html#z20'),
    SEL('card_button', 'ปุ่มซ้ายบนการ์ดรถ', [('details', 'ดูรายละเอียด'), ('pdf', 'สเปก PDF')]),
    TX('card_tag', 'ป้ายมุมรูปบนการ์ด (เว้นว่างได้)'),
    SEL('card_tag_style', 'สีป้าย', [('normal', 'น้ำเงิน'), ('cold', 'ฟ้า (ห้องเย็น)')]),
    LIST('card_facts', 'ตัวเลขบนการ์ดรถ (3 บรรทัด)', [TX('label', 'หัวข้อ'), S('value', 'ค่า')], summary='{label_th}: {value}'),
    NUM('length', 'ความยาว (มม.) สำหรับภาพลายเส้น'),
    NUM('width', 'ความกว้าง (มม.)'),
    NUM('height', 'ความสูง (มม.)'),
    LIST('specs', 'ข้อมูลจำเพาะ', [
        S('key', 'รหัสแถว (ดูที่ ตารางสเปกรถ)'), TX('value', 'ค่า', desc='ถ้าค่าเหมือนกันทุกภาษา ใส่เฉพาะภาษาไทยได้'),
    ], summary='{key}: {value_th}'),
    TX('cmp_volume', 'ตารางเปรียบเทียบ: ปริมาตร'),
    S('cmp_payload', 'ตารางเปรียบเทียบ: บรรทุก'),
    S('cmp_range', 'ตารางเปรียบเทียบ: ระยะวิ่ง'),
    S('cmp_battery', 'ตารางเปรียบเทียบ: แบตเตอรี่'),
    S('cmp_cold', 'ตารางเปรียบเทียบ: ห้องเย็น', desc='ใส่ — ถ้าไม่มี'),
    S('cmp_speed', 'ตารางเปรียบเทียบ: ความเร็ว'),
    S('cmp_dims', 'ตารางเปรียบเทียบ: ขนาด'),
    IMGS('spin', 'ภาพหมุนรอบคัน 360° (เลือก 24–36 รูป เรียงตามมุมรอบคัน)',
         desc='ถ่ายรถทุกๆ 10–15 องศาให้ครบรอบ ภาพขนาดเท่ากันทุกรูป ถ้ามีตั้งแต่ 8 รูปขึ้นไป หน้ารุ่นรถจะลากหมุนดูได้'),
    FILE3D('model3d', 'ไฟล์ 3D ของรถ (.glb) เว้นว่างได้', desc='ถ้ามีไฟล์นี้ จะใช้แทนภาพหมุน ลูกค้าลากหมุน/ซูมได้อิสระ (ไฟล์ไม่เกิน 25 MB)'),
]

PAGE_FIELDS = [
    TX('seo_title', 'ชื่อหน้า (แท็บเบราว์เซอร์และ Google)', req=True),
    TX('seo_desc', 'คำอธิบายหน้าสำหรับ Google', long=True),
]
CTA_TOPICS = [('demo', 'นัดหมายสาธิต'), ('quote', 'ขอใบเสนอราคา'), ('education', 'การศึกษา'),
              ('security', 'หุ่นยนต์ความปลอดภัย'), ('ai-agent', 'AI Agent'), ('partner', 'พันธมิตร'), ('other', 'อื่นๆ')]
PAGE_FIELDS_CTA = PAGE_FIELDS + [
    TX('cta_title', 'แถบปิดท้ายหน้า: หัวข้อ (เว้นว่าง = ใช้ข้อความมาตรฐาน)', long=True),
    TX('cta_lead', 'แถบปิดท้ายหน้า: คำอธิบาย (เว้นว่าง = ใช้ข้อความมาตรฐาน)', long=True),
    SEL('cta_topic', 'แถบปิดท้ายหน้า: ปุ่มนัดสาธิตเลือกเรื่องในแบบฟอร์มเป็น', CTA_TOPICS),
    BG('cta_bg', 'แถบปิดท้ายหน้า: 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
]


def PHERO(extra=()):
    return [IMG(), ALT(), TX('crumb', 'ชื่อหน้าในแถบเส้นทาง'), TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อใหญ่', long=True),
            TX('lead', 'คำอธิบาย', long=True)] + list(extra)


# ================================================================ helpers for models
def mkey(v):
    """Model key from a stored reference ('content/models/z5.json' → 'z5')."""
    v = (v or '').strip().replace('\\', '/')
    v = v.rsplit('/', 1)[-1]
    return v[:-5] if v.endswith('.json') else v


_models = None


def models():
    global _models
    if _models is None:
        _models = {k: d for k, d in collection('models')}
    return _models


def model(v):
    return models().get(mkey(v)) or {}


def form_model(m):
    return s(m, 'model_name').replace(' ', '-')


# ================================================================ page shell
HEAD_SCRIPT = ("<script>(function(){var l='th';try{var s=localStorage.getItem('sx-lang');if(s==='zh'||s==='en'||s==='th')l=s;}catch(e){}"
               "var d=document.documentElement;d.setAttribute('data-lang',l);d.setAttribute('lang',l==='zh'?'zh-CN':l);})();</script>")


def hidden_pages():
    """Pages switched off in the back office (their menu links are left out)."""
    try:
        import p_tools
        return p_tools.disabled_pages()
    except ImportError:
        return set()


def link_shown(url):
    """False when the link goes to a page switched off in the back office."""
    return (url or '').split('#')[0].split('?')[0] not in hidden_pages()


def _shown(it, key='link'):
    return link_shown(s(it, key))


def _sub(items_, current):
    out = []
    for it in items_:
        if not _shown(it):
            continue
        if it.get('divider_before'):
            out.append('<hr>')
        link = s(it, 'link')
        cur = ' aria-current="page"' if link == current else ''
        out.append(f'<a href="{href(link)}"{cur}><b>{Tk(it, "title")}</b><span class="sub-hint">{Tk(it, "hint")}</span></a>')
    return ''.join(out)


def _pages_in(menu_items):
    return {s(i, 'link').split('#')[0] for i in menu_items}


def header(current):
    m, co = C('site/menu'), C('site/company')
    import p_business
    # three menu groups: 1 = the main business (RoboVan), 2 = other solutions, 3 = about the company
    pm = items(m, 'products_menu') + p_business.menu_items('products')
    sm = items(m, 'solutions_menu') + p_business.menu_items('solutions')
    am = items(m, 'about_menu') + p_business.menu_items('about')
    own = {'index.html', 'contact.html'}
    prod_cur = ' is-current' if current in _pages_in(pm) - own else ''
    sol_cur = ' is-current' if current in _pages_in(sm) - own - _pages_in(pm) else ''
    about_cur = ' is-current' if current in _pages_in(am) - own - _pages_in(pm) - _pages_in(sm) else ''

    def link(target, key):
        cur = ' aria-current="page"' if target == current else ''
        return f'<a class="nav-link" href="{target}"{cur}>{Tk(m, key)}</a>'

    def group(key, menu, cur):
        if not any(_shown(it) for it in menu):
            return ''
        return f'''<div class="nav-item{cur}">
        <button class="nav-toggle" type="button" aria-expanded="false">{Tk(m, key)}{ic('chev')}</button>
        <div class="sub">{_sub(menu, current)}</div>
      </div>'''
    logo = media(s(co, 'logo'), 'img')
    logo_light = media(s(co, 'logo_white'), 'img') or logo
    return f'''<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="index.html"{aria(tri(m, 'home_aria'))}><img class="logo-dark" src="{esc(logo)}" alt="{esc(s(co, 'site_name'))}" width="103" height="30"><img class="logo-light" src="{esc(logo_light)}" alt="" width="103" height="30" aria-hidden="true"></a>
    <nav class="nav" id="site-nav"{aria(tri(m, 'menu_aria'))}>
      {link('index.html', 'nav_home')}
      {group('nav_products', pm, prod_cur)}
      {group('nav_solutions', sm, sol_cur)}
      {group('nav_about', am, about_cur)}
      {link('contact.html', 'nav_contact')}
    </nav>
    <div class="header-actions">
      <div class="lang" role="group"{aria(tri(m, 'lang_aria'))}>
        <button type="button" data-set-lang="th" aria-pressed="true" lang="th">ไทย</button><button type="button" data-set-lang="zh" aria-pressed="false" lang="zh-CN">中文</button><button type="button" data-set-lang="en" aria-pressed="false" lang="en">EN</button>
      </div>
      <a class="btn btn-primary btn-sm" href="{href(s(m, 'nav_demo_link'))}">{Tk(m, 'nav_demo')}</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"{aria(tri(m, 'open_menu_aria'))}>{ic('menu')}</button>
    </div>
  </div>
</header>'''


SOCIAL_ICON = {'tiktok': 'tiktok', 'facebook': 'link', 'instagram': 'camera', 'line': 'chat', 'linkedin': 'link',
               'youtube': 'play', 'x': 'link', 'other': 'link'}


def social_name(it):
    return dict(NETWORKS).get(s(it, 'network'), s(it, 'network'))


def footer():
    m, co = C('site/menu'), C('site/company')

    def col(title_key, list_key):
        lis = ''.join(f'<a href="{href(s(i, "link"))}">{Tk(i, "label")}</a>' for i in items(m, list_key) if _shown(i))
        return f'<div class="footer-col"><h4>{Tk(m, title_key)}</h4>{lis}</div>'
    socials = ''.join(
        f'<li>{ic(SOCIAL_ICON.get(s(i, "network"), "link"))}<a href="{href(s(i, "url"))}" target="_blank" rel="noopener">{fmt(social_name(i))} {fmt(s(i, "handle"))}</a></li>'
        for i in items(co, 'socials') if s(i, 'url'))
    phone = f'\n          <li>{ic("phone")}<span class="num">{fmt(s(co, "phone"))}</span></li>' if s(co, 'phone') else ''
    email = f'\n          <li>{ic("mail")}<span>{fmt(s(co, "email"))}</span></li>' if s(co, 'email') else ''
    addr = f'\n          <li>{ic("pin")}<span>{Tk(co, "address")}</span></li>' if has(co, 'address') else ''
    soc = f'\n          {socials}' if socials else ''
    logo = media(s(co, 'logo'), 'img')
    solutions = any(_shown(i) for i in items(m, 'footer_solutions'))
    sol_col = f"\n      {col('footer_solutions_title', 'footer_solutions')}" if solutions else ''
    grid_cls = 'footer-grid f5' if solutions else 'footer-grid'
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="{grid_cls}">
      <div class="footer-brand">
        <img class="logo-dark" src="{esc(logo)}" alt="{esc(s(co, 'site_name'))}" width="110" height="32" loading="lazy"><img class="logo-light" src="{esc(media(s(co, 'logo_white'), 'img') or logo)}" alt="" width="110" height="32" loading="lazy" aria-hidden="true">
        <p class="footer-tag">{fmt(s(co, 'tagline'))}</p>
        {Bk('p', co, 'footer_about')}
      </div>
      {col('footer_products_title', 'footer_products')}{sol_col}
      {col('footer_company_title', 'footer_company')}
      <div class="footer-col">
        <h4>{Tk(m, 'footer_contact_title')}</h4>
        <ul class="footer-contact" style="display:grid;gap:10px">{phone}{email}{addr}{soc}
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {fmt(s(co, 'copyright_year'))} {fmt(s(co, 'copyright_name'))} · {Tk(co, 'rights')}</span>
      <span>{Tk(co, 'footer_note')}</span>
    </div>
  </div>
</footer>'''


def page(fname, page_data, body, extra_head='', current=None, share=None):
    """Full HTML document. current: menu item to highlight (default fname); share: picture for LINE/Facebook."""
    co, m = C('site/company'), C('site/menu')
    t_th, t_zh, t_en = tri(page_data, 'seo_title')
    d3 = tri(page_data, 'seo_desc')
    share = media(share or s(co, 'share_image'), 'img')
    fav = media(s(co, 'favicon'), 'img')
    apple = media(s(co, 'apple_icon'), 'img')
    head = f'''<title>{esc(t_th)}</title>
<meta name="description" content="{esc(d3[0])}">
<meta name="sx-title-th" content="{esc(t_th)}"><meta name="sx-title-zh" content="{esc(t_zh)}"><meta name="sx-title-en" content="{esc(t_en)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{esc(s(co, 'site_name'))}"><meta property="og:title" content="{esc(t_th)}">
<meta property="og:description" content="{esc(d3[2])}"><meta property="og:image" content="{esc(share)}">
<meta name="theme-color" content="#1C3564">
<link rel="icon" type="image/png" href="{esc(fav)}"><link rel="apple-touch-icon" href="{esc(apple)}">
{HEAD_SCRIPT}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&amp;family=Prompt:wght@300;400;500;600&amp;display=swap">
<link rel="stylesheet" href="assets/css/style.css">{extra_head}'''
    st = C('site/settings')
    html_cls = ' class="auto-dark"' if st.get('dark_mode') else ''
    scheme = 'light dark' if st.get('dark_mode') else 'light only'
    qbar = quick_bar(st, co)
    dark = re.match(r'\s*<section class="(hero|phero phero--(photo|chat))\b', body)
    classes = (['hero-dark'] if dark else []) + (['has-quickbar'] if qbar else [])
    body_cls = f' class="{" ".join(classes)}"' if classes else ''
    import promo
    popup = promo.render(fname)
    content = f'''{sprite()}
<a class="skip" href="#main">{Tk(m, 'skip')}</a>
{header(current or fname)}
<main id="main">
{body}
</main>
{footer()}{qbar}{popup}
<script src="assets/js/main.js" defer></script>'''
    return f'''<!doctype html>
<html lang="th" data-lang="th"{html_cls}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="{scheme}">
{head}
</head>
<body{body_cls}>
{content}
</body>
</html>
'''


def quick_bar(st, co):
    """LINE / call / demo buttons fixed to the bottom of phone screens."""
    if not st.get('quick_bar'):
        return ''
    btns = []
    line = next((s(x, 'url') for x in items(co, 'socials') if s(x, 'network') == 'line' and s(x, 'url')), '')
    if line:
        btns.append(f'<a class="qb qb-line" href="{href(line)}" target="_blank" rel="noopener">{ic("chat")}{Tk(st, "quick_line")}</a>')
    tel = re.sub(r'[^\d+]', '', s(co, 'phone'))
    if tel:
        btns.append(f'<a class="qb qb-call" href="tel:{esc(tel)}">{ic("phone")}{Tk(st, "quick_call")}</a>')
    if s(st, 'quick_demo_link') and has(st, 'quick_demo'):
        btns.append(f'<a class="qb qb-demo" href="{href(s(st, "quick_demo_link"))}">{ic("calendar")}{Tk(st, "quick_demo")}</a>')
    if not btns:
        return ''
    return f'\n<nav class="quickbar qb-{len(btns)}"{aria(tri(st, "quick_aria"))}>{"".join(btns)}</nav>'


# ================================================================ shared sections
def crumbs(trail):
    """trail: [(href or None, (th, zh, en))]"""
    parts = []
    for i, (h, t3) in enumerate(trail):
        if i:
            parts.append('<span class="sep">/</span>')
        parts.append(f'<a href="{h}">{T(t3)}</a>' if h else f'<span>{T(t3)}</span>')
    return f'<nav class="crumbs"{aria(tri(C("site/labels"), "crumb_aria"))}>{"".join(parts)}</nav>'


def trail(section, hero):
    """Breadcrumb for a page: section is None, 'products' (RoboVan), 'solutions' or 'about'."""
    lb = C('site/labels')
    out = [('index.html', tri(lb, 'crumb_home'))]
    if section == 'products':
        out.append(('products.html', tri(lb, 'crumb_products')))
    elif section == 'solutions':
        out.append(('products.html#solutions', tri(lb, 'crumb_solutions') if has(lb, 'crumb_solutions') else tri(lb, 'crumb_products')))
    elif section == 'about':
        out.append(('about.html', tri(lb, 'crumb_about')))
    out.append((None, tri(hero, 'crumb')))
    return out


def phero(media_html, media_kind, trail_, hero, extra=''):
    return f'''<section class="phero phero--{media_kind}">
  <div class="phero-grid">
    <div class="phero-media is-{media_kind}">{media_html}</div>
    <div class="phero-copy">
      {crumbs(trail_)}
      <span class="eyebrow">{Tk(hero, 'eyebrow')}</span>
      <h1 class="h1">{Tk(hero, 'title')}</h1>
      {Bk('p', hero, 'lead', cls='lead')}
      {extra}
    </div>
  </div>
</section>'''


_SEC_OPEN = re.compile(r'<section\b[^>]*>')


def bgv(html, d, key='bg', nth=0, sid=None):
    """Put the background video (or picture) chosen in the back office behind one <section> of html.

    d[key] is {"video", "poster", "shade"}. The section gets has-bgv (dark text colours, see style.css) and a
    film layer; main.js loads the film only when the section comes into view. nth: which <section> in html
    (0 = the first); sid: the section with this id instead. Nothing chosen = html unchanged."""
    bg = (d or {}).get(key) or {}
    if not html or not isinstance(bg, dict):
        return html
    video, poster = media(s(bg, 'video'), 'video'), media(s(bg, 'poster'), 'img')
    if not (video or poster):
        return html
    shade = s(bg, 'shade')
    if shade not in ('light', 'medium', 'strong'):
        shade = 'medium'
    if sid:
        m = re.search(r'<section\b[^>]*\bid="' + re.escape(sid) + r'"[^>]*>', html)
    else:
        found = list(_SEC_OPEN.finditer(html))
        m = found[nth] if len(found) > nth else None
    if not m:
        return html
    tag = m.group(0)
    if ' class="' in tag:
        tag = re.sub(r' class="([^"]*)"', lambda c: f' class="{c.group(1)} has-bgv bgv-{shade}"', tag, count=1)
    else:
        tag = tag[:-1] + f' class="has-bgv bgv-{shade}">'
    if video:
        pa = f' poster="{esc(poster)}"' if poster else ''
        layer = f'\n  <div class="bgv" aria-hidden="true"><video muted loop playsinline preload="none"{pa} data-src="{esc(video)}"></video></div>'
    else:
        layer = f'\n  <div class="bgv" aria-hidden="true" style="background-image:url(&quot;{esc(poster)}&quot;)"></div>'
    return html[:m.start()] + tag + layer + html[m.end():]


def cta_band(page_data):
    lb = C('site/labels')
    h3 = tri(page_data, 'cta_title') if has(page_data, 'cta_title') else tri(lb, 'cta_title')
    lead3 = tri(page_data, 'cta_lead') if has(page_data, 'cta_lead') else tri(lb, 'cta_lead')
    topic = s(page_data, 'cta_topic') or 'demo'
    html = f'''<section class="cta-band">
  <div class="wrap cta-inner">
    <div>
      <h2 class="h2">{T(h3)}</h2>
      {B('p', lead3, cls='lead')}
    </div>
    <div class="btn-row">
      <a class="btn btn-light" href="contact.html?topic={esc(topic)}">{ic('calendar')}{Tk(lb, 'cta_demo')}</a>
      <a class="btn btn-ghost" href="{href(s(lb, 'cta_quote_link'))}">{Tk(lb, 'cta_quote')}</a>
    </div>
  </div>
</section>'''
    return bgv(html, page_data, 'cta_bg')


def head(d, lead=True, link=True):
    """Section heading block (eyebrow, title, optional lead and right-hand link)."""
    ld = Bk('p', d, 'lead', cls='lead') if lead and has(d, 'lead') else ''
    if link and s(d, 'link') and has(d, 'link_label'):
        return (f'<div class="section-head split"><div><span class="eyebrow">{Tk(d, "eyebrow")}</span><h2 class="h2">{Tk(d, "title")}</h2>{ld}</div>'
                f'<a class="link-arrow" href="{href(s(d, "link"))}">{Tk(d, "link_label")}{ic("arrow")}</a></div>')
    return f'<div class="section-head"><span class="eyebrow">{Tk(d, "eyebrow")}</span><h2 class="h2">{Tk(d, "title")}</h2>{ld}</div>'


def figures(rows, cls=''):
    out = []
    for r in rows:
        u = f'<small>{fmt(s(r, "unit"))}</small>' if s(r, 'unit') else ''
        out.append(f'<div class="fig"><b>{fmt(s(r, "value"))}{u}</b><span>{Tk(r, "label")}</span></div>')
    return f'<div class="figures {cls}">{"".join(out)}</div>'


def kv(rows):
    """rows: [((th, zh, en) label, html value)]"""
    return '<dl class="kv">' + ''.join(f'<div><dt>{T(k)}</dt><dd>{v}</dd></div>' for k, v in rows) + '</dl>'


def features(rows, cls=''):
    out = [f'<div class="feature">{ic(s(r, "icon"))}<h3>{Tk(r, "title")}</h3>{Bk("p", r, "text")}</div>' for r in rows]
    return f'<div class="features {cls}">{"".join(out)}</div>'


def checks(rows):
    return '<ul class="checks">' + ''.join(f'<li>{ic("check")}{Tk(r, "text")}</li>' for r in rows) + '</ul>'


def steps(rows, cls=''):
    out = []
    for n, r in enumerate(rows, 1):
        goal = ' is-goal' if n == len(rows) and 'goal' in cls else ''
        out.append(f'<div class="step{goal}"><span class="pin">{n:02d}</span><h3>{Tk(r, "title")}</h3>{Bk("p", r, "text")}</div>')
    return f'<div class="steps {cls.replace("goal", "").strip()}">{"".join(out)}</div>'


def uses(rows):
    return '<ul class="uses">' + ''.join(f'<li>{ic(s(r, "icon"))}{Tk(r, "text")}</li>' for r in rows) + '</ul>'


def chips(rows, link=True):
    out = []
    for r in rows:
        if link and s(r, 'anchor'):
            out.append(f'<a class="chip" href="#{esc(s(r, "anchor"))}">{ic(s(r, "icon"))}{Tk(r, "label")}</a>')
        else:
            out.append(f'<span class="chip">{ic(s(r, "icon"))}{TC(tri(r, "label"))}</span>')
    return out


def chat_art(rows, style='', bubble_style=''):
    st = f' style="{style}"' if style else ''
    bs = f' style="{bubble_style}"' if bubble_style else ''
    bubbles = ''.join(
        f'\n      <div class="bubble {"me" if s(r, "side") == "me" else "ai"}"{bs}><span class="who">{TC(tri(r, "who"))}</span>{Tk(r, "text")}</div>'
        for r in rows)
    return f'<div class="chat-art"{st}>{bubbles}\n    </div>'


def video_card(v, extra_cls=''):
    poster = media(s(v, 'poster'), 'img')
    src = media(s(v, 'video'), 'video')
    kind = 'video/webm' if src.lower().endswith('.webm') else 'video/mp4'
    poster_attr = f' poster="{esc(poster)}"' if poster else ''
    cap = f'<figcaption>{Tk(v, "caption")}</figcaption>' if has(v, 'caption') else ''
    return (f'<figure class="video-card {extra_cls}"><video controls preload="none" playsinline{poster_attr}>'
            f'<source src="{esc(src)}" type="{kind}"></video>{cap}</figure>')


def gallery(rows):
    out = []
    for r in rows:
        inner = img(r)
        if r.get('studio'):
            inner = f'<div class="studio">{inner}</div>'
        cap = f'<figcaption>{Tk(r, "caption")}</figcaption>' if has(r, 'caption') else ''
        out.append(f'<figure class="{esc(s(r, "size") or "g-third")}">{inner}{cap}</figure>')
    return '<div class="gallery-grid">' + ''.join(out) + '</div>'


def swatches():
    sw = items(C('site/specs'), 'swatches')
    return ('<div class="swatches">' + ''.join(
        f'<span class="swatch" style="background:{esc(s(x, "color"))}" title="{esc(s(x, "name"))}"></span>' for x in sw) + '</div>')


def options(rows):
    out = []
    for r in rows:
        extra = ''
        if r.get('swatches'):
            extra = swatches()
        elif s(r, 'link') and has(r, 'link_label'):
            extra = f'<a class="link-arrow" href="{href(s(r, "link"))}">{Tk(r, "link_label")}{ic("arrow")}</a>'
        out.append(f'<div class="option"><b>{Tk(r, "title")}</b>{Bk("p", r, "text")}{extra}</div>')
    return '<div class="options">' + ''.join(out) + '</div>'


def downloads(rows):
    out = []
    for r in rows:
        url = media(s(r, 'file'), 'docs')
        if not url:
            continue
        size = file_size(url)
        meta = f'PDF · {size}' if size else 'PDF'
        out.append(f'<a class="dl" href="{esc(url)}" target="_blank" rel="noopener"><span class="dl-ic">{ic("doc")}</span>'
                   f'<span><b>{fmt(s(r, "title"))}</b><span>{T((meta, meta, meta))}</span></span>{ic("download", "ic ic-go")}</a>')
    return '<div class="downloads">' + ''.join(out) + '</div>'


# ================================================================ vehicles
def spec_values(m):
    out = {}
    for r in items(m, 'specs'):
        k = s(r, 'key')
        if not k:
            continue
        zh, en = str(r.get('value_zh') or '').strip(), str(r.get('value_en') or '').strip()
        out[k] = fmt(s(r, 'value_th')) if not zh and not en else T(tri(r, 'value'))
    return out


def spec_table(model_refs):
    sp = C('site/specs')
    labels = {s(r, 'key'): tri(r, 'label') for r in items(sp, 'rows')}
    ms = [model(r) for r in model_refs]
    vals = [spec_values(m) for m in ms]
    head_ = ''.join(f'<th scope="col">{fmt(s(m, "model_name"))}</th>' for m in ms)
    rows = []
    for g in items(sp, 'groups'):
        present = [k for k in (g.get('keys') or []) if any(k in v for v in vals)]
        if not present:
            continue
        rows.append(f'<tr class="group"><th colspan="{len(ms) + 1}" scope="colgroup">{Tk(g, "title")}</th></tr>')
        for k in present:
            cells = ''.join(f'<td>{v[k] if k in v else "—"}</td>' for v in vals)
            rows.append(f'<tr><th scope="row">{T(labels.get(k, (k, k, k)))}</th>{cells}</tr>')
    return (f'<div class="spec-wrap"><table class="spec"><thead><tr><th scope="col">{Tk(sp, "item_header")}</th>{head_}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _num(v, default):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return default


def dims_svg(m):
    """Side and front outline of a generic RoboVan with the model's real dimensions."""
    Lm, Wm, Hm = _num(m.get('length'), 3700), _num(m.get('width'), 1500), _num(m.get('height'), 2000)
    name = s(m, 'model_name')
    sc = min(300 / Lm, 150 / Hm)
    lp, hp, wp = Lm * sc, Hm * sc, Wm * sc
    x0, g = 24, 186
    top = g - hp
    wr = 330 * sc
    body_bottom = g - wr * 0.95
    nose_x = x0 + lp * 0.80
    side = (f'<path class="dim-body" d="M{x0:.1f} {top:.1f} H{nose_x:.1f} '
            f'Q{x0 + lp:.1f} {top + hp * 0.06:.1f} {x0 + lp:.1f} {top + hp * 0.30:.1f} V{body_bottom:.1f} H{x0:.1f} Z"/>'
            f'<path class="dim-soft" d="M{x0 + 6:.1f} {top + 6:.1f} H{nose_x - 8:.1f} V{body_bottom - 8:.1f} H{x0 + 6:.1f} Z"/>'
            f'<rect class="dim-body" x="{nose_x - 30:.1f}" y="{top - 7:.1f}" width="22" height="7" rx="2"/>'
            f'<rect class="dim-wheel" x="{x0 + 4:.1f}" y="{body_bottom:.1f}" width="{lp - 8:.1f}" height="{wr * 0.5:.1f}" rx="3"/>')
    for cx in (x0 + lp * 0.2, x0 + lp * 0.8):
        side += f'<circle class="dim-wheel" cx="{cx:.1f}" cy="{g - wr:.1f}" r="{wr:.1f}"/><circle class="dim-hub" cx="{cx:.1f}" cy="{g - wr:.1f}" r="{wr * 0.42:.1f}"/>'
    side += f'<path class="dim-line" d="M{x0 - 10} {g}H{x0 + lp + 10:.1f}" stroke-dasharray="3 4"/>'
    yl = g + 22
    side += (f'<path class="dim-line" d="M{x0} {yl - 6}V{yl + 6}M{x0 + lp:.1f} {yl - 6}V{yl + 6}M{x0} {yl}H{x0 + lp:.1f}"/>'
             f'<text x="{x0 + lp / 2:.1f}" y="{yl + 18}" text-anchor="middle">{Lm:,} mm</text>')
    xh = x0 + lp + 22
    side += (f'<path class="dim-line" d="M{xh - 6} {top:.1f}H{xh + 6}M{xh - 6} {g}H{xh + 6}M{xh} {top:.1f}V{g}"/>'
             f'<text x="{xh + 12:.1f}" y="{(top + g) / 2:.1f}" transform="rotate(90 {xh + 12:.1f} {(top + g) / 2:.1f})" text-anchor="middle">{Hm:,} mm</text>')
    fx = x0 + lp + 70
    front = (f'<rect class="dim-body" x="{fx:.1f}" y="{top:.1f}" width="{wp:.1f}" height="{body_bottom - top:.1f}" rx="10"/>'
             f'<rect class="dim-soft" x="{fx + wp * 0.18:.1f}" y="{top + hp * 0.16:.1f}" width="{wp * 0.64:.1f}" height="{hp * 0.22:.1f}" rx="5"/>'
             f'<rect class="dim-wheel" x="{fx + 4:.1f}" y="{body_bottom:.1f}" width="{wr * 0.7:.1f}" height="{g - body_bottom:.1f}" rx="3"/>'
             f'<rect class="dim-wheel" x="{fx + wp - 4 - wr * 0.7:.1f}" y="{body_bottom:.1f}" width="{wr * 0.7:.1f}" height="{g - body_bottom:.1f}" rx="3"/>'
             f'<path class="dim-line" d="M{fx:.1f} {yl - 6}V{yl + 6}M{fx + wp:.1f} {yl - 6}V{yl + 6}M{fx:.1f} {yl}H{fx + wp:.1f}"/>'
             f'<text x="{fx + wp / 2:.1f}" y="{yl + 18}" text-anchor="middle">{Wm:,} mm</text>')
    vw = fx + wp + 16
    return f'<svg viewBox="0 0 {vw:.0f} 236" role="img" aria-label="{esc(name)} {Lm} x {Wm} x {Hm} mm">{side}{front}</svg>'


def dims_card(ref):
    m = model(ref)
    name = s(m, 'model_name')
    cap = tuple(x.replace('{model}', name) for x in tri(C('site/specs'), 'drawing_caption'))
    return f'<figure class="dims">{dims_svg(m)}<figcaption class="dim-cap">{T(cap)}</figcaption></figure>'


def product_card(ref):
    k = mkey(ref)
    m = model(ref)
    lb = C('site/labels')
    tag = ''
    if has(m, 'card_tag'):
        cold = ' cold' if s(m, 'card_tag_style') == 'cold' else ''
        tag = f'<span class="pcard-tag{cold}">{Tk(m, "card_tag")}</span>'
    rows = [(tri(r, 'label'), fmt(s(r, 'value'))) for r in items(m, 'card_facts')]
    pdf = media(s(m, 'pdf'), 'docs')
    if s(m, 'card_button') == 'pdf' and pdf:
        a1 = f'<a class="btn btn-outline btn-sm" href="{esc(pdf)}" target="_blank" rel="noopener">{ic("download")}{Tk(lb, "card_pdf")}</a>'
    else:
        a1 = f'<a class="btn btn-outline btn-sm" href="{href(s(m, "page"))}">{Tk(lb, "card_details")}</a>'
    a2 = f'<a class="btn btn-primary btn-sm" href="contact.html?topic=quote&amp;model={esc(form_model(m))}">{Tk(lb, "card_quote")}</a>'
    return f'''<article class="pcard" id="card-{esc(k)}">
  <div class="pcard-media">{tag}{img(m, alt=s(m, 'full_name'))}</div>
  <div class="pcard-body">
    <div class="pcard-title"><h3>{fmt(s(m, 'model_name'))}</h3><span>{Tk(m, 'type')}</span></div>
    {kv(rows)}
    <div class="pcard-actions">{a1}{a2}</div>
  </div>
</article>'''
