// Profile questions: nine short steps. Fields the contract has go to the backend (see buildBody).
// Fields it does not have yet (tools, languages, schedule, email time ...) are kept in store.js and shown on the Profile page.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { U, saveExtras } from "../store.js";
import { readCv } from "../slots.js";
import { h, go, field, choice, seg, toggle, levelWord, pills } from "../ui.js";
import { ill } from "../art.js";

const LEVELS = [1, 2, 3];
let lists = null;
const blank = () => ({ name: "", role: "", examples: [""], skills: [], goal: "", hours: "", interests: [] });
async function load() {
  if (!lists) {
    const [roles, skills, personas] = await Promise.all([api.roles(), api.skills().catch(() => ({ skills: [] })), api.demoPersonas().catch(() => ({ personas: [] }))]);
    lists = { roles: roles.roles, skills: skills.skills, personas: personas.personas };
  }
  return lists;
}
// The body for POST /profiles. Only contract fields. No age, date of birth, gender or years of experience anywhere.
export function buildBody() {
  const F = S.form, hrs = parseInt(F.hours, 10);
  const body = {
    display_name: (F.name || U.user.name).trim(), work_examples: F.examples.map((x) => x.trim()).filter(Boolean),
    declared_skills: F.skills.filter((s) => s.name.trim()).map((s) => ({ name: s.name.trim(), level: s.level })),
    preferences: { interests: F.interests, weekly_hours: hrs >= 1 && hrs <= 40 ? hrs : null },
    motivation: { styles: S.styles, check_in: S.checkIn, paused: S.paused }, consent: true,
  };
  if (F.role.trim()) body.current_role = F.role.trim();
  if (F.goal) body.stated_goal_role_id = F.goal;
  return body;
}
// Returns { step, msg } for the first thing missing, or null.
export function firstProblem() {
  const F = S.form, ex = F.examples.map((x) => x.trim()).filter(Boolean);
  if (!ex.length || ex.some((x) => x.length < 10)) return { step: 1, msg: T.wiz.s1.need };
  if (S.styles.length < 1) return { step: 8, msg: T.wiz.s8.needStyle };
  if (!S.consent) return { step: 9, msg: T.wiz.s9.needConsent };
  return null;
}
// Weekly free/busy grid. Click a block to cycle: not set, free, busy. Also used on the Profile page.
export function scheduleGrid(onChange) {
  const t = T.wiz.s7, wrap = h("div", { class: "sched", role: "group", "aria-label": T.prof.sched });
  const next = { "": "free", free: "busy", busy: "" };
  wrap.append(h("div"), ...t.days.map((d) => h("div", { class: "h", text: d })));
  t.slots.forEach((label, r) => {
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
export const scheduleLegend = () => h("div", { class: "legend" }, h("span", null, h("i", { style: "background:#bfe5c9" }), T.wiz.s7.free), h("span", null, h("i", { style: "background:#f6c9bd" }), T.wiz.s7.busy), h("span", null, h("i", { style: "background:#eef1f6" }), T.wiz.s7.unset), h("small", { text: T.wiz.s7.hint }));
// A list of short text items (tools, languages) the person adds one by one.
function chips(list, placeholder, addLabel, label) {
  const box = h("div"), inp = h("input", { type: "text", maxlength: "60", placeholder, "aria-label": label });
  const paint = () => box.replaceChildren(h("div", { class: "pills", style: "margin-bottom:10px" }, list.map((v, i) => h("span", { class: "chip" }, v, h("button", { class: "linkbtn", type: "button", "aria-label": `${T.wiz.s2.remove} ${v}`, style: "margin-left:6px;text-decoration:none", text: "×", onclick: () => { list.splice(i, 1); saveExtras(); paint(); } })))));
  const add = () => { const v = inp.value.trim(); if (v && !list.includes(v) && list.length < 20) { list.push(v); inp.value = ""; saveExtras(); paint(); } };
  inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); add(); } });
  paint();
  return h("div", null, box, h("div", { class: "row" }, h("div", { style: "flex:1;min-width:200px" }, inp), h("button", { class: "btn ghost", type: "button", text: addLabel, onclick: add })));
}

