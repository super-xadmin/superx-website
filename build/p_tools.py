# -*- coding: utf-8 -*-
"""Sales tools: ROI calculator (roi.html) and model finder (choose.html). Every text, number and question
comes from the back office (หน้าเว็บ → คำนวณความคุ้มค่า / ช่วยเลือกรุ่น)."""
import json

from core import C, s, items, tri, has, esc, fmt, T, Tk, Bk, media, img, href, ic, strs, LANGS
from schema import TX, NUM, BOOL, LIST, OBJ, MODELS
from layout import (PAGE_FIELDS_CTA, PHERO, page, phero, trail, cta_band, head, model, mkey, models, form_model)

INPUTS = [('trips', 'จำนวนเที่ยวต่อวัน'), ('km', 'ระยะทางต่อเที่ยว'), ('drivers', 'จำนวนคนขับตอนนี้'),
          ('wage', 'ค่าแรงคนขับต่อคนต่อเดือน'), ('days', 'วันทำงานต่อเดือน'), ('fuel', 'ค่าน้ำมันรถเดิมต่อกิโลเมตร')]
INPUT_FIELDS = [TX('label', 'ชื่อช่อง'), TX('unit', 'หน่วย (เช่น เที่ยว, กม., บาท)'), NUM('value', 'ค่าเริ่มต้น'), NUM('max', 'ค่าสูงสุดที่กรอกได้')]


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _numtxt(v):
    f = _num(v)
    return str(int(f)) if f == int(f) else str(f)


