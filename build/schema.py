# -*- coding: utf-8 -*-
"""Back-office (Pages CMS) field definitions.

Each content file is described once with the helpers below. The same description is used to
  1) write .pages.yml, the back-office menu and forms, and
  2) check that every value in content/ has a field in the back office.
"""
from core import ICON_NAMES

LANG_LABEL = (('th', 'ไทย'), ('zh', '中文'), ('en', 'English'))


def _f(kind, name, label, **kw):
    d = {'kind': kind, 'name': name, 'label': label}
    d.update(kw)
    return d


# ---------------------------------------------------------------- field helpers
def TX(name, label, long=False, req=False, desc=None, rich=False):
    """Text in three languages, stored as name_th / name_zh / name_en."""
    return _f('tx', name, label, long=long, req=req, desc=desc, rich=rich)


def S(name, label, long=False, req=False, desc=None, readonly=False):
    """One value used for every language (numbers, names, links)."""
    return _f('str', name, label, long=long, req=req, desc=desc, readonly=readonly)


def LINK(name='link', label='ลิงก์', desc='เช่น contact.html?topic=demo หรือ https://...'):
    return _f('str', name, label, long=False, req=False, desc=desc, readonly=False)


def NUM(name, label, desc=None):
    return _f('num', name, label, desc=desc)


def BOOL(name, label, desc=None):
    return _f('bool', name, label, desc=desc)


def DATE(name, label, desc=None):
    return _f('date', name, label, desc=desc)


def IMG(name='image', label='รูปภาพ', desc=None):
    return _f('img', name, label, desc=desc)


def ALT(name='alt', label='คำอธิบายรูป (alt)'):
    return _f('str', name, label, long=False, req=False, desc='ภาษาอังกฤษสั้นๆ บอกว่าในรูปมีอะไร ช่วยเรื่อง Google และผู้พิการทางสายตา', readonly=False)


def VID(name='video', label='วิดีโอ (MP4)', desc=None):
    return _f('vid', name, label, desc=desc)


def DOC(name='file', label='ไฟล์ PDF', desc=None):
    return _f('doc', name, label, desc=desc)


def SEL(name, label, values, desc=None):
    """values: [(stored value, label shown in the back office)]"""
    return _f('sel', name, label, values=values, desc=desc)


def ICON(name='icon', label='ไอคอน'):
    return _f('sel', name, label, values=[(k, f'{v} ({k})') for k, v in ICON_NAMES.items()], desc=None)


def MODEL(name='model', label='รุ่นรถ', desc=None):
    return _f('ref', name, label, collection='models', desc=desc)


def MODELS(name='models', label='รุ่นรถ (เลือกได้หลายรุ่น)', desc=None):
    return _f('refs', name, label, collection='models', desc=desc)


def IMGS(name, label, desc=None):
    """Several images in one field (stored as a list)."""
    return _f('imgs', name, label, desc=desc)


def FILE3D(name='model3d', label='ไฟล์ 3D (.glb)', desc=None):
    return _f('3d', name, label, desc=desc)


def LIST(name, label, fields, summary=None, desc=None):
    return _f('list', name, label, fields=fields, summary=summary, desc=desc)


def SLIST(name, label, desc=None):
    return _f('slist', name, label, desc=desc)


def OBJ(name, label, fields, desc=None):
    return _f('obj', name, label, fields=fields, desc=desc)


# ---------------------------------------------------------------- common groups of fields
def HEAD(lead=False, link=False):
    out = [TX('eyebrow', 'หัวข้อเล็ก (ตัวสีฟ้าเหนือหัวข้อ)'), TX('title', 'หัวข้อ', long=True)]
    if lead:
        out.append(TX('lead', 'คำอธิบายใต้หัวข้อ', long=True))
    if link:
        out += [TX('link_label', 'ข้อความลิงก์มุมขวา'), LINK('link', 'ลิงก์มุมขวา')]
    return out


def CHAT(name='chat', label='ข้อความแชตตัวอย่าง'):
    return LIST(name, label, [
        SEL('side', 'ฝั่ง', [('me', 'ลูกค้า (ขวา)'), ('ai', 'AI (ซ้าย)')]),
        TX('who', 'ชื่อผู้พูด'),
        TX('text', 'ข้อความ', long=True),
    ], summary='{who_th}: {text_th}')


FEATURE = [ICON(), TX('title', 'หัวข้อ'), TX('text', 'รายละเอียด', long=True)]
STEP = [TX('title', 'หัวข้อขั้นตอน'), TX('text', 'รายละเอียด', long=True)]
BULLET = [TX('text', 'ข้อความ')]


# ---------------------------------------------------------------- Pages CMS YAML
def _desc(d, f):
    if f.get('desc'):
        d['description'] = f['desc']
    return d


