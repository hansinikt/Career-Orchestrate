// Skill Check: questions the course does not ask. Empty until the backend sends questions.
import { T } from "../strings.js";
import { h, bar, crumb, emptyState } from "../ui.js";
import * as slots from "../slots.js";

export default async function skillcheck() {
  const t = T.sk;
  const qs = await slots.questions();
  const body = h("div");
  let i = 0, picked = null, shown = false;
  const draw = () => {
    if (!qs.length) { body.replaceChildren(emptyState("check", t.emptyTitle, t.emptyText)); return; }
    if (i >= qs.length) { body.replaceChildren(h("div", { class: "card" }, h("h3", { text: t.end }))); return; }
    const q = qs[i], out = h("p", { class: "small", role: "status" });
    const opts = q.options.map((o, k) => h("label", { class: "choice" }, h("input", { type: "radio", name: "q", value: String(k), checked: picked === k, onchange: () => { picked = k; } }), h("span", { class: "box", text: o })));
    body.replaceChildren(h("div", { class: "card", style: "padding:28px" }, h("small", { style: "font-weight:700;letter-spacing:.06em", text: `${t.question} ${i + 1} / ${qs.length}` }), bar(i / qs.length * 100, t.title),
      h("h3", { style: "margin:18px 0", text: q.text }), h("div", { class: "stack" }, opts), out,
      h("div", { class: "row between", style: "margin-top:16px" }, h("button", { class: "btn ghost", type: "button", text: t.skip, onclick: () => { i++; picked = null; draw(); } }),
        h("button", { class: "btn", type: "button", text: t.check, onclick: () => {
          if (picked === null) { out.textContent = t.pick; return; }
          out.textContent = q.answer_index == null ? t.next : picked === q.answer_index ? t.right : t.notQuite;
          setTimeout(() => { i++; picked = null; draw(); }, 900);
        } }))));
  };
  draw();
  return h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead }))),
    h("div", { class: "split" }, body, h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.aboutTitle }), h("p", { class: "muted", text: t.about }))));
}