# ================================================================ ROI calculator
class Roi:
    FILE, DIR, LABEL = 'roi.html', 'pages/roi', 'คำนวณความคุ้มค่า (ROI)'
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (เปิด/ปิด ชื่อหน้า แถบปิดท้าย)',
         [BOOL('enabled', 'เปิดใช้งานหน้านี้ (ใส่ตัวเลขจริงในหัวข้อ 3 ให้ครบก่อนเปิด)')] + PAGE_FIELDS_CTA),
        ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
        ('inputs', '2. ช่องที่ลูกค้ากรอก', [TX('title', 'หัวข้อกล่องกรอกข้อมูล'), TX('lead', 'คำอธิบาย', long=True)]
         + [OBJ(k, f'ช่อง: {lab}', INPUT_FIELDS) for k, lab in INPUTS]),
        ('assumptions', '3. ตัวเลขฝั่ง RoboVan ที่ใช้คำนวณ (ลูกค้าไม่เห็น)', [
            NUM('van_km_day', 'ระยะทางที่ RoboVan 1 คันวิ่งได้ต่อวัน (กม.)'),
            NUM('van_cost_month', 'ค่าใช้จ่าย RoboVan ต่อคันต่อเดือน (บาท) เช่น ค่าเช่า + บริการ'),
            NUM('energy_km', 'ค่าไฟของ RoboVan ต่อกิโลเมตร (บาท)'),
            NUM('staff_month', 'ค่าเจ้าหน้าที่ดูแล / ควบคุมระยะไกลต่อเดือน (บาท) รวมทุกคัน'),
        ]),
        ('results', '4. ข้อความผลลัพธ์และปุ่ม', [
            TX('saving_title', 'หัวข้อผลลัพธ์ (เช่น ประหยัดได้ประมาณ)'), TX('baht', 'คำว่า บาท'), TX('per_year', 'คำว่า ต่อปี'),
            TX('percent_label', 'ข้อความหลังเปอร์เซ็นต์ (เช่น ของค่าใช้จ่ายเดิม)'),
            TX('current_label', 'แถว: ค่าใช้จ่ายแบบเดิมต่อปี'), TX('robovan_label', 'แถว: ค่าใช้จ่ายเมื่อใช้ RoboVan ต่อปี'),
            TX('vans_label', 'แถว: จำนวน RoboVan ที่ต้องใช้'), TX('vans_unit', 'หน่วยรถ (เช่น คัน)'),
            TX('km_label', 'แถว: ระยะทางรวมต่อปี'), TX('km_unit', 'หน่วยระยะทาง (เช่น กม.)'),
            TX('no_saving', 'ข้อความเมื่อยังไม่คุ้ม', long=True), TX('button', 'ปุ่มส่งผลไปขอใบเสนอราคา'),
            TX('message', 'ข้อความที่ใส่ในแบบฟอร์มให้อัตโนมัติ', long=True,
               desc='ใช้ {trips} {km} {drivers} {wage} {days} {fuel} {vans} {current} {robovan} {saving} แทนตัวเลข'),
            TX('note', 'หมายเหตุใต้ผลลัพธ์', long=True),
        ]),
    ]

    def enabled(self):
        return bool(C(f'{self.DIR}/page').get('enabled'))

    def render(self):
        if not self.enabled():
            return None
        D = self.DIR
        h, i, a, r = (C(f'{D}/{k}') for k in ('hero', 'inputs', 'assumptions', 'results'))
        hero = phero(img(h, lazy=False), 'photo', trail('products', h), h)
        fields = []
        for k, _lab in INPUTS:
            f = i.get(k) or {}
            mx = f' max="{esc(_numtxt(f.get("max")))}"' if _num(f.get('max')) > 0 else ''
            fields.append(f'<label class="roi-field" for="roi-{k}"><span class="roi-label">{Tk(f, "label")}</span>'
                          f'<span class="roi-input"><input id="roi-{k}" name="{k}" type="number" inputmode="decimal" min="0"{mx} step="any" '
                          f'value="{esc(_numtxt(f.get("value")))}"><span class="roi-unit">{Tk(f, "unit")}</span></span></label>')
        data = {
            'a': {k: _num(a.get(k)) for k in ('van_km_day', 'van_cost_month', 'energy_km', 'staff_month')},
            'msg': {k: x for (k, _lg), x in zip(LANGS, tri(r, 'message'))},
        }
        baht = Tk(r, 'baht')
        body = f'''<section class="section">
  <div class="wrap roi" data-roi>
    <form class="roi-form" novalidate onsubmit="return false">
      <h2 class="h3">{Tk(i, 'title')}</h2>
      {Bk('p', i, 'lead', cls='small')}
      {chr(10).join('      ' + x if n else x for n, x in enumerate(fields))}
    </form>
    <div class="roi-result" aria-live="polite">
      <span class="roi-kicker">{Tk(r, 'saving_title')}</span>
      <div class="roi-big"><b id="roi-r-saving">0</b><span>{baht} / {Tk(r, 'per_year')}</span></div>
      <p class="roi-pct"><b id="roi-r-pct">0%</b> {Tk(r, 'percent_label')}</p>
      {Bk('p', r, 'no_saving', cls='roi-none')}
      <dl class="roi-break">
        <div><dt>{Tk(r, 'current_label')}</dt><dd><span id="roi-r-current">0</span> {baht}</dd></div>
        <div><dt>{Tk(r, 'robovan_label')}</dt><dd><span id="roi-r-robovan">0</span> {baht}</dd></div>
        <div><dt>{Tk(r, 'vans_label')}</dt><dd><span id="roi-r-vans">0</span> {Tk(r, 'vans_unit')}</dd></div>
        <div><dt>{Tk(r, 'km_label')}</dt><dd><span id="roi-r-km">0</span> {Tk(r, 'km_unit')}</dd></div>
      </dl>
      <a class="btn btn-light" id="roi-quote" href="contact.html?topic=quote">{ic('calendar')}{Tk(r, 'button')}</a>
      {Bk('p', r, 'note', cls='note')}
    </div>
  </div>
</section>
<script type="application/json" id="roi-data">{_json(data)}</script>'''
        pg = C(f'{D}/page')
        return page(self.FILE, pg, hero + body + cta_band(pg))


# ================================================================ model finder
def showcase(mo):
    """One van large with its key figures and the two buttons (same look as the home line-up)."""
    lb = C('site/labels')
    facts = ''.join(f'<div><dt>{Tk(x, "label")}</dt><dd>{fmt(s(x, "value"))}</dd></div>' for x in items(mo, 'card_facts'))
    pdf = media(s(mo, 'pdf'), 'docs')
    if s(mo, 'card_button') == 'pdf' and pdf:
        a1 = f'<a class="btn btn-primary" href="{esc(pdf)}" target="_blank" rel="noopener">{ic("download")}{Tk(lb, "card_pdf")}</a>'
    else:
        a1 = f'<a class="btn btn-primary" href="{href(s(mo, "page"))}">{Tk(lb, "card_details")}</a>'
    a2 = f'<a class="btn btn-outline" href="contact.html?topic=quote&amp;model={esc(form_model(mo))}">{Tk(lb, "card_quote")}</a>'
    return (f'<div class="lineup-stage">{img(mo, alt=s(mo, "full_name"))}</div>'
            f'<div class="lineup-name"><h3>{fmt(s(mo, "model_name"))}</h3><span>{Tk(mo, "type")}</span></div>'
            f'<dl class="lineup-facts">{facts}</dl><div class="btn-row">{a1}{a2}</div>')