export default async function wizard(arg) {
  const L = await load();
  const step = Math.min(9, Math.max(1, parseInt(arg, 10) || 1));
  if (!S.form) S.form = blank();
  const F = S.form, X = U.x, W = T.wiz;
  if (!F.name) F.name = U.user.name;
  const editing = !!S.profileId;
  const root = h("div", { class: "wiz" });
  let focusLast = null, msg = null, warn = true;
  const bind = (key) => (e) => { F[key] = e.target.value; };

  const aside = h("aside", { "aria-label": "Profile steps" }, h("small", { text: W.stepOf(step) }),
    h("ol", null, W.steps.map((name, i) => h("li", { class: i + 1 < step ? "done" : i + 1 === step ? "here" : "" },
      h("a", { href: `#/onboard/${i + 1}`, style: "display:flex;gap:12px;align-items:center;color:inherit;text-decoration:none", "aria-current": i + 1 === step ? "step" : null }, h("span", { class: "n", text: i + 1 < step ? "✓" : String(i + 1) }), name)))));

  function fill(p) {
    if (!p) return;
    Object.assign(F, { name: p.display_name, role: p.current_role || "", examples: p.work_examples.slice(0, 5), skills: p.declared_skills.map((s) => ({ name: s.name, level: s.level })), goal: p.stated_goal_role_id || "", hours: F.hours || "6" });
    msg = W.s1.demoFilled; warn = false; draw();
  }
  function s1() {
    const cvMsg = h("p", { class: "small", role: "status" });
    const file = h("input", { type: "file", id: "cv-file", accept: ".txt,.md,.pdf,.doc,.docx", "aria-label": W.s1.cvBtn, style: "max-width:260px" });
    file.addEventListener("change", async () => {
      const f = file.files[0]; if (!f) return;
      const lines = await readCv(f);
      if (lines && lines.length) { F.examples = lines; cvMsg.textContent = W.s1.cvRead(lines.length); draw(); } else cvMsg.textContent = W.s1.cvOther;
    });
    const sel = h("select", { id: "demo-sel", "aria-label": W.s1.demoBtn }, L.personas.map((p) => h("option", { value: p.persona_id, text: `${p.display_name}, ${p.current_role}` })));
    const an = L.personas.find((p) => p.display_name === "Anitha Raman"); if (an) sel.value = an.persona_id;
    const examples = F.examples.map((val, i) => {
      const cnt = h("div", { class: "counter", text: `${val.length} / 1000` });
      const ta = h("textarea", { id: `f-ex-${i}`, class: "ex", maxlength: "1000", "aria-label": W.s1.example(i + 1), value: val, oninput: (e) => { F.examples[i] = e.target.value; cnt.textContent = `${e.target.value.length} / 1000`; } });
      return h("div", { class: "field" }, h("div", { class: "row between" }, h("label", { for: ta.id, text: W.s1.example(i + 1) }), F.examples.length > 1 ? h("button", { class: "linkbtn", type: "button", text: W.s1.remove, onclick: () => { F.examples.splice(i, 1); draw(); } }) : null), ta, cnt);
    });
    return [h("div", { class: "cv-box" }, ill("cv", 64), h("div", { style: "flex:1;min-width:240px" }, h("b", { text: W.s1.cvTitle }), h("p", { class: "small muted", text: W.s1.cvHelp }), h("div", { style: "margin-top:10px" }, file), cvMsg)),
      h("div", { class: "row", style: "margin-top:12px" }, h("div", { style: "min-width:240px;flex:1" }, sel), h("button", { class: "btn ghost small", type: "button", text: W.s1.demoBtn, onclick: () => fill(L.personas.find((p) => p.persona_id === sel.value)) })),
      h("div", { class: "cols2", style: "margin-top:20px" }, field(W.s1.role, h("input", { type: "text", id: "f-role", maxlength: "80", value: F.role, oninput: bind("role") })), field(W.s1.industry, h("input", { type: "text", id: "f-ind", maxlength: "60", value: X.industry, oninput: (e) => { X.industry = e.target.value; saveExtras(); } }))),
      h("div", { style: "margin-top:20px" }, h("h3", { style: "font-size:1.15rem", text: W.s1.examplesTitle }), h("p", { class: "hint", text: W.s1.examplesHelp })), examples,
      F.examples.length < 5 ? h("button", { class: "btn ghost small", type: "button", text: W.s1.add, onclick: () => { F.examples.push(""); focusLast = "textarea.ex"; draw(); } }) : null];
  }
  function s2() {
    const rows = F.skills.map((s, i) => h("div", { class: "row", style: "align-items:flex-end;margin-bottom:10px" },
      h("div", { style: "flex:2;min-width:180px" }, h("input", { type: "text", list: "skill-names", maxlength: "80", "aria-label": `${W.s2.skill} ${i + 1}`, value: s.name, oninput: (e) => { s.name = e.target.value; } })),
      h("div", { style: "flex:1;min-width:150px" }, h("select", { "aria-label": `${W.s2.level} ${i + 1}`, value: String(s.level), onchange: (e) => { s.level = Number(e.target.value); } }, LEVELS.map((l) => h("option", { value: String(l), text: levelWord(l) })))),
      h("button", { class: "linkbtn", type: "button", text: W.s2.remove, onclick: () => { F.skills.splice(i, 1); draw(); } })));
    return [h("h3", { style: "font-size:1.15rem", text: W.s2.skillsTitle }), rows, h("datalist", { id: "skill-names" }, L.skills.map((s) => h("option", { value: s.name }))),
      F.skills.length < 30 ? h("button", { class: "btn ghost small", type: "button", text: W.s2.add, onclick: () => { F.skills.push({ name: "", level: 2 }); focusLast = "input[list]"; draw(); } }) : null,
      h("div", { style: "margin-top:26px" }, h("h3", { style: "font-size:1.15rem", text: W.s2.toolsTitle }), h("p", { class: "hint", text: W.s2.toolsHelp }), chips(X.tools, W.s2.toolPh, W.s2.addTool, W.s2.toolsTitle))];
  }
  function s3() {
    return [h("div", { class: "stack" }, X.certsHeld.map((c, i) => h("div", { class: "row", style: "align-items:flex-end" },
      h("div", { style: "flex:2;min-width:200px" }, field(W.s3.name, h("input", { type: "text", id: `ch-n-${i}`, maxlength: "100", value: c.name, oninput: (e) => { c.name = e.target.value; saveExtras(); } }))),
      h("div", { style: "flex:1;min-width:160px" }, field(W.s3.issuer, h("input", { type: "text", id: `ch-i-${i}`, maxlength: "80", value: c.issuer, oninput: (e) => { c.issuer = e.target.value; saveExtras(); } }))),
      X.certsHeld.length > 1 ? h("button", { class: "linkbtn", type: "button", text: W.s3.remove, onclick: () => { X.certsHeld.splice(i, 1); saveExtras(); draw(); } }) : null))),
      X.certsHeld.length < 10 ? h("button", { class: "btn ghost small", type: "button", text: W.s3.add, onclick: () => { X.certsHeld.push({ name: "", issuer: "" }); saveExtras(); draw(); } }) : null];
  }
  function s4() {
    const edu = h("select", { id: "f-edu", onchange: (e) => { X.edu = e.target.value; saveExtras(); }, value: X.edu }, W.s4.eduOpts.map((o) => h("option", { value: o, text: o })));
    return [h("div", { class: "cols2" }, field(W.s4.edu, edu), field(W.s4.field, h("input", { type: "text", id: "f-field", maxlength: "80", value: X.field, oninput: (e) => { X.field = e.target.value; saveExtras(); } }))),
      h("div", { style: "margin-top:20px" }, h("h3", { style: "font-size:1.15rem;margin-bottom:10px", text: W.s4.langs }), chips(X.langs, W.s4.langPh, W.s2.addTool, W.s4.langs))];
  }
  function s5() {
    const goal = h("select", { id: "f-goal", onchange: bind("goal"), value: F.goal }, h("option", { value: "", text: W.s5.goalNone }), L.roles.map((r) => h("option", { value: r.role_id, text: r.title })));
    const interests = h("div", { class: "choices", role: "group", "aria-label": W.s5.interests }, Object.entries(T.s2.interests).map(([k, label]) =>
      choice("checkbox", "interest", label, "", F.interests.includes(k), (e) => { F.interests = e.target.checked ? [...F.interests, k] : F.interests.filter((x) => x !== k); draw(); }, !F.interests.includes(k) && F.interests.length >= 3)));
    return [field(W.s5.goal, goal, { hint: W.s5.goalHelp }), h("div", { class: "field" }, h("p", { class: "lbl", text: W.s5.interests }), h("p", { class: "hint", text: W.s5.interestsHelp }), interests),
      h("div", { class: "field" }, h("p", { class: "lbl", text: W.s5.direction }), seg("dir", W.s5.dirOpts, X.direction, (v) => { X.direction = v; saveExtras(); }))];
  }
  function s6() {
    return [h("div", { class: "field" }, h("p", { class: "lbl", text: W.s6.why }), pills("why", W.s6.whyOpts, X.why, (o, on) => { X.why = on ? [...X.why, o] : X.why.filter((x) => x !== o); saveExtras(); })),
      field(W.s6.limits, h("textarea", { id: "f-limits", maxlength: "500", placeholder: W.s6.limitsPh, value: X.limits, oninput: (e) => { X.limits = e.target.value; saveExtras(); } }))];
  }
  function s7() {
    const hours = h("input", { type: "number", id: "f-hours", min: "1", max: "40", inputmode: "numeric", value: F.hours, oninput: bind("hours"), style: "max-width:140px" });
    const by = h("select", { id: "f-by", onchange: (e) => { X.finishBy = e.target.value; saveExtras(); }, value: X.finishBy }, W.s7.byOpts.map((o) => h("option", { value: o, text: o })));
    return [h("div", { class: "split", style: "grid-template-columns:1.4fr 1fr" }, h("div", { class: "stack" }, scheduleLegend(), scheduleGrid()),
      h("div", { class: "stack" }, field(W.s7.hours, hours, { hint: W.s7.hoursHelp }), h("div", { class: "field" }, h("p", { class: "lbl", text: W.s7.best }), pills("best", W.s7.bestOpts, X.best, (o, on) => { X.best = on ? [...X.best, o] : X.best.filter((x) => x !== o); saveExtras(); })), field(W.s7.by, by)))];
  }
  function s8() {
    const grid = h("div", { class: "choices" }, Object.keys(T.styles).map((k) => choice("checkbox", "mstyle", T.styles[k], T.styleHelp[k], S.styles.includes(k),
      (e) => { S.styles = e.target.checked ? [...S.styles, k].slice(0, 2) : S.styles.filter((x) => x !== k); draw(); }, !S.styles.includes(k) && S.styles.length >= 2)));
    return [h("div", { class: "field" }, h("p", { class: "lbl", text: W.s8.formats }), pills("fmt", W.s8.formatOpts, X.formats, (o, on) => { X.formats = on ? [...X.formats, o] : X.formats.filter((x) => x !== o); saveExtras(); })),
      h("div", { class: "field" }, h("p", { class: "lbl", text: W.s8.styleTitle }), h("p", { class: "hint", text: W.s8.styleHelp }), grid),
      h("div", { class: "field" }, h("p", { class: "lbl", text: W.s8.checkIn }), seg("checkin", Object.entries(T.checkIn), S.checkIn, (v) => { S.checkIn = v; })),
      h("div", { class: "field" }, toggle(W.s8.pause, W.s8.pauseHelp, S.paused, (v) => { S.paused = v; }))];
  }
  function s9() {
    const time = h("input", { type: "time", id: "f-mt", value: X.mailTime, style: "max-width:160px", onchange: (e) => { X.mailTime = e.target.value; saveExtras(); } });
    const lang = h("select", { id: "f-lang", onchange: (e) => { X.lang = e.target.value; saveExtras(); }, value: X.lang }, W.s9.langOpts.map((o) => h("option", { value: o, text: o })));
    const consent = h("input", { type: "checkbox", id: "f-consent", checked: S.consent, onchange: (e) => { S.consent = e.target.checked; } });
    return [h("div", { class: "field" }, toggle(W.s9.mail, W.s9.mailHelp, X.mail, (v) => { X.mail = v; saveExtras(); })), field(W.s9.mailTime, time),
      h("div", { class: "field" }, h("p", { class: "lbl", text: W.s9.access }), pills("acc", W.s9.accessOpts, X.access, (o, on) => { X.access = on ? [...X.access, o] : X.access.filter((x) => x !== o); saveExtras(); })), field(W.s9.lang, lang),
      h("label", { class: "check card", style: "margin-top:20px" }, consent, h("span", { text: W.s9.consent })), h("p", { class: "small faint", text: W.s9.privacy })];
  }
  const STEPS = [s1, s2, s3, s4, s5, s6, s7, s8, s9];
  function next() {
    let p = null;
    if (step === 1) { const q = firstProblem(); if (q && q.step === 1) p = q; }
    else if (step === 8) { if (S.styles.length < 1) p = { step: 8, msg: W.s8.needStyle }; }
    else if (step === 9) p = firstProblem();
    if (p) { msg = p.msg; warn = true; if (p.step !== step) { S.flash = p.msg; go(`#/onboard/${p.step}`); } else draw(); return; }
    go(step === 9 ? "#/building" : `#/onboard/${step + 1}`);
  }
  const bodyT = [W.s1, W.s2, W.s3, W.s4, W.s5, W.s6, W.s7, W.s8, W.s9][step - 1];
  function draw() {
    const main = h("section", { class: "wmain" }, h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem", text: bodyT.title }), h("p", { class: "lead", style: "margin:8px 0 22px", text: bodyT.lead }),
      msg ? h("div", { class: "note" + (warn ? " warn" : ""), role: "status", text: msg }) : null, h("div", { class: "stack" }, STEPS[step - 1]()),
      h("div", { class: "foot" }, step > 1 ? h("a", { class: "btn ghost", href: `#/onboard/${step - 1}`, text: W.back }) : h("span"), h("button", { class: "btn" + (step === 9 ? " org" : ""), type: "button", text: step === 9 ? (editing ? W.edit : W.finish) : W.next, onclick: next })));
    root.replaceChildren(aside, main);
    if (focusLast) { const els = root.querySelectorAll(focusLast); if (els.length) els[els.length - 1].focus(); focusLast = null; }
  }
  draw();
  return root;
}
