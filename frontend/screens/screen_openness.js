// Side page: job advert check.
import { api } from "../api.js";
import { T } from "../strings.js";
import { h, pageHead, errorPanel, spinner } from "../ui.js";

export default async function screenOpenness() {
  const t = T.ad;
  const ta = h("textarea", { id: "ad-text", maxlength: "5000", style: "min-height:160px" });
  const cnt = h("div", { class: "counter", text: t.countOf(0) });
  ta.addEventListener("input", () => { cnt.textContent = t.countOf(ta.value.length); });
  const out = h("div", { class: "stack" });
  const run = async () => {
    const v = ta.value.trim();
    if (v.length < 20 || v.length > 5000) { out.replaceChildren(h("p", { class: "err", role: "alert", text: t.needLength })); return; }
    out.replaceChildren(spinner());
    try {
      const r = await api.readinessCheck(v);
      out.replaceChildren(r.status === "no_flags"
        ? h("div", { class: "status pass", role: "status" }, h("span", { text: T.opennessNone }))
        : h("div", { class: "stack" }, h("div", { class: "status flagged", role: "status" }, h("b", { text: T.opennessFlagged(r.flags.length) })),
          r.flags.map((f) => h("article", { class: "card" }, h("p", null, h("b", { text: t.matched + ": " }), h("span", { class: "mark", text: f.matched_text })), h("p", { class: "small" }, h("b", { text: t.why + ": " }), f.why), h("p", { class: "small" }, h("b", { text: t.suggestion + ": " }), f.suggestion)))),
        r.skills_first ? h("p", { class: "small", text: t.skillsFirst }) : null,
        h("div", { class: "note" }, r.limitations.map((l) => h("p", { text: l }))));
    } catch (e) { out.replaceChildren(errorPanel(e, run)); }
  };
  return h("div", { class: "page" }, pageHead(t.title, t.lead),
    h("section", { class: "card" }, h("label", { for: "ad-text", text: t.label }), h("p", { class: "hint", text: t.help }), ta, cnt,
      h("div", { class: "row" }, h("button", { class: "btn", type: "button", text: t.run, onclick: run }), h("button", { class: "btn ghost", type: "button", text: t.example, onclick: () => { ta.value = t.exampleText; cnt.textContent = t.countOf(ta.value.length); } }))), out);
}
