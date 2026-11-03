// Screen 4 (Gate 2): ranked roles with reasons. The worker chooses one.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, pageHead, bandChip, levelWord, num, handleError } from "../ui.js";

export default async function screen4() {
  if (!S.profileId) { go("#/onboard"); return null; }
  const R = await api.recommendations(S.profileId);
  const t = T.s4;
  const choose = (role) => { S.roleId = role.role_id; go("#/5"); };
  const nameOf = (rec, id) => { const g = rec.gaps.find((x) => x.skill_id === id); return g ? g.name : id; };

  const why = (rec) => h("details", { class: "why" }, h("summary", { text: t.why }),
    h("div", { class: "cols" },
      h("div", null, h("h4", { text: t.matchedTitle }), rec.matched.length ? h("ul", null, rec.matched.map((m) => h("li", null,
        h("b", { text: m.name }), h("div", { class: "lv", text: `${t.you}: ${levelWord(m.user_level)} · ${t.needed}: ${levelWord(m.required_level)}` }),
        m.evidence_quotes.map((q) => h("div", { class: "quote-src" }, h("span", { class: "mark", text: `“${q}”` })))))) : h("p", { class: "muted small", text: "—" })),
      h("div", null, h("h4", { text: t.gapsTitle }), rec.gaps.length ? h("ul", null, rec.gaps.map((g) => h("li", null,
        h("b", { text: g.name }), g.mandatory ? h("span", { class: "must", text: t.required }) : null,
        h("div", { class: "lv", text: `${t.you}: ${levelWord(g.user_level)} · ${t.needed}: ${levelWord(g.required_level)} · ${t.hours(num(g.est_hours))}` })))) : h("p", { class: "muted small", text: t.noGaps }))));

  const blocking = (rec) => rec.blocking_gaps.length ? h("p", { class: "small" }, h("b", { text: t.blocking + ": " }), rec.blocking_gaps.map((id) => nameOf(rec, id)).join(", ")) : null;
  const score = (rec) => h("span", { class: "small faint", text: `${t.scoreLabel}: ${rec.score}` });

  const goalCard = R.goal ? h("section", { class: "card goal", "aria-label": t.yourGoal(R.goal.title) },
    h("p", { class: "kicker", text: t.goalHeading }),
    h("div", { class: "roletitle" }, h("h2", { text: R.goal.title }), bandChip(R.goal.band)),
    h("p", { class: "muted", text: T.bandHelp[R.goal.band] }),
    h("p", { text: t.hoursNeeded(num(R.goal.est_gap_hours)) }), blocking(R.goal),
    h("p", { class: "small muted", text: R.goal.explanation }), why(R.goal),
    h("div", { class: "cardfoot" }, score(R.goal), h("button", { class: "btn", type: "button", text: t.chooseGoal, onclick: () => choose(R.goal) }))) : null;

  const roleCard = (rec) => h("article", { class: "card rolecard", "aria-label": rec.title },
    h("div", { class: "rank", "aria-label": `Rank ${rec.rank}`, text: String(rec.rank) }),
    h("div", { class: "stack" },
      h("div", { class: "roletitle" }, h("h3", { text: rec.title }), bandChip(rec.band)),
      h("p", { class: "small muted", text: rec.explanation }), blocking(rec), why(rec),
      h("div", { class: "cardfoot" }, score(rec), h("button", { class: "btn ghost", type: "button", text: t.choose, onclick: () => choose(rec) }))));

  return h("div", { class: "page" },
    pageHead(t.title, t.lead, T.yourDecision),
    goalCard,
    R.recommendations.length ? h("section", { class: "stack" }, h("h2", { text: t.allRoles }), R.recommendations.map(roleCard)) : h("div", { class: "empty" }, h("p", { text: t.empty }), h("a", { class: "btn", href: "#/3", text: T.s3.title })),
    h("div", { class: "note" }, h("p", { text: R.disclaimer }), h("p", { class: "small", text: t.provisional })));
}
