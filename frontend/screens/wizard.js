// Profile questions: nine short steps. Fields the contract has go to the backend (see buildBody).
// Fields it does not have (phone, tools, education list, schedule ...) are kept in store.js and shown on the Profile page.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { U, saveExtras } from "../store.js";
import { readCvText } from "../slots.js";
import { h, go, field, ask, choice, toggle, pills, trash } from "../ui.js";
import { ill } from "../art.js";

const LEVELS = [1, 2, 3];
let lists = null;
const KF = "co_form";
const blank = () => ({ name: "", phone: "", role: "", industry: "", examples: [""], skills: [], goalText: "", goal: "", hours: "", picks: [] });
function loadForm() { try { const v = JSON.parse(sessionStorage.getItem(KF)); return v && Array.isArray(v.examples) ? Object.assign(blank(), v) : null; } catch (e) { return null; } }
function saveForm() { try { sessionStorage.setItem(KF, JSON.stringify(S.form)); } catch (e) { /* storage blocked: fine */ } }
async function load() {
  if (!lists) {
    const [roles, skills, personas] = await Promise.all([api.roles(), api.skills().catch(() => ({ skills: [] })), api.demoPersonas().catch(() => ({ personas: [] }))]);
    lists = { roles: roles.roles, skills: skills.skills, personas: personas.personas };
  }
  return lists;
}

// Kinds of work people can pick. Each belongs to one of the five groups the role matching understands (the tag).
const INTERESTS = [
  ["Helping and supporting people", "people"], ["Hiring and onboarding new joiners", "people"], ["Training and teaching others", "people"], ["Looking after customers", "people"], ["Coordinating a team", "people"],
  ["Working with numbers", "data"], ["Spreadsheets and reports", "data"], ["Finding patterns in data", "data"], ["Keeping accurate records", "data"], ["Charts and dashboards", "data"],
  ["Keeping things running smoothly", "operations"], ["Improving how work gets done", "operations"], ["Scheduling and logistics", "operations"], ["Vendors and supplies", "operations"], ["Office administration", "operations"],
  ["Planning and organising projects", "planning"], ["Setting priorities and deadlines", "planning"], ["Coordinating timelines", "planning"], ["Budgets and costs", "planning"],
  ["Following policies and rules", "compliance"], ["Checking quality", "compliance"], ["Risk and safety", "compliance"], ["Documentation and audits", "compliance"],
];
const tagsOf = (picks) => { const out = []; picks.forEach((l) => { const o = INTERESTS.find((x) => x[0] === l); if (o && !out.includes(o[1])) out.push(o[1]); }); return out; };

