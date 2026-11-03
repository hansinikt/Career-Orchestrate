// Missions: small tasks tied to your course chapters. Each has its own progress bar, proof upload and a "Not now" button.
import { T } from "../strings.js";
import { h, bar, crumb, emptyState } from "../ui.js";
import { showEncouragement } from "../panels.js";
import * as slots from "../slots.js";

export default async function missions() {
  const t = T.mis;
  const list = await slots.missions();
  const refresh = () => window.dispatchEvent(new HashChangeEvent("hashchange"));
  const row = (m, i) => {
    const file = h("input", { type: "file", "aria-label": `${t.chooseFile}: ${m.title}`, style: "max-width:240px" }), out = h("small", { class: "err", role: "status" });
    const run = (fn) => fn().then(refresh, (e) => { out.textContent = e.message; });
    let act = null;
    if (m.status === "open") act = h("div", { class: "stack", style: "gap:10px" }, h("div", { class: "row" }, file),
      h("div", { class: "row" },
        h("button", { class: "btn org small", type: "button", text: t.upload, onclick: () => { if (!file.files[0]) { out.textContent = t.needFile; return; } out.textContent = t.saving; run(() => slots.saveProof(m.id, file.files[0])); } }),
        m.percent < 50 ? h("button", { class: "btn ghost small", type: "button", text: t.start, onclick: () => run(() => slots.startMission(m.id)) }) : null,
        h("button", { class: "btn ghost small", type: "button", text: t.notNow, onclick: () => run(async () => { const msg = await slots.declineMission(m.id); if (msg) showEncouragement(msg.text, { href: "#/missions", label: T.enc.back }); }) })), out);
    else if (m.status === "declined") act = h("div", { class: "stack", style: "gap:8px" }, h("span", { class: "st", text: t.setAside }), h("button", { class: "btn ghost small", type: "button", text: t.bringBack, onclick: () => run(() => slots.reopenMission(m.id)) }), out);
    else if (m.status === "done") act = h("span", { class: "st green", text: t.done });
    const stage = m.percent >= 100 ? t.stages[2] : m.percent >= 50 ? t.stages[1] : t.stages[0];
    return h("div", { class: "card item" }, h("span", { class: "mnum", text: String(i + 1) }),
      h("div", { class: "grow" }, h("h4", { text: m.title }), m.chapter_title ? h("div", { class: "sub", text: t.chapter(m.chapter_title) }) : h("div", { class: "sub", text: t.from(m.source) }), h("p", { text: m.brief }),
        h("div", { style: "max-width:380px;margin-top:8px" }, bar(m.percent, m.title), h("small", { class: "faint", text: stage })), act ? h("div", { style: "margin-top:14px" }, act) : null));
  };
  // Missions of a course that is not open yet are shown as one greyed, locked box per course. Inside the open course, the next missions are greyed one by one.
  const courseOf = (m) => { const x = /^Course (\d+): (.*)$/.exec(m.source || ""); return x ? [Number(x[1]), x[2]] : null; };
  const active = new Set(list.filter((m) => m.status !== "locked").map((m) => (courseOf(m) || [])[0]));
  const nodes = []; let n = 0;
  for (let k = 0; k < list.length; k++) {
    const m = list[k], c = courseOf(m);
    if (m.status !== "locked" || !c) { nodes.push(row(m, n++)); continue; }
    if (active.has(c[0])) { n++; nodes.push(h("div", { class: "card item lockedbox", "aria-label": m.title }, h("span", { class: "mnum", "aria-hidden": "true", text: "🔒" }), h("div", { class: "grow" }, h("h4", { text: m.title }), h("p", { text: t.nextText })))); continue; }
    while (k + 1 < list.length && list[k + 1].status === "locked" && (list[k + 1].source || "").startsWith(`Course ${c[0]}:`)) k++;
    nodes.push(h("div", { class: "card item lockedbox", "aria-label": t.lockedTitle(c[0]) }, h("span", { class: "mnum", "aria-hidden": "true", text: "🔒" }),
      h("div", { class: "grow" }, h("h4", { text: t.lockedTitle(c[0]) }), h("div", { class: "sub", text: c[1] }), h("p", { text: t.lockedText(c[0]) }))));
  }
  return h("div", { class: "page" }, crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead }))),
    h("div", { class: "stack" }, nodes.length ? nodes : emptyState("mission", t.emptyTitle, t.emptyText)));
}
