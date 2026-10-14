/* SUPERX AI website — language switch, navigation, video, copy buttons and the contact form */
(function () {
  'use strict';
  var LANGS = ['th', 'zh', 'en'];
  var root = document.documentElement;

  /* Where the contact form can send by itself:
     - Cloudflare (workers.dev, pages.dev, super-x.tech): POST /api/lead, which posts a card to the sales team's Lark group (worker.js)
     - Netlify: Netlify Forms
     Anywhere else (opened from a folder, a preview link) it shows the message to send by email. */
  var LEAD_API_HOSTS = [/\.pages\.dev$/i, /\.workers\.dev$/i, /(^|\.)super-x\.tech$/i, /^(localhost|127\.0\.0\.1)$/];
  var NETLIFY_HOSTS = [/\.netlify\.app$/i];

  /* Form and copy-button texts edited in the back office (contact page → messages), written into the page as JSON */
  var PAGE_MSGS = {};
  try {
    var msgEl = document.getElementById('form-msgs');
    if (msgEl) PAGE_MSGS = JSON.parse(msgEl.textContent) || {};
  } catch (e) { PAGE_MSGS = {}; }

  function store(key, val) {
    try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; }
    return null;
  }

  /* ---------- Language ---------- */
  function currentLang() {
    var l = root.getAttribute('data-lang');
    return LANGS.indexOf(l) > -1 ? l : 'th';
  }
  function applyLang(l) {
    root.setAttribute('data-lang', l);
    root.setAttribute('lang', l === 'zh' ? 'zh-CN' : l);
    var t = document.querySelector('meta[name="sx-title-' + l + '"]');
    if (t) document.title = t.getAttribute('content');
    document.querySelectorAll('[data-ph-' + l + ']').forEach(function (el) {
      el.setAttribute('placeholder', el.getAttribute('data-ph-' + l));
    });
    document.querySelectorAll('option[data-' + l + ']').forEach(function (el) {
      el.textContent = el.getAttribute('data-' + l);
    });
    document.querySelectorAll('[data-aria-' + l + ']').forEach(function (el) {
      el.setAttribute('aria-label', el.getAttribute('data-aria-' + l));
    });
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-set-lang') === l ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () {
      var l = b.getAttribute('data-set-lang');
      store('sx-lang', l);
      applyLang(l);
    });
  });
  applyLang(currentLang());

  /* ---------- Header ---------- */
  /* Over a film or photo hero the header is see-through; it turns solid once the page scrolls or the menu opens */
  var header = document.querySelector('.site-header');
  var menuBtn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  function onScroll() {
    if (!header) return;
    var y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 4);
    header.classList.toggle('is-solid', y > 40 || !!(nav && nav.classList.contains('is-open')));
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      onScroll();
    });
  }
  document.querySelectorAll('.nav-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.nav-item');
      var open = !item.classList.contains('is-open');
      document.querySelectorAll('.nav-item.is-open').forEach(function (i) { i.classList.remove('is-open'); i.querySelector('.nav-toggle').setAttribute('aria-expanded', 'false'); });
      if (open) { item.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item')) {
      document.querySelectorAll('.nav-item.is-open').forEach(function (i) { i.classList.remove('is-open'); i.querySelector('.nav-toggle').setAttribute('aria-expanded', 'false'); });
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-item.is-open').forEach(function (i) { i.classList.remove('is-open'); });
      if (nav && nav.classList.contains('is-open')) { nav.classList.remove('is-open'); if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false'); onScroll(); }
    }
  });

  /* ---------- Hero video ---------- */
  var video = document.querySelector('.hero-media video');
  var playBtn = document.querySelector('.play-btn');
  if (video) {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var setBtn = function () {
      if (!playBtn) return;
      var paused = video.paused;
      playBtn.querySelector('.i-pause').style.display = paused ? 'none' : '';
      playBtn.querySelector('.i-play').style.display = paused ? '' : 'none';
    };
    if (reduce) { video.removeAttribute('autoplay'); video.pause(); }
    else { var p = video.play(); if (p && p.catch) p.catch(function () { setBtn(); }); }
    video.addEventListener('play', setBtn);
    video.addEventListener('pause', setBtn);
    if (playBtn) playBtn.addEventListener('click', function () { if (video.paused) video.play(); else video.pause(); });
    setBtn();
  }

  var motionOK = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* ---------- Model line-up (home): tabs switch the van on show ---------- */
  document.querySelectorAll('.lineup-tabs').forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (!panel) return;
        panel.hidden = !on;
        if (on && motionOK) { panel.classList.remove('is-entering'); void panel.offsetWidth; panel.classList.add('is-entering'); }
      });
      if (focus) tab.focus();
      tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t, false); });
      t.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : null;
        if (n === null) return;
        e.preventDefault();
        select(tabs[(n + tabs.length) % tabs.length], true);
      });
    });
  });

  /* ---------- Card rows that slide sideways (home: applications) ---------- */
  document.querySelectorAll('[data-rail]').forEach(function (box) {
    var rail = box.querySelector('.rail');
    var prev = box.querySelector('.rail-btn.prev');
    var next = box.querySelector('.rail-btn.next');
    if (!rail) return;
    var step = function () {
      var card = rail.querySelector('.rail-card');
      return card ? card.getBoundingClientRect().width + 18 : 320;
    };
    var update = function () {
      if (prev) prev.disabled = rail.scrollLeft < 8;
      if (next) next.disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 8;
    };
    var go = function (dir) { rail.scrollBy({ left: dir * step(), behavior: motionOK ? 'smooth' : 'auto' }); };
    if (prev) prev.addEventListener('click', function () { go(-1); });
    if (next) next.addEventListener('click', function () { go(1); });
    rail.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---------- Numbers count up once when they come into view ---------- */
  function countUp(el) {
    var node = el.firstChild;
    if (!node || node.nodeType !== 3) return;
    var m = node.nodeValue.match(/^(\s*)([\d,]*\d)(\.\d+)?(.*)$/);
    if (!m) return;
    var end = parseFloat((m[2] + (m[3] || '')).replace(/,/g, ''));
    if (!(end > 0)) return;
    var decimals = m[3] ? m[3].length - 1 : 0;
    var commas = m[2].indexOf(',') > -1;
    var format = function (v) {
      var s = v.toFixed(decimals);
      if (commas) { var parts = s.split('.'); parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ','); s = parts.join('.'); }
      return m[1] + s + m[4];
    };
    var original = node.nodeValue, start = null, dur = 1400;
    var tick = function (ts) {
      if (start === null) start = ts;
      var p = Math.min(1, (ts - start) / dur);
      node.nodeValue = p < 1 ? format(end * (1 - Math.pow(1 - p, 3))) : original;
      if (p < 1) window.requestAnimationFrame(tick);
    };
    node.nodeValue = format(0);
    window.requestAnimationFrame(tick);
  }

  /* ---------- Gentle reveal of blocks below the first screen ---------- */
  if ('IntersectionObserver' in window && motionOK) {
    var counters = Array.prototype.slice.call(document.querySelectorAll('.stat b, .target b'));
    var blocks = Array.prototype.slice.call(document.querySelectorAll(
      'main .section-head, main .flow, main .stats, main .modules, main .lineup-nav, main .phones, main .rail, main .cases, ' +
      'main .features, main .split > *, main .case-detail, main .steps, main .vm, main .news-feature, main .news-list, main .contact-grid > *, ' +
      'main .thmap, main .spec-layout, main .gallery-grid, main .line, main .options, main .downloads, main .pcards, main .cta-inner, main .models2, main .uses, main .target, main .control-grid > *'
    )).filter(function (el) { return !el.closest('.hero, .phero') && el.getBoundingClientRect().top > window.innerHeight; });
    blocks.forEach(function (el) { el.classList.add('reveal'); });
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        seen.unobserve(en.target);
        if (en.target.classList.contains('reveal')) en.target.classList.add('is-in');
        else countUp(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    blocks.forEach(function (el) { seen.observe(el); });
    counters.forEach(function (el) { seen.observe(el); });
  }

  /* ---------- Light sections: background lines drift slower than the page ---------- */
  if (motionOK) {
    var mists = Array.prototype.slice.call(document.querySelectorAll('.section--mist'));
    var drift = function () {
      var vh = window.innerHeight;
      mists.forEach(function (s) {
        var r = s.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        s.style.setProperty('--drift', Math.round((r.top - vh / 2) * -0.15) + 'px');
      });
    };
    window.addEventListener('scroll', function () { window.requestAnimationFrame(drift); }, { passive: true });
    drift();
  }

  /* ---------- Cards tilt toward the mouse (computers with a mouse only) ---------- */
  if (motionOK && window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.pcard, .module, .rail-card, .case, .model-card').forEach(function (card) {
      card.classList.add('tilt');
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        card.classList.add('is-tilting');
        card.style.transform = 'perspective(900px) rotateX(' + (-y * 6).toFixed(2) + 'deg) rotateY(' + (x * 8).toFixed(2) + 'deg) translateY(-4px)';
      });
      card.addEventListener('pointerleave', function () { card.classList.remove('is-tilting'); card.style.transform = ''; });
    });
  }

  /* ---------- ROI calculator (roi.html) ---------- */
  var roi = document.querySelector('[data-roi]');
  var roiData = document.getElementById('roi-data');
  if (roi && roiData) {
    var R = {};
    try { R = JSON.parse(roiData.textContent) || {}; } catch (e) { R = {}; }
    var A = R.a || {};
    var val = function (k) { var el = document.getElementById('roi-' + k); var v = el ? parseFloat(el.value) : 0; return isFinite(v) && v > 0 ? v : 0; };
    var money = function (v) { return Math.round(v).toLocaleString('en-US'); };
    var put = function (id, text) { var el = document.getElementById(id); if (el) el.textContent = text; };
    var calc = function () {
      var trips = val('trips'), km = val('km'), drivers = val('drivers'), wage = val('wage'), days = val('days'), fuel = val('fuel');
      var dailyKm = trips * km, yearKm = dailyKm * days * 12;
      var vans = dailyKm > 0 ? Math.max(1, Math.ceil(dailyKm / Math.max(1, A.van_km_day || 150))) : 0;
      var current = drivers * wage * 12 + yearKm * fuel;
      var robovan = vans * (A.van_cost_month || 0) * 12 + yearKm * (A.energy_km || 0) + (vans ? (A.staff_month || 0) * 12 : 0);
      var saving = current - robovan;
      var pct = current > 0 ? Math.round(saving / current * 100) : 0;
      put('roi-r-saving', money(Math.max(0, saving)));
      put('roi-r-pct', Math.max(0, pct) + '%');
      put('roi-r-current', money(current)); put('roi-r-robovan', money(robovan));
      put('roi-r-vans', String(vans)); put('roi-r-km', money(yearKm));
      roi.classList.toggle('is-loss', saving <= 0 && current > 0);
      var tpl = (R.msg && (R.msg[currentLang()] || R.msg.th)) || '';
      var fill = { trips: trips, km: km, drivers: drivers, wage: money(wage), days: days, fuel: fuel, vans: vans,
                   current: money(current), robovan: money(robovan), saving: money(Math.max(0, saving)) };
      var text = tpl.replace(/\{(\w+)\}/g, function (m0, k) { return fill.hasOwnProperty(k) ? String(fill[k]) : m0; });
      var quote = document.getElementById('roi-quote');
      if (quote) quote.href = 'contact.html?topic=quote&qty=' + vans + '&msg=' + encodeURIComponent(text);
    };
    roi.addEventListener('input', calc);
    document.querySelectorAll('.lang button').forEach(function (b) { b.addEventListener('click', function () { setTimeout(calc, 0); }); });
    calc();
  }

  /* ---------- Model finder (choose.html) ---------- */
  var quiz = document.querySelector('[data-quiz]');
  if (quiz) {
    var groups = Array.prototype.slice.call(quiz.querySelectorAll('.quiz-q'));
    var out = quiz.querySelector('.quiz-out'), pending = quiz.querySelectorAll('.quiz-pending');
    var cards = Array.prototype.slice.call(quiz.querySelectorAll('.quiz-card'));
    var order = cards.map(function (c) { return c.getAttribute('data-model'); });
    var decide = function (scroll) {
      var picked = groups.map(function (g) { return g.querySelector('input:checked'); });
      var done = picked.every(Boolean);
      if (!done) { if (out) out.hidden = true; pending.forEach(function (p) { p.style.display = ''; }); return; }
      var score = {};
      picked.forEach(function (inp) {
        (inp.getAttribute('data-models') || '').split(' ').forEach(function (k) { if (k) score[k] = (score[k] || 0) + 1; });
      });
      var ranked = order.filter(function (k) { return score[k]; }).sort(function (a, b) { return (score[b] - score[a]) || (order.indexOf(a) - order.indexOf(b)); });
      var best = ranked[0];
      cards.forEach(function (c) { c.hidden = c.getAttribute('data-model') !== best; if (!c.hidden && motionOK) { c.classList.remove('is-entering'); void c.offsetWidth; c.classList.add('is-entering'); } });
      var also = quiz.querySelector('.quiz-also'), list = quiz.querySelector('.quiz-also-list');
      var others = ranked.slice(1).filter(function (k) { return score[k] === score[best]; }).slice(0, 3);
      if (list) {
        list.innerHTML = '';
        others.forEach(function (k) {
          var c = quiz.querySelector('.quiz-card[data-model="' + k + '"]'); if (!c) return;
          var a = document.createElement('a'); a.className = 'chip'; a.href = c.getAttribute('data-link'); a.textContent = c.getAttribute('data-name');
          list.appendChild(a);
        });
      }
      if (also) also.hidden = !others.length;
      if (out) out.hidden = !best;
      pending.forEach(function (p) { p.style.display = best ? 'none' : ''; });
      if (scroll && best && out) out.scrollIntoView({ behavior: motionOK ? 'smooth' : 'auto', block: 'start' });
    };
    quiz.addEventListener('change', function () { decide(true); });
    var reset = quiz.querySelector('[data-quiz-reset]');
    if (reset) reset.addEventListener('click', function () {
      quiz.querySelectorAll('input:checked').forEach(function (i) { i.checked = false; });
      decide(false);
      quiz.scrollIntoView({ behavior: motionOK ? 'smooth' : 'auto', block: 'start' });
    });
    decide(false);
  }

  /* ---------- 360° view: drag (or arrow keys) to turn the van ---------- */
  document.querySelectorAll('.spin[data-frames]').forEach(function (box) {
    var frames = [];
    try { frames = JSON.parse(box.getAttribute('data-frames')) || []; } catch (e) { frames = []; }
    var pic = box.querySelector('img');
    if (frames.length < 2 || !pic) return;
    var cache = [], idx = 0, loaded = false;
    var load = function () { if (loaded) return; loaded = true; frames.forEach(function (src, i) { var im = new Image(); im.decoding = 'async'; im.src = src; cache[i] = im; }); };
    var show = function (i) { idx = (i % frames.length + frames.length) % frames.length; pic.src = frames[idx]; };
    var startX = 0, startIdx = 0, dragging = false;
    box.addEventListener('pointerdown', function (e) { load(); dragging = true; startX = e.clientX; startIdx = idx; box.classList.add('is-dragging'); box.setPointerCapture(e.pointerId); });
    box.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var step = Math.max(4, box.clientWidth / frames.length / 1.2);
      show(startIdx - Math.round((e.clientX - startX) / step));
    });
    var stop = function () { dragging = false; box.classList.remove('is-dragging'); };
    box.addEventListener('pointerup', stop); box.addEventListener('pointercancel', stop);
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); load(); show(idx + (e.key === 'ArrowRight' ? 1 : -1)); }
    });
    if ('IntersectionObserver' in window) {
      var seenSpin = new IntersectionObserver(function (en) {
        if (!en[0].isIntersecting) return;
        seenSpin.disconnect(); load();
        if (!motionOK) return;
        var n = 0, timer = setInterval(function () { if (dragging || ++n > frames.length) { clearInterval(timer); return; } show(idx + 1); }, 90);
      });
      seenSpin.observe(box);
    }
  });

  /* ---------- Section nav highlight (model pages) ---------- */
  var subLinks = Array.prototype.slice.call(document.querySelectorAll('.subnav a[href^="#"]'));
  if (subLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    subLinks.forEach(function (a) { var s = document.getElementById(a.getAttribute('href').slice(1)); if (s) map[s.id] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          subLinks.forEach(function (a) { a.classList.remove('is-active'); });
          map[en.target.id].classList.add('is-active');
        }
      });
    }, { rootMargin: '-35% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
  }

  /* ---------- Copy buttons ---------- */
  function copyText(text, btn) {
    var done = function () {
      var label = btn.querySelector('.copy-label');
      if (!label) return;
      var old = label.innerHTML;
      var copied = PAGE_MSGS.copied || { th: 'คัดลอกแล้ว', zh: '已复制', en: 'Copied' };
      label.textContent = copied[currentLang()] || copied.th || '';
      setTimeout(function () { label.innerHTML = old; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackSelect(btn); });
    } else { fallbackSelect(btn); }
  }
  function fallbackSelect(btn) {
    var target = btn.getAttribute('data-copy-target');
    var el = target ? document.querySelector(target) : btn.parentElement.querySelector('.value');
    if (!el) return;
    if (el.select) { el.focus(); el.select(); return; }
    var r = document.createRange(); r.selectNodeContents(el);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-copy], [data-copy-target]');
    if (!btn) return;
    var text = btn.getAttribute('data-copy');
    if (!text) { var t = document.querySelector(btn.getAttribute('data-copy-target')); text = t ? (t.value || t.textContent) : ''; }
    copyText(text, btn);
  });

  /* ---------- Contact form ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    var params;
    try { params = new URLSearchParams(window.location.search); } catch (e) { params = null; }
    if (params) {
      var setSel = function (id, val) {
        var s = document.getElementById(id); if (!s || !val) return;
        for (var i = 0; i < s.options.length; i++) { if (s.options[i].value === val) { s.value = val; break; } }
      };
      setSel('f-interest', params.get('topic'));
      setSel('f-model', params.get('model'));
      /* Filled in from the ROI calculator */
      var qty = params.get('qty'), msg = params.get('msg');
      var qtyEl = document.getElementById('f-qty'), msgEl = document.getElementById('f-message');
      if (qtyEl && qty && /^\d{1,4}$/.test(qty)) qtyEl.value = qty;
      if (msgEl && msg && !msgEl.value) msgEl.value = msg.slice(0, 1500);
    }
    var result = document.getElementById('form-result');
    var statusLine = document.getElementById('form-status');
    var msgs = {
      sending: { th: 'กำลังส่งข้อมูล…', zh: '正在提交…', en: 'Sending…' },
      okTitle: { th: 'ได้รับข้อมูลแล้ว ขอบคุณครับ', zh: '已收到您的信息，谢谢！', en: 'Thank you. We have your message.' },
      okBody: { th: 'ทีมงาน SuperX AI จะติดต่อกลับโดยเร็วที่สุด', zh: 'SuperX AI 团队会尽快与您联系。', en: 'The SuperX AI team will be in touch soon.' },
      offTitle: { th: 'ส่งข้อความนี้ถึงเราทางอีเมลหรือ LINE', zh: '请通过邮件发送以下信息', en: 'Send this message to us by email' },
      offBody: { th: 'แบบฟอร์มจะส่งอัตโนมัติเมื่อเว็บไซต์ออนไลน์แล้ว ระหว่างนี้กดคัดลอกข้อความด้านล่าง แล้วส่งไปที่ info@super-x.tech หรือโทร 02-323-2800', zh: '网站正式上线后表单将自动提交。目前请复制以下内容发送至 info@super-x.tech，或致电 02-323-2800。', en: 'The form submits automatically once the site is online. For now, copy the message below and send it to info@super-x.tech, or call 02-323-2800.' },
      failTitle: { th: 'ส่งอัตโนมัติไม่สำเร็จ', zh: '自动提交未成功', en: 'We couldn’t send this automatically' },
      failBody: { th: 'ขออภัย ระบบส่งข้อมูลขัดข้อง กรุณากดคัดลอกข้อความด้านล่าง แล้วส่งไปที่ info@super-x.tech หรือโทร 02-323-2800', zh: '抱歉，系统暂时无法提交。请复制以下内容发送至 info@super-x.tech，或致电 02-323-2800。', en: 'Sorry, something went wrong. Please copy the message below and send it to info@super-x.tech, or call 02-323-2800.' },
      copy: { th: 'คัดลอกข้อความ', zh: '复制内容', en: 'Copy message' },
      mail: { th: 'เปิดอีเมล', zh: '打开邮件', en: 'Open email' }
    };
    Object.keys(msgs).forEach(function (k) {
      var v = PAGE_MSGS[k];
      if (v && typeof v === 'object') msgs[k] = { th: v.th || msgs[k].th, zh: v.zh || v.en || msgs[k].zh, en: v.en || v.th || msgs[k].en };
    });
    var mailTo = typeof PAGE_MSGS.email === 'string' && PAGE_MSGS.email ? PAGE_MSGS.email : 'info@super-x.tech';
    var tr = function (k) { return msgs[k][currentLang()]; };
    var labelOf = function (el) {
      var lab = form.querySelector('label[for="' + el.id + '"] [data-l="' + currentLang() + '"]');
      return lab ? lab.textContent.replace(/\s*\*$/, '') : el.name;
    };
    var compose = function () {
      var lines = [];
      form.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (!el.id || el.type === 'hidden' || el.type === 'checkbox' || el.closest('.hp')) return;
        var v = el.tagName === 'SELECT' ? (el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : '') : el.value;
        if (v) lines.push(labelOf(el) + ': ' + v);
      });
      return lines.join('\n');
    };
    var showOffline = function (failed) {
      var text = compose();
      var subject = 'SuperX AI website enquiry';
      result.className = 'form-result';
      result.innerHTML = '<h3></h3><p></p><textarea id="form-copy" readonly></textarea>' +
        '<div class="btn-row"><button type="button" class="btn btn-primary btn-sm" data-copy-target="#form-copy"><span class="copy-label"></span></button>' +
        '<a class="btn btn-outline btn-sm" id="form-mail"></a></div>';
      result.querySelector('h3').textContent = tr(failed ? 'failTitle' : 'offTitle');
      result.querySelector('p').textContent = tr(failed ? 'failBody' : 'offBody');
      result.querySelector('textarea').value = text;
      result.querySelector('.copy-label').textContent = tr('copy');
      var mail = result.querySelector('#form-mail');
      mail.textContent = tr('mail');
      mail.href = 'mailto:' + mailTo + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      result.hidden = false;
      statusLine.textContent = '';
    };
    var showOk = function () {
      result.className = 'form-result ok';
      result.innerHTML = '<h3></h3><p></p>';
      result.querySelector('h3').textContent = tr('okTitle');
      result.querySelector('p').textContent = tr('okBody');
      result.hidden = false;
      statusLine.textContent = '';
      form.reset();
    };
    var submitBtn = form.querySelector('button[type="submit"]');
    var busy = false;
    var onHost = function (list) {
      return window.location.protocol.indexOf('http') === 0 && list.some(function (re) { return re.test(window.location.hostname); });
    };
    var cameFrom = function () {
      try { var r = new URL(document.referrer); return r.host === window.location.host ? r.pathname : ''; } catch (e) { return ''; }
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return;
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var viaApi = onHost(LEAD_API_HOSTS), viaNetlifyHost = onHost(NETLIFY_HOSTS);
      if (!viaApi && !viaNetlifyHost) { showOffline(false); return; }
      busy = true;
      if (submitBtn) submitBtn.disabled = true;
      statusLine.textContent = tr('sending');
      var finish = function (ok) {
        busy = false;
        if (submitBtn) submitBtn.disabled = false;
        if (ok) showOk(); else showOffline(true);
      };
      var fd = new FormData(form);
      var netlify = function () {
        return fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(fd).toString() })
          .then(function (r) { return r.ok; });
      };
      if (!viaApi) { netlify().then(finish, function () { finish(false); }); return; }
      var data = {};
      fd.forEach(function (v, k) { if (typeof v === 'string') data[k] = v; });
      data.lang = currentLang();
      data.from = cameFrom();
      fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) {
          if (r.status === 404 || r.status === 405) return netlify(); // site is hosted without _worker.js
          return r.json().then(function (j) { return !!(j && j.ok); }, function () { return false; });
        })
        .then(finish, function () { finish(false); });
    });
  }
  /* ---------- Background videos on sections (🎬 in the back office) ---------- */
  // A film is downloaded only when its section comes near the screen, plays only while it is on screen,
  // and stays still for people who ask for less motion or for data saving (they can press play).
  var bgSecs = document.querySelectorAll('.has-bgv');
  if (bgSecs.length) {
    var bgCalm = (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) ||
      !!(navigator.connection && navigator.connection.saveData);
    Array.prototype.forEach.call(bgSecs, function (sec) {
      var v = sec.querySelector('.bgv video');
      if (!v) return;
      var btn = sec.querySelector('.bgv-btn');
      var stopped = bgCalm;
      var showBtn = function () { if (btn) btn.classList.toggle('is-paused', stopped || v.paused); };
      var start = function () {
        if (!v.getAttribute('src')) v.setAttribute('src', v.getAttribute('data-src') || '');
        var p = v.play();
        if (p && p.catch) p.catch(function () { showBtn(); });
      };
      v.addEventListener('playing', function () { sec.classList.add('bgv-on'); showBtn(); });
      if (btn) {
        btn.hidden = false;
        btn.classList.toggle('is-paused', stopped);
        btn.addEventListener('click', function () {
          stopped = !v.paused;
          if (stopped) v.pause(); else start();
          btn.classList.toggle('is-paused', stopped);
        });
      }
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) { if (!stopped) start(); } else if (!v.paused) v.pause();
          });
        }, { rootMargin: '200px 0px' }).observe(sec);
      } else if (!stopped) start();
    });
  }
  /* ---------- Chat pictures play like a real conversation ---------- */
  // The customer writes first, the AI Agent shows "typing…" and then answers; the chat repeats while on screen.
  if (motionOK) {
    Array.prototype.forEach.call(document.querySelectorAll('.chat-art'), function (art) {
      var bubbles = Array.prototype.slice.call(art.querySelectorAll('.bubble'));
      if (bubbles.length < 2) return;
      var typing = document.createElement('div');
      typing.className = 'chat-typing';
      typing.setAttribute('aria-hidden', 'true');
      typing.innerHTML = '<i></i><i></i><i></i>';
      art.appendChild(typing);
      art.classList.add('is-anim');
      var timer = null, step = 0, visible = false;
      var later = function (fn, ms) { timer = setTimeout(fn, ms); };
      var next = function () {
        if (!visible) return;
        if (step >= bubbles.length) {
          later(function () {
            art.classList.add('is-fading');
            later(function () {
              bubbles.forEach(function (b) { b.classList.remove('is-on'); });
              art.classList.remove('is-fading');
              step = 0;
              later(next, 500);
            }, 700);
          }, 4000);
          return;
        }
        var b = bubbles[step];
        if (b.classList.contains('ai')) {
          typing.style.left = b.offsetLeft + 'px';
          typing.style.top = b.offsetTop + 'px';
          typing.classList.add('is-on');
          later(function () {
            typing.classList.remove('is-on');
            b.classList.add('is-on');
            step++;
            later(next, 1100);
          }, 1300);
        } else {
          b.classList.add('is-on');
          step++;
          later(next, 900);
        }
      };
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting && !visible) { visible = true; later(next, 400); }
            else if (!e.isIntersecting && visible) { visible = false; clearTimeout(timer); typing.classList.remove('is-on'); }
          });
        }, { threshold: 0.3 }).observe(art);
      } else {
        bubbles.forEach(function (b) { b.classList.add('is-on'); });
      }
    });
  }
  /* ---------- App screens: float, and light up one phone at a time ---------- */
  if (motionOK) {
    Array.prototype.forEach.call(document.querySelectorAll('.phones'), function (box) {
      var cards = Array.prototype.slice.call(box.querySelectorAll('.phone-card'));
      if (cards.length < 2) return;
      box.classList.add('is-alive');
      var i = -1, timer = null, hold = false;
      var show = function (n) {
        cards.forEach(function (c, k) { c.classList.toggle('is-focus', k === n); });
        box.classList.add('has-focus');
      };
      var stepOn = function () { if (!hold) { i = (i + 1) % cards.length; show(i); } };
      var start = function () { if (!timer) { stepOn(); timer = setInterval(stepOn, 3000); } };
      var stop = function () { clearInterval(timer); timer = null; };
      cards.forEach(function (c, k) {
        c.addEventListener('mouseenter', function () { hold = true; i = k; show(k); });
        c.addEventListener('mouseleave', function () { hold = false; });
      });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          entries.forEach(function (e) { if (e.isIntersecting) setTimeout(start, 1400); else stop(); });
        }, { threshold: 0.35 }).observe(box);
      } else start();
    });
  }
  /* ---------- Thailand map: pointing at a zone lights up its pin and its row ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-thmap]'), function (map) {
    var hot = function (n, on) {
      Array.prototype.forEach.call(map.querySelectorAll('[data-pin="' + n + '"]'), function (el) { el.classList.toggle('is-hot', on); });
    };
    Array.prototype.forEach.call(map.querySelectorAll('[data-pin]'), function (el) {
      var n = el.getAttribute('data-pin');
      el.addEventListener('mouseenter', function () { hot(n, true); });
      el.addEventListener('mouseleave', function () { hot(n, false); });
    });
  });
})();
