/*
 * SUPERX AI website: live chat between visitors and the sales team, answered in Lark.
 *
 * How it works
 *   1. A visitor opens the chat box (💬 bottom right), gives name + phone, and writes.
 *   2. A bot posts a card for that visitor in the team's Lark group; every message the visitor sends
 *      is added as a reply in the card's thread.
 *   3. Anyone in the group answers inside that thread. The answer shows up in the visitor's chat box
 *      within a few seconds (the page asks for new messages every few seconds while the box is open).
 *      Replies that start with // stay inside Lark (notes for the team).
 *
 * Everything is kept in one Durable Object (ChatHub, SQLite storage on Cloudflare): conversations,
 * messages, the Lark group, a short-lived Lark token and simple rate limits. Conversations older than
 * 90 days are deleted.
 *
 * Settings: Cloudflare > Workers & Pages > superx-website > Settings > Variables and Secrets (type Secret)
 *   LARK_APP_ID, LARK_APP_SECRET   the Lark app with a bot (see README 8.1)
 *   LARK_VERIFICATION_TOKEN        Lark app > Events & Callbacks > Encryption strategy > Verification Token
 *   LARK_ENCRYPT_KEY               optional, only if an Encrypt Key is set there too
 *   LARK_CHAT_ID                   optional: the group's chat_id. Without it, the first group the bot is
 *                                  added to is used (the bot says so in that group).
 *   LARK_API_BASE                  optional, default https://open.larksuite.com (Feishu: https://open.feishu.cn)
 *
 * Addresses (all under /api/chat/)
 *   POST start   {name, phone, text, lang, from, consent}   -> {ok, id, token, messages}
 *   POST send    {id, token, text}                          -> {ok, messages}
 *   GET  poll?id=&after=   header X-Chat-Token              -> {ok, messages}
 *   POST lark    events from Lark (URL verification, new messages in the group, bot added to a group)
 */

const KEEP_DAYS = 90;
const MAX_TEXT = 1000;
const MAX_BODY = 16 * 1024;
const TIMEOUT_MS = 10000;
const LANGS = { th: 'ไทย', zh: '中文', en: 'English' };

/* ---------- Worker side: checks, then hand over to the Durable Object ---------- */

export async function handleChat(request, env, url) {
  const path = url.pathname.replace(/\/+$/, '');
  if (!env.CHAT) return json(503, { ok: false, error: 'not_configured' });
  const hub = env.CHAT.get(env.CHAT.idFromName('hub'));

  if (path === '/api/chat/lark') {
    if (request.method !== 'POST') return json(405, { ok: false });
    return hub.fetch(request);
  }
  const route = { '/api/chat/start': 'POST', '/api/chat/send': 'POST', '/api/chat/poll': 'GET' }[path];
  if (!route) return json(404, { ok: false, error: 'not_found' });
  if (request.method !== route) return json(405, { ok: false, error: 'method_not_allowed' });
  // Only this website may use the chat.
  const origin = request.headers.get('Origin');
  if (origin && !sameHost(origin, request.url)) return json(403, { ok: false, error: 'forbidden' });
  if (route === 'POST') {
    const declared = Number(request.headers.get('Content-Length') || 0);
    if (declared > MAX_BODY) return json(413, { ok: false, error: 'too_large' });
  }
  return hub.fetch(request);
}

/* ---------- Durable Object ---------- */

