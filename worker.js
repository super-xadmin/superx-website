/*
 * SUPERX AI website: sends each contact-form submission to the sales team's Lark group.
 *
 * Cloudflare runs this file (see wrangler.jsonc). It only answers POST /api/lead.
 * Every other address is passed straight to the website files in public/.
 *
 * The enquiry topics and models come from the contact form in the back office
 * (หน้าเว็บ → ติดต่อเรา → แบบฟอร์ม). build/build.py writes them to worker-data.json before each deploy.
 *
 * Settings: Cloudflare > Workers & Pages > superx-website > Settings > Variables and Secrets.
 * Add each one as type "Secret".
 *
 *   LARK_WEBHOOK_URL      required  Webhook address of the custom bot in the sales group
 *   LARK_WEBHOOK_SECRET   optional  Only if "Signature verification" is switched on for that bot
 *   LARK_CRM_URL          optional  Link to the SALE CRM table, shown as a button on each card
 *
 *   Optional: also add each lead to SALE CRM. Needs a Lark app that is allowed to edit the Base.
 *   LARK_APP_ID, LARK_APP_SECRET, LARK_BASE_APP_TOKEN, LARK_BASE_TABLE_ID
 *   LARK_API_BASE         optional  default https://open.larksuite.com (Feishu: https://open.feishu.cn)
 */
import SITE from './worker-data.json';

const CARD_COLOURS = ['blue', 'wathet', 'turquoise', 'green', 'yellow', 'orange', 'red', 'carmine', 'violet', 'purple', 'indigo', 'grey'];

// Used only if worker-data.json has no topics (it always should).
const DEFAULT_INTERESTS = {
  demo: ['📅', 'นัดหมายสาธิต', '预约演示', 'blue'],
  quote: ['💰', 'ขอใบเสนอราคา', '索取报价', 'orange'],
  buy: ['🛒', 'ซื้อรถ RoboVan', '购买 RoboVan', 'orange'],
  lease: ['🔑', 'เช่ารถ RoboVan', '租赁 RoboVan', 'orange'],
  brochure: ['📄', 'ขอเอกสาร / สเปกชีท', '索取资料 / 参数表', 'wathet'],
  education: ['🎓', 'รถไร้คนขับเพื่อการศึกษา', '教育无人车', 'wathet'],
  security: ['🛡️', 'หุ่นยนต์ความปลอดภัยและงานพิเศษ', '安防与特种机器人', 'wathet'],
  'ai-agent': ['🤖', 'AI Agent', 'AI Agent', 'wathet'],
  partner: ['🤝', 'ร่วมเป็นพันธมิตร / ตัวแทนจำหน่าย', '成为合作伙伴 / 经销商', 'turquoise'],
  other: ['💬', 'อื่น ๆ', '其他', 'wathet'],
};
const DEFAULT_MODELS = ['Z5', 'Z5-Plus', 'Z5-Cold-Chain', 'Z5-Multi-Locker', 'Z10', 'Z10-Cold-Chain', 'Z20', 'L4-Suite'];

// icon, Thai, Chinese, card colour
const INTERESTS = readInterests(SITE && SITE.topics);
const MODELS = Array.isArray(SITE && SITE.models) && SITE.models.length ? SITE.models.map(String) : DEFAULT_MODELS;
const CONTACT = {
  email: (SITE && SITE.contact && SITE.contact.email) || 'info@super-x.tech',
  phone: (SITE && SITE.contact && SITE.contact.phone) || '02-323-2800',
};
const LANGS = { th: 'ไทย', zh: '中文', en: 'English' };
const MAX_BODY = 32 * 1024;
const TIMEOUT_MS = 10000;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/lead' || url.pathname === '/api/lead/') {
      try {
        return await handleLead(request, env);
      } catch (err) {
        console.error('lead: unexpected error', err && err.stack ? err.stack : err);
        return reply(request, 500, { ok: false, error: 'server_error' });
      }
    }
    if (env.ASSETS) return env.ASSETS.fetch(request);
    return new Response('Not found', { status: 404 });
  },
};

