// Profile: everything the person told us. Work, skills and goal are edited in the questions (the roadmap is rebuilt).
// Schedule, encouragement and email can be changed here directly.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S, setProfileId, resetJourney } from "../state.js";
import { U, saveExtras } from "../store.js";
import { h, go, crumb, choice, seg, toggle, levelWord, errorPanel } from "../ui.js";
import { scheduleGrid, scheduleLegend } from "./wizard.js";
import * as slots from "../slots.js";

export default async function profile(arg) {
  const t = T.prof, X = U.x;
  const [p, roles, plan, miss] = await Promise.all([api.getProfile(S.profileId), api.roles(), slots.plan(), slots.missions()]);
  const roleTitle = (id) => { const r = roles.roles.find((x) => x.role_id === id); return r ? r.title : null; };
  const edit = (step) => h("a", { class: "btn ghost small", href: `#/onboard/${step}`, text: t.edit });
  const kv = (k, v) => h("div", null, h("small", { class: "faint", text: k }), h("div", { style: "font-weight:600", text: v || t.none }));
  const sec = (id, title, editLink, ...kids) => h("section", { class: "card", id }, h("div", { class: "row between" }, h("h3", { style: "font-size:1.25rem", text: title }), editLink), ...kids);

  const work = sec("work", t.work, edit(2), h("div", { class: "cols2" }, kv(T.wiz.s2.role, p.current_role), kv(T.wiz.s2.industry, (S.form || {}).industry || X.industry), kv(T.wiz.s1.phone, (S.form || {}).phone || X.phone), kv(T.wiz.s1.email, X.email)), h("ul", { style: "margin:0;padding-left:20px" }, p.work_examples.map((e) => h("li", { text: e }))));
  const skills = sec("skills", t.skills, edit(3), h("div", { class: "pills" }, p.declared_skills.length ? p.declared_skills.map((s) => h("span", { class: "chip" }, s.name, h("i", { text: levelWord(s.level) }))) : h("span", { class: "muted", text: t.none })), X.tools.length ? h("div", { class: "pills" }, X.tools.map((x) => h("span", { class: "chip", text: x }))) : null);
  const goal = sec("goal", t.goal, edit(6), h("div", { class: "cols2" }, kv(T.wiz.s6.goal, (S.form && S.form.goalText) || roleTitle(p.stated_goal_role_id) || (plan && plan.role_title)), kv(T.wiz.s6.interests, ((S.form && S.form.picks) || []).join(", "))));
  const eduText = X.eduList.filter((e) => e.field || e.institution).map((e) => `${(T.wiz.s5.levels.find((l) => l[0] === e.level) || [])[1] || ""}: ${[e.field, e.institution].filter(Boolean).join(", ")}`).join("; ");
  const more = sec("more", t.more, edit(5), h("div", { class: "cols2" }, kv(T.wiz.s5.title, eduText), kv(T.wiz.s7.why, (X.situations || []).map((k) => (T.wiz.s7.whyOpts.find((o) => o[0] === k) || [])[1]).filter(Boolean).join(", ")), kv(T.wiz.s9.formats, X.formats.join(", ")), kv(T.wiz.s7.barriers, X.barriers.map((k) => (T.wiz.s7.barrierOpts.find((o) => o[0] === k) || [])[1]).filter(Boolean).join(", "))));
  const schedule = sec("schedule", t.time, edit(8), h("p", { class: "muted", text: p.preferences && p.preferences.weekly_hours ? t.hoursWeek(p.preferences.weekly_hours) : t.none }), scheduleLegend(), scheduleGrid());

  // encouragement: saved to the backend
  const mot = Object.assign({ styles: [], check_in: "weekly", paused: false }, p.motivation || {});
  const pauseNote = h("p", { class: "hint", role: "status", text: mot.paused ? T.wiz.s9.pauseOn : T.wiz.s9.pauseOff });
  let styles = [...mot.styles]; const out = h("span", { class: "small muted", role: "status" }), grid = h("div", { class: "choices" });
  const paint = () => grid.replaceChildren(...Object.keys(T.styles).map((k) => choice("checkbox", "mstyle", T.styles[k], T.styleHelp[k], styles.includes(k), (e) => { styles = e.target.checked ? [...styles, k] : styles.filter((x) => x !== k); paint(); })));
  paint();
  const enc = sec("encourage", t.encourage, null, grid, h("div", null, seg("mcheck", Object.entries(T.checkIn), mot.check_in, (v) => { mot.check_in = v; })), toggle(T.wiz.s9.pause, "", mot.paused, (v) => { const was = mot.paused; mot.paused = v; pauseNote.textContent = v ? T.wiz.s9.pauseOn : (was ? T.wiz.s9.resumed : T.wiz.s9.pauseOff); }), pauseNote,
    h("div", { class: "row" }, h("button", { class: "btn small", type: "button", text: t.save, onclick: async () => {
      if (!styles.length) { out.textContent = T.wiz.s9.needStyle; return; }
      try { await api.setMotivation(S.profileId, { styles, check_in: mot.check_in, paused: mot.paused }); S.styles = styles; S.checkIn = mot.check_in; S.paused = mot.paused; out.textContent = t.saved; } catch (e) { out.textContent = e.message; } } }), out));

  // email: preferences are kept on this device; the preview is a demo email built from what is on screen
  const today = slots.todayMission(miss), first = slots.courseRows(plan, null)[0];
  const preview = h("div", { class: "card", style: "background:#f7f8fa" }, h("small", { class: "faint", text: `To: ${U.user.email}` }), h("h4", { text: T.prof.mailSubject }),
    h("p", { text: T.prof.mailHello(U.user.name.split(" ")[0]) }), h("p", { text: today ? T.prof.mailMission(today.title) : first ? T.prof.mailCourse(first.title) : T.prof.mailNone }));
  const email = sec("email", t.email, null, toggle(T.prof.mailToggle, T.prof.mailHelp, X.mail, (v) => { X.mail = v; saveExtras(); }),
    h("div", { style: "max-width:200px" }, h("label", { for: "p-mt", text: T.prof.mailTime }), h("input", { type: "time", id: "p-mt", value: X.mailTime, onchange: (e) => { X.mailTime = e.target.value; saveExtras(); } })), preview);

  // delete my data
  const delBox = h("div"); let armed = false;
  const drawDel = () => delBox.replaceChildren(h("p", { class: "small muted", text: t.deleteWarn }), h("button", { class: "btn ghost small", type: "button", text: armed ? t.delete + "?" : t.delete, onclick: async () => {
    if (!armed) { armed = true; drawDel(); return; }
    try { await api.deleteProfile(S.profileId); setProfileId(null); resetJourney(); S.form = null; S.flash = t.deleted; go("#/onboard"); } catch (e) { delBox.replaceChildren(errorPanel(e)); } } }));
  drawDel();

  const node = h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead }))), work, skills, goal, schedule, more, enc, email, h("section", { class: "card" }, delBox));
  if (arg) setTimeout(() => { const el = document.getElementById(arg); if (el) el.scrollIntoView(); }, 0);
  return node;
}