export class ChatHub {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS conv (
      id TEXT PRIMARY KEY, token TEXT, name TEXT, phone TEXT, lang TEXT, page TEXT,
      root TEXT, created INTEGER, updated INTEGER)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS msg (
      seq INTEGER PRIMARY KEY AUTOINCREMENT, conv TEXT, who TEXT, text TEXT, at INTEGER, lark TEXT)`);
    this.sql.exec('CREATE INDEX IF NOT EXISTS msg_conv ON msg (conv, seq)');
    this.sql.exec('CREATE INDEX IF NOT EXISTS conv_root ON conv (root)');
    this.sql.exec('CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT, until INTEGER)');
  }

  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '');
    try {
      if (path === '/api/chat/lark') return await this.larkEvent(request);
      if (path === '/api/chat/poll') return this.poll(request, url);
      const body = await readJson(request);
      if (!body) return json(400, { ok: false, error: 'bad_request' });
      if (path === '/api/chat/start') return await this.start(request, body);
      if (path === '/api/chat/send') return await this.send(body);
      return json(404, { ok: false, error: 'not_found' });
    } catch (err) {
      console.error('chat: unexpected error', err && err.stack ? err.stack : err);
      return json(500, { ok: false, error: 'server_error' });
    }
  }

  // Once a day: forget old conversations.
  async alarm() {
    const cut = Date.now() - KEEP_DAYS * 864e5;
    const old = [...this.sql.exec('SELECT id FROM conv WHERE updated < ?', cut)].map((r) => r.id);
    for (const id of old) {
      this.sql.exec('DELETE FROM msg WHERE conv = ?', id);
      this.sql.exec('DELETE FROM conv WHERE id = ?', id);
    }
    this.sql.exec('DELETE FROM kv WHERE until IS NOT NULL AND until < ?', Date.now());
    await this.ctx.storage.setAlarm(Date.now() + 864e5);
  }

  /* --- visitor side --- */

  async start(request, b) {
    if (str(b.website)) return json(200, { ok: true, id: '', token: '', messages: [] }); // spam robot
    const name = one(b.name, 80);
    const phone = one(b.phone, 30);
    const text = multi(b.text, MAX_TEXT);
    const lang = LANGS[b.lang] ? b.lang : 'th';
    const from = one(b.from, 100);
    const missing = [];
    if (!name) missing.push('name');
    if ((phone.match(/\d/g) || []).length < 9) missing.push('phone');
    if (!text) missing.push('text');
    if (b.consent !== true) missing.push('consent');
    if (missing.length) return json(400, { ok: false, error: 'invalid', fields: missing });

    const ip = request.headers.get('CF-Connecting-IP') || 'local';
    if (!this.allow(`start:${ip}`, 10, 3600e3)) return json(429, { ok: false, error: 'too_many' });

    const chat = await this.chatId();
    if (!chat || !this.ready()) return json(503, { ok: false, error: 'not_configured' });

    const id = randomId(16);
    const token = randomId(24);
    const now = Date.now();
    const page = /^\/[\w\-./%]*$/.test(from) ? from : '';
    const sent = await this.lark('POST', '/open-apis/im/v1/messages?receive_id_type=chat_id', {
      receive_id: chat, msg_type: 'interactive', content: JSON.stringify(card({ name, phone, lang, page })),
    });
    if (!sent.ok) {
      console.error('chat: could not post the card', sent.code, sent.msg);
      return json(502, { ok: false, error: 'lark_failed' });
    }
    this.sql.exec('INSERT INTO conv (id, token, name, phone, lang, page, root, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      id, token, name, phone, lang, page, sent.data.message_id, now, now);
    await this.ensureAlarm();
    const ok = await this.fromVisitor(id, sent.data.message_id, text);
    if (!ok) return json(502, { ok: false, error: 'lark_failed' });
    return json(200, { ok: true, id, token, messages: this.since(id, 0) });
  }

  async send(b) {
    const c = this.conv(str(b.id), str(b.token));
    if (!c) return json(403, { ok: false, error: 'unknown_chat' });
    const text = multi(b.text, MAX_TEXT);
    if (!text) return json(400, { ok: false, error: 'invalid', fields: ['text'] });
    if (!this.allow(`send:${c.id}`, 30, 600e3)) return json(429, { ok: false, error: 'too_many' });
    const ok = await this.fromVisitor(c.id, c.root, text);
    if (!ok) return json(502, { ok: false, error: 'lark_failed' });
    const after = Number(b.after) || 0;
    return json(200, { ok: true, messages: this.since(c.id, after) });
  }

  poll(request, url) {
    const c = this.conv(str(url.searchParams.get('id')), str(request.headers.get('X-Chat-Token')));
    if (!c) return json(403, { ok: false, error: 'unknown_chat' });
    return json(200, { ok: true, messages: this.since(c.id, Number(url.searchParams.get('after')) || 0) });
  }

  async fromVisitor(id, root, text) {
    const r = await this.lark('POST', `/open-apis/im/v1/messages/${encodeURIComponent(root)}/reply`, {
      msg_type: 'text', content: JSON.stringify({ text: `💬 ลูกค้า · 客户: ${safeText(text)}` }), reply_in_thread: true,
    });
    if (!r.ok) {
      console.error('chat: could not post the message', r.code, r.msg);
      return false;
    }
    const now = Date.now();
    this.sql.exec('INSERT INTO msg (conv, who, text, at, lark) VALUES (?, ?, ?, ?, ?)', id, 'me', text, now, r.data.message_id || '');
    this.sql.exec('UPDATE conv SET updated = ? WHERE id = ?', now, id);
    return true;
  }

  conv(id, token) {
    if (!/^[\w-]{10,64}$/.test(id) || !token) return null;
    const row = [...this.sql.exec('SELECT * FROM conv WHERE id = ?', id)][0];
    return row && safeEqual(row.token, token) ? row : null;
  }

  since(id, after) {
    return [...this.sql.exec('SELECT seq, who, text, at FROM msg WHERE conv = ? AND seq > ? ORDER BY seq LIMIT 200', id, after)]
      .map((r) => ({ seq: r.seq, who: r.who, text: r.text, at: r.at }));
  }

  /* --- Lark side --- */

  async larkEvent(request) {
    const raw = await request.text();
    if (raw.length > 256 * 1024) return json(413, { ok: false });
    let body;
    try { body = JSON.parse(raw); } catch (e) { return json(400, { ok: false }); }
    const encryptKey = str(this.env.LARK_ENCRYPT_KEY).trim();
    if (body && body.encrypt) {
      if (!encryptKey) return json(400, { ok: false });
      try { body = JSON.parse(await decrypt(body.encrypt, encryptKey)); } catch (e) { return json(400, { ok: false }); }
    }
    const want = str(this.env.LARK_VERIFICATION_TOKEN).trim();
    const got = str(body.token || (body.header && body.header.token));
    if (!want || !safeEqual(want, got)) return json(403, { ok: false });

    if (body.type === 'url_verification') return json(200, { challenge: str(body.challenge) });

    const head = body.header || {};
    const eventId = str(head.event_id);
    if (eventId) {
      if (this.get(`ev:${eventId}`)) return json(200, { ok: true });      // Lark sends again if we were slow
      this.put(`ev:${eventId}`, '1', 2 * 864e5);
    }
    const ev = body.event || {};
    if (head.event_type === 'im.chat.member.bot.added_v1') {
      if (!str(this.env.LARK_CHAT_ID).trim() && !this.get('chat') && ev.chat_id) {
        this.put('chat', str(ev.chat_id));
        await this.lark('POST', '/open-apis/im/v1/messages?receive_id_type=chat_id', {
          receive_id: str(ev.chat_id), msg_type: 'text',
          content: JSON.stringify({ text: '✅ เชื่อมแชทจากเว็บไซต์กับกลุ่มนี้แล้ว ลูกค้าที่แชทบนเว็บจะขึ้นเป็นการ์ดในกลุ่มนี้ ตอบในเธรดของการ์ด = ส่งถึงลูกค้า · 网站聊天已连接到本群' }),
        });
      }
      return json(200, { ok: true });
    }
    if (head.event_type !== 'im.message.receive_v1') return json(200, { ok: true });

    const m = ev.message || {};
    const sender = ev.sender || {};
    if (sender.sender_type !== 'user') return json(200, { ok: true });  // our own bot's messages
    const root = str(m.root_id) || str(m.parent_id);
    if (!root) return json(200, { ok: true });
    const c = [...this.sql.exec('SELECT id FROM conv WHERE root = ?', root)][0];
    if (!c) return json(200, { ok: true });
    if ([...this.sql.exec('SELECT seq FROM msg WHERE lark = ?', str(m.message_id))].length) return json(200, { ok: true });

    const text = messageText(m).trim();
    if (!text) {
      await this.lark('POST', `/open-apis/im/v1/messages/${encodeURIComponent(root)}/reply`, {
        msg_type: 'text', content: JSON.stringify({ text: 'ℹ️ ส่งถึงลูกค้าได้เฉพาะข้อความตัวอักษร รูปหรือไฟล์ยังส่งไม่ได้ · 目前只能发送文字' }), reply_in_thread: true,
      });
      return json(200, { ok: true });
    }
    if (text.startsWith('//')) return json(200, { ok: true });          // note for the team only
    const now = Date.now();
    this.sql.exec('INSERT INTO msg (conv, who, text, at, lark) VALUES (?, ?, ?, ?, ?)', c.id, 'staff', text.slice(0, 4000), now, str(m.message_id));
    this.sql.exec('UPDATE conv SET updated = ? WHERE id = ?', now, c.id);
    return json(200, { ok: true });
  }

  ready() {
    return !!(str(this.env.LARK_APP_ID).trim() && str(this.env.LARK_APP_SECRET).trim());
  }

  async chatId() {
    return str(this.env.LARK_CHAT_ID).trim() || this.get('chat') || '';
  }

  async token() {
    const cached = this.get('token');
    if (cached) return cached;
    const res = await larkFetch(this.base(), '/open-apis/auth/v3/tenant_access_token/internal', 'POST', null, {
      app_id: str(this.env.LARK_APP_ID).trim(), app_secret: str(this.env.LARK_APP_SECRET).trim(),
    });
    const t = res.raw && res.raw.tenant_access_token;
    if (!t) return '';
    const life = Math.max(60, (Number(res.raw.expire) || 7200) - 300) * 1000;
    this.put('token', t, life);
    return t;
  }

  async lark(method, path, body) {
    const t = await this.token();
    if (!t) return { ok: false, code: 'token', msg: 'no tenant token' };
    const r = await larkFetch(this.base(), path, method, t, body);
    if (r.code === 99991663 || r.code === 99991661) {                    // token expired early: try once more
      this.del('token');
      const t2 = await this.token();
      return t2 ? larkFetch(this.base(), path, method, t2, body) : r;
    }
    return r;
  }

  base() {
    return (str(this.env.LARK_API_BASE).trim() || 'https://open.larksuite.com').replace(/\/+$/, '');
  }

  async ensureAlarm() {
    if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + 864e5);
  }

  // Small key/value store with expiry, in the same database.
  get(k) {
    const row = [...this.sql.exec('SELECT v, until FROM kv WHERE k = ?', k)][0];
    if (!row) return '';
    if (row.until && row.until < Date.now()) { this.del(k); return ''; }
    return row.v;
  }
  put(k, v, ttl) {
    this.sql.exec('INSERT OR REPLACE INTO kv (k, v, until) VALUES (?, ?, ?)', k, v, ttl ? Date.now() + ttl : null);
  }
  del(k) {
    this.sql.exec('DELETE FROM kv WHERE k = ?', k);
  }
  allow(k, max, windowMs) {
    const n = Number(this.get(`rate:${k}`)) || 0;
    if (n >= max) return false;
    const row = [...this.sql.exec('SELECT until FROM kv WHERE k = ?', `rate:${k}`)][0];
    this.put(`rate:${k}`, String(n + 1), row && row.until ? row.until - Date.now() : windowMs);
    return true;
  }
}

/* ---------- Lark helpers ---------- */

async function larkFetch(base, path, method, token, body) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8' };
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(base + path, { method, headers, body: body ? JSON.stringify(body) : undefined, signal: AbortSignal.timeout(TIMEOUT_MS) });
  } catch (e) {
    return { ok: false, code: 'network', msg: String(e && e.message ? e.message : e), data: {}, raw: {} };
  }
  const raw = await res.json().catch(() => ({}));
  return { ok: res.ok && raw.code === 0, code: raw.code !== undefined ? raw.code : res.status, msg: raw.msg || '', data: raw.data || {}, raw };
}

function card(c) {
  const time = bangkokTime();
  const field = (label, value) => ({ is_short: true, text: { tag: 'lark_md', content: `**${label}**\n${md(value)}` } });
  const fields = [field('👤 ชื่อ · 姓名', c.name), field('📞 โทร · 电话', c.phone), field('🌐 ภาษา · 语言', LANGS[c.lang])];
  if (c.page) fields.push(field('📄 แชทจากหน้า · 来源页面', c.page));
  return {
    config: { wide_screen_mode: true },
    header: { template: 'green', title: { tag: 'plain_text', content: `💬 แชทใหม่จากเว็บไซต์ · 网站新对话 — ${c.name}`.slice(0, 150) } },
    elements: [
      { tag: 'div', fields },
      { tag: 'note', elements: [{ tag: 'plain_text', content:
        `ตอบในเธรดของการ์ดนี้ = ส่งถึงลูกค้าบนเว็บ · ขึ้นต้นด้วย // = โน้ตในทีม ไม่ส่งถึงลูกค้า\n在本卡片的话题中回复即发送给客户 · 以 // 开头为内部备注\n🌐 ${time} (GMT+7)` }] },
    ],
  };
}

