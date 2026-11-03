// One job option: what the worker has, what is still to build, and the courses for the role (simplest first).
// "Choose this path" is the human decision that used to be the role choice screen. It starts building the plan.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, crumb, bandChip, levelWord, emptyState, num } from "../ui.js";
import { ill } from "../art.js";
import * as slots from "../slots.js";
import { courseCard } from "./coursecard.js";
import { timeStrip } from "./timestrip.js";

const bone = (w, hgt = 14) => h("div", { class: "bone", style: `width:${w};height:${hgt}px` });
const skeletonRow = () => h("div", { class: "card item", style: "padding:20px 24px;gap:20px", "aria-hidden": "true" }, ill("course", 56),
  h("div", { class: "grow" }, bone("60%", 18), h("div", { style: "height:8px" }), bone("35%", 12), h("div", { style: "height:8px" }), bone("80%", 12)));

export default async function role(roleId) {
  if (!S.profileId) { go("#/onboard"); return null; }
  const R = await api.recommendations(S.profileId), t = T.role, s4 = T.s4;
  const rec = R.recommendations.find((x) => x.role_id === roleId);
  if (!rec) return h("div", { class: "page" }, crumb(T.jobs.crumb), emptyState("goal", t.notFound, null, h("a", { class: "btn", href: "#/jobs", text: t.back })));
  const [path, info] = await Promise.all([slots.rolePath(rec.role_id), api.roles().then((r) => r.roles.find((x) => x.role_id === rec.role_id), () => null)]);
  const courses = path.courses, build = path.requirements.filter((x) => !x.have).map((x) => x.name);
  const toBuild = build.length ? build : rec.gaps.map((g) => g.name);
  const weekly = await slots.weeklyHours();
  const totalH = courses.reduce((a, c) => a + (c.hours || 0), 0);
  const plan = await slots.plan(), chosen = !!(plan && plan.role_id === rec.role_id);
  const choose = () => { S.roleId = rec.role_id; S.changeRole = false; go("#/5"); };

  // courses, grouped by level in the order the Course Scout sent them
  let body;
  if (!courses.length) body = [h("div", { class: "note", role: "status" }, h("b", { text: t.waitTitle }), h("p", { text: t.waitText })), skeletonRow(), skeletonRow(), skeletonRow()];
  else {
    body = []; let last = null, n = 0;
    courses.forEach((c) => { const lv = c.level || "unknown"; if (lv !== last) { body.push(h("h3", { style: "margin-top:10px", text: t.levels[lv] || t.levels.unknown })); last = lv; } body.push(courseCard(c, ++n)); });
  }

  return h("div", { class: "page" }, crumb(t.crumb(rec.title)),
    h("div", { class: "head" }, h("div", null, h("div", { class: "roletitle" }, h("h1", { id: "page-title", tabindex: "-1", text: rec.title }), bandChip(rec.band)), info && info.summary ? h("p", { class: "lead", text: info.summary }) : null),
      h("a", { class: "btn ghost", href: "#/jobs", onclick: () => { S.changeRole = true; }, text: chosen ? t.change : t.back })),
    h("div", { class: "panel", style: "margin-top:18px" }, h("div", { class: "cols2" },
      h("div", null, h("small", { class: "faint", text: t.have }), h("div", { class: "pills", style: "margin-top:4px" }, rec.matched.map((m) => h("span", { class: "chip", text: m.name })))),
      h("div", null, h("small", { class: "faint", text: t.build }), h("div", { class: "pills", style: "margin-top:4px" }, toBuild.map((n) => h("span", { class: "chip gap", text: n })))))),
    h("section", { class: "stack", style: "margin-top:20px", "aria-label": t.coursesTitle }, h("h2", { text: t.coursesTitle }), h("p", { class: "muted", text: t.coursesLead }), timeStrip(courses.length, totalH, weekly), body),
    h("div", { class: "cardfoot", style: "margin-top:26px" }, h("span", { class: "small muted", text: chosen ? t.chosenText : t.chooseHelp }), chosen ? h("span", { class: "st green", text: "✓ " + t.chosenTag }) : h("button", { class: "btn", type: "button", text: t.choose, onclick: choose })));
}
