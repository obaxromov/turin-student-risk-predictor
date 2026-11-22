"use strict";
/* Student Risk Predictor: front end. Plain JS, no libraries.
   Text is always put in with textContent (never innerHTML), so nothing a user types can run as code. */

const LANGS = { en: "EN", ru: "RU", uz: "UZ" };
const LI = { en: 0, ru: 1, uz: 2 };
// A few texts that only exist in the web version (everything else comes from /api/i18n).
const L = {
  loading: ["Loading…", "Загрузка…", "Yuklanmoqda…"],
  soon: ["This page is not available in the website yet.", "Эта страница пока не реализована на сайте.", "Bu sahifa hali veb-saytda tayyor emas."],
  expired: ["Your session ended. Please sign in again.", "Сессия закончилась. Войдите снова.", "Seans tugadi. Qaytadan kiring."],
  neterr: ["Cannot reach the server. Try again.", "Нет связи с сервером. Попробуйте ещё раз.", "Serverga ulanib boʻlmadi. Qayta urining."],
  retry: ["Retry", "Повторить", "Qayta urinish"],
  theme: ["Theme", "Тема", "Mavzu"], light: ["Light", "Светлая", "Yorugʻ"], dark: ["Dark", "Тёмная", "Qorongʻi"],
  model_wait: ["The model is getting ready. This takes a few seconds the first time.", "Модель готовится. В первый раз это занимает несколько секунд.", "Model tayyorlanmoqda. Birinchi marta bir necha soniya ketadi."],
  none_now: ["Nobody needs attention right now.", "Сейчас никому не требуется внимание.", "Hozir hech kimga eʼtibor kerak emas."],
  workspace: ["TEACHER WORKSPACE", "КАБИНЕТ ПРЕПОДАВАТЕЛЯ", "OʻQITUVCHI ISH MAYDONI"],
  workspace_student: ["STUDENT WORKSPACE", "КАБИНЕТ СТУДЕНТА", "TALABA ISH MAYDONI"],
  workspace_admin: ["ADMIN WORKSPACE", "ПАНЕЛЬ АДМИНИСТРАТОРА", "ADMIN BOSHQARUVI"],
  insights: ["LEARNING ANALYTICS", "УЧЕБНАЯ АНАЛИТИКА", "TAʼLIM TAHLILI"],
  login_eyebrow: ["A clearer view of every learning journey", "Каждый учебный путь — на виду", "Har bir oʻquv yoʻli nazoratda"],
  login_head: ["See the signals. Support the student.", "Замечайте сигналы. Поддерживайте студентов.", "Belgilarni koʻring. Talabani qoʻllang."],
  login_intro: ["A calmer way to understand progress and know where to focus your attention.", "Удобный способ следить за прогрессом и понимать, кому нужна поддержка.", "Rivojlanishni kuzatish va eʼtiborni qayerga qaratishni bilishning qulay usuli."],
  login_step_1: ["Understand progress", "Следите за прогрессом", "Oʻzlashtirishni kuzating"],
  login_step_2: ["Notice changes early", "Замечайте изменения вовремя", "Oʻzgarishlarni erta sezing"],
  login_step_3: ["Guide the next step", "Помогайте двигаться дальше", "Keyingi qadamni belgilang"],
  login_welcome: ["Welcome back", "С возвращением", "Xush kelibsiz"],
  login_help: ["Sign in to open your learning workspace.", "Войдите, чтобы открыть учебную панель.", "Taʼlim boshqaruv paneliga kirish uchun tizimga kiring."],
  demo_access: ["Or explore the demo", "Или откройте демоверсию", "Yoki demoni sinab koʻring"],
  stat_caption: ["Current cohort", "Текущая группа", "Joriy guruh"],
  stat_needs: ["Students needing support", "Нуждаются в поддержке", "Yordamga muhtoj talabalar"],
  stat_activity: ["Activity change", "Изменение активности", "Faollikdagi oʻzgarish"],
  distribution: ["Cohort at a glance", "Распределение группы", "Guruh holati"],
  distribution_note: ["A quick view of where support may be useful.", "Краткий обзор возможных точек поддержки.", "Yordam kerak boʻlishi mumkin boʻlgan holatlarning qisqa koʻrinishi."],
  priority_label: ["PRIORITY VIEW", "ПРИОРИТЕТЫ", "USTUVOR VAZIFALAR"],
  activity_label: ["RECENT ACTIVITY", "НЕДАВНЯЯ АКТИВНОСТЬ", "SOʻNGGI FAOLLIK"],
  privacy_note: ["Academic prototype · Not for real student records", "Учебный прототип · Не для реальных данных студентов", "Oʻquv prototipi · Haqiqiy talaba maʼlumotlari uchun emas"],
  profile: ["Account settings", "Настройки аккаунта", "Hisob sozlamalari"],
  status_ok: ["On-track students", "Студенты по плану", "Reja boʻyicha oʻqiyotganlar"],
  search_student: ["Find a student ID", "Найти по ID студента", "Talaba ID sini izlash"],
  no_matches: ["No students match your search.", "Нет студентов по вашему запросу.", "Qidiruvga mos talabalar topilmadi."],
  recent_four: ["Last 4 weeks", "Последние 4 недели", "Soʻnggi 4 hafta"],
  all_weeks: ["All weeks", "Все недели", "Barcha haftalar"],
  jump_content: ["Skip to content", "Перейти к содержимому", "Asosiy qismga oʻtish"],
  password_show: ["Show password", "Показать пароль", "Parolni koʻrsatish"],
  password_hide: ["Hide password", "Скрыть пароль", "Parolni yashirish"],
  demo_preview: ["A thoughtful space for better decisions", "Продуманное пространство для важных решений", "Yaxshi qarorlar uchun qulay muhit"],
  live_system: ["Your learning workspace", "Ваша учебная панель", "Sizning taʼlim ish joyingiz"],
  mainNav: ["Main navigation", "Основная навигация", "Asosiy navigatsiya"],

};