// Text of a Lark message (plain text or rich "post"); mentions are left out.
function messageText(m) {
  let content = {};
  try { content = JSON.parse(m.content || '{}'); } catch (e) { return ''; }
  if (m.message_type === 'text') return String(content.text || '').replace(/@_user_\d+\s?/g, '').replace(/@_all\s?/g, '');
  if (m.message_type === 'post') {
    const post = content.content ? content : (content.zh_cn || content.en_us || content.ja_jp || Object.values(content)[0] || {});
    const lines = (post.content || []).map((line) => (line || []).map((el) => {
      if (el.tag === 'text') return el.text || '';
      if (el.tag === 'a') return el.text ? `${el.text} (${el.href || ''})` : (el.href || '');
      return '';
    }).join(''));
    return [post.title || '', ...lines].filter(Boolean).join('\n');
  }
  return '';
}

// Lark "Encrypt Key": AES-256-CBC, key = SHA-256 of the Encrypt Key, first 16 bytes are the IV.
async function decrypt(b64, encryptKey) {
  const keyBytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(encryptKey));
  const key = await crypto.subtle.importKey('raw', keyBytes, { name: 'AES-CBC' }, false, ['decrypt']);
  const data = Uint8Array.from(atob(b64), (ch) => ch.charCodeAt(0));
  const plain = await crypto.subtle.decrypt({ name: 'AES-CBC', iv: data.slice(0, 16) }, key, data.slice(16));
  return new TextDecoder().decode(plain);
}

