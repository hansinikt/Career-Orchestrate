// Missions: small tasks with proof upload. Empty until the backend sends missions.
import { T } from "../strings.js";
import { h, bar, crumb, emptyState } from "../ui.js";
import * as slots from "../slots.js";

export default async function missions() {
  const t = T.mis;
  const list = await slots.missions();
  const done = list.filter((m) => m.status === "done").length;
  const row = (m, i) => {
    const file = h("input", { type: "file", "aria-label": `${t.chooseFile}: ${m.title}`, style: "max-width:240px" }), out = h("small", { class: "err", role: "status" });
    const act = m.status === "done" ? h("span", { class: "st green", text: t.done })
      : m.status === "locked" ? null
      : h("div", { class: "row" }, file, h("button", { class: "btn org small", type: "button", text: t.upload, onclick: () => { if (!file.files[0]) { out.textContent = t.needFile; return; } slots.saveProof(m.id, file.files[0]); window.dispatchEvent(new HashChangeEvent("hashchange")); } }), out);
    return h("div", { class: "card item" }, h("span", { class: "mnum", text: String(i + 1) }), h("div", { class: "grow" }, h("h4", { text: m.title }), h("p", { text: m.brief }), h("div", { class: "sub", text: t.from(m.source) })), act);
  };
  const how = h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.howTitle }), t.how.map((s, i) => h("div", { class: "item" }, h("span", { class: "chip", text: String(i + 1) }), h("span", { text: s }))));
  return h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead }))),
    h("div", { class: "split" }, h("div", { class: "stack" }, list.length ? list.map(row) : emptyState("mission", t.emptyTitle, t.emptyText), h("div", null, h("small", { class: "faint", text: t.progress }), h("div", { style: "margin-top:8px" }, bar(list.length ? done / list.length * 100 : 0, t.progress)))), how));
}