const S = { lang: "en", i18n: {}, cfg: { demo_mode: false }, token: null, user: null, menuOpen: false, overviewCache: null, overviewCachedAt: 0, trendRange: "all", predictionDrafts: new Map() };

try { const l = localStorage.getItem("lang"); if (l in LANGS) S.lang = l; } catch (e) { /* storage blocked */ }
try { S.token = sessionStorage.getItem("token"); } catch (e) { /* storage blocked: sign-in lasts until reload */ }

/* ---------- helpers ---------- */
function t(key, vars) {
  const e = S.i18n[key] || L[key];
  let s = e ? (e[LI[S.lang]] ?? e[0]) : key;
  if (vars) for (const k in vars) s = s.split("{" + k + "}").join(String(vars[k]));
  return s;
}
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const k in attrs || {}) {
    const v = attrs[k];
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined && c !== false) el.append(c.nodeType ? c : document.createTextNode(String(c)));
  return el;
}
const NS = "http://www.w3.org/2000/svg";
function svg(tag, attrs, ...kids) {
  const el = document.createElementNS(NS, tag);
  for (const k in attrs || {}) el.setAttribute(k, attrs[k]);
  for (const c of kids.flat()) if (c) el.append(c.nodeType ? c : document.createTextNode(String(c)));
  return el;
}
function rich(text) { // **bold** and blank-line paragraphs, built with DOM nodes
  return text.split("\n\n").map(p => h("p", null, p.split("**").map((part, i) => i % 2 ? h("strong", null, part) : part)));
}
function setLang(l) {
  S.lang = l; document.documentElement.lang = l;
  try { localStorage.setItem("lang", l); } catch (e) { /* ignore */ }
  render();
}
function setTheme(th) {
  document.documentElement.setAttribute("data-theme", th);
  try { localStorage.setItem("theme", th); } catch (e) { /* ignore */ }
  // Theme changes are visual only: do not reset the page, flash a skeleton,
  // or request the model data again.
  document.querySelectorAll('.seg[data-setting="theme"] button').forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.value === th));
  });
}
function currentTheme() {
  const a = document.documentElement.getAttribute("data-theme");
  if (a) return a;
  return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json" };
  if (S.token) headers.Authorization = "Bearer " + S.token;
  let res;
  try { res = await fetch(path, { method: opts.method || "GET", headers, body: opts.body ? JSON.stringify(opts.body) : undefined }); }
  catch (e) { throw { kind: "net" }; }
  let data = null;
  try { data = await res.json(); } catch (e) { /* empty body */ }
  if (res.status === 401 && S.user) { endSession(); location.hash = "#/login"; throw { kind: "expired" }; }
  if (!res.ok) throw { kind: "http", status: res.status, data };
  return data;
}
function startSession(d) {
  S.token = d.token; S.user = d.user;
  try { sessionStorage.setItem("token", d.token); } catch (e) { /* ignore */ }
}
function endSession() {
  S.token = null; S.user = null; S.menuOpen = false; S.overviewCache = null; S.overviewCachedAt = 0;
  S.predictionDrafts.clear();
  try { sessionStorage.removeItem("token"); } catch (e) { /* ignore */ }
}

