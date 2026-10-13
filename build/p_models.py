# -*- coding: utf-8 -*-
"""Vehicle model pages: z5.html, z10.html, cold-chain.html (same layout, separate content)."""
from core import C, s, items, tri, has, esc, fmt, T, Tk, Bk, media, img, href, ic
from schema import TX, S, LINK, BOOL, IMG, ALT, VID, DOC, ICON, MODEL, LIST, SEL, FEATURE
from layout import (PAGE_FIELDS_CTA, page, phero, trail, cta_band, figures, uses, features, gallery, video_card, options, downloads,
                    spec_table, dims_card, model, form_model)

SIZES = [('g-wide', 'กว้าง 2 ช่อง'), ('g-tall', 'สูง 2 แถว'), ('g-third', '1 ใน 3'), ('g-half', 'ครึ่งแถว')]

SECTIONS = [
    ('page', 'ตั้งค่าหน้า (ชื่อหน้า / แถบปิดท้าย)', PAGE_FIELDS_CTA),
    ('hero', '1. ภาพรถและหัวข้อ', [
        MODEL('model', 'รุ่นหลักของหน้านี้ (ใช้รูปรถและลิงก์ขอราคา)'),
        IMG('image', 'รูปแทนรูปรถ (เว้นว่าง = ใช้รูปของรุ่น)'),
        TX('crumb', 'ชื่อหน้าในแถบเส้นทาง'), TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'ชื่อรุ่น (หัวข้อใหญ่)'), TX('lead', 'คำอธิบาย', long=True),
        LIST('figures', 'ตัวเลขเด่น', [S('value', 'ตัวเลข'), S('unit', 'หน่วย'), TX('label', 'คำอธิบาย')], summary='{value} {unit}'),
    ]),
    ('media', '2. ภาพและวิดีโอ', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'),
        LIST('gallery', 'ภาพ', [SEL('size', 'ขนาดช่อง', SIZES), IMG(), ALT(), TX('caption', 'คำบรรยาย'),
                                BOOL('studio', 'พื้นหลังสตูดิโอ (สำหรับรูปรถพื้นโปร่งใส)')]),
        LIST('videos', 'วิดีโอ', [VID(), IMG('poster', 'ภาพก่อนกดเล่น'), TX('caption', 'คำบรรยาย', long=True)]),
        BOOL('videos_first', 'แสดงวิดีโอก่อนภาพ'),
    ]),
    ('overview', '3. ตำแหน่งผลิตภัณฑ์', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True),
        LIST('paragraphs', 'ย่อหน้า (ใช้ **ข้อความ** เพื่อทำตัวหนา)', [TX('text', 'ข้อความ', long=True), S('anchor', 'รหัสลิงก์ไปย่อหน้านี้ (#) เว้นว่างได้')]),
    ]),
    ('uses', '4. การใช้งาน', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'), LIST('items', 'งานที่เหมาะ', [ICON(), TX('text', 'ข้อความ')]),
    ]),
    ('features', '5. จุดเด่น', [TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'), LIST('items', 'จุดเด่น', FEATURE)]),
    ('specs', '6. ข้อมูลจำเพาะ', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'),
        LIST('models', 'รุ่นในตาราง (ค่าสเปกแก้ที่เมนู ข้อมูลรถแต่ละรุ่น)', [MODEL()], summary='{model}'),
        MODEL('drawing', 'รุ่นที่ใช้วาดภาพลายเส้นขนาดรถ'),
    ]),
    ('options', '7. ตัวเลือก', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'),
        LIST('items', 'ตัวเลือก', [TX('title', 'หัวข้อ'), TX('text', 'คำอธิบาย', long=True), TX('link_label', 'ข้อความลิงก์ (เว้นว่างได้)'), LINK(),
                                   BOOL('swatches', 'แสดงวงกลมสีตัวรถ')]),
    ]),
    ('downloads', '8. ดาวน์โหลด', [
        TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ'), TX('lead', 'คำอธิบาย', long=True),
        LIST('items', 'เอกสาร', [DOC(), S('title', 'ชื่อเอกสาร')], summary='{title}'),
    ]),
]


def sec_head(d):
    return f'''<div class="section-head"><span class="eyebrow">{Tk(d, 'eyebrow')}</span>
      <h2 class="h2">{Tk(d, 'title')}</h2></div>'''


