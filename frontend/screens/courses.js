// Courses: the courses of the role you chose, simplest first, each one expandable. Roles with no course data fall back to the plan's steps.
import { T } from "../strings.js";
import { h, bar, crumb, emptyState, num } from "../ui.js";
import { ill } from "../art.js";
import * as slots from "../slots.js";
import { scoutCard } from "../panels.js";
import { courseCard } from "./coursecard.js";

export default async function courses() {
  const t = T.crs;
  const [plan, prog] = await Promise.all([slots.plan(), slots.progress()]);
  const rc = await slots.chosenCourses(plan);
  const rows = slots.courseRows(plan, prog);
  const list = h("div", { class: "stack" });
  const q = h("input", { type: "search", id: "c-q", placeholder: t.search, "aria-label": t.search, style: "min-width:240px;border-radius:22px" });
  const draw = () => {
    const needle = q.value.trim().toLowerCase();
    if (rc.length) {
      const shown = rc.map((c, i) => [c, i + 1]).filter(([c]) => !needle || c.title.toLowerCase().includes(needle) || (c.provider || "").toLowerCase().includes(needle));
      list.replaceChildren(...(shown.length ? shown.map(([c, n]) => courseCard(c, n)) : [h("p", { class: "muted", text: T.search.none })]));
      return;
    }
    const shown = rows.filter((r) => !needle || r.title.toLowerCase().includes(needle) || r.skill_name.toLowerCase().includes(needle));
    if (!rows.length) { list.replaceChildren(emptyState("course", t.emptyTitle, t.emptyText, h("a", { class: "btn", href: "#/jobs", text: t.makePlan }))); return; }
    list.replaceChildren(...shown.map((r) => h("div", { class: "card item", style: "padding:22px 26px;gap:22px" }, ill("course", 64),
      h("div", { class: "grow" }, h("h4", { style: "font-size:1.15rem", text: r.title }), h("div", { class: "sub", text: r.sub }), h("p", { text: r.text }),
        r.hasCourse ? null : h("p", { class: "small", style: "color:var(--ink-3)", text: t.noCourse }), h("div", { style: "margin-top:10px;max-width:420px" }, bar(r.percent, r.title))),
      h("div", { style: "text-align:right;min-width:120px" }, h("small", { class: "faint", text: t.hours }), h("div", { style: "font-weight:700;font-size:1.25rem;margin-bottom:10px", text: num(r.hours) }), h("a", { class: "btn", href: `#/course/${r.order}`, text: t.open })))));
  };
  q.addEventListener("input", draw);
  draw();
  const has = rc.length || rows.length;
  return h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead })), has ? q : null),
    !rc.length && rows.length ? scoutCard(() => window.dispatchEvent(new HashChangeEvent("hashchange"))) : null, list);
}