/* ---------- shared pieces ---------- */
function langSeg() {
  return h("div", { class: "seg", role: "group", "aria-label": t("language") },
    Object.keys(LANGS).map(k => h("button", { type: "button", "aria-pressed": String(S.lang === k), onclick: () => setLang(k) }, LANGS[k])));
}
function themeSeg() {
  const cur = currentTheme();
  return h("div", { class: "seg", role: "group", "data-setting": "theme", "aria-label": t("theme") },
    ["light", "dark"].map(k => h("button", { type: "button", "data-value": k, "aria-pressed": String(cur === k), onclick: () => setTheme(k) }, t(k))));
}
function brandMark() {
  // Four connected points, like an upward learning trajectory.
  return h("span", { class: "brand-mark", "aria-hidden": "true" }, svg("svg", { width: 22, height: 22, viewBox: "0 0 32 32" },
    svg("path", { d: "M5 24l7-9 7 4 8-13", fill: "none", stroke: "currentColor", "stroke-width": 3.2, "stroke-linecap": "round", "stroke-linejoin": "round" }),
    svg("circle", { cx: 5, cy: 24, r: 2.3, fill: "currentColor" }),
    svg("circle", { cx: 27, cy: 6, r: 2.3, fill: "currentColor" })));
}
function icon(name) {
  const paths = {
    people: ["M16 18c-4.8 0-8 2.4-8 5v1h16v-1c0-2.6-3.2-5-8-5Z", "M16 14a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z"],
    focus: ["M16 5a11 11 0 1 0 0 22 11 11 0 0 0 0-22Z", "M16 10v7", "M16 22h.01"],
    activity: ["M3 17h6l4-9 6 15 4-9h6"],
    arrow: ["M5 16h22", "m19 8 8 8-8 8"],
    chevron: ["m9 13 7 7 7-7"],
    search: ["M22 22l7 7", "M13.5 23a9.5 9.5 0 1 0 0-19 9.5 9.5 0 0 0 0 19Z"],
  };
  return svg("svg", { class: "ui-icon", viewBox: "0 0 32 32", width: 20, height: 20, fill: "none", stroke: "currentColor", "stroke-width": 1.9, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" },
    (paths[name] || paths.activity).map(d => svg("path", { d })));
}
function demoPill() { return h("span", { class: "pill" }, t("demo_badge")); }
function badge(tier) { return h("span", { class: "badge t-" + tier }, t("tier_" + tier)); }

function reasonText(r) {
  if (!r) return t("dt_why_none");
  const f = r.feature, v = r.value, m = r.median;
  let vs, ms = "";
  if (f === "attendance_trend" || f === "logins_trend") vs = (v >= 0 ? "+" : "") + v.toFixed(0);
  else if (f === "logins_per_week") { vs = v.toFixed(1); ms = m.toFixed(1); }
  else { vs = v.toFixed(0); ms = m.toFixed(0); }
  return t("why_" + f, { v: vs, m: ms });
}
function trendText(v) {
  if (Math.round(Math.abs(v)) === 0) return "→ 0%";
  return (v > 0 ? "▲ " : "▼ ") + Math.abs(v).toFixed(0) + "%";
}

/* ---------- login ---------- */
function loginView() {
  const err = h("div", { class: "err", role: "alert", hidden: true });
  const user = h("input", { id: "u", name: "username", autocomplete: "username", required: true, maxlength: 60 });
  const pass = h("input", { id: "p", name: "password", type: "password", autocomplete: "current-password", required: true, maxlength: 200 });
  const showPass = h("button", { class: "password-toggle", type: "button", "aria-label": t("password_show"),
    onclick: () => { const visible = pass.type === "password"; pass.type = visible ? "text" : "password";
      showPass.textContent = visible ? t("password_hide") : t("password_show");
      showPass.setAttribute("aria-label", showPass.textContent); } }, t("password_show"));
  const btn = h("button", { class: "btn primary block", type: "submit" }, t("sign_in"));
  let busy = false;
  const fail = (msg) => { err.textContent = msg; err.hidden = false; };

  async function done(d) { startSession(d); location.hash = d.user.role === "admin" ? "#/accounts" : (d.user.role === "student" ? "#/home" : "#/overview"); render(); }
  async function submit(ev) {
    ev.preventDefault(); if (busy) return; busy = true; btn.disabled = true; err.hidden = true;
    try { await done(await api("/api/login", { method: "POST", body: { username: user.value, password: pass.value } })); }
    catch (e) {
      if (e.kind === "net") fail(t("neterr"));
      else if (e.data && e.data.error === "locked") fail(t("login_locked", { s: e.data.seconds }));
      else fail(t("login_failed"));
      pass.value = "";
    } finally { busy = false; btn.disabled = false; }
  }
  async function demo(role) {
    if (busy) return;
    busy = true; btn.disabled = true; err.hidden = true;
    try { await done(await api("/api/demo-login", { method: "POST", body: { role } })); }
    catch (e) { fail(t("neterr")); }
    finally { busy = false; btn.disabled = false; }
  }
  const demoBlock = S.cfg.demo_login_enabled ? [
    h("hr", { class: "sep" }),
    h("div", { class: "muted small demo-label" }, t("demo_access")),
    h("div", { class: "demo-row" }, ["teacher", "student", "admin"].map(r => h("button", { class: "btn", type: "button", onclick: () => demo(r) }, t("role_" + r)))),
    h("div", null, h("span", { class: "pill" }, t("demo_badge")), " ", h("span", { class: "muted small" }, t("demo_hint"))),
  ] : [];
  const form = h("form", { class: "auth-card", onsubmit: submit },
    h("div", { class: "auth-brand" }, brandMark(), h("span", null, t("app_title"))),
    h("div", { class: "auth-heading" },
      h("h1", null, t("login_welcome")),
      h("p", { class: "muted" }, t("login_help"))),
    err,
    h("div", { class: "auth-fields" },
      h("label", { class: "auth-field" }, t("username"), user),
      h("label", { class: "auth-field" }, t("password"), h("span", { class: "password-wrap" }, pass, showPass))),
    btn,
    h("div", { class: "auth-demo" }, ...demoBlock),
    h("div", { class: "auth-options" }, langSeg(), themeSeg()),
    h("p", { class: "auth-footnote" }, t("privacy_note")));
  return h("main", { class: "auth-page" }, form);
}

/* ---------- shell ---------- */
const NAV = {
  teacher: [["overview", "nav_overview"], ["courses", "nav_courses"], ["assignments", "nav_homework"], ["students", "nav_students"], ["predict", "nav_predict"], ["model", "nav_model"]],
  student: [["home", "nav_home"], ["courses", "nav_courses"], ["assignments", "nav_homework"]],
  admin: [["accounts", "nav_accounts"]],
};


function shell(route, body) {
  const u = S.user;
  const menu = h("div", { class: "menu", id: "acct-menu", hidden: !S.menuOpen },
    h("div", { class: "menu-title" }, t("profile")),
    h("div", { class: "menu-identity" }, h("span", { class: "avatar large" }, u.username.slice(0, 1).toUpperCase()),
      h("div", null, h("b", null, u.username), h("p", { class: "muted small" }, t("role_" + u.role)))),
    h("div", { class: "menu-settings" }, h("span", { class: "muted small" }, t("language")), langSeg(),
      h("span", { class: "muted small" }, t("theme")), themeSeg()),
    h("button", { class: "btn block signout", type: "button", onclick: signOut }, t("sign_out")));
  const toggle = h("button", { class: "account-toggle", type: "button", "aria-expanded": String(S.menuOpen), "aria-controls": "acct-menu",
    onclick: () => { S.menuOpen = !S.menuOpen; menu.hidden = !S.menuOpen; toggle.setAttribute("aria-expanded", String(S.menuOpen)); } },
    h("span", { class: "avatar" }, u.username.slice(0, 1).toUpperCase()),
    h("span", { class: "account-name" }, u.username), icon("chevron"));
  return h("div", { class: "app-shell" },
    h("a", { class: "skip-link", href: "#main-content", onclick: ev => {
      ev.preventDefault(); const main = document.getElementById("main-content");
      if (main) { main.focus(); main.scrollIntoView(); }
    } }, t("jump_content")),
    h("header", { class: "topbar" }, h("div", { class: "topbar-in" },
      h("div", { class: "brand" }, brandMark(), h("div", { class: "brand-text" }, h("strong", null, t("app_title")), h("span", null, t("insights")))),
       h("nav", { class: "tabs tabs-" + u.role, "aria-label": t("mainNav") }, NAV[u.role].map(([k, key]) =>
        h("a", { class: "tab", href: "#/" + k, "aria-current": route === k ? "page" : null }, t(key)))),
      h("div", { class: "acct" }, toggle, menu))),
    h("main", { id: "main-content", tabindex: "-1" }, body),
    h("footer", { class: "app-footer" }, h("div", null, t("privacy_note"))));
}
async function signOut() {
  try { await api("/api/logout", { method: "POST" }); } catch (e) { /* leave anyway */ }
  endSession(); location.hash = "#/login"; render();
}
function placeholder(key) {
  return h("div", { class: "card empty" }, h("h2", null, t(key)), h("p", { class: "muted" }, t("soon")));
}
function errorBox(e, retry) {
  const msg = e.kind === "net" ? t("neterr") : t("neterr");
  return h("div", { class: "card empty" }, h("p", null, msg), h("button", { class: "btn", type: "button", onclick: retry }, t("retry")));
}

/* ---------- overview ---------- */
function tierBar(cnt) {
  const total = (cnt.help + cnt.watch + cnt.ok) || 1;
  const bar = h("div", { class: "tierbar", role: "img", "aria-label": ["help", "watch", "ok"].map(k => t("tier_" + k) + " " + cnt[k]).join(", ") });
  for (const k of ["help", "watch", "ok"]) { const seg = h("i", { class: "t-" + k }); seg.style.width = (cnt[k] / total * 100) + "%"; bar.append(seg); }
  const legend = h("div", { class: "legend" }, ["help", "watch", "ok"].map(k => h("span", { class: "t-" + k }, h("span", { class: "dot" }), t("tier_" + k) + " ", h("b", null, cnt[k]))));
  return h("div", null, bar, legend);
}
function urgentTable(d, rows = d.urgent) {
  if (!rows.length) return h("p", { class: "muted no-results" }, d.urgent.length ? t("no_matches") : t("none_now"));
  return h("div", { class: "tablewrap" }, h("table", { class: "tbl" },
    h("thead", null, h("tr", null, ["col_student", "col_tier", "col_risk", "col_reason"].map(k => h("th", { scope: "col" }, t(k))))),
    h("tbody", null, rows.map(r => {
      const fill = h("i"); fill.style.width = r.risk + "%";
      return h("tr", null,
        h("td", { class: "id" }, r.student_id), h("td", null, badge(r.tier)),
        h("td", null, h("div", { class: "risk t-" + r.tier }, h("div", { class: "bar" }, fill), h("span", null, r.risk + "%"))),
        h("td", null, reasonText(r.reason)));
    }))));
}
function urgentPanel(d) {
  const results = h("div", { class: "priority-results" }, urgentTable(d));
  const search = h("input", { class: "student-search", type: "search", maxlength: 40,
    autocomplete: "off", "aria-label": t("search_student"), placeholder: t("search_student"),
    oninput: () => { const query = search.value.trim().toLowerCase();
      results.replaceChildren(urgentTable(d, d.urgent.filter(r => r.student_id.toLowerCase().includes(query)))); } });
  return h("section", { class: "card priority-card" },
    h("div", { class: "section-head priority-head" },
      h("div", null, h("p", { class: "eyebrow" }, t("priority_label")), h("h2", null, t("urgent_title"))),
      h("div", { class: "search-shell" }, icon("search"), search)), results);
}
function activityMatrix(d) {
  // GitHub-inspired weekly cells: only 8 actual aggregate weeks exist.
  const picker = h('select', { class: 'field activity-picker', 'aria-label': t('activityPick') });
  const heat = h('div', { class: 'weekly-heatmap' });
  const label = h('div', { class: 'activity-focus-meta' });
  const profile = linkButton(t('viewProfile'), () => goTo('student/'+picker.value), 'quiet');
  const dotLevel = v => v >= 80 ? 'l4' : v >= 60 ? 'l3' : v >= 40 ? 'l2' : v >= 20 ? 'l1' : '';
  function draw(person) {
    const vals = person.weeks;
    heat.replaceChildren(...vals.map((v,i) => h('div', { class: 'week-chip '+dotLevel(v),
      title: t('week_n')+' '+(i+1)+': '+v.toFixed(0)+'%',
      'aria-label': t('week_n')+' '+(i+1)+' '+v.toFixed(0)+'%', tabindex: '0' },
        h('span',null,String(i+1)), h('strong',null,v.toFixed(0)+'%'))));
    label.replaceChildren(h('strong',null,person.student_id),
      h('span',null, t('activityWeek')),
      h('b',null,(vals.reduce((a,b)=>a+b,0)/vals.length).toFixed(0)+'%'));
    profile.hidden=false;
  }
  picker.append(h('option',{value:''},t('loading')));
  picker.addEventListener('change',() => {
    const person=S.activityStudents?.find(r=>r.student_id===picker.value);
    if(person)draw(person);
  });
  const panel=h('div',{class:'activity-module'},
    h('div',{class:'activity-top'},h('div',null,h('h2',null,t('mx_title')),
      h('p',{class:'muted small'},t('activityPick'))),picker),
    label,heat,h('div',{class:'activity-bottom'},h('p',{class:'muted small'},t('activityNoHistory')),profile));
  const load = arr => {
    S.activityStudents=arr;
    picker.replaceChildren(...arr.map(r=>h('option',{value:r.student_id,selected:r.student_id===S.activitySelected?true:null},r.student_id+' · '+r.group)));
    const person=arr.find(r=>r.student_id===S.activitySelected)||arr[0];
    if(person){picker.value=person.student_id;draw(person);}
    picker.addEventListener('change',()=>{S.activitySelected=picker.value;});
  };
  if(S.activityStudents) load(S.activityStudents);
  else api('/api/students').then(data=>{if(panel.isConnected)load(data.students);}).catch(()=>{
    picker.replaceChildren(h('option',null,t('neterr')));
  });
  return panel;
}
function lineChart(d, lastFour = false) {
  const count = lastFour ? Math.min(4, d.weeks) : d.weeks;
  const start = d.weeks-count, W=600,H=260,p={l:34,r:16,t:18,b:30};
  const g=svg('svg',{class:'chart smooth-chart',viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':t('trend_chart_title')});
  for (const v of [0,25,50,75,100]) {
    const y=p.t+(1-v/100)*(H-p.t-p.b);
    g.append(svg('line',{class:'grid-l',x1:p.l,x2:W-p.r,y1:y,y2:y}),
      svg('text',{x:p.l-7,y:y+4,'text-anchor':'end'},v));
  }
  for (let i=0;i<count;i++)
    g.append(svg('text',{x:p.l+i*(W-p.l-p.r)/Math.max(1,count-1),y:H-8,'text-anchor':'middle'},i+start+1));
  for(const k of ['help','watch','ok']){
    const series=d.tier_series[k];if(!series)continue;
    const vals=series.slice(start),path=smoothPath(vals,W,H,p);
    const glow=svg('path',{d:path,class:'smooth-glow s-'+k});
    g.append(glow);
    const line=svg('path',{d:path,class:'ln s-'+k});
    line.append(svg('title',null,t('tier_'+k)+': '+vals.map(v=>v.toFixed(1)+'%').join(' · ')));
    g.append(line);
  }
  return h('div',null,g,h('div',{class:'legend'},['help','watch','ok'].map(k=>h('span',{class:'t-'+k},h('span',{class:'dot'}),t('tier_'+k)))));
}
function trendPanel(d) {
  const chart = h("div", { class: "trend-chart-body" }, lineChart(d, S.trendRange === "four"));
  const controls = h("div", { class: "seg chart-range", role: "group", "aria-label": t("trend_chart_title") },
    ["four", "all"].map(k => h("button", { type: "button", "aria-pressed": String(S.trendRange === k),
      onclick: () => {
        S.trendRange = k;
        chart.replaceChildren(lineChart(d, k === "four"));
        controls.querySelectorAll("button").forEach((b, idx) => b.setAttribute("aria-pressed", String(["four", "all"][idx] === k)));
      } }, t(k === "four" ? "recent_four" : "all_weeks"))));
  return h("section", { class: "card trend-card" },
    h("div", { class: "section-head" }, h("div", null, h("h2", null, t("trend_chart_title"))), controls), chart);
}
function donut(d) {
  const R = 52, C = 2 * Math.PI * R, total = (d.counts.help + d.counts.watch + d.counts.ok) || 1;
  const g = svg("svg", { class: "donut", width: 150, height: 150, viewBox: "0 0 150 150", role: "img", "aria-label": t("comp_title") });
  g.append(svg("circle", { cx: 75, cy: 75, r: R, fill: "none", stroke: "var(--surface-2)", "stroke-width": 16 }));
  let off = 0;
  for (const k of ["help", "watch", "ok"]) {
    const len = d.counts[k] / total * C; if (!len) continue;
    g.append(svg("circle", { class: "ring r-" + k, cx: 75, cy: 75, r: R, "stroke-dasharray": `${len} ${C - len}`, "stroke-dashoffset": -off, transform: "rotate(-90 75 75)" }));
    off += len;
  }
  g.append(svg("text", { x: 75, y: 80, "text-anchor": "middle", "font-size": 26 }, total), svg("text", { x: 75, y: 98, "text-anchor": "middle", "font-size": 11, class: "u" }, t("students_unit")));
  return h("div", null, h("h2", null, t("comp_title")), h("div", { class: "donut-wrap" }, g, tierBarLegend(d.counts)));
}
function tierBarLegend(cnt) {
  return h("div", { class: "legend" }, ["help", "watch", "ok"].map(k => h("span", { class: "t-" + k }, h("span", { class: "dot" }), t("tier_" + k) + " ", h("b", null, cnt[k]))));
}
function groupBars(d) {
  const W=600,H=220,p={l:34,r:12,t:18,b:30},n=Math.max(1,d.groups.length);
  const bw=Math.min(76,(W-p.l-p.r)/n*.54),y=v=>p.t+(1-v/100)*(H-p.t-p.b);
  const g=svg('svg',{class:'chart cohort-chart',viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':t('groups_title')});
  const defs=svg('defs',null,
    svg('linearGradient',{id:'cohort-glass-fill',x1:'0',x2:'0',y1:'0',y2:'1'},
      svg('stop',{offset:'0%','stop-color':'#ff9da2'}),
      svg('stop',{offset:'52%','stop-color':'#ed6574'}),
      svg('stop',{offset:'100%','stop-color':'#bf415b'})));
  g.append(defs);
  for(const v of [0,25,50,75,100])g.append(svg('line',{class:'grid-l',x1:p.l,x2:W-p.r,y1:y(v),y2:y(v)}),
    svg('text',{x:p.l-7,y:y(v)+4,'text-anchor':'end'},v));
  d.groups.forEach((r,i)=>{
    const cx=p.l+(i+.5)*(W-p.l-p.r)/n,top=y(r.flagged),height=Math.max(1,y(0)-top);
    g.append(svg('rect',{class:'bar-aura',x:cx-bw/2-4,y:top-4,width:bw+8,height:height+5,rx:13}),
      svg('rect',{class:'bar-glow',x:cx-bw/2,y:top,width:bw,height:height,rx:11}),
      svg('rect',{class:'bar-f',x:cx-bw/2,y:top,width:bw,height:height,rx:11,fill:'url(#cohort-glass-fill)'}),
      svg('text',{x:cx,y:top-11,'text-anchor':'middle',class:'value-label'},r.flagged+'%'),
      svg('text',{x:cx,y:H-8,'text-anchor':'middle'},r.group));
  });
  return h('div',null,h('h2',null,t('groups_title')),g,h('p',{class:'muted small'},t('groups_axis')));
}
function statCard(value, label, note, glyph, kind) {
  return h("div", { class: "stat-card" },
    h("div", { class: "stat-card-top" }, h("span", { class: "stat-label" }, label), h("span", { class: "stat-icon " + (kind || "") }, icon(glyph))),
    h("div", { class: "stat-number" }, value),
    h("p", { class: "stat-note" }, note));
}
function sectionHead(title, eyebrow, subtitle) {
  return h("div", { class: "section-head" },
    h("div", null, eyebrow ? h("p", { class: "eyebrow" }, eyebrow) : null,
      h("h2", null, title), subtitle ? h("p", { class: "muted small" }, subtitle) : null));
}
function overviewView(d) {
  const pageHead = h("div", { class: "hero" },
    h("div", { class: "hero-copy" },
      h("div", { class: "hero-overline" }, h("span", { class: "overline-square" }), t("workspace"), h("span", { class: "overline-sep" }, "/"), t("nav_overview")),
      h("h1", null, t("ov_title")),
      h("p", { class: "muted hero-description" }, t("ov_sub", { w: d.weeks, n: d.students }))),
    h("div", { class: "hero-meta" }, d.demo ? demoPill() : null));
  return h("div", { class: "dashboard" },
    pageHead,
    h("div", { class: "stat-grid" },
      statCard(d.students, t("sec_people"), t("stat_caption"), "people"),
      statCard(d.counts.help, t("tier_help"), t("stat_needs"), "focus", "urgent"),
      statCard(trendText(d.trend), t("stat_trend"), t("stat_activity"), "activity"),
      statCard(d.counts.ok, t("tier_ok"), t("status_ok"), "people", "positive")),
    h("div", { class: "grid feature-grid" },
      trendPanel(d),
      h("section", { class: "card distribution-card" },
        sectionHead(t("distribution"), null, t("distribution_note")),
        donut(d), tierBar(d.counts))),
    h("div", { class: "grid priority-grid" },
      urgentPanel(d),
      h("section", { class: "card activity-card" }, activityMatrix(d))),
    h("div", { class: "grid secondary-grid" },
      h("section", { class: "card" }, groupBars(d)),
      h("section", { class: "card explanation" }, sectionHead(t("how_to_read")),
        h("div", { class: "body" }, rich(t("how_to_read_body", { h: d.thresholds.help, w: d.thresholds.watch })),
          h("p", { class: "small" }, t("model_line", { auc: d.auc }))))));
}

/* ---------- router ---------- */
let seq = 0;
async function render() {
  const mine=++seq,root=document.getElementById('app');
  document.title=t('app_title');
  const raw=location.hash.replace(/^#\//,'')||'';
  const route=raw.split('?')[0];
  if(!S.user){
    if(S.token){try{const me=await api('/api/me');S.user=me.user;}catch(e){endSession();}if(mine!==seq)return;}
    if(!S.user){root.replaceChildren(loginView());return;}
  }
  const role=S.user.role,known=NAV[role].map(x=>x[0]);
  const profilePrediction=/^predict\/student\/([^/]+)$/.exec(route);
  const predictionDetail=route==='predict/new'||route==='predict/csv'||profilePrediction!==null;
  const extra=role==='teacher'&&(route.startsWith('student/')||route==='new-assignment'||predictionDetail);
  const assignmentDetail=(role==='student'||role==='teacher')&&/^assignment\/\d+$/.test(route);
  const page=known.includes(route)||extra||assignmentDetail?route:known[0];
  if(page!==route){location.hash='#/'+page;return;}
  const activeNav=extra&&predictionDetail?'predict':
    page.startsWith('student/')?'students':page.startsWith('assignment/')||page==='new-assignment'?'assignments':page;
  const slot=h('div',{class:'page-slot'},h('div',{class:'skeleton'}));
  root.replaceChildren(shell(activeNav,slot));
  const paths={overview:'/api/overview',students:'/api/students',predict:'/api/model',model:'/api/model',
    courses:'/api/courses',assignments:'/api/assignments',home:'/api/home',accounts:'/api/accounts',
    'new-assignment':'/api/courses','predict/new':'/api/model','predict/csv':'/api/model'};
  const url=profilePrediction?'/api/students/'+profilePrediction[1]:
    page.startsWith('student/')?'/api/students/'+page.split('/')[1]:
    page.startsWith('assignment/')?'/api/assignments/'+page.split('/')[1]:paths[page];
  if(!url){slot.replaceChildren(placeholder('nav_overview'));return;}
  const show=d=>{
    if(page==='overview')return overviewView(d);
    if(page==='students')return studentsPage(d);
    if(page.startsWith('student/'))return studentDetailPage(d);
    if(page==='predict')return predictPage(d);
    if(page==='predict/new'||profilePrediction)return singlePredictionPage(d);
    if(page==='predict/csv')return csvPredictionPage(d);
    if(page==='model')return modelPage(d);
    if(page==='courses')return coursePage(d);
    if(page==='assignments')return assignmentsPage(d);
    if(page.startsWith('assignment/'))return assignmentDetailPage(d);
    if(page==='new-assignment')return newAssignmentPage(d);
    if(page==='home')return homePage(d);
    if(page==='accounts')return accountsPage(d);
    return placeholder('nav_overview');
  };
  const load=async()=>{
    if(page==='overview'&&S.overviewCache&&Date.now()-S.overviewCachedAt<30_000){
      slot.replaceChildren(show(S.overviewCache));return;
    }
    slot.replaceChildren(h('div',{class:'skeleton'}));
    try{
      const d=await api(url);
      if(page==='overview'){S.overviewCache=d;S.overviewCachedAt=Date.now();}
      if(mine===seq)slot.replaceChildren(show(d));
    }catch(e){if(mine===seq&&e.kind!=='expired')slot.replaceChildren(errorBox(e,load));}
  };
  load();
}
async function boot() {
  document.documentElement.lang=S.lang;
  try {
    const [cfg,i18n]=await Promise.all([fetch('/api/config').then(r=>r.json()),fetch('/api/i18n').then(r=>r.json())]);
    S.cfg=cfg;S.i18n=i18n;
  }catch(e){document.getElementById('app').textContent=t('neterr');return;}
  window.addEventListener('hashchange',()=>{
    S.menuOpen=false;
    window.scrollTo(0,0);
    render();
  });
  document.addEventListener('pointermove',ev=>{
    const el=ev.target.closest('.btn,.account-toggle,.seg button,.course-tile,.liquid-trigger');
    if(!el)return;
    const r=el.getBoundingClientRect();
    el.style.setProperty('--pointer-x',((ev.clientX-r.left)/r.width*100).toFixed(1)+'%');
    el.style.setProperty('--pointer-y',((ev.clientY-r.top)/r.height*100).toFixed(1)+'%');
  },{passive:true});
  document.addEventListener('click',ev=>{
    const m=document.getElementById('acct-menu');
    if(S.menuOpen&&m&&!ev.target.closest('.acct')){S.menuOpen=false;m.hidden=true;const b=document.querySelector('.account-toggle');if(b)b.setAttribute('aria-expanded','false');}
  });
  document.addEventListener('keydown',ev=>{
    if(ev.key==='Escape'&&S.menuOpen){S.menuOpen=false;
      const menu=document.getElementById('acct-menu'),toggle=document.querySelector('.account-toggle');
      if(menu)menu.hidden=true;if(toggle){toggle.setAttribute('aria-expanded','false');toggle.focus();}
    }
  });
  render();
}
boot();