class ModelPage:
    SECTIONS = SECTIONS

    def __init__(self, fname, folder, label):
        self.FILE, self.DIR, self.LABEL = fname, f'pages/{folder}', label

    def render(self):
        D = self.DIR
        lb = C('site/labels')
        h = C(f'{D}/hero')
        m = model(s(h, 'model'))
        mv = esc(form_model(m))
        extra = figures(items(h, 'figures')) + f'''<div class="btn-row">
      <a class="btn btn-primary" href="contact.html?topic=quote&amp;model={mv}">{Tk(lb, 'model_quote')}</a>
      <a class="btn btn-outline" href="contact.html?topic=demo&amp;model={mv}">{ic('calendar')}{Tk(lb, 'model_demo')}</a></div>'''
        pic = img(h, lazy=False, alt=s(m, 'full_name')) if s(h, 'image') else img(m, lazy=False, alt=s(m, 'full_name'))
        hero = phero(pic, 'vehicle', trail('products', h), h, extra)

        nav = ''.join(f'<a href="#{esc(s(x, "section"))}">{Tk(x, "label")}</a>' for x in items(lb, 'model_nav'))
        subnav = '<nav class="subnav" aria-label="sections"><div class="wrap subnav-row">' + nav + '</div></nav>'

        md = C(f'{D}/media')
        vids = [video_card(v) for v in items(md, 'videos')]
        gal = gallery(items(md, 'gallery'))
        if vids and md.get('videos_first'):
            wrap = 'class="grid-2" ' if len(vids) > 1 else ''
            media_html = f'<div {wrap}style="margin-bottom:14px">' + ''.join(vids) + '</div>' + gal
        elif vids:
            wrap = 'class="grid-2" ' if len(vids) > 1 else ''
            media_html = gal + f'<div {wrap}style="margin-top:14px">' + ''.join(vids) + '</div>'
        else:
            media_html = gal

        ov = C(f'{D}/overview')
        paras = []
        for p in items(ov, 'paragraphs'):
            block = Bk('p', p, 'text')
            paras.append(f'<div id="{esc(s(p, "anchor"))}">{block}</div>' if s(p, 'anchor') else block)
        overview = f'''<div class="split">
  <div class="stack"><span class="eyebrow">{Tk(ov, 'eyebrow')}</span>
    <h2 class="h2">{Tk(ov, 'title')}</h2></div>
  <div class="prose">
    {chr(10).join('    ' + x if i else x for i, x in enumerate(paras))}
  </div>
</div>'''

        us, ft, sp, op, dl = (C(f'{D}/{k}') for k in ('uses', 'features', 'specs', 'options', 'downloads'))
        spc = C('site/specs')
        spec_html = f'''<section class="section" id="specs">
  <div class="wrap">
    {sec_head(sp)}
    <div class="spec-layout">
      <div>{spec_table([s(r, 'model') for r in items(sp, 'models')])}
        <div class="spec-foot">{Bk('p', spc, 'charge_note', cls='note')}{Bk('p', spc, 'rights_note', cls='note')}</div>
      </div>
      {dims_card(s(sp, 'drawing'))}
    </div>
  </div>
</section>'''
        sections = f'''{subnav}
<section class="section" id="media">
  <div class="wrap">
    {sec_head(md)}
    {media_html}
  </div>
</section>
<section class="section section--mist" id="overview">
  <div class="wrap">{overview}</div>
</section>
<section class="section" id="uses">
  <div class="wrap">
    {sec_head(us)}
    {uses(items(us, 'items'))}
  </div>
</section>
<section class="section section--mist" id="features">
  <div class="wrap">
    {sec_head(ft)}
    {features(items(ft, 'items'))}
  </div>
</section>
{spec_html}
<section class="section section--mist" id="options">
  <div class="wrap">
    {sec_head(op)}
    {options(items(op, 'items'))}
  </div>
</section>
<section class="section" id="downloads">
  <div class="wrap split">
    <div class="stack"><span class="eyebrow">{Tk(dl, 'eyebrow')}</span>
      <h2 class="h2">{Tk(dl, 'title')}</h2>
      {Bk('p', dl, 'lead', cls='lead')}</div>
    {downloads(items(dl, 'items'))}
  </div>
</section>'''
        pg = C(f'{D}/page')
        return page(self.FILE, pg, hero + sections + cta_band(pg))


MODULES = [ModelPage('z5.html', 'z5', 'RoboVan Z5'), ModelPage('z10.html', 'z10', 'RoboVan Z10'),
           ModelPage('cold-chain.html', 'cold-chain', 'รถห้องเย็น Cold-Chain')]
