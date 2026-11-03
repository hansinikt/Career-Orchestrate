// Screen 7: fairness check (adviser view).
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, pageHead, errorPanel, spinner, field } from "../ui.js";

const FMT = { skills_jaccard: (v) => v.toFixed(2), kendall_tau: (v) => v.toFixed(2), max_abs_score_delta: (v) => v.toFixed(3), plan_hours_delta: (v) => String(Math.round(v * 10) / 10), top3_overlap: (v) => String(v), lexicon_hits: (v) => String(v) };

export default async function screen7() {
  const t = T.s7;
  if (!S.profileId) return h("div", { class: "page" }, pageHead(t.title, t.lead), h("div", { class: "empty" }, h("p", { text: t.needProfile }), h("a", { class: "btn", href: "#/onboard", text: t.createProfile })));
  const out = h("div", { class: "stack" });
  const buttons = [h("button", { class: "btn", type: "button", text: t.run, onclick: () => run(false) }), h("button", { class: "btn ghost", type: "button", text: t.runCanary, onclick: () => run(true) })];
  async function run(canary) {
    buttons.forEach((b) => { b.disabled = true; }); out.replaceChildren(spinner(t.runningNote));
    try { show(await api.startAudit(S.profileId, canary)); } catch (e) { out.replaceChildren(errorPanel(e, () => run(canary))); }
    buttons.forEach((b) => { b.disabled = false; });
  }
  function show(a) {
    const bad = new Set(a.variants.flatMap((v) => v.flags.map((f) => `${v.variant_id}|${f.metric}`)));
    const label = (id) => t.variants[id] || id;
    const rows = a.variants.map((v) => h("tr", { class: v.flags.length ? "flag" : "" }, h("td", null, h("b", { text: label(v.variant_id) }), h("div", { class: "small faint", text: v.variant_id })),
      Object.keys(t.cols).map((m) => h("td", { class: "num" + (bad.has(`${v.variant_id}|${m}`) ? " bad" : "") }, (FMT[m] || String)(v.metrics[m])))));
    const flags = a.variants.flatMap((v) => v.flags);
    const review = h("div", { class: "panel" });
    drawReview(review, a);
    out.replaceChildren(
      h("div", { class: "status " + a.status, role: "status" }, h("b", { text: a.status === "pass" ? t.pass : t.flagged }), h("span", { text: a.status === "pass" ? t.passText : t.flaggedText })),
      h("div", { class: "tablewrap" }, h("table", null, h("thead", null, h("tr", null, h("th", { text: t.variant }), Object.values(t.cols).map((c) => h("th", { class: "num", text: c })))), h("tbody", null, rows))),
      flags.length ? h("section", { class: "panel" }, h("h2", { text: t.flagsHeading }), h("ul", null, flags.map((f) => h("li", { text: `${label(f.variant_id)}: ${f.message}` })))) : null,
      h("section", { class: "panel" }, h("h2", { text: t.limitsTitle }), h("ul", null, a.limitations.map((l) => h("li", { text: l })), h("li", { text: T.fairnessNote }))), review);
  }
  function drawReview(box, a) {
    if (a.review) { box.replaceChildren(h("h2", { text: t.reviewTitle }), h("p", { text: t.reviewed(a.review.reviewer, T.s7.decisions[a.review.decision] || a.review.decision) }), a.review.note ? h("p", { class: "muted", text: a.review.note }) : null); return; }
    const who = h("input", { type: "text", id: "rv-who", maxlength: "60" }), note = h("textarea", { id: "rv-note", maxlength: "500" }), msg = h("div");
    const dec = h("select", { id: "rv-dec" }, Object.entries(t.decisions).map(([k, v]) => h("option", { value: k, text: v })));
    box.replaceChildren(h("h2", { text: t.reviewTitle }), field(t.reviewer, who), field(t.decision, dec), field(t.note, note), msg,
      h("button", { class: "btn", type: "button", text: t.saveReview, onclick: async () => {
        if (!who.value.trim()) { msg.replaceChildren(h("p", { class: "err", text: t.needReviewer })); return; }
        const body = { reviewer: who.value.trim(), decision: dec.value }; if (note.value.trim()) body.note = note.value.trim();
        try { const r = await api.reviewAudit(a.audit_id, body); a.review = r.review || r; drawReview(box, a); } catch (e) { msg.replaceChildren(errorPanel(e)); } } }));
  }
  return h("div", { class: "page" }, pageHead(t.title, t.lead), h("div", { class: "row" }, buttons), out);
}
