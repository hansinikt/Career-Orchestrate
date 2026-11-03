// One course (one plan step). Progress is written to the backend; the message comes from the backend too.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, bar, crumb, num, errorPanel, emptyState } from "../ui.js";
import * as slots from "../slots.js";

export default async function course(arg) {
  const t = T.crs;
  const [plan, prog0, miss] = await Promise.all([slots.plan(), slots.progress(), slots.missions()]);
  const order = parseInt(arg, 10);
  const rows = slots.courseRows(plan, prog0), row = rows.find((r) => r.order === order);
  if (!row) { go("#/courses"); return null; }
  const related = miss.filter((m) => new RegExp(`^${t.step(order)}(?!\\d)`).test(m.source));
  const root = h("div", { class: "page" });
  let prog = prog0, note = null, chap = null;
  try { chap = await api.chapters(S.profileId, order); } catch (e) { chap = null; }   // no chapter list: the manual progress buttons are used

  const states = h("div", { class: "seg", role: "radiogroup", "aria-label": t.mark });
  async function update(pct) {
    try { prog = await api.updateProgress(S.profileId, { step_order: order, percent: pct }); note = t.saved; draw(); }
    catch (e) { root.append(errorPanel(e, () => update(pct))); }
  }
  function message() {
    const m = prog && prog.next_message; if (!m) return null;
    const fb = h("div", { class: "row" });
    const give = async (ok) => { try { await api.messageFeedback(S.profileId, m.message_id, ok); fb.replaceChildren(h("span", { class: "small muted", text: T.s6.thanks })); } catch (e) { fb.replaceChildren(errorPanel(e)); } };
    fb.append(h("button", { class: "btn ghost small", type: "button", text: T.s6.helpful, onclick: () => give(true) }), h("button", { class: "btn ghost small", type: "button", text: T.s6.notHelpful, onclick: () => give(false) }));
    return h("section", { class: "msg", "aria-live": "polite" }, h("p", { text: m.text }), fb);
  }
  async function tick(id, done) {
    try { const r = await api.tickChapter(S.profileId, order, id, done); prog = await api.getProgress(S.profileId); if (r.next_message) prog.next_message = r.next_message; chap = r; note = t.saved; draw(); }
    catch (e) { root.append(errorPanel(e, () => tick(id, done))); }
  }
  function draw() {
    const cur = (prog && prog.steps.find((s) => s.order === order)) || { percent: 0 };
    const chapterCard = chap && chap.source === "chapters"
      ? h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.chaptersTitle }), h("p", { class: "muted small", text: t.chaptersHelp }),
          h("div", { class: "stack", style: "gap:8px" }, chap.chapters.map((c) => h("label", { class: "row", style: "gap:10px;align-items:center;cursor:pointer" }, h("input", { type: "checkbox", checked: c.done, onchange: (e) => tick(c.chapter_id, e.target.checked) }), h("span", { text: c.title })))),
          note ? h("small", { role: "status", class: "faint", text: note }) : null) : null;
    const segs = h("div", { class: "seg", role: "radiogroup", "aria-label": t.mark }, t.states.map(([label, pct]) => h("label", null,
      h("input", { type: "radio", name: "cstate", value: String(pct), checked: cur.percent === pct, onchange: () => update(pct) }), h("span", { text: label }))));
    const facts = [[t.provider, row.provider], [t.duration, row.duration], [t.cost, row.cost], [t.hours, num(row.hours)]].filter(([, v]) => v);
    root.replaceChildren(crumb(t.detailCrumb(row.title)),
      h("div", { class: "head" }, h("div", { style: "max-width:760px" }, h("h1", { id: "page-title", tabindex: "-1", text: row.title }), h("div", { class: "sub", text: row.sub }), h("p", { class: "lead", text: row.text })),
        row.url ? h("a", { class: "btn org", href: row.url, target: "_blank", rel: "noopener noreferrer", text: t.openPage }) : null),
      h("div", { class: "split" }, h("div", { class: "stack" }, message(),
        chapterCard || h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.mark }), segs, note ? h("small", { role: "status", class: "faint", text: note }) : null),
        h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.related }), related.length ? related.map((m) => h("div", { class: "row between" }, h("b", { text: m.title }), h("a", { class: "btn ghost small", href: "#/missions", text: T.mis.open }))) : h("p", { class: "muted", text: t.relatedEmpty }))),
        h("div", { class: "stack" }, h("div", { class: "card" }, h("h3", { style: "font-size:1.2rem", text: t.progress }), bar(cur.percent, row.title),
          h("div", { class: "kv" }, h("div", null, h("small", { text: t.lastActivity }), h("b", { text: prog && prog.last_activity_at ? prog.last_activity_at.slice(0, 10) : t.none }))),
          ),
          facts.length ? h("div", { class: "card" }, facts.map(([k, v]) => h("div", { class: "row between" }, h("small", { text: k }), h("b", { text: v })))) : null,
          row.hasCourse ? h("p", { class: "small muted", text: t.checkPage }) : h("div", { class: "note", text: t.noCourse }))));
  }
  draw();
  return root;
}