/* ---------- Small helpers ---------- */

function str(v) {
  if (typeof v !== 'string' && typeof v !== 'number') return '';
  return String(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F​-‏‪-‮⁦-⁩﻿]/g, '');
}
function one(v, max) { return str(v).replace(/\s+/g, ' ').trim().slice(0, max); }
function multi(v, max) {
  return str(v).replace(/\r\n?/g, '\n').replace(/[^\S\n]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim().slice(0, max);
}
// Lark text messages turn <at ...> into mentions: show look-alike brackets instead.
function safeText(v) { return String(v).replace(/</g, '＜').replace(/>/g, '＞'); }
function md(value) {
  const swap = { '<': '＜', '>': '＞', '[': '［', ']': '］', '*': '＊', '~': '～', '`': '｀', '&': '＆', '\\': '＼' };
  return String(value || '–').replace(/[<>[\]*~`&\\]/g, (c) => swap[c]);
}
function randomId(n) {
  const b = crypto.getRandomValues(new Uint8Array(n));
  return btoa(String.fromCharCode(...b)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function safeEqual(a, b) {
  a = String(a); b = String(b);
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
function sameHost(origin, requestUrl) {
  try { return new URL(origin).host === new URL(requestUrl).host; } catch (e) { return false; }
}
async function readJson(request) {
  const text = await request.text();
  if (text.length > MAX_BODY) return null;
  try { const v = JSON.parse(text); return v && typeof v === 'object' && !Array.isArray(v) ? v : null; } catch (e) { return null; }
}
function bangkokTime() {
  const t = new Date(Date.now() + 7 * 3600 * 1000);
  const p = (n) => String(n).padStart(2, '0');
  return `${p(t.getUTCDate())}/${p(t.getUTCMonth() + 1)}/${t.getUTCFullYear()} ${p(t.getUTCHours())}:${p(t.getUTCMinutes())}`;
}
function json(status, data) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' } });
}
