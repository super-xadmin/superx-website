# -*- coding: utf-8 -*-
"""Business / solution pages added from the back office (📦 ธุรกิจ / โซลูชัน).

Each file in content/business/ becomes one page: <page name>.html. Every part of the page is optional;
empty parts are left out.
"""
import re

from core import C, collection, s, items, tri, has, esc, fmt, T, Tk, Bk, img, href, ic, LANGS
from schema import TX, S, LINK, BOOL, NUM, IMG, ALT, VID, LIST, SEL, ICON, FEATURE, STEP, BG
from layout import page, phero, cta_band, head, features, steps, gallery, video_card, CTA_TOPICS, bgv

PARENTS = [('solutions', 'โซลูชันอื่น'), ('products', 'RoboVan (ธุรกิจหลัก)'), ('about', 'เกี่ยวกับ SuperX'), ('none', 'ไม่ต้องแสดง')]
DEFAULT_PARENT = 'solutions'   # menu group used when none is chosen

BUSINESS_FIELDS = [
    S('page', 'ชื่อหน้า (ภาษาอังกฤษตัวเล็ก ไม่เว้นวรรค เช่น ai-agent-pro)', req=True,
      desc='ใช้เป็นที่อยู่หน้าเว็บ เช่น ai-agent-pro.html ตั้งครั้งเดียว ไม่ควรเปลี่ยนภายหลัง'),
    BOOL('hide', 'ซ่อนหน้านี้ (ยังไม่แสดงบนเว็บ)'),
    NUM('order', 'ลำดับในเมนู (เลขน้อยแสดงก่อน)'),
    SEL('menu', 'แสดงในเมนูด้านบนใต้หัวข้อ (เว้นว่าง = โซลูชันอื่น)', PARENTS),
    TX('menu_title', 'ชื่อในเมนู'), TX('menu_hint', 'คำอธิบายสั้นใต้ชื่อในเมนู'),
    TX('seo_title', 'ชื่อหน้า (แท็บเบราว์เซอร์และ Google)', req=True),
    TX('seo_desc', 'คำอธิบายหน้าสำหรับ Google', long=True),
    # 1. hero
    IMG('image', '1. ภาพหลักด้านบน'), ALT(),
    TX('eyebrow', '1. ข้อความเล็กเหนือหัวข้อ'), TX('title', '1. หัวข้อใหญ่', long=True, desc='ใช้ **คำ** เพื่อทำเป็นสีฟ้า'),
    TX('lead', '1. คำอธิบาย', long=True),
    TX('button_label', '1. ข้อความปุ่ม'), LINK('button_link', '1. ลิงก์ปุ่ม'),
    BG('hero_bg', '1. 🎬 วิดีโอพื้นหลังด้านบน (ไม่ใส่ก็ได้)'),
    # 2. intro
    TX('intro_title', '2. หัวข้อแนะนำ', long=True),
    LIST('intro', '2. ย่อหน้าแนะนำ', [TX('text', 'ข้อความ', long=True)]),
    IMG('intro_image', '2. รูปข้างย่อหน้า'), ALT('intro_alt'),
    BG('intro_bg', '2. 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
    # 3. features
    TX('features_title', '3. หัวข้อจุดเด่น', long=True),
    LIST('features', '3. จุดเด่น', FEATURE),
    BG('features_bg', '3. 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
    # 4. steps
    TX('steps_title', '4. หัวข้อขั้นตอน', long=True),
    LIST('steps', '4. ขั้นตอน', STEP),
    BG('steps_bg', '4. 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
    # 5. gallery + video
    TX('media_title', '5. หัวข้อภาพและวิดีโอ', long=True),
    LIST('gallery', '5. รูปภาพ', [IMG(), ALT(), TX('caption', 'คำบรรยาย')], summary='{alt}'),
    VID('video', '5. วิดีโอ (MP4 ไม่เกิน 25 MB)'), IMG('poster', '5. ภาพก่อนกดเล่นวิดีโอ'), TX('video_caption', '5. คำบรรยายวิดีโอ'),
    BG('media_bg', '5. 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
    # 6. faq
    TX('faq_title', '6. หัวข้อคำถามที่พบบ่อย', long=True),
    LIST('faq', '6. คำถามที่พบบ่อย', [TX('q', 'คำถาม'), TX('a', 'คำตอบ', long=True)], summary='{q_th}'),
    BG('faq_bg', '6. 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
    # 7. closing band
    TX('cta_title', '7. แถบปิดท้าย: หัวข้อ (เว้นว่าง = ข้อความมาตรฐาน)', long=True),
    TX('cta_lead', '7. แถบปิดท้าย: คำอธิบาย', long=True),
    SEL('cta_topic', '7. ปุ่มนัดสาธิตเลือกเรื่องในแบบฟอร์มเป็น', CTA_TOPICS),
    BG('cta_bg', '7. แถบปิดท้าย: 🎬 วิดีโอพื้นหลัง (ไม่ใส่ก็ได้)'),
]

COLLECTIONS = [('business', '📦 ธุรกิจ / โซลูชัน (เพิ่มหน้าใหม่ได้เอง)', 'business', BUSINESS_FIELDS,
                {'fields': ['title_th', 'page', 'menu', 'hide'], 'primary': 'title_th', 'sort': ['order', 'title_th'],
                 'default': {'sort': 'order', 'order': 'asc'}})]

RESERVED = {'index', 'products', 'z5', 'z10', 'cold-chain', 'education', 'security', 'ai-agent', 'about', 'cases',
            'news', 'contact', '404', 'roi', 'choose'}


def page_name(d, slug):
    n = re.sub(r'[^a-z0-9-]+', '-', (s(d, 'page') or slug).lower()).strip('-') or 'business'
    if n in RESERVED or n.startswith('news-'):
        n = 'biz-' + n
    return n + '.html'


def _order(d):
    try:
        return float(d.get('order'))
    except (TypeError, ValueError):
        return 9999.0


def all_business():
    rows = [(slug, d) for slug, d in collection('business') if not d.get('hide') and has(d, 'title')]
    rows.sort(key=lambda x: (_order(x[1]), x[0]))
    return [dict(d, _page=page_name(d, slug)) for slug, d in rows]


def menu_items(parent):
    """Extra entries for the header menu (products or about)."""
    out = []
    for d in all_business():
        if (s(d, 'menu') or DEFAULT_PARENT) != parent:
            continue
        e = {'link': d['_page']}
        for i, (k, _lg) in enumerate(LANGS):
            e[f'title_{k}'] = (tri(d, 'menu_title') if has(d, 'menu_title') else tri(d, 'title'))[i].replace('**', '').replace('\n', ' ')
            e[f'hint_{k}'] = tri(d, 'menu_hint')[i]
        out.append(e)
    return out


def _sec(cls, inner, title=None):
    h = f'<div class="section-head"><h2 class="h2">{T(title)}</h2></div>\n    ' if title and any(title) else ''
    return f'''<section class="{cls}">
  <div class="wrap">
    {h}{inner}
  </div>
</section>'''


def render_one(d):
    lb = C('site/labels')
    btn = ''
    if s(d, 'button_link') and has(d, 'button_label'):
        btn = f'<div class="btn-row"><a class="btn btn-primary" href="{href(s(d, "button_link"))}">{Tk(d, "button_label")}</a></div>'
    hero_d = {}
    for i, (k, _lg) in enumerate(LANGS):
        hero_d[f'eyebrow_{k}'] = tri(d, 'eyebrow')[i]
        hero_d[f'title_{k}'] = tri(d, 'title')[i]
        hero_d[f'lead_{k}'] = tri(d, 'lead')[i]
    crumb_title = tuple(x.replace('**', '').replace('\n', ' ') for x in (tri(d, 'menu_title') if has(d, 'menu_title') else tri(d, 'title')))
    trail_ = [('index.html', tri(lb, 'crumb_home'))]
    parent = s(d, 'menu') or DEFAULT_PARENT
    if parent == 'about':
        trail_.append(('about.html', tri(lb, 'crumb_about')))
    elif parent == 'products':
        trail_.append(('products.html', tri(lb, 'crumb_products')))
    else:
        trail_.append(('products.html#solutions', tri(lb, 'crumb_solutions') if has(lb, 'crumb_solutions') else tri(lb, 'crumb_products')))
    trail_.append((None, crumb_title))
    if s(d, 'image'):
        hero = phero(img(d, lazy=False), 'photo', trail_, hero_d, btn)
    else:
        hero = phero('', 'chat', trail_, hero_d, btn)
    hero = bgv(hero, d, 'hero_bg')
    parts, n = [], 0

    def bg():
        return 'section section--mist' if n % 2 else 'section'
    if items(d, 'intro'):
        paras = '\n      '.join(Bk('p', p, 'text') for p in items(d, 'intro'))
        title = f'<h2 class="h2">{Tk(d, "intro_title")}</h2>' if has(d, 'intro_title') else ''
        pic = img(d, key='intro_image', alt_key='intro_alt', cls='rounded-img ratio-4-3')
        inner = f'<div class="split"><div class="prose">{title}\n      {paras}</div>{pic}</div>' if pic else f'<div class="prose" style="margin-inline:auto">{title}\n      {paras}</div>'
        parts.append(bgv(_sec(bg(), inner), d, 'intro_bg')); n += 1
    if items(d, 'features'):
        parts.append(bgv(_sec(bg(), features(items(d, 'features')), tri(d, 'features_title')), d, 'features_bg')); n += 1
    if items(d, 'steps'):
        cls = 's4' if len(items(d, 'steps')) == 4 else ''
        parts.append(bgv(_sec(bg(), steps(items(d, 'steps'), cls), tri(d, 'steps_title')), d, 'steps_bg')); n += 1
    if items(d, 'gallery') or s(d, 'video'):
        inner = ''
        if s(d, 'video'):
            th, zh, en = tri(d, 'video_caption')
            inner += video_card({'video': s(d, 'video'), 'poster': s(d, 'poster'), 'caption_th': th, 'caption_zh': zh, 'caption_en': en})
        if items(d, 'gallery'):
            size = 'g-half' if len(items(d, 'gallery')) % 3 else 'g-third'
            inner += ('<div style="margin-top:14px"></div>' if inner else '') + gallery([dict(g, size=size) for g in items(d, 'gallery')])
        parts.append(bgv(_sec(bg(), inner, tri(d, 'media_title')), d, 'media_bg')); n += 1
    if items(d, 'faq'):
        qa = '\n      '.join(f'<details class="faq-item"><summary>{Tk(f, "q")}</summary>{Bk("p", f, "a")}</details>' for f in items(d, 'faq'))
        parts.append(bgv(_sec(bg(), f'<div class="faq">\n      {qa}\n    </div>', tri(d, 'faq_title')), d, 'faq_bg')); n += 1
    pg = {k: d.get(k) for k in d if k.startswith(('seo_', 'cta_'))}
    return page(d['_page'], pg, hero + ''.join(parts) + cta_band(pg))


def extra_pages():
    return [(d['_page'], render_one(d)) for d in all_business()]