def cms_fields(fields):
    out = []
    for f in fields:
        k, n, lab = f['kind'], f['name'], f['label']
        if k == 'tx':
            t = 'rich-text' if f.get('rich') else ('text' if f.get('long') else 'string')
            for code, lname in LANG_LABEL:
                d = {'name': f'{n}_{code}', 'label': f'{lab} · {lname}', 'type': t}
                if f.get('rich'):
                    d['options'] = {'format': 'html', 'media': 'images'}
                if f.get('req') and code == 'th':
                    d['required'] = True
                if code == 'th':
                    _desc(d, f)
                out.append(d)
        elif k == 'str':
            d = {'name': n, 'label': lab, 'type': 'text' if f.get('long') else 'string'}
            if f.get('req'):
                d['required'] = True
            if f.get('readonly'):
                d['readonly'] = True
            out.append(_desc(d, f))
        elif k == 'num':
            out.append(_desc({'name': n, 'label': lab, 'type': 'number'}, f))
        elif k == 'bool':
            out.append(_desc({'name': n, 'label': lab, 'type': 'boolean'}, f))
        elif k == 'date':
            out.append(_desc({'name': n, 'label': lab, 'type': 'date', 'options': {'format': 'yyyy-MM-dd'}}, f))
        elif k == 'img':
            out.append(_desc({'name': n, 'label': lab, 'type': 'image', 'options': {'media': 'images'}}, f))
        elif k == 'vid':
            out.append(_desc({'name': n, 'label': lab, 'type': 'file', 'options': {'media': 'videos', 'extensions': ['mp4', 'webm']}}, f))
        elif k == 'doc':
            out.append(_desc({'name': n, 'label': lab, 'type': 'file', 'options': {'media': 'docs', 'extensions': ['pdf']}}, f))
        elif k == 'sel':
            vals = [{'name': v, 'label': l} for v, l in f['values']]
            out.append(_desc({'name': n, 'label': lab, 'type': 'select', 'options': {'values': vals}}, f))
        elif k == 'imgs':
            out.append(_desc({'name': n, 'label': lab, 'type': 'image', 'options': {'media': 'images', 'multiple': True}}, f))
        elif k == '3d':
            out.append(_desc({'name': n, 'label': lab, 'type': 'file', 'options': {'media': 'models3d', 'extensions': ['glb', 'gltf']}}, f))
        elif k == 'refs':
            out.append(_desc({'name': n, 'label': lab, 'type': 'reference',
                              'options': {'collection': f['collection'], 'value': '{path}', 'label': '{fields.model_name}',
                                          'search': 'model_name', 'multiple': True}}, f))
        elif k == 'ref':
            out.append(_desc({'name': n, 'label': lab, 'type': 'reference',
                              'options': {'collection': f['collection'], 'value': '{path}', 'label': '{fields.model_name}', 'search': 'model_name'}}, f))
        elif k == 'list':
            summary = f.get('summary') or _auto_summary(f['fields'])
            d = {'name': n, 'label': lab, 'type': 'object',
                 'list': {'collapsible': {'collapsed': True, 'summary': summary}},
                 'fields': cms_fields(f['fields'])}
            out.append(_desc(d, f))
        elif k == 'slist':
            out.append(_desc({'name': n, 'label': lab, 'type': 'string', 'list': True}, f))
        elif k == 'obj':
            out.append(_desc({'name': n, 'label': lab, 'type': 'object', 'fields': cms_fields(f['fields'])}, f))
        else:
            raise ValueError(k)
    return out


def _auto_summary(fields):
    for f in fields:
        if f['kind'] == 'tx':
            return '{' + f['name'] + '_th}'
    for f in fields:
        if f['kind'] in ('str', 'ref', 'sel'):
            return '{' + f['name'] + '}'
    return 'รายการที่ {index}'


# ---------------------------------------------------------------- checks
def keys_of(fields):
    out = {}
    for f in fields:
        if f['kind'] == 'tx':
            for code, _ in LANG_LABEL:
                out[f"{f['name']}_{code}"] = f
        else:
            out[f['name']] = f
    return out


def validate(fields, data, where):
    """Problems in data compared with the field list (unknown keys, wrong shapes)."""
    probs = []
    if not isinstance(data, dict):
        return [f'{where}: not an object']
    known = keys_of(fields)
    for k, v in data.items():
        f = known.get(k)
        if f is None:
            probs.append(f'{where}: "{k}" has no back-office field')
            continue
        kind = f['kind']
        if kind in ('list',):
            if not isinstance(v, list):
                probs.append(f'{where}.{k}: should be a list')
                continue
            for i, item in enumerate(v):
                probs += validate(f['fields'], item, f'{where}.{k}[{i}]')
        elif kind == 'obj':
            probs += validate(f['fields'], v, f'{where}.{k}')
        elif kind in ('slist', 'imgs', 'refs'):
            if v in (None, ''):
                continue
            if isinstance(v, str):
                continue
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                probs.append(f'{where}.{k}: should be a list of text')
        elif kind == '__never__':
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                probs.append(f'{where}.{k}: should be a list of text')
        elif kind == 'num':
            if v not in (None, '') and not isinstance(v, (int, float)):
                probs.append(f'{where}.{k}: should be a number')
        elif kind == 'bool':
            if not isinstance(v, bool):
                probs.append(f'{where}.{k}: should be true/false')
        elif kind == 'sel':
            if v not in ('', None) and v not in [x for x, _ in f['values']]:
                probs.append(f'{where}.{k}: "{v}" is not one of the choices')
        else:
            if v is not None and not isinstance(v, str):
                probs.append(f'{where}.{k}: should be text')
    return probs
