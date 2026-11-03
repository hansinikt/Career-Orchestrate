// Screen 3 (Gate 1): the worker decides on every suggested skill.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, pageHead, levelWord, errorPanel, spinner } from "../ui.js";

export default async function screen3() {
  if (!S.profileId) { S.flash = T.s2.lead; go("#/onboard"); return null; }
  if (!S.extract || S.extract.profile_id !== S.profileId) { S.extract = await api.extract(S.profileId); S.decisions = {}; S.added = []; }
  const t = T.s3, X = S.extract, D = S.decisions;
  const skillsRes = await api.skills().catch(() => ({ skills: [] }));
  const total = X.suggestions.length;
  const cards = new Map();
  const bar = { count: h("span", { class: "small muted" }), meter: h("i"), btn: h("button", { class: "btn", type: "button", text: t.submit, onclick: submit }), hint: h("span", { class: "small muted" }), out: h("div") };

  const refresh = () => {
    const done = X.suggestions.filter((s) => D[s.suggestion_id] && D[s.suggestion_id].action).length;
    bar.count.textContent = t.decided(done, total);
    bar.meter.style.width = total ? `${(done / total) * 100}%` : "0";
    bar.btn.disabled = done < total;
    bar.hint.textContent = done < total ? t.needAll : "";
    cards.forEach((el, id) => { const a = D[id] && D[id].action; el.classList.toggle("decided", a === "accept" || a === "edit"); el.classList.toggle("rejected", a === "reject"); });
  };
  const decide = (s, action, levelSel) => { D[s.suggestion_id] = { action, level: action === "edit" ? Number(levelSel.value) : undefined }; levelSel.parentElement.hidden = action !== "edit"; refresh(); };

  const card = (s) => {
    const cur = D[s.suggestion_id] || {};
    const lvl = h("select", { id: `lv-${s.suggestion_id}`, "aria-label": `${t.editLevel}: ${s.name}`, onchange: () => { if (D[s.suggestion_id] && D[s.suggestion_id].action === "edit") D[s.suggestion_id].level = Number(lvl.value); } }, [1, 2, 3].map((l) => h("option", { value: String(l), text: levelWord(l) })));
    lvl.value = String(cur.level || s.suggested_level);
    const lvlBox = h("div", { style: "max-width:220px;margin-top:10px", hidden: cur.action !== "edit" }, h("label", { for: lvl.id, text: t.editLevel }), lvl);
    const name = `d-${s.suggestion_id}`;
    const opt = (val, label) => h("label", null, h("input", { type: "radio", name, value: val, checked: cur.action === val, onchange: () => decide(s, val, lvl) }), h("span", { text: label }));
    const ev = s.evidence.length
      ? s.evidence.map((e) => h("blockquote", { class: "quote evidence" }, h("span", { class: "mark", text: `“${e.quote}”` }), h("span", { class: "quote-src", text: t.fromExample(e.work_example_index + 1) })))
      : h("span", { class: "noev", text: T.noEvidence });
    const el = h("article", { class: "card skillcard", "aria-label": s.name },
      h("div", { class: "skillhead" }, h("h3", { text: s.name }), h("span", { class: "chip" }, levelWord(s.suggested_level)), h("span", { class: "badge", text: T.sourceBadge[s.source] || s.source })),
      h("p", { class: "muted small", text: s.explanation }), h("div", null, ev),
      h("div", null, h("div", { class: "seg", role: "radiogroup", "aria-label": s.name }, opt("accept", t.accept), opt("edit", t.edit), opt("reject", t.reject)), lvlBox));
    cards.set(s.suggestion_id, el);
    return el;
  };

  // skills the worker adds (picked from the catalogue)
  const addedList = h("div", { class: "stack" });
  const drawAdded = () => addedList.replaceChildren(...S.added.map((a, i) => h("div", { class: "row" }, h("span", { class: "chip" }, a.name, h("i", { text: levelWord(a.level) })), h("button", { class: "linkbtn", type: "button", text: t.remove, onclick: () => { S.added.splice(i, 1); drawAdded(); fillPick(); } }))));
  const pick = h("select", { id: "add-pick" }), pickLvl = h("select", { id: "add-lvl", "aria-label": t.addLevel }, [1, 2, 3].map((l) => h("option", { value: String(l), text: levelWord(l) })));
  pickLvl.value = "2";
  const fillPick = () => {
    const taken = new Set([...X.suggestions.map((s) => s.skill_id), ...S.added.map((a) => a.skill_id)]);
    pick.replaceChildren(h("option", { value: "", text: t.addSkill }), ...skillsRes.skills.filter((s) => !taken.has(s.skill_id)).map((s) => h("option", { value: s.skill_id, text: s.name })));
  };
  fillPick(); drawAdded();
  const addBtn = h("button", { class: "btn ghost", type: "button", text: t.addButton, onclick: () => {
    if (!pick.value) return; const sk = skillsRes.skills.find((s) => s.skill_id === pick.value);
    S.added.push({ skill_id: sk.skill_id, name: sk.name, level: Number(pickLvl.value) }); drawAdded(); fillPick();
  } });

  async function submit() {
    const body = { decisions: X.suggestions.map((s) => { const d = D[s.suggestion_id]; return d.action === "edit" ? { suggestion_id: s.suggestion_id, action: "edit", level: d.level || s.suggested_level } : { suggestion_id: s.suggestion_id, action: d.action }; }),
      added_skills: S.added.map((a) => ({ skill_id: a.skill_id, level: a.level })) };
    bar.out.replaceChildren(spinner()); bar.btn.disabled = true;
    try { await api.confirm(S.profileId, body); go("#/jobs"); }
    catch (e) { bar.btn.disabled = false; bar.out.replaceChildren(errorPanel(e, submit)); }
  }

  const page = h("div", { class: "page" },
    pageHead(t.title, t.lead, T.yourDecision),
    (X.warnings && X.warnings.length) ? h("div", { class: "note" }, X.warnings.map((w) => h("p", { text: w }))) : null,
    h("div", { class: "stack" }, X.suggestions.map(card)),
    X.unmatched_declared.length ? h("section", { class: "panel" }, h("h2", { text: t.unmatchedTitle }), h("p", { class: "hint", text: t.unmatchedHelp }), h("div", { class: "row" }, X.unmatched_declared.map((n) => h("span", { class: "badge", text: n })))) : null,
    h("section", { class: "panel" }, h("h2", { text: t.addTitle }), h("div", { class: "row" }, h("div", { style: "flex:2;min-width:200px" }, pick), h("div", { style: "flex:1;min-width:140px" }, pickLvl), addBtn), addedList),
    bar.out,
    h("div", { class: "stickybar" }, h("div", { class: "row" }, bar.count, h("div", { class: "meter" }, bar.meter), bar.hint), bar.btn));
  refresh();
  return page;
}
