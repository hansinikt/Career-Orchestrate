// Panels that show the agents' own work: the trace ("Which agents worked on this"), the market view, and the Course Scout.
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

export async function marketCard() {
  const t = T.market; let m = null;
  try { m = await api.getMarket(S.profileId); } catch (e) { if (!quiet(e)) throw e; }
  return h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.title }), h("p", { class: "muted small", text: t.lead }),
    m && m.next_skills.length ? h("div", { class: "stack", style: "gap:8px" }, m.next_skills.map((x) => h("div", { class: "row between" }, h("b", { text: x.name }), h("small", { class: "faint", text: t.asked(x.roles_asking, m.roles_in_catalogue) }))), h("small", { class: "faint", text: m.source_note })) : h("p", { class: "muted", text: t.empty }));
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

// The updated CV: plain text for applicant tracking systems.
export function cvCard() {
  const t = T.cvx, out = h("div", { class: "stack" }), msg = h("p", { class: "small", role: "status" });
  const make = h("button", { class: "btn org", type: "button", text: t.make, onclick: async () => {
    make.disabled = true; msg.textContent = t.making;
    try {
      const d = await api.getCv(S.profileId); msg.textContent = "";
      const url = URL.createObjectURL(new Blob([d.text], { type: "text/plain" }));
      out.replaceChildren(h("pre", { class: "cvpre", style: "white-space:pre-wrap;background:var(--line-2);border-radius:10px;padding:16px;max-height:340px;overflow:auto;font-size:.88rem", text: d.text }),
        h("div", { class: "row" }, h("a", { class: "btn", href: url, download: d.file_name, text: t.download }),
          h("button", { class: "btn ghost", type: "button", text: t.copy, onclick: async (e) => { try { await navigator.clipboard.writeText(d.text); e.target.textContent = t.copied; } catch (_) { /* clipboard may be blocked */ } } })));
    } catch (e) { msg.textContent = e.code === "SKILLS_NOT_CONFIRMED" ? t.empty : e.message; } finally { make.disabled = false; }
  } });
  return h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.title }), h("p", { class: "muted small", text: t.lead }), make, msg, out);
}