async function handleLead(request, env) {
  if (request.method !== 'POST') {
    return reply(request, 405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });
  }

  // Only accept the form from this website itself.
  const origin = request.headers.get('Origin');
  if (origin && !sameHost(origin, request.url)) return reply(request, 403, { ok: false, error: 'forbidden' });

  const declared = Number(request.headers.get('Content-Length') || 0);
  if (declared > MAX_BODY) return reply(request, 413, { ok: false, error: 'too_large' });
  const text = await request.text();
  if (text.length > MAX_BODY) return reply(request, 413, { ok: false, error: 'too_large' });

  const type = (request.headers.get('Content-Type') || '').toLowerCase();
  let raw;
  try {
    if (type.includes('application/json')) raw = JSON.parse(text);
    else if (type.includes('application/x-www-form-urlencoded')) raw = Object.fromEntries(new URLSearchParams(text));
    else return reply(request, 415, { ok: false, error: 'unsupported_type' });
  } catch (e) {
    return reply(request, 400, { ok: false, error: 'bad_request' });
  }
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return reply(request, 400, { ok: false, error: 'bad_request' });

  // Hidden "bot-field" is only ever filled in by spam robots: say thanks and drop it.
  if (str(raw['bot-field'])) return reply(request, 200, { ok: true });

  const lead = readLead(raw);
  const missing = [];
  if (!lead.name) missing.push('name');
  if (!lead.company) missing.push('company');
  if ((lead.phone.match(/\d/g) || []).length < 6) missing.push('phone');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) missing.push('email');
  if (!lead.consent) missing.push('consent');
  if (missing.length) return reply(request, 400, { ok: false, error: 'invalid', fields: missing });

  const webhook = str(env.LARK_WEBHOOK_URL).trim();
  if (!/^(https:\/\/|http:\/\/(127\.0\.0\.1|localhost)(:\d+)?\/)/i.test(webhook)) {
    console.error('lead: LARK_WEBHOOK_URL is not set');
    return reply(request, 503, { ok: false, error: 'not_configured' });
  }

  // Many links in the message usually means spam. Still delivered, but marked.
  const suspicious = (lead.message.match(/https?:\/\/|www\./gi) || []).length > 2;

  let crm = null;
  if (!suspicious && env.LARK_APP_ID && env.LARK_APP_SECRET && env.LARK_BASE_APP_TOKEN && env.LARK_BASE_TABLE_ID) {
    try {
      crm = await addToCrm(env, lead);
    } catch (e) {
      crm = { ok: false, error: 'network' };
    }
    if (!crm.ok) console.error('lead: SALE CRM write failed', crm.error);
  }

  const options = { suspicious, crm, crmUrl: httpsUrl(env.LARK_CRM_URL) };
  let sent = await sendToLark(env, webhook, { msg_type: 'interactive', card: buildCard(lead, options) });
  if (!sent.ok) {
    console.error('lead: card not accepted', sent.code, sent.msg);
    // Try once more as plain text so the lead still reaches the group.
    sent = await sendToLark(env, webhook, { msg_type: 'text', content: { text: buildText(lead, options) } });
  }
  if (!sent.ok) {
    console.error('lead: Lark did not accept the message', sent.code, sent.msg);
    return reply(request, 502, { ok: false, error: 'lark_failed', code: sent.code });
  }
  return reply(request, 200, { ok: true });
}

