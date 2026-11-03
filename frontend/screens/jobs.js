// Job options: the roles that fit the skills the worker confirmed, closest fit first. Five show; "More roles" shows the rest.
// Order and content come from the matching agent (GET /recommendations). Nothing here is pinned or recomputed.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, crumb, bandChip, emptyState, num } from "../ui.js";
import * as slots from "../slots.js";
import { timeStrip } from "./timestrip.js";

const SHOWN = 5;

export default async function jobs() {
  if (!S.profileId) { go("#/onboard"); return null; }
  // The site remembers where you left off: once you have chosen a role, this tab opens that role. "Choose a different role" brings the list back.
  const plan = await slots.plan();
  if (plan && plan.role_id && !S.changeRole) { go(`#/role/${plan.role_id}`); return null; }
  S.changeRole = false;
  const R = await api.recommendations(S.profileId), t = T.jobs;
  const weekly = await slots.weeklyHours();
  const recs = R.recommendations, goalId = R.goal ? R.goal.role_id : null;
  if (!recs.length) return h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head col" }, h("h1", { id: "page-title", tabindex: "-1", text: t.title })), emptyState("goal", t.empty, null, h("a", { class: "btn", href: "#/3", text: t.toSkills })));

  const card = (rec) => {
    const isGoal = rec.role_id === goalId;
    const build = rec.build_skills && rec.build_skills.length ? rec.build_skills : rec.gaps.map((g) => g.name);
    return h("article", { class: "card rolecard" + (isGoal ? " goal" : ""), "aria-label": rec.title },
      h("div", { class: "rank", "aria-label": `Rank ${rec.rank}`, text: String(rec.rank) }),
      h("div", { class: "stack" },
        isGoal ? h("p", { class: "kicker", text: t.goalTag }) : null,
        h("div", { class: "roletitle" }, h("h3", { text: rec.title }), bandChip(rec.band)),
        h("div", null, h("small", { class: "faint", text: t.have }), h("div", { class: "pills", style: "margin-top:4px" }, rec.matched.map((m) => h("span", { class: "chip", text: m.name })))),
        h("div", null, h("small", { class: "faint", text: t.build }), h("div", { class: "pills", style: "margin-top:4px" },
          (build.length ? build.map((n) => h("span", { class: "chip gap", text: n })) : h("span", { class: "small muted", text: t.nothingToBuild })))),
        timeStrip(rec.course_count, rec.course_hours, weekly),
        h("div", { class: "cardfoot" }, h("span"), h("a", { class: "btn" + (isGoal ? "" : " ghost"), href: `#/role/${rec.role_id}`, text: t.seeCourses }))));
  };

  const top = recs.slice(0, SHOWN), rest = recs.slice(SHOWN).filter((r) => r.role_id !== goalId);
  const goalExtra = R.goal && !top.some((r) => r.role_id === goalId) ? R.goal : null;   // we always show the role the worker asked for
  const list = h("div", { class: "stack", style: "margin-top:22px" }, top.map(card), goalExtra ? card(goalExtra) : null);
  const extra = h("div", { class: "stack", style: "margin-top:16px", hidden: true }, rest.map(card));
  const btn = h("button", { class: "btn ghost", type: "button", "aria-expanded": "false", text: t.moreCount(rest.length), onclick: () => {
    extra.hidden = !extra.hidden; btn.setAttribute("aria-expanded", String(!extra.hidden)); btn.textContent = extra.hidden ? t.moreCount(rest.length) : t.less; } });
  return h("div", { class: "page" }, crumb(t.crumb),
    h("div", { class: "head col" }, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead })),
    list, extra, rest.length ? h("div", { style: "text-align:center;margin-top:26px" }, btn) : null);
}
