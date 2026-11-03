// Dashboard: today's mission (the big blue box), the roadmap tiles, resume learning, and the progress gauge.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { U } from "../store.js";
import { h, go, bar, itemCard, emptyState, num } from "../ui.js";
import { gaugeSvg, ill } from "../art.js";
import * as slots from "../slots.js";
import { agentsCard, gapsCard, showEncouragement } from "../panels.js";

export default async function dashboard() {
  const t = T.dash;
  const [plan, prog, miss, profile] = await Promise.all([slots.plan(), slots.progress(), slots.missions(), api.getProfile(S.profileId)]);
  const rc = await slots.chosenCourses(plan), today = slots.todayMission(miss);
  const courses = rc.length ? rc.map((c) => ({ title: c.title })) : slots.courseRows(plan, prog);
  const items = slots.roadmapItems(courses, miss, plan, prog);
  const root = h("div", { class: "page" });

  const proofBox = () => {
    const file = h("input", { type: "file", id: "d-proof", "aria-label": t.proofDrop }), out = h("p", { class: "small", role: "status" });
    const notNow = h("button", { class: "btn ghost", type: "button", style: "width:100%;margin-top:8px", text: T.mis.notNow, onclick: async () => {
      try { const msg = await slots.declineMission(today.id); if (msg) showEncouragement(msg.text, { href: "#/missions", label: T.enc.back }); window.dispatchEvent(new HashChangeEvent("hashchange")); } catch (e) { out.textContent = e.message; } } });
    return h("div", { class: "proof" }, h("b", { text: t.proofTitle }), h("div", { class: "drop" }, t.proofDrop, h("br"), file), out,
      h("button", { class: "btn org", type: "button", style: "width:100%", text: t.proofBtn, onclick: () => { if (!file.files[0]) { out.textContent = T.mis.needFile; return; } out.textContent = T.mis.saving; slots.saveProof(today.id, file.files[0]).then(() => window.dispatchEvent(new HashChangeEvent("hashchange")), (e) => { out.textContent = e.message; }); } }), notNow);
  };
  const banner = today
    ? h("section", { class: "banner", "aria-label": t.todayTag }, h("div", null, h("small", { text: t.todayTag }), h("div", { class: "t", text: today.title }), h("p", { text: today.brief })), proofBox())
    : h("section", { class: "banner idle", "aria-label": t.todayTag }, h("div", null, h("small", { text: t.todayTag }), h("div", { class: "t", text: t.idleTitle }), h("p", { text: t.idleText })));

  const first = rc.length ? null : (courses.find((c) => c.percent > 0 && c.percent < 100) || courses[0]);
  const resume = rc.length
    ? h("div", { class: "card" }, h("div", { class: "row between" }, h("div", { class: "item" }, ill("course", 44), h("div", null, h("h4", { text: rc[0].title }), h("div", { class: "sub", text: [T.role.step(1), rc[0].provider].filter(Boolean).join(" · ") }))), h("a", { class: "btn ghost", href: "#/courses", text: t.resumeBtn })))
    : first
    ? h("div", { class: "card" }, h("div", { class: "row between" }, h("div", { class: "item" }, ill("course", 44), h("div", null, h("h4", { text: first.title }), h("div", { class: "sub", text: first.sub }))), h("a", { class: "btn ghost", href: `#/course/${first.order}`, text: t.resumeBtn })), bar(first.percent, first.title))
    : emptyState("course", t.resumeEmpty, t.resumeEmptyText, null, true);

  const gauge = h("div", { class: "card", style: "text-align:center" }, gaugeSvg(prog ? prog.percent : null),
    prog && prog.percent > 0 ? h("div", { class: "num-big", style: "margin-top:-58px;margin-bottom:34px", text: `${prog.percent}%` }) : null,
    h("p", { class: "muted small", text: prog && prog.steps_total ? t.gaugeOf(prog.steps_done, prog.steps_total) : t.gaugeCaption }));

  root.append(banner,
    h("div", null, h("h1", { id: "page-title", tabindex: "-1", style: "font-size:1.7rem", text: t.welcome(U.user.name.split(" ")[0]) }), h("p", { class: "muted", text: plan ? t.goal(plan.role_title) : t.noGoal })),
    h("div", { class: "split", style: "grid-template-columns:1.5fr 1fr" }, h("div", { class: "stack" }, h("h3", { text: t.roadmap }), h("div", { class: "grid g2" }, items.map((it) => itemCard({ kind: it.kind, size: 52, title: it.title, sub: it.sub, href: it.href }))), h("h3", { style: "margin-top:26px", text: t.resume }), resume),
      h("div", { class: "stack" }, h("h3", { text: t.gaugeTitle }), gauge)),
    h("div", { class: "grid g2", style: "margin-top:26px;align-items:start" }, await agentsCard(), await gapsCard(plan)));

  // Encouragement: shown full screen only when the backend sends a message for a missed or returning person, and messages are not paused.
  const m = prog && prog.next_message, paused = profile.motivation && profile.motivation.paused;
  if (m && ["behind", "welcome_back"].includes(m.event) && !paused && !S.encDismissed) { S.encDismissed = true; showEncouragement(m.text); }
  return root;
}