function readLead(raw) {
  const one = (v, max) => str(v).replace(/\s+/g, ' ').trim().slice(0, max);
  const multi = (v, max) => str(v).replace(/\r\n?/g, '\n').replace(/[^\S\n]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim().slice(0, max);
  const has = (obj, key) => typeof key === 'string' && Object.prototype.hasOwnProperty.call(obj, key);
  const qty = one(raw.quantity, 7);
  const from = one(raw.from, 100);
  return {
    name: one(raw.name, 100),
    company: one(raw.company, 150),
    position: one(raw.position, 100),
    phone: one(raw.phone, 40),
    email: one(raw.email, 150),
    line: one(raw.line, 60),
    interest: has(INTERESTS, raw.interest) ? raw.interest : 'other',
    model: MODELS.includes(raw.model) ? raw.model : '',
    quantity: /^\d{1,6}$/.test(qty) && Number(qty) > 0 ? String(Number(qty)) : '',
    message: multi(raw.message, 3000),
    lang: has(LANGS, raw.lang) ? raw.lang : '',
    from: /^\/[\w\-./]*$/.test(from) ? from : '',
    consent: raw.consent === true || ['yes', 'on', 'true'].includes(str(raw.consent).toLowerCase()),
  };
}

/* ---------- Lark message ---------- */

function buildCard(lead, o) {
  const [icon, th, zh, colour] = INTERESTS[lead.interest];
  const topic = th === zh ? th : `${th} · ${zh}`;
  const field = (label, value) => ({ is_short: true, text: { tag: 'lark_md', content: `**${label}**\n${md(value)}` } });

  const fields = [
    field('👤 ผู้ติดต่อ · 联系人', lead.position ? `${lead.name} (${lead.position})` : lead.name),
    field('🏢 บริษัท · 公司', lead.company),
    field('📞 โทร · 电话', lead.phone),
    field('✉️ อีเมล · 邮箱', lead.email),
  ];
  if (lead.line) fields.push(field('💬 LINE', lead.line));
  fields.push(field('🚚 รุ่นที่สนใจ · 意向车型', lead.model ? lead.model.replace(/-/g, ' ') : 'ยังไม่ระบุ · 未定'));
  if (lead.quantity) fields.push(field('🔢 จำนวนรถ · 数量', `${lead.quantity} คัน · 辆`));
  if (lead.lang) fields.push(field('🌐 ภาษาที่ลูกค้าใช้ · 客户语言', LANGS[lead.lang]));

  const elements = [{ tag: 'div', fields }];
  if (lead.message) {
    elements.push({ tag: 'hr' });
    elements.push({ tag: 'div', text: { tag: 'lark_md', content: '**📝 รายละเอียดหน้างานและเส้นทาง · 现场与线路说明**' } });
    elements.push({ tag: 'div', text: { tag: 'plain_text', content: lead.message } });
  }
  if (o.crmUrl) {
    elements.push({
      tag: 'action',
      actions: [{ tag: 'button', text: { tag: 'plain_text', content: '📇 เปิด SALE CRM' }, type: 'primary', url: o.crmUrl }],
    });
  }
  elements.push({ tag: 'note', elements: [{ tag: 'plain_text', content: footerLines(lead, o).join('\n') }] });

  return {
    config: { wide_screen_mode: true },
    header: {
      template: o.suspicious ? 'grey' : colour,
      title: { tag: 'plain_text', content: `${o.suspicious ? '⚠️' : icon} ${topic} — ${lead.company || lead.name}`.slice(0, 150) },
    },
    elements,
  };
}

function buildText(lead, o) {
  const [icon, th, zh] = INTERESTS[lead.interest];
  const s = (v) => String(v).replace(/</g, '＜').replace(/>/g, '＞');
  const lines = [
    `${o.suspicious ? '⚠️' : icon} ลูกค้าใหม่จากเว็บไซต์ SuperX AI · 官网新线索`,
    `เรื่อง · 需求: ${th === zh ? th : `${th} · ${zh}`}`,
    `ผู้ติดต่อ · 联系人: ${s(lead.name)}${lead.position ? ` (${s(lead.position)})` : ''}`,
    `บริษัท · 公司: ${s(lead.company)}`,
    `โทร · 电话: ${s(lead.phone)}`,
    `อีเมล · 邮箱: ${s(lead.email)}`,
  ];
  if (lead.line) lines.push(`LINE: ${s(lead.line)}`);
  lines.push(`รุ่นที่สนใจ · 意向车型: ${lead.model ? lead.model.replace(/-/g, ' ') : 'ยังไม่ระบุ · 未定'}`);
  if (lead.quantity) lines.push(`จำนวนรถ · 数量: ${lead.quantity}`);
  if (lead.lang) lines.push(`ภาษาที่ลูกค้าใช้ · 客户语言: ${LANGS[lead.lang]}`);
  if (lead.message) lines.push('', 'รายละเอียด · 说明:', s(lead.message));
  lines.push('', ...footerLines(lead, o));
  return lines.join('\n');
}

function footerLines(lead, o) {
  const out = [`🌐 เว็บไซต์ SuperX AI · 官网 · ${bangkokTime()} (GMT+7)`];
  if (lead.from) out.push(`มาจากหน้า · 来源页面: ${lead.from}`);
  if (o.crm) out.push(o.crm.ok ? '✅ บันทึกลง SALE CRM แล้ว · 已写入 CRM' : `⚠️ บันทึกลง SALE CRM ไม่สำเร็จ · CRM 写入失败 (${o.crm.error})`);
  if (o.suspicious) out.push('⚠️ ข้อความมีลิงก์หลายอัน อาจเป็นสแปม · 可能是垃圾信息');
  return out;
}

// Customer text shown inside lark_md: swap the characters Lark treats as formatting,
// mentions or links for look-alike full-width characters.
function md(value) {
  const swap = { '<': '＜', '>': '＞', '[': '［', ']': '］', '*': '＊', '~': '～', '`': '｀', '&': '＆', '\\': '＼' };
  return String(value || '–').replace(/[<>[\]*~`&\\]/g, (c) => swap[c]);
}

async function sendToLark(env, webhook, message) {
  const body = Object.assign({}, message);
  const secret = str(env.LARK_WEBHOOK_SECRET).trim();
  if (secret) {
    body.timestamp = String(Math.floor(Date.now() / 1000));
    body.sign = await larkSign(body.timestamp, secret);
  }
  let res;
  try {
    res = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    return { ok: false, code: 'network', msg: String(e && e.message ? e.message : e) };
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* not JSON */ }
  const code = data.code !== undefined ? data.code : data.StatusCode;
  return { ok: res.ok && code === 0, code: code !== undefined ? code : res.status, msg: data.msg || data.StatusMessage || '' };
}

// Lark custom-bot signature: HMAC-SHA256 keyed with "timestamp\nsecret" over an empty message, then Base64.
async function larkSign(timestamp, secret) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(`${timestamp}\n${secret}`), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', key, new Uint8Array(0)));
  let bin = '';
  for (const b of sig) bin += String.fromCharCode(b);
  return btoa(bin);
}

/* ---------- Optional: SALE CRM record ---------- */

async function addToCrm(env, lead) {
  const base = (str(env.LARK_API_BASE).trim() || 'https://open.larksuite.com').replace(/\/+$/, '');
  const tokenRes = await fetch(`${base}/open-apis/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ app_id: str(env.LARK_APP_ID).trim(), app_secret: str(env.LARK_APP_SECRET).trim() }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  const tokenData = await tokenRes.json().catch(() => ({}));
  if (!tokenData.tenant_access_token) return { ok: false, error: `token ${tokenData.code !== undefined ? tokenData.code : tokenRes.status}` };

  // Field and option names exactly as they are in SALE CRM (some contain double or trailing spaces).
  const fields = {
    '客户名称 ชื่อลูกค้า': lead.company,
    '对接人姓名 ผู้ติดต่อ': lead.name,
    '联系电话 เบอร์โทรศัพร์': lead.phone.replace(/[^\d+]/g, ''),
    '客户邮箱 เมล': lead.email,
  };
  if (lead.interest === 'lease') fields['采购方式 วิธีการจัดซื้อ'] = '租赁 เช่า';
  if (lead.interest === 'buy') fields['采购方式 วิธีการจัดซื้อ'] = '直接采购 ซื้อขาด ';

  const app = encodeURIComponent(str(env.LARK_BASE_APP_TOKEN).trim());
  const table = encodeURIComponent(str(env.LARK_BASE_TABLE_ID).trim());
  const res = await fetch(`${base}/open-apis/bitable/v1/apps/${app}/tables/${table}/records`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${tokenData.tenant_access_token}`, 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ fields }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  const data = await res.json().catch(() => ({}));
  if (data.code === 0) return { ok: true };
  return { ok: false, error: String(data.code !== undefined ? data.code : res.status) };
}

/* ---------- Helpers ---------- */

function readInterests(topics) {
  const out = {};
  if (Array.isArray(topics)) {
    for (const t of topics) {
      const value = t && typeof t.value === 'string' ? t.value.trim() : '';
      if (!value || value === '__proto__' || Object.prototype.hasOwnProperty.call(out, value)) continue;
      const th = String(t.th || t.en || value);
      const zh = String(t.zh || t.en || th);
      const colour = CARD_COLOURS.includes(t.color) ? t.color : 'wathet';
      out[value] = [String(t.icon || '💬'), th, zh, colour];
    }
  }
  const result = Object.keys(out).length ? out : Object.assign({}, DEFAULT_INTERESTS);
  if (!result.other) result.other = DEFAULT_INTERESTS.other;
  return result;
}

function str(v) {
  if (typeof v !== 'string' && typeof v !== 'number') return '';
  // Drop control characters, zero-width and text-direction marks.
  return String(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F​-‏‪-‮⁦-⁩﻿]/g, '');
}

function sameHost(origin, requestUrl) {
  try { return new URL(origin).host === new URL(requestUrl).host; } catch (e) { return false; }
}

function httpsUrl(v) {
  const s = str(v).trim();
  return /^https:\/\/[^\s"'<>]+$/i.test(s) ? s : '';
}

function bangkokTime() {
  const t = new Date(Date.now() + 7 * 3600 * 1000);
  const p = (n) => String(n).padStart(2, '0');
  return `${p(t.getUTCDate())}/${p(t.getUTCMonth() + 1)}/${t.getUTCFullYear()} ${p(t.getUTCHours())}:${p(t.getUTCMinutes())}`;
}

// JSON for the website's own script; a small page for browsers that posted the form without JavaScript.
function reply(request, status, data, extraHeaders) {
  const headers = Object.assign({ 'Cache-Control': 'no-store' }, extraHeaders || {});
  const accept = (request.headers.get('Accept') || '') + ' ' + (request.headers.get('Content-Type') || '');
  if (accept.includes('application/json')) {
    headers['Content-Type'] = 'application/json; charset=utf-8';
    return new Response(JSON.stringify(data), { status, headers });
  }
  headers['Content-Type'] = 'text/html; charset=utf-8';
  return new Response(resultPage(data.ok), { status, headers });
}

function resultPage(ok) {
  const t = ok
    ? ['ได้รับข้อมูลแล้ว ขอบคุณครับ', 'ทีมงาน SuperX AI จะติดต่อกลับโดยเร็วที่สุด', '已收到您的信息，谢谢！SuperX AI 团队会尽快与您联系。', 'Thank you. The SuperX AI team will be in touch soon.']
    : ['ส่งข้อมูลไม่สำเร็จ', `กรุณาส่งอีเมลถึง ${esc(CONTACT.email)} หรือโทร ${esc(CONTACT.phone)}`, `提交未成功，请发送邮件至 ${esc(CONTACT.email)} 或致电 ${esc(CONTACT.phone)}。`, `Sorry, that didn’t go through. Please email ${esc(CONTACT.email)} or call ${esc(CONTACT.phone)}.`];
  return `<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SUPERX AI</title>
<style>body{margin:0;font-family:Prompt,Poppins,system-ui,sans-serif;background:#fff;color:#1C3564;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box}main{max-width:520px}h1{font-size:24px;margin:0 0 8px}p{margin:6px 0;color:#41506e;line-height:1.6}a{display:inline-block;margin-top:18px;padding:12px 22px;border-radius:999px;background:#1C3564;color:#fff;text-decoration:none}</style></head>
<body><main><h1>${t[0]}</h1><p>${t[1]}</p><p>${t[2]}</p><p>${t[3]}</p><a href="/contact.html">กลับไปหน้าติดต่อเรา · Back</a></main></body></html>`;
}

function esc(v) {
  return String(v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
