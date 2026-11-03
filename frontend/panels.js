// Panels that show the agents' own work: the trace ("What ran for you"), what is left to build for the chosen role, and the Course Scout.
// Everything shown comes from the API and is inserted as text. Nothing is computed here.
import { api, ApiError } from "./api.js";
import { T } from "./strings.js";
import { S } from "./state.js";
import { h } from "./ui.js";
import { ill } from "./art.js";

const quiet = (e) => e instanceof ApiError && ["NO_ACTIVE_PLAN", "SKILLS_NOT_CONFIRMED", "NOT_FOUND"].includes(e.code);

export async function agentsCard() {
  const t = T.agents; let steps = [];
  try { steps = (await api.getTrace(S.profileId)).steps; } catch (e) { if (!quiet(e)) throw e; }
  return h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.title }), h("p", { class: "muted small", text: t.lead }),
    steps.length ? h("ol", { class: "trace", style: "list-style:none;margin:14px 0 0;padding:0;display:grid;gap:10px" }, steps.map((s) =>
      h("li", { style: "display:flex;gap:12px;align-items:flex-start" }, h("span", { class: "chip", text: String(s.step) }),
        h("div", null, h("b", { text: t.names[s.agent] || s.agent }), " ", h("span", { class: "pill-s", style: "font-size:.78rem;color:var(--ink-3)", text: "· " + (t.modes[s.mode] || s.mode.replace(/_/g, " ")) }),
          h("div", { class: "small", text: s.output_summary }), s.stopped_at_gate ? h("div", { class: "small", style: "color:var(--brand);font-weight:600", text: t.decided }) : null)))) : h("p", { class: "muted", text: t.empty }));
}

// What is left to build for the role the person chose. The list comes from the role's requirements (GET /paths/{role}); nothing is computed here.
export async function gapsCard(plan) {
  const t = T.market; let r = null;
  try { if (plan && plan.role_id) r = await api.rolePath(S.profileId, plan.role_id); } catch (e) { if (!quiet(e)) throw e; }
  const todo = r ? r.requirements.filter((x) => !x.have) : [], have = r ? r.requirements.filter((x) => x.have) : [];
  return h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.title(plan && plan.role_title) }), h("p", { class: "muted small", text: t.lead }),
    todo.length ? h("div", { class: "stack", style: "gap:10px" }, todo.map((x) => h("div", null, h("b", { text: x.name }), h("div", { class: "small faint", text: x.evidence })))) : h("p", { class: "muted", text: t.empty }),
    have.length ? h("div", { style: "margin-top:14px" }, h("small", { class: "faint", text: t.have }), h("div", { class: "pills", style: "margin-top:4px" }, have.map((x) => h("span", { class: "chip", text: x.name })))) : null);
}

// Course Scout: proposes a catalogue course per step. The person approves; only then does the plan change.
export function scoutCard(onApproved) {
  const t = T.scout, box = h("div", { class: "stack" }), out = h("p", { class: "small", role: "status" });
  const ask = h("button", { class: "btn org", type: "button", text: t.ask, onclick: async () => {
    ask.disabled = true; out.textContent = t.asking;
    try { show(await api.scout(S.profileId)); out.textContent = ""; } catch (e) { out.textContent = e.message; } finally { ask.disabled = false; }
  } });
  const show = (r) => {
    const changes = r.steps.filter((s) => s.pick_resource_id && s.pick_resource_id !== s.current_resource_id);
    const approve = async (list) => { try { await api.scoutApprove(S.profileId, list.map((s) => ({ order: s.order, resource_id: s.pick_resource_id }))); out.textContent = t.approved; onApproved(); } catch (e) { out.textContent = e.message; } };
    box.replaceChildren(h("small", { class: "faint", text: r.mode === "agent" ? t.modeAgent : t.modeRules }),
      ...(changes.length ? changes.map((s) => { const c = s.candidates.find((x) => x.resource_id === s.pick_resource_id);
        return h("div", { class: "card item" }, h("div", { class: "grow" }, h("h4", { text: c ? c.title : s.skill_name }), h("div", { class: "sub", text: `${T.crs.step(s.order)} · ${s.skill_name}${c ? " · " + c.provider : ""}` }), h("p", { text: s.reason })),
          h("button", { class: "btn small", type: "button", text: t.approve, onclick: () => approve([s]) })); }) : [h("p", { class: "muted", text: t.none })]),
      ...(changes.length > 1 ? [h("button", { class: "btn", type: "button", text: t.approveAll, onclick: () => approve(changes) })] : []), h("small", { class: "faint", text: r.note }));
  };
  return h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.title }), h("p", { class: "muted small", text: t.lead }), ask, out, box);
}

// Full-screen encouragement. The text comes from the backend. Closeable by button or Escape.
export function showEncouragement(text, primary) {
  const close = () => { over.remove(); document.removeEventListener("keydown", esc); }, esc = (e) => { if (e.key === "Escape") close(); };
  const over = h("div", { class: "over", role: "dialog", "aria-modal": "true", "aria-label": "Encouragement" },
    h("button", { class: "x", type: "button", "aria-label": T.enc.close, text: "×", onclick: close }),
    h("div", { class: "in" }, h("div", { class: "sun", "aria-hidden": "true" }, ill("goal", 56)), h("div", { class: "t", text }),
      h("div", { class: "row" }, h("a", { class: "btn org lg", href: (primary && primary.href) || "#/courses", text: (primary && primary.label) || T.enc.open, onclick: close }), h("button", { class: "btn ghost lg", type: "button", style: "color:#fff;border-color:#fff", text: T.enc.later, onclick: close }))));
  document.addEventListener("keydown", esc); document.body.append(over); return over;
}

