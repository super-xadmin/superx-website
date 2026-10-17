# -*- coding: utf-8 -*-
"""Page registry: which pages exist, their back-office menus, and checks."""
import os

import core
from core import C, collection, s, items, tri
from schema import cms_fields, validate, BG
import layout
import p_home
import promo
import chat

PAGE_MODULES = [p_home]
COLLECTIONS = []   # filled below: (name, label, folder, fields, view)


def _try(name):
    try:
        return __import__(name)
    except ImportError:
        return None


for _n in ('p_products', 'p_models', 'p_solutions', 'p_tools', 'p_about', 'p_cases', 'p_news', 'p_contact', 'p_404'):
    _m = _try(_n)
    if _m is not None:
        PAGE_MODULES += getattr(_m, 'MODULES', [_m])
        COLLECTIONS += getattr(_m, 'COLLECTIONS', [])

import p_business  # noqa: E402
COLLECTIONS += p_business.COLLECTIONS
COLLECTIONS.insert(0, ('models', '🚐 ข้อมูลรถแต่ละรุ่น (สเปก / การ์ด / ตาราง)', 'models', layout.MODEL_FIELDS,
                       {'fields': ['model_name', 'full_name'], 'primary': 'model_name'}))


def section_fields(m, key, fields):
    """Fields of one page section; sections listed in the page's BG_KEYS also get the 🎬 background video group."""
    if key in getattr(m, 'BG_KEYS', ()):
        return list(fields) + [BG()]
    return fields


def render_all():
    for m in PAGE_MODULES:
        html = m.render()
        if html is not None:   # pages switched off in the back office are not made
            yield m.FILE, html
        for extra in getattr(m, 'extra_pages', lambda: [])():
            yield extra
    for extra in p_business.extra_pages():
        yield extra


def worker_data():
    """Data the form sender (worker.js) needs: enquiry topics and models from the contact form, company email and phone."""
    f = C('pages/contact/form')
    topics = [{'value': s(o, 'value'), 'th': tri(o, 'label')[0], 'zh': tri(o, 'label')[1], 'en': tri(o, 'label')[2],
               'icon': s(o, 'lark_icon') or '💬', 'color': s(o, 'lark_color') or 'wathet'} for o in items(f, 'interests')]
    models = [s(o, 'value') for o in items(f, 'models') if s(o, 'value')]
    co = C('site/company')
    return {'topics': topics, 'models': models, 'contact': {'email': s(co, 'email'), 'phone': s(co, 'phone')}}


def check():
    probs = []
    for rel, _label, fields in layout.SITE_FILES:
        probs += validate(fields, C(rel), rel)
    probs += validate(promo.FIELDS, C(promo.REL), promo.REL)
    probs += validate(chat.FIELDS, C(chat.REL), chat.REL)
    for m in PAGE_MODULES:
        for key, _label, fields in m.SECTIONS:
            rel = f'{m.DIR}/{key}'
            if not os.path.exists(os.path.join(core.CONTENT, rel + '.json')):
                probs.append(f'{rel}: file missing')
            probs += validate(section_fields(m, key, fields), C(rel), rel)
    for name, _label, folder, fields, _view in COLLECTIONS:
        for slug, d in collection(folder):
            probs += validate(fields, d, f'{folder}/{slug}')
    return probs


def _file_entry(name, label, rel, fields):
    return {'name': name, 'label': label, 'type': 'file', 'path': f'content/{rel}.json', 'format': 'json', 'fields': cms_fields(fields)}


def cms_config():
    site = {'name': 'site', 'label': '⚙️ ตั้งค่าทั้งเว็บไซต์', 'type': 'group',
            'items': [_file_entry(rel.replace('/', '-'), label, rel, fields) for rel, label, fields in layout.SITE_FILES]}
    cols = []
    for name, label, folder, fields, view in COLLECTIONS:
        e = {'name': name, 'label': label, 'type': 'collection', 'path': f'content/{folder}', 'format': 'json',
             'fields': cms_fields(fields)}
        if view:
            e['view'] = view
        if name == 'news':
            e['filename'] = '{year}-{month}-{day}-{hour}{minute}{second}.json'
        elif name == 'business':
            e['filename'] = '{page}.json'
            e['exclude'] = ['.gitkeep']
        elif name == 'cases':
            e['filename'] = '{anchor}.json'
        elif name == 'models':
            e['filename'] = '{model_name}.json'
        cols.append(e)
    page_groups = []
    for m in PAGE_MODULES:
        base = m.DIR.split('/')[-1]
        page_groups.append({'name': f'page-{base}', 'label': m.LABEL, 'type': 'group',
                            'items': [_file_entry(f'{base}-{key}', label, f'{m.DIR}/{key}', section_fields(m, key, fields))
                                      for key, label, fields in m.SECTIONS]})
    pages_group = {'name': 'pages', 'label': '📄 หน้าเว็บ (แก้ทีละหัวข้อ)', 'type': 'group', 'items': page_groups}
    popup = _file_entry('popup', promo.LABEL, promo.REL, promo.FIELDS)
    chatbox = _file_entry('chat', chat.LABEL, chat.REL, chat.FIELDS)
    return {
        'media': [
            {'name': 'images', 'label': 'รูปภาพ', 'input': 'assets/img', 'output': '/assets/img',
             'extensions': ['jpg', 'jpeg', 'png', 'webp', 'gif', 'svg', 'avif']},
            {'name': 'videos', 'label': 'วิดีโอ', 'input': 'assets/video', 'output': '/assets/video', 'extensions': ['mp4', 'webm']},
            {'name': 'docs', 'label': 'ไฟล์ PDF / โบรชัวร์', 'input': 'assets/docs', 'output': '/assets/docs', 'extensions': ['pdf']},
            {'name': 'models3d', 'label': 'ไฟล์ 3D (.glb)', 'input': 'assets/3d', 'output': '/assets/3d', 'extensions': ['glb', 'gltf']},
        ],
        # most used first: news and the pop-up / promotion, then pages, projects, vehicle data, site settings
        'content': [c for c in cols if c['name'] == 'news'] + [popup, chatbox, pages_group] + [c for c in cols if c['name'] == 'business'] + [c for c in cols if c['name'] == 'cases']
                   + [c for c in cols if c['name'] not in ('news', 'cases', 'business')] + [site],
    }


def write_cms():
    import yaml

    class _Dumper(yaml.SafeDumper):
        pass

    def _str(dumper, data):
        style = '|' if '\n' in data else None
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)
    _Dumper.add_representer(str, _str)
    text = ('# Back-office settings for Pages CMS (https://app.pagescms.org).\n'
            '# This file is generated by build/build.py --cms. Edit the field lists in build/*.py, not here.\n')
    text += yaml.dump(cms_config(), Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=200)
    with open(os.path.join(core.ROOT, '.pages.yml'), 'w', encoding='utf-8') as f:
        f.write(text)
    print('wrote .pages.yml')
