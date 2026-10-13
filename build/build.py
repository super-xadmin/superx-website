# -*- coding: utf-8 -*-
"""Build the SUPERX AI website from content/ into public/.

Cloudflare runs this automatically before every deploy (see wrangler.jsonc):
    python3 build/build.py
Options:
    --check   only check content files against the back-office fields
    --cms     also rewrite .pages.yml (needs PyYAML; run on a computer, not on Cloudflare)
"""
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
import pages  # noqa: E402

OUT = os.path.join(core.ROOT, 'public')
MAX_ASSET = 25 * 1024 * 1024   # Cloudflare serves files up to 25 MiB each
SKIP_NAMES = {'.DS_Store', 'Thumbs.db', 'desktop.ini', '.gitkeep'}


def absolutize(html):
    """Pages served at any address (404) need root-relative links."""
    html = re.sub(r'(\s(?:href|src|poster)=")(?!https?:|#|/|mailto:|tel:|data:)', r'\1/', html)
    return html.replace('content="assets/', 'content="/assets/')


def copy_assets(out):
    """Copy assets/ to public/assets/, leaving out system files and files too big for Cloudflare."""
    warnings = []
    for folder, _dirs, files in os.walk(core.ASSETS):
        rel = os.path.relpath(folder, core.ROOT)
        os.makedirs(os.path.join(out, rel), exist_ok=True)
        for fn in files:
            if fn in SKIP_NAMES or fn.startswith('._'):
                continue
            src = os.path.join(folder, fn)
            size = os.path.getsize(src)
            if size > MAX_ASSET:
                warnings.append(f'{rel}/{fn} is {size / 1048576:.0f} MB, over the 25 MB limit: left out of the website')
                continue
            shutil.copy2(src, os.path.join(out, rel, fn))
    return warnings


def build(out=OUT):
    t0 = time.time()
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for w in copy_assets(out):
        print('WARNING:', w)
    n = 0
    for fname, html in pages.render_all():
        if fname == '404.html':
            html = absolutize(html)
        with open(os.path.join(out, fname), 'w', encoding='utf-8') as f:
            f.write(html)
        n += 1
    with open(os.path.join(core.ROOT, 'worker-data.json'), 'w', encoding='utf-8') as f:
        json.dump(pages.worker_data(), f, ensure_ascii=False, indent=1)
    print(f'built {n} pages into {os.path.relpath(out, core.ROOT)}/ in {time.time() - t0:.1f}s')


if __name__ == '__main__':
    probs = pages.check()
    for p in probs:
        print('WARNING:', p)
    if '--check' in sys.argv:
        sys.exit(1 if probs else 0)
    if '--cms' in sys.argv:
        pages.write_cms()
    build()
