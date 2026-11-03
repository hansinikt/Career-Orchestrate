// One job option: what the worker has, what is still to build, and the courses for the role (simplest first).
// "Choose this path" is the human decision that used to be the role choice screen. It starts building the plan.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, crumb, bandChip, levelWord, emptyState, num } from "../ui.js";
import { ill } from "../art.js";
import * as slots from "../slots.js";

const bone = (w, hgt = 14) => h("div", { class: "bone", style: `width:${w};height:${hgt}px` });
const skeletonRow = () => h("div", { class: "card item", style: "padding:20px 24px;gap:20px", "aria-hidden": "true" }, ill("course", 56),
  h("div", { class: "grow" }, bone("60%", 18), h("div", { style: "height:8px" }), bone("35%", 12), h("div", { style: "height:8px" }), bone("80%", 12)));

function courseRow(c, n) {
  const r = T.role, tags = [];
  tags.push(c.rating != null ? r.rating(c.rating, c.rating_count) : r.noRating);
  tags.push(c.cost ? r.cost(c.cost) : r.costNone);
  tags.push(c.certificate === true ? r.cert.yes : c.certificate === false ? r.cert.no : r.cert.unknown);
  if (c.prerequisites) tags.push(r.prereq(c.prerequisites));
  return h("div", { class: "card item", style: "padding:20px 24px;gap:20px" }, ill("course", 56),
    h("div", { class: "grow" }, h("h4", { style: "font-size:1.08rem", text: c.title }), h("div", { class: "sub", text: [r.step(n), c.provider].filter(Boolean).join(" · ") }),
      c.why ? h("p", { class: "small" }, h("b", { text: r.why + ": " }), c.why) : null,
      c.covers && c.covers.length ? h("p", { class: "small muted" }, h("b", { text: r.covers + ": " }), c.covers.join(", ")) : null,
      h("div", { class: "pills", style: "margin-top:6px" }, tags.map((x) => h("span", { class: "badge", text: x })), c.verified ? null : h("span", { class: "badge warn", text: r.unverified }))),
    h("div", { style: "text-align:right;min-width:130px" }, h("small", { class: "faint", text: r.hours }), h("div", { style: "font-weight:700;font-size:1.2rem;margin-bottom:10px", text: c.duration_text || "—" }),
      c.url ? h("a", { class: "btn ghost small", href: c.url, target: "_blank", rel: "noopener noreferrer", text: r.open }) : null));
}

export default async function role(roleId) {
  if (!S.profileId) { go("#/onboard"); return null; }
  const R = await api.recommendations(S.profileId), t = T.role, s4 = T.s4;
  const rec = R.recommendations.find((x) => x.role_id === roleId);
  if (!rec) return h("div", { class: "page" }, crumb(T.jobs.crumb), emptyState("goal", t.notFound, null, h("a", { class: "btn", href: "#/jobs", text: t.back })));
  const [courses, info] = await Promise.all([slots.roleCourses(rec.role_id), api.roles().then((r) => r.roles.find((x) => x.role_id === rec.role_id), () => null)]);
  const choose = () => { S.roleId = rec.role_id; go("#/5"); };

  const why = h("details", { class: "why" }, h("summary", { text: s4.why }),
    h("div", { class: "cols" },
      h("div", null, h("h4", { text: s4.matchedTitle }), rec.matched.length ? h("ul", null, rec.matched.map((m) => h("li", null, h("b", { text: m.name }),
        h("div", { class: "lv", text: `${s4.you}: ${levelWord(m.user_level)} · ${s4.needed}: ${levelWord(m.required_level)}` }),
        m.evidence_quotes.map((q) => h("div", { class: "quote-src" }, h("span", { class: "mark", text: `“${q}”` })))))) : h("p", { class: "muted small", text: "—" })),
      h("div", null, h("h4", { text: s4.gapsTitle }), rec.gaps.length ? h("ul", null, rec.gaps.map((g) => h("li", null, h("b", { text: g.name }), g.mandatory ? h("span", { class: "must", text: s4.required }) : null,
        h("div", { class: "lv", text: `${s4.you}: ${levelWord(g.user_level)} · ${s4.needed}: ${levelWord(g.required_level)} · ${s4.hours(num(g.est_hours))}` })))) : h("p", { class: "muted small", text: s4.noGaps }))));

  // courses, grouped by level in the order the Course Scout sent them
  let body;
  if (!courses.length) body = [h("div", { class: "note", role: "status" }, h("b", { text: t.waitTitle }), h("p", { text: t.waitText })), skeletonRow(), skeletonRow(), skeletonRow()];
  else {
    body = []; let last = null, n = 0;
    courses.forEach((c) => { const lv = c.level || "unknown"; if (lv !== last) { body.push(h("h3", { style: "margin-top:10px", text: t.levels[lv] || t.levels.unknown })); last = lv; } body.push(courseRow(c, ++n)); });
  }

  return h("div", { class: "page" }, crumb(t.crumb(rec.title)),
    h("div", { class: "head" }, h("div", null, h("div", { class: "roletitle" }, h("h1", { id: "page-title", tabindex: "-1", text: rec.title }), bandChip(rec.band)), info && info.summary ? h("p", { class: "lead", text: info.summary }) : null),
      h("a", { class: "btn ghost", href: "#/jobs", text: t.back })),
    h("div", { class: "panel", style: "margin-top:18px" }, h("div", { class: "cols2" },
      h("div", null, h("small", { class: "faint", text: t.have }), h("div", { class: "pills", style: "margin-top:4px" }, rec.matched.map((m) => h("span", { class: "chip", text: m.name })))),
      h("div", null, h("small", { class: "faint", text: t.build }), h("div", { class: "pills", style: "margin-top:4px" }, rec.gaps.map((g) => h("span", { class: "chip gap" }, g.name, h("i", { text: `${num(g.est_hours)} h` }))))))),
    why,
    h("section", { class: "stack", style: "margin-top:20px", "aria-label": t.coursesTitle }, h("h2", { text: t.coursesTitle }), h("p", { class: "muted", text: t.coursesLead }), body),
    h("div", { class: "cardfoot", style: "margin-top:26px" }, h("span", { class: "small muted", text: t.chooseHelp }), h("button", { class: "btn", type: "button", text: t.choose, onclick: choose })));
}
