// Screen 5: the learning plan for the chosen role.
import { api, ApiError } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, pageHead, num, errorPanel } from "../ui.js";

export default async function screen5() {
  if (!S.profileId) { go("#/onboard"); return null; }
  const t = T.s5;
  const f = S.form && parseInt(S.form.hours, 10);
  const hours = f >= 1 && f <= 40 ? f : undefined;
  let plan;
  try {
    plan = S.roleId ? await api.makePlan(S.profileId, hours ? { role_id: S.roleId, weekly_hours: hours } : { role_id: S.roleId }) : await api.getPlan(S.profileId);
  } catch (e) {
    if (e instanceof ApiError && (e.code === "NO_ACTIVE_PLAN" || (e.code === "NOT_FOUND" && S.profileId && !S.roleId))) {
      return h("div", { class: "page" }, pageHead(t.title), h("div", { class: "empty" }, h("p", { text: t.noPlan }), h("a", { class: "btn", href: "#/4", text: t.chooseRole })));
    }
    throw e;
  }
  S.roleId = plan.role_id;
  const out = h("div");

  const resourceBox = (step) => {
    const r = step.resource;
    if (step.status !== "resource_found" || !r) return h("div", { class: "resource missing" }, h("p", { class: "small", text: t.noResource || T.noResource }));
    const ver = r.verification_status;
    const badge = ver === "verified" ? h("span", { class: "badge ok", text: T.badgeVerified + (r.last_verified ? ` ${r.last_verified}` : "") }) : h("span", { class: "badge warn", text: ver === "sample_placeholder" ? T.badgeSample : T.badgeUnverified });
    return h("div", { class: "resource" }, h("div", { class: "row" }, h("b", { text: r.title }), badge),
      h("p", { class: "small muted", text: `${t.provider}: ${r.provider} · ${t.duration}: ${r.duration_text}` }),
      r.url ? h("a", { href: r.url, target: "_blank", rel: "noopener noreferrer", text: t.openCourse }) : null);
  };
  const hoursForm = () => {
    const inp = h("input", { type: "number", id: "wk", min: "1", max: "40", inputmode: "numeric", style: "max-width:120px" });
    return h("div", { class: "panel" }, h("p", { text: t.needHours }), h("div", { class: "row" }, h("label", { for: "wk", class: "sr", text: t.hoursLabel }), inp,
      h("button", { class: "btn ghost", type: "button", text: t.updateHours, onclick: async () => {
        const v = parseInt(inp.value, 10); if (!(v >= 1 && v <= 40)) return;
        if (S.form) S.form.hours = String(v);
        try { await api.makePlan(S.profileId, { role_id: plan.role_id, weekly_hours: v }); location.hash = "#/5"; window.dispatchEvent(new HashChangeEvent("hashchange")); }
        catch (e) { out.replaceChildren(errorPanel(e)); }
      } })));
  };

  return h("div", { class: "page" },
    pageHead(t.title, t.forRole(plan.role_title)),
    h("div", { class: "card summary" }, h("span", { class: "big", text: t.totalHours(num(plan.total_est_hours)) }),
      plan.weeks_at_pace ? h("span", { class: "muted", text: t.weeks(plan.weeks_at_pace, plan.weekly_hours) }) : null),
    plan.weeks_at_pace ? null : hoursForm(), out,
    plan.includes_unverified_resources ? h("div", { class: "note warn", role: "status", text: t.unverifiedBanner }) : null,
    h("ol", { class: "timeline" }, plan.steps.map((st) => h("li", null, h("span", { class: "num", "aria-hidden": "true", text: String(st.order) }),
      h("div", { class: "card" }, h("h3", { text: `${t.stepWord} ${st.order}: ${st.skill_name}` }), h("p", { class: "small muted", text: st.rationale }),
        h("p", { class: "small", text: T.s4.hours(num(st.est_hours)) }), resourceBox(st))))),
    h("div", { class: "note", text: plan.disclaimer }),
    h("div", { class: "row" }, h("a", { class: "btn", href: "#/progress", text: t.start })));
}