// Match what the person typed to the closest role we have. exact is true when the title is the same or contained.
const STOP = new Set(["and", "the", "of", "a", "an", "for", "to", "in", "senior", "junior", "lead", "manager", "executive", "officer", "associate", "assistant"]);
const words = (t) => String(t || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter((w) => w && !STOP.has(w));
export function matchRole(text, roles) {
  const t = String(text || "").trim().toLowerCase(); if (!t) return null;
  const exact = roles.find((r) => r.title.toLowerCase() === t || t.includes(r.title.toLowerCase()) || r.title.toLowerCase().includes(t) && t.length >= 4);
  if (exact) return { role: exact, exact: true };
  const w = new Set(words(t)); let best = null, score = 0;
  roles.forEach((r) => { const rw = words(r.title + " " + (r.family || "")); const n = rw.filter((x) => w.has(x)).length; if (n > score) { score = n; best = r; } });
  return best ? { role: best, exact: false } : null;
}

// The body for POST /profiles. Only contract fields. No age, date of birth, gender or years of experience anywhere.
export function buildBody() {
  const F = S.form, hrs = parseInt(F.hours, 10);
  const body = {
    display_name: (F.name || U.user.name).trim(), work_examples: F.examples.map((x) => x.trim()).filter(Boolean),
    declared_skills: F.skills.filter((s) => s.name.trim()).map((s) => ({ name: s.name.trim(), level: s.level })),
    preferences: { interests: tagsOf(F.picks), weekly_hours: hrs >= 1 && hrs <= 40 ? hrs : null },
    motivation: { styles: S.styles, check_in: S.checkIn, paused: S.paused }, consent: true,
  };
  if (F.role.trim()) body.current_role = F.role.trim();
  if (F.goal) body.stated_goal_role_id = F.goal;
  return body;
}
// Returns { step, msg, id } for the first thing missing on one step, or null. Required fields carry a * on screen.
const W0 = () => T.wiz;
function problemFor(step) {
  const F = S.form, X = U.x, W = W0();
  const bad = (msg, id) => ({ step, msg, id });
  if (step === 1) {
    if (!F.name.trim()) return bad(W.s1.needName, "f-name");
    if (F.phone.replace(/\D/g, "").length < 7) return bad(W.s1.needPhone, "f-phone");
    if (!/^\S+@\S+\.\S+$/.test(String(X.email || "").trim())) return bad(W.s1.needEmail, "f-email");
  }
  if (step === 2) {
    if (!F.role.trim()) return bad(W.s2.needRole, "f-role");
    if (!F.industry.trim()) return bad(W.s2.needIndustry, "f-ind");
    const ex = F.examples.map((x) => x.trim()).filter(Boolean);
    if (!ex.length || ex.some((x) => x.length < 10)) return bad(W.s2.need, "f-ex-0");
  }
  if (step === 3 && !F.skills.some((s) => s.name.trim())) return bad(W.s3.needSkill, "add-skill");
  if (step === 5 && !X.eduList.some((e) => (e.field || "").trim() || (e.institution || "").trim())) return bad(W.s5.needEdu, "edu-f-0");
  if (step === 6) {
    if (!F.goalText.trim()) return bad(W.s6.needGoal, "f-goal");
    if (!F.picks.length) return bad(W.s6.needInterest, "int-q");
  }
  if (step === 7 && !(X.situations || []).length) return bad(W.s7.needWhy, "why-group");
  if (step === 8) { const n = parseInt(F.hours, 10); if (!(n >= 1 && n <= 40)) return bad(W.s8.needHours, "f-hours"); }
  if (step === 9) {
    if (!X.formats.length) return bad(W.s9.needFormat, "fmt-group");
    if (S.styles.length < 1) return bad(W.s9.needStyle, "style-group");
  }
  return null;
}
export function firstProblem() {
  if (!S.form) return { step: 1, msg: T.wiz.fillAll };
  for (let s = 1; s <= 9; s++) { const p = problemFor(s); if (p) return p; }
  return null;
}
// The body for PUT /profiles/{id}/background: education, certificates, tools, barriers, situation, learning formats.
const FORMATS = { "Videos": "video", "Reading": "reading", "Hands-on practice": "hands_on", "Live sessions": "live" };
const cut = (v, n) => String(v || "").trim().slice(0, n);
export function backgroundBody() {
  const X = U.x, body = { education: [], certifications: [], languages: [], tools: [], barriers: [], learning_formats: [] };
  for (const e of X.eduList.slice(0, 5)) { if (!cut(e.field, 80) && !cut(e.institution, 80)) continue; const it = { level: e.level }; if (cut(e.field, 80)) it.field = cut(e.field, 80); if (cut(e.institution, 80)) it.institution = cut(e.institution, 80); body.education.push(it); }
  for (const c of X.certsHeld) { if (cut(c.name, 100)) { const it = { name: cut(c.name, 100) }; if (cut(c.issuer, 80)) it.issuer = cut(c.issuer, 80); body.certifications.push(it); } }
  body.certifications = body.certifications.slice(0, 10);
  body.languages = X.langs.map((v) => cut(v, 60)).filter(Boolean).slice(0, 8);
  body.tools = X.tools.map((v) => cut(v, 60)).filter(Boolean).slice(0, 20);
  body.barriers = X.barriers.slice(0, 7);
  body.learning_formats = X.formats.map((f) => FORMATS[f]).filter(Boolean);
  if ((X.situations || []).length) { body.situations = X.situations.slice(0, 5); body.situation = X.situations[0]; }
  return body;
}
// Weekly free/busy grid. Click a block to cycle: not set, free, busy. Also used on the Profile page.
export function scheduleGrid(onChange) {
  const t = T.wiz.s8, wrap = h("div", { class: "sched", role: "group", "aria-label": T.prof.sched });
  const next = { "": "free", free: "busy", busy: "" };
  wrap.append(h("div"), ...t.days.map((d) => h("div", { class: "h", text: d })));
  t.slots.forEach((slot, r) => {
    const label = t.slotLabels[r] || slot;
    wrap.append(h("div", { class: "r", text: label }));
    t.days.forEach((d, c) => {
      const key = `${c}-${r}`;
      const btn = h("button", { type: "button", "data-v": U.x.schedule[key] || "", "aria-label": `${d} ${label}: ${U.x.schedule[key] ? t[U.x.schedule[key]] : t.unset}`, onclick: () => {
        const v = next[U.x.schedule[key] || ""]; if (v) U.x.schedule[key] = v; else delete U.x.schedule[key];
        btn.dataset.v = v; btn.setAttribute("aria-label", `${d} ${label}: ${v ? t[v] : t.unset}`); saveExtras(); if (onChange) onChange();
      } });
      wrap.append(btn);
    });
  });
  return wrap;
}
export const scheduleLegend = () => h("div", { class: "legend" }, h("span", null, h("i", { style: "background:#bfe5c9" }), T.wiz.s8.free), h("span", null, h("i", { style: "background:#f6c9bd" }), T.wiz.s8.busy), h("span", null, h("i", { style: "background:#eef1f6" }), T.wiz.s8.unset), h("small", { text: T.wiz.s8.hint }));
// A list of short text items (tools) the person adds one by one.
function chips(list, placeholder, addLabel, label) {
  const box = h("div"), inp = h("input", { type: "text", maxlength: "60", placeholder, "aria-label": label });
  const paint = () => box.replaceChildren(h("div", { class: "pills", style: "margin-bottom:10px" }, list.map((v, i) => h("span", { class: "chip" }, v, h("button", { class: "linkbtn", type: "button", "aria-label": `${T.wiz.s3.remove} ${v}`, style: "margin-left:6px;text-decoration:none", text: "×", onclick: () => { list.splice(i, 1); saveExtras(); paint(); } })))));
  const add = () => { const v = inp.value.trim(); if (v && !list.includes(v) && list.length < 20) { list.push(v); inp.value = ""; saveExtras(); paint(); } };
  inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); add(); } });
  paint();
  return h("div", null, box, h("div", { class: "row" }, h("div", { style: "flex:1;min-width:200px" }, inp), h("button", { class: "btn ghost", type: "button", text: addLabel, onclick: add })));
}
// How well do you know it: a small three-way switch, with what the chosen level means shown beside it.
function levelPick(name, level, onchange, label) {
  const hints = T.wiz.s3.levelHelp, seg = h("div", { class: "lvl2", role: "radiogroup", "aria-label": label }), hint = h("span", { class: "lvhint", "aria-live": "polite" });
  const paint = (cur) => { hint.textContent = hints[cur] || ""; };
  LEVELS.forEach((l) => seg.append(h("label", null, h("input", { type: "radio", name, value: String(l), checked: l === level, onchange: () => { onchange(l); paint(l); } }), h("span", { text: T.levels[l] }))));
  paint(level); return h("div", { class: "lvlcell" }, seg, hint);
}
// Search plus removable tags. Picking adds a tag, the x removes it, and the list of choices updates each time.
function tagPicker(F) {
  const t = T.wiz.s6, q = h("input", { type: "search", id: "int-q", placeholder: t.search, "aria-label": t.search, autocomplete: "off" });
  const sel = h("div", { class: "tagpick", "aria-live": "polite" }), opts = h("div", { class: "tagpick" });
  const paint = () => {
    sel.replaceChildren(...(F.picks.length ? F.picks.map((l) => h("span", { class: "tag-sel" }, l, h("button", { type: "button", "aria-label": `${t.remove} ${l}`, text: "×", onclick: () => { F.picks = F.picks.filter((x) => x !== l); saveForm(); paint(); } })))
      : [h("span", { class: "hint", style: "margin:0", text: t.nonePicked })]));
    const needle = q.value.trim().toLowerCase();
    const shown = INTERESTS.filter(([l]) => !F.picks.includes(l) && (!needle || l.toLowerCase().includes(needle)));
    opts.replaceChildren(...(shown.length ? shown.map(([l]) => h("button", { class: "opt-btn", type: "button", text: "+ " + l, onclick: () => { F.picks = [...F.picks, l]; saveForm(); paint(); } })) : [h("span", { class: "hint", style: "margin:0", text: t.noResults })]));
  };
  q.addEventListener("input", paint); paint();
  return h("div", null, h("p", { class: "lbl", style: "margin:0 0 6px;font-weight:600", text: t.picked }), sel, h("div", { class: "optbox" }, q, opts));
}

