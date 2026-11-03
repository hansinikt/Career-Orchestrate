// Screen 2: your work. Sends ProfileCreate, then asks for skill suggestions.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S, setProfileId, resetJourney } from "../state.js";
import { h, go, pageHead, field, choice, errorPanel, spinner, levelWord } from "../ui.js";

const blank = () => ({ name: "", role: "", examples: [""], skills: [], goal: "", hours: "", interests: [] });
const LEVELS = [1, 2, 3];

export default async function screen2() {
  const t = T.s2;
  if (!S.form) S.form = blank();
  const F = S.form;
  const [rolesRes, skillsRes, personasRes] = await Promise.all([api.roles(), api.skills().catch(() => ({ skills: [] })), api.demoPersonas().catch(() => ({ personas: [] }))]);
  const root = h("div", { class: "page" });
  let msg = null, busy = false, focusLast = null;

  const draw = () => {
    const errs = {};
    root.replaceChildren(pageHead(t.title, t.lead), demoBox(), formBox());
    if (focusLast) { const els = root.querySelectorAll(focusLast); if (els.length) els[els.length - 1].focus(); focusLast = null; }
  };
  function demoBox() {
    const sel = h("select", { id: "demo-sel", "aria-label": t.demoSelect }, personasRes.personas.map((p) => h("option", { value: p.persona_id, text: `${p.display_name}, ${p.current_role}` })));
    const anitha = personasRes.personas.find((p) => p.display_name === "Anitha Raman");
    if (anitha) sel.value = anitha.persona_id;
    return h("section", { class: "panel" }, h("h2", { text: t.demoTitle }), h("p", { class: "hint", text: t.demoHelp }),
      personasRes.personas.length ? h("div", { class: "row" }, h("div", { style: "min-width:240px;flex:1" }, sel),
        h("button", { class: "btn ghost", type: "button", text: t.demoButton, onclick: () => fill(personasRes.personas.find((p) => p.persona_id === sel.value)) })) : null,
      msg ? h("p", { class: "small", role: "status", text: msg }) : null);
  }
  function fill(p) {
    if (!p) return;
    S.form = Object.assign(blank(), { name: p.display_name, role: p.current_role || "", examples: p.work_examples.slice(0, 5), skills: p.declared_skills.map((s) => ({ name: s.name, level: s.level })), goal: p.stated_goal_role_id || "", hours: "6" });
    Object.assign(F, S.form); S.form = F;
    msg = t.demoFilled; draw();
  }
  const bind = (key) => (e) => { F[key] = e.target.value; };
  function formBox() {
    const name = h("input", { type: "text", id: "f-name", maxlength: "60", autocomplete: "name", value: F.name, oninput: bind("name") });
    const role = h("input", { type: "text", id: "f-role", maxlength: "80", value: F.role, oninput: bind("role") });
    const examples = F.examples.map((val, i) => {
      const cnt = h("div", { class: "counter", text: t.counter(val.length) });
      const ta = h("textarea", { id: `f-ex-${i}`, class: "ex", maxlength: "1000", "aria-label": t.exampleLabel(i + 1), oninput: (e) => { F.examples[i] = e.target.value; cnt.textContent = t.counter(e.target.value.length); }, value: val });
      return h("div", { class: "field" }, h("div", { class: "row between" }, h("label", { for: ta.id, text: t.exampleLabel(i + 1) }),
        F.examples.length > 1 ? h("button", { class: "linkbtn", type: "button", text: t.removeExample, onclick: () => { F.examples.splice(i, 1); draw(); } }) : null), ta, cnt);
    });
    const skillRows = F.skills.map((s, i) => h("div", { class: "row", style: "align-items:flex-end;margin-bottom:10px" },
      h("div", { style: "flex:2;min-width:180px" }, h("input", { type: "text", list: "skill-names", maxlength: "80", "aria-label": `${t.skillName} ${i + 1}`, value: s.name, oninput: (e) => { s.name = e.target.value; } })),
      h("div", { style: "flex:1;min-width:150px" }, h("select", { "aria-label": `${t.skillLevel} ${i + 1}`, value: String(s.level), onchange: (e) => { s.level = Number(e.target.value); } }, LEVELS.map((l) => h("option", { value: String(l), text: levelWord(l) })))),
      h("button", { class: "linkbtn", type: "button", text: t.removeSkill, onclick: () => { F.skills.splice(i, 1); draw(); } })));
    const goal = h("select", { id: "f-goal", onchange: bind("goal"), value: F.goal }, h("option", { value: "", text: t.goalNone }), rolesRes.roles.map((r) => h("option", { value: r.role_id, text: r.title })));
    const hours = h("input", { type: "number", id: "f-hours", min: "1", max: "40", inputmode: "numeric", value: F.hours, oninput: bind("hours"), style: "max-width:140px" });
    const interests = h("div", { class: "choices", role: "group", "aria-label": t.interestsTitle }, Object.entries(t.interests).map(([k, label]) =>
      choice("checkbox", "interest", label, "", F.interests.includes(k), (e) => { F.interests = e.target.checked ? [...F.interests, k] : F.interests.filter((x) => x !== k); draw(); }, !F.interests.includes(k) && F.interests.length >= 3)));
    const out = h("div", { id: "form-out" });
    const submit = h("button", { class: "btn", type: "button", text: t.submit, disabled: busy, onclick: () => send(out) });
    return h("section", { class: "card" },
      h("h2", { text: t.aboutYou }), field(t.name, name), field(t.role, role),
      h("div", { class: "field" }, h("h2", { text: t.examplesTitle }), h("p", { class: "hint", text: t.examplesHelp })), examples,
      F.examples.length < 5 ? h("button", { class: "btn ghost small", type: "button", text: t.addExample, onclick: () => { F.examples.push(""); focusLast = "textarea.ex"; draw(); } }) : null,
      h("div", { class: "field" }, h("h2", { text: t.skillsTitle }), h("p", { class: "hint", text: t.skillsHelp })), skillRows,
      h("datalist", { id: "skill-names" }, skillsRes.skills.map((s) => h("option", { value: s.name }))),
      F.skills.length < 30 ? h("button", { class: "btn ghost small", type: "button", text: t.addSkill, onclick: () => { F.skills.push({ name: "", level: 2 }); focusLast = "input[list]"; draw(); } }) : null,
      field(t.goalTitle, goal, { hint: t.goalHelp }), field(t.hoursTitle, hours, { hint: t.hoursHelp }),
      h("div", { class: "field" }, h("p", { class: "lbl", text: t.interestsTitle }), h("p", { class: "hint", text: t.interestsHelp }), interests),
      h("p", { class: "small muted", text: T.s1.privacy }),
      out, h("div", { class: "row" }, submit));
  }
  async function send(out) {
    const problems = [];
    if (!F.name.trim()) problems.push(t.needName);
    const ex = F.examples.map((x) => x.trim()).filter(Boolean);
    if (!ex.length || ex.some((x) => x.length < 10)) problems.push(t.needExample);
    if (problems.length) { out.replaceChildren(h("div", { class: "errorbox", role: "alert" }, problems.map((p) => h("p", { text: p })))); return; }
    if (!S.consent || S.styles.length < 1) { S.flash = !S.consent ? T.s1.needConsent : T.s1.needStyle; go("#/1"); return; }
    const hrs = parseInt(F.hours, 10);
    const body = {
      display_name: F.name.trim(), work_examples: ex,
      declared_skills: F.skills.filter((s) => s.name.trim()).map((s) => ({ name: s.name.trim(), level: s.level })),
      preferences: { interests: F.interests, weekly_hours: hrs >= 1 && hrs <= 40 ? hrs : null },
      motivation: { styles: S.styles, check_in: S.checkIn, paused: S.paused },
      consent: true,
    };
    if (F.role.trim()) body.current_role = F.role.trim();
    if (F.goal) body.stated_goal_role_id = F.goal;
    out.replaceChildren(spinner(t.working)); busy = true;
    try {
      if (S.profileId) { try { await api.deleteProfile(S.profileId); } catch (e) { /* old profile already gone */ } }
      resetJourney();
      const profile = await api.createProfile(body); setProfileId(profile.profile_id);
      S.extract = await api.extract(profile.profile_id);
      go("#/3");
    } catch (e) { busy = false; out.replaceChildren(errorPanel(e, () => send(out))); }
  }
  draw();
  return root;
}