class Chooser:
    FILE, DIR, LABEL = 'choose.html', 'pages/choose', 'ช่วยเลือกรุ่นรถ'
    SECTIONS = [
        ('page', 'ตั้งค่าหน้า (เปิด/ปิด ชื่อหน้า แถบปิดท้าย)', [BOOL('enabled', 'เปิดใช้งานหน้านี้')] + PAGE_FIELDS_CTA),
        ('hero', '1. ภาพหลักและหัวข้อ', PHERO()),
        ('quiz', '2. คำถามและคำตอบ', [
            TX('eyebrow', 'หัวข้อเล็ก'), TX('title', 'หัวข้อ', long=True), TX('lead', 'คำอธิบาย', long=True),
            LIST('questions', 'คำถาม (แนะนำ 3–4 ข้อ)', [
                TX('q', 'คำถาม'),
                LIST('options', 'คำตอบให้เลือก', [TX('label', 'คำตอบ'), MODELS('models', 'รุ่นที่เหมาะกับคำตอบนี้ (เลือกได้หลายรุ่น)')],
                     summary='{label_th}'),
            ], summary='{q_th}'),
        ]),
        ('result', '3. ผลลัพธ์', [
            TX('title', 'หัวข้อเหนือรุ่นที่แนะนำ'), TX('pending', 'ข้อความก่อนตอบครบทุกข้อ'),
            TX('also', 'ข้อความนำรุ่นใกล้เคียง'), TX('restart', 'ปุ่มเริ่มใหม่'),
        ]),
    ]

    def enabled(self):
        return bool(C(f'{self.DIR}/page').get('enabled'))

    def render(self):
        if not self.enabled():
            return None
        D = self.DIR
        h, q, r = (C(f'{D}/{k}') for k in ('hero', 'quiz', 'result'))
        hero = phero(img(h, lazy=False), 'photo', trail('products', h), h)
        qs, used = [], []
        for n, qu in enumerate(items(q, 'questions'), 1):
            opts = []
            for o in items(qu, 'options'):
                keys = [mkey(x) for x in strs(o, 'models') if model(x)]
                used += [k for k in keys if k not in used]
                opts.append(f'<label class="quiz-opt"><input type="radio" name="q{n}" data-models="{esc(" ".join(keys))}">'
                            f'<span>{Tk(o, "label")}</span></label>')
            qs.append(f'<li class="quiz-q"><fieldset><legend><span class="pin">{n:02d}</span><span>{Tk(qu, "q")}</span></legend>'
                      f'<div class="quiz-opts">{"".join(opts)}</div></fieldset></li>')
        cards = ''.join(f'<div class="quiz-card lineup-panel" data-model="{esc(k)}" data-name="{esc(s(models()[k], "model_name"))}" '
                        f'data-link="{href(s(models()[k], "page"))}" hidden>{showcase(models()[k])}</div>' for k in used)
        body = f'''<section class="section">
  <div class="wrap quiz" data-quiz>
    {head(q)}
    <ol class="quiz-qs">
      {chr(10).join('      ' + x if n else x for n, x in enumerate(qs))}
    </ol>
    <div class="quiz-result" id="quiz-result">
      {Bk('p', r, 'pending', cls='quiz-pending')}
      <div class="quiz-out" hidden>
        <h2 class="h2">{Tk(r, 'title')}</h2>
        {cards}
        <p class="quiz-also" hidden><span>{Tk(r, 'also')}</span> <span class="quiz-also-list chips"></span></p>
        <button class="btn btn-outline" type="button" data-quiz-reset>{Tk(r, 'restart')}</button>
      </div>
    </div>
  </div>
</section>'''
        pg = C(f'{D}/page')
        return page(self.FILE, pg, hero + body + cta_band(pg))


MODULES = [Roi(), Chooser()]


def disabled_pages():
    return {m.FILE for m in MODULES if not m.enabled()}