export default async function wizard(arg) {
  const L = await load();
  if (!S.form) S.form = loadForm() || blank();
  const stepArg = parseInt(arg, 10);
  const step = Math.min(9, Math.max(1, stepArg || U.x.step || 1));
  U.x.step = step; saveExtras();
  const F = S.form, X = U.x, W = T.wiz;
  if (!F.name) F.name = U.user.name;
  if (!X.email) X.email = U.user.email || "";
  const editing = !!S.profileId;
  const root = h("div", { class: "wiz" });
  let focusLast = null, msg = null, warn = true, focusId = null;
  const bind = (key) => (e) => { F[key] = e.target.value; saveForm(); };
  const inp = (id, key, extra) => h("input", Object.assign({ type: "text", id, value: F[key], oninput: bind(key) }, extra || {}));

  const aside = h("aside", { "aria-label": "Profile steps" }, h("small", { text: W.stepOf(step) }),
    h("ol", null, W.steps.map((name, i) => h("li", { class: i + 1 < step ? "done" : i + 1 === step ? "here" : "" },
      h("a", { href: `#/onboard/${i + 1}`, style: "display:flex;gap:12px;align-items:center;color:inherit;text-decoration:none", "aria-current": i + 1 === step ? "step" : null }, h("span", { class: "n", text: i + 1 < step ? "✓" : String(i + 1) }), name)))));

  function fill(p) {
    if (!p) return;
    const goalRole = L.roles.find((r) => r.role_id === p.stated_goal_role_id);
    Object.assign(F, { name: p.display_name, role: p.current_role || "", industry: F.industry || "IT", phone: F.phone || "9000000000", examples: p.work_examples.slice(0, 5), skills: p.declared_skills.map((s) => ({ name: s.name, level: s.level })), goal: p.stated_goal_role_id || "", goalText: goalRole ? goalRole.title : F.goalText, hours: F.hours || "6" });
    if (!F.picks.length) F.picks = ["Helping and supporting people", "Office administration"];
    if (!X.eduList.some((e) => e.field || e.institution)) X.eduList = [{ level: "bachelor", field: "Commerce", institution: "City college" }];
    if (!(X.situations || []).length) X.situations = ["promotion"];
    if (!X.formats.length) X.formats = ["Videos"];
    if (!S.styles.length) S.styles = ["progress", "encouragement"];
    saveExtras(); saveForm(); msg = W.s2.demoFilled; warn = false; draw();
  }
  function s1() {
    const email = h("input", { type: "email", id: "f-email", value: X.email, autocomplete: "email", oninput: (e) => { X.email = e.target.value; saveExtras(); } });
    const phone = h("input", { type: "tel", id: "f-phone", value: F.phone, inputmode: "tel", autocomplete: "tel", maxlength: "20", oninput: bind("phone") });
    return [ask(W.s1.name, W.s1.nameHelp, inp("f-name", "name", { maxlength: "60", autocomplete: "name" }), { req: true }), ask(W.s1.phone, W.s1.phoneHelp, phone, { req: true }), ask(W.s1.email, W.s1.emailHelp, email, { req: true })];
  }
  function s2() {
    const cvMsg = h("p", { class: "small", role: "status" });
    const paste = h("textarea", { id: "cv-paste", maxlength: "20000", placeholder: W.s2.cvPastePh, "aria-label": W.s2.cvPaste, style: "min-height:110px" });
    const readBtn = h("button", { class: "btn ghost small", type: "button", text: W.s2.cvReadBtn });
    const read = async (text) => {
      if (text.trim().length < 40) { cvMsg.textContent = W.s2.cvShort; return; }
      cvMsg.textContent = W.s2.cvReading; readBtn.disabled = true;
      try { applyCv(await api.parseCv(text)); } catch (e) { cvMsg.textContent = W.s2.cvFail; } finally { readBtn.disabled = false; }
    };
    const applyCv = (r) => {
      if (r.current_role && !F.role.trim()) F.role = r.current_role;
      if (r.work_examples.length) F.examples = r.work_examples.slice(0, 5).map((x) => x.slice(0, 1000));
      if (r.skills.length) F.skills = r.skills.slice(0, 30).map((n) => ({ name: n.slice(0, 80), level: 2 }));
      if (r.tools.length) X.tools = r.tools.slice(0, 20);
      if (r.certifications.length) X.certsHeld = r.certifications.slice(0, 10).map((c) => ({ name: c.name, issuer: c.issuer || "" }));
      if (r.languages.length) X.langs = r.languages.slice(0, 8);
      const eds = r.education.filter((e) => e.level).slice(0, 5).map((e) => ({ level: e.level, field: e.field || "", institution: e.institution || "" }));
      if (eds.length) X.eduList = eds;
      saveExtras(); saveForm();
      const found = (r.work_examples.length || r.skills.length) ? "" : W.s2.cvNothing;
      msg = found || W.s2.cvDone(r.ignored_lines ? W.s2.cvIgnored(r.ignored_lines) : ""); warn = !!found; draw();
    };
    readBtn.addEventListener("click", () => read(paste.value));
    const file = h("input", { type: "file", id: "cv-file", accept: ".txt,.md,.pdf,.doc,.docx", "aria-label": W.s2.cvBtn, style: "max-width:260px" });
    file.addEventListener("change", async () => {
      const f = file.files[0]; if (!f) return;
      cvMsg.textContent = W.s2.cvReading;
      let text; try { text = await readCvText(f); } catch (e) { cvMsg.textContent = e && e.code === "VALIDATION_ERROR" ? e.message : W.s2.cvFail; return; }
      if (text === null) { cvMsg.textContent = W.s2.cvOther; return; }
      paste.value = text; read(text);
    });
    const sel = h("select", { id: "demo-sel", "aria-label": W.s2.demoBtn }, L.personas.map((p) => h("option", { value: p.persona_id, text: `${p.display_name}, ${p.current_role}` })));
    const an = L.personas.find((p) => p.display_name === "Anitha Raman"); if (an) sel.value = an.persona_id;
    const examples = F.examples.map((val, i) => {
      const cnt = h("div", { class: "counter", text: `${val.length} / 1000` });
      const ta = h("textarea", { id: `f-ex-${i}`, class: "ex", maxlength: "1000", placeholder: W.s2.taskPh, "aria-label": W.s2.task(i + 1), value: val, oninput: (e) => { F.examples[i] = e.target.value; saveForm(); cnt.textContent = `${e.target.value.length} / 1000`; } });
      return h("div", { class: "field" }, h("div", { class: "row between" }, h("label", { for: ta.id, style: "font-weight:600", text: W.s2.task(i + 1) }), F.examples.length > 1 ? trash(W.s2.remove, () => { F.examples.splice(i, 1); saveForm(); draw(); }) : null), ta, cnt);
    });
    return [h("div", { class: "cv-box" }, ill("cv", 64), h("div", { style: "flex:1;min-width:240px" }, h("b", { text: W.s2.cvTitle }), h("p", { class: "small muted", text: W.s2.cvHelp }), h("div", { style: "margin-top:10px" }, file), h("div", { class: "field", style: "margin-top:12px" }, h("label", { for: "cv-paste", text: W.s2.cvPaste }), paste, h("div", { style: "margin-top:8px" }, readBtn)), cvMsg)),
      h("div", { class: "row", style: "margin-top:12px" }, h("div", { style: "min-width:240px;flex:1" }, sel), h("button", { class: "btn ghost small", type: "button", text: W.s2.demoBtn, onclick: () => fill(L.personas.find((p) => p.persona_id === sel.value)) })),
      h("div", { style: "margin-top:24px" }, ask(W.s2.role, W.s2.roleHelp, inp("f-role", "role", { maxlength: "80" }), { req: true }), ask(W.s2.industry, W.s2.industryHelp, inp("f-ind", "industry", { maxlength: "60" }), { req: true })),
      h("div", { class: "field q", style: "margin-top:24px" }, h("p", { class: "qt" }, W.s2.tasksTitle, h("span", { class: "req", "aria-hidden": "true", text: " *" })), h("p", { class: "hint", text: W.s2.tasksHelp })), examples,
      F.examples.length < 5 ? h("button", { class: "btn ghost small", type: "button", text: W.s2.add, onclick: () => { F.examples.push(""); saveForm(); focusLast = "textarea.ex"; draw(); } }) : null];
  }
  function s3() {
    const rows = F.skills.map((s, i) => h("div", { class: "srow" },
      h("input", { type: "text", class: "sname", list: "skill-names", maxlength: "80", "aria-label": `${W.s3.skill} ${i + 1}`, value: s.name, oninput: (e) => { s.name = e.target.value; saveForm(); } }),
      levelPick(`lv-${i}`, s.level, (l) => { s.level = l; saveForm(); }, `${W.s3.level} ${i + 1}`),
      trash(W.s3.remove, () => { F.skills.splice(i, 1); saveForm(); draw(); })));
    const table = rows.length ? h("div", { class: "skilltable" }, h("div", { class: "shead", "aria-hidden": "true" }, h("span", { text: W.s3.skill }), h("span", { text: W.s3.level }), h("span"), h("span")), ...rows) : null;
    const addBtn = F.skills.length < 30 ? h("button", { id: "add-skill", class: "btn ghost small", type: "button", text: W.s3.add, onclick: () => { F.skills.push({ name: "", level: 2 }); saveForm(); focusLast = "input[list]"; draw(); } }) : null;
    return [h("div", { class: "field q" }, h("p", { class: "qt" }, W.s3.skillsTitle, h("span", { class: "req", "aria-hidden": "true", text: " *" })), h("p", { class: "hint", text: W.s3.skillsHelp }), F.skills.length ? h("p", { class: "hint", text: W.s3.fromCv }) : null),
      table, h("datalist", { id: "skill-names" }, L.skills.map((s) => h("option", { value: s.name }))), addBtn,
      h("div", { style: "margin-top:28px" }, ask(W.s3.toolsTitle, W.s3.toolsHelp, chips(X.tools, W.s3.toolPh, W.s3.addTool, W.s3.toolsTitle), { forId: "none" }))];
  }
  function s4() {
    return [h("div", { class: "stack" }, X.certsHeld.map((c, i) => h("div", { class: "row", style: "align-items:flex-end" },
      h("div", { style: "flex:2;min-width:200px" }, ask(W.s4.name, null, h("input", { type: "text", id: `ch-n-${i}`, maxlength: "100", value: c.name, oninput: (e) => { c.name = e.target.value; saveExtras(); } }))),
      h("div", { style: "flex:1;min-width:160px" }, ask(W.s4.issuer, null, h("input", { type: "text", id: `ch-i-${i}`, maxlength: "80", value: c.issuer, oninput: (e) => { c.issuer = e.target.value; saveExtras(); } }))),
      X.certsHeld.length > 1 ? trash(W.s4.remove, () => { X.certsHeld.splice(i, 1); saveExtras(); draw(); }) : null))),
      X.certsHeld.length < 10 ? h("button", { class: "btn ghost small", type: "button", text: W.s4.add, onclick: () => { X.certsHeld.push({ name: "", issuer: "" }); saveExtras(); draw(); } }) : null];
  }
  function s5() {
    const rows = X.eduList.map((e, i) => {
      if (!W.s5.levels.some((o) => o[0] === e.level)) e.level = "bachelor";
      const lv = h("select", { id: `edu-l-${i}`, "aria-label": W.s5.level, onchange: (ev) => { e.level = ev.target.value; saveExtras(); }, value: e.level }, W.s5.levels.map(([v, l]) => h("option", { value: v, text: l })));
      return h("div", { class: "edurow" }, ask(W.s5.level, null, lv, { req: i === 0 }),
        ask(W.s5.field, null, h("input", { type: "text", id: `edu-f-${i}`, maxlength: "80", value: e.field || "", oninput: (ev) => { e.field = ev.target.value; saveExtras(); } })),
        ask(W.s5.institution, null, h("input", { type: "text", id: `edu-i-${i}`, maxlength: "80", value: e.institution || "", oninput: (ev) => { e.institution = ev.target.value; saveExtras(); } })),
        X.eduList.length > 1 ? trash(W.s5.remove, () => { X.eduList.splice(i, 1); saveExtras(); draw(); }) : h("span"));
    });
    const order = W.s5.levels.map((l) => l[0]);
    return [h("div", { class: "stack" }, rows), X.eduList.length < 5 ? h("button", { class: "btn ghost small", type: "button", text: W.s5.add, onclick: () => { const used = X.eduList.map((e) => e.level); X.eduList.push({ level: order.find((l) => !used.includes(l)) || "diploma", field: "", institution: "" }); saveExtras(); draw(); } }) : null];
  }
  function s6() {
    const goalNote = h("p", { class: "hint", role: "status", style: "margin:6px 0 0" });
    const showMatch = () => {
      const txt = F.goalText.trim(); F.goal = ""; goalNote.textContent = "";
      if (!txt) return;
      const m = matchRole(txt, L.roles);
      if (m) { F.goal = m.role.role_id; goalNote.textContent = m.exact ? "" : W.s6.goalClosest(txt, m.role.title); } else goalNote.textContent = W.s6.goalNone(txt);
    };
    const goal = h("input", { type: "text", id: "f-goal", list: "role-names", maxlength: "80", placeholder: W.s6.goalPh, value: F.goalText, oninput: (e) => { F.goalText = e.target.value; showMatch(); saveForm(); } });
    showMatch();
    return [ask(W.s6.goal, W.s6.goalHelp, h("div", null, goal, h("datalist", { id: "role-names" }, L.roles.map((r) => h("option", { value: r.title }))), goalNote), { req: true, forId: "f-goal" }),
      ask(W.s6.interests, W.s6.interestsHelp, tagPicker(F), { req: true, forId: "int-q" })];
  }
  function s7() {
    const why = h("div", { class: "choices", id: "why-group", role: "group", "aria-label": W.s7.why }, W.s7.whyOpts.map(([k, label]) => choice("checkbox", "why", label, "", (X.situations || []).includes(k), (e) => { const cur = X.situations || []; X.situations = e.target.checked ? [...cur, k] : cur.filter((x) => x !== k); saveExtras(); })));
    const barriers = h("div", { class: "choices", role: "group", "aria-label": W.s7.barriers }, W.s7.barrierOpts.map(([k, label]) =>
      choice("checkbox", "barrier", label, "", X.barriers.includes(k), (e) => { X.barriers = e.target.checked ? [...X.barriers, k] : X.barriers.filter((x) => x !== k); saveExtras(); })));
    return [ask(W.s7.why, W.s7.whyHelp, why, { req: true, forId: "none" }), ask(W.s7.barriers, W.s7.barriersHelp, barriers, { forId: "none" })];
  }
  function s8() {
    const hours = h("input", { type: "number", id: "f-hours", min: "1", max: "40", inputmode: "numeric", value: F.hours, oninput: bind("hours"), style: "max-width:140px" });
    return [h("div", { class: "stack" }, scheduleLegend(), scheduleGrid()),
      h("div", { style: "margin-top:34px;max-width:420px" }, ask(W.s8.hours, W.s8.hoursHelp, hours, { req: true }))];
  }
  function s9() {
    const fmts = h("div", { id: "fmt-group" }, pills("fmt", W.s9.formatOpts, X.formats, (o, on) => { X.formats = on ? [...X.formats, o] : X.formats.filter((x) => x !== o); saveExtras(); }));
    const grid = h("div", { class: "choices", id: "style-group" }, Object.keys(T.styles).map((k) => choice("checkbox", "mstyle", T.styles[k], T.styleHelp[k], S.styles.includes(k),
      (e) => { S.styles = e.target.checked ? [...S.styles, k] : S.styles.filter((x) => x !== k); })));
    const note = h("p", { class: "hint", role: "status", text: S.paused ? W.s9.pauseOn : W.s9.pauseOff });
    return [ask(W.s9.formats, W.s9.formatsHelp, fmts, { req: true, forId: "none" }), ask(W.s9.styleTitle, W.s9.styleHelp, grid, { req: true, forId: "none" }),
      ask(W.s9.checkIn, null, h("div", { class: "seg", role: "radiogroup" }, Object.entries(T.checkIn).map(([v, l]) => h("label", null, h("input", { type: "radio", name: "checkin", value: v, checked: S.checkIn === v, onchange: () => { S.checkIn = v; } }), h("span", { text: l })))), { forId: "none" }),
      h("div", { class: "field" }, toggle(W.s9.pause, "", S.paused, (v) => { const was = S.paused; S.paused = v; note.textContent = v ? W.s9.pauseOn : (was ? W.s9.resumed : W.s9.pauseOff); }), note)];
  }
  const STEPS = [s1, s2, s3, s4, s5, s6, s7, s8, s9];
  function next() {
    const p = step === 9 ? firstProblem() : problemFor(step);
    if (p) {
      msg = `${W.fillAll} ${p.msg}`; warn = true; focusId = p.id;
      if (p.step !== step) { S.flash = msg; go(`#/onboard/${p.step}`); } else draw();
      return;
    }
    if (step === 9) { S.flash = W.s9.mailNote; X.mail = true; saveExtras(); }
    go(step === 9 ? "#/building" : `#/onboard/${step + 1}`);
  }
  const bodyT = [W.s1, W.s2, W.s3, W.s4, W.s5, W.s6, W.s7, W.s8, W.s9][step - 1];
  function draw() {
    const main = h("section", { class: "wmain" }, h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem", text: bodyT.title }), h("p", { class: "lead", style: "margin:8px 0 22px", text: bodyT.lead }),
      msg ? h("div", { class: "note" + (warn ? " warn" : ""), role: "alert", text: msg }) : null, h("div", { class: "stack" }, STEPS[step - 1]()),
      h("div", { class: "foot" }, step > 1 ? h("a", { class: "btn ghost", href: `#/onboard/${step - 1}`, text: W.back }) : h("span"), h("button", { class: "btn" + (step === 9 ? " org" : ""), type: "button", text: step === 9 ? (editing ? W.edit : W.finish) : W.next, onclick: next })));
    root.replaceChildren(aside, main);
    saveForm();
    if (focusLast) { const els = root.querySelectorAll(focusLast); if (els.length) els[els.length - 1].focus(); focusLast = null; }
    if (focusId) { const el = root.querySelector("#" + focusId); if (el) { el.classList.add("invalid"); if (el.focus) el.focus(); } focusId = null; }
  }
  draw();
  return root;
}
