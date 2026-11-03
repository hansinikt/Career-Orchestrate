// Screen 6: progress and encouragement. Messages come from the API only; this screen never writes its own.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, pageHead, num, errorPanel, choice, seg, toggle } from "../ui.js";

export default async function screen6() {
  if (!S.profileId) { go("#/onboard"); return null; }
  const t = T.s6;
  const [first, plan, profile] = await Promise.all([api.getProgress(S.profileId), api.getPlan(S.profileId), api.getProfile(S.profileId)]);
  const root = h("div", { class: "page" });
  const mot = Object.assign({ styles: [], check_in: "weekly", paused: false }, profile.motivation || {});

  function draw(p, note) {
    const steps = p.steps.map((s) => h("div", { class: "card" }, h("div", { class: "row between" }, h("h3", { text: s.skill_name }), h("span", { class: "small muted", text: `${T.s4.hours(num(s.est_hours))} · ${t.stepPercent(s.percent)}` })),
      h("div", { class: "seg", role: "radiogroup", "aria-label": s.skill_name }, t.stepStates.map(([label, pct]) =>
        h("label", null, h("input", { type: "radio", name: `step-${s.order}`, value: String(pct), checked: s.percent === pct, onchange: () => update(s.order, pct) }), h("span", { text: label }))))));
    const m = p.next_message;
    root.replaceChildren(
      pageHead(t.title, plan.role_title ? T.s5.forRole(plan.role_title) : null),
      h("div", { class: "card" }, h("div", { class: "row between" }, h("span", { class: "pct", text: `${p.percent}%` }), h("span", { class: "muted", text: `${t.hoursOf(num(p.hours_done), num(p.hours_total))} · ${t.stepsOf(p.steps_done, p.steps_total)}` })),
        h("div", { class: "bar", role: "progressbar", "aria-valuenow": String(p.percent), "aria-valuemin": "0", "aria-valuemax": "100", "aria-label": t.title }, h("i", { style: `width:${p.percent}%` }))),
      messageBox(m, p), h("div", { class: "stack" }, steps), settings(),
      h("div", { class: "row" }, h("a", { class: "linkbtn", href: "#/7", text: t.runFairness })));
  }
  function messageBox(m, p) {
    if (!m) return h("div", { class: "empty" }, h("p", { class: "muted", text: t.noMessage }));
    const fb = h("div", { class: "row" });
    const give = async (ok) => { try { await api.messageFeedback(S.profileId, m.message_id, ok); fb.replaceChildren(h("span", { class: "small muted", text: t.thanks })); } catch (e) { fb.replaceChildren(errorPanel(e)); } };
    fb.append(h("button", { class: "btn ghost small", type: "button", text: t.helpful, onclick: () => give(true) }), h("button", { class: "btn ghost small", type: "button", text: t.notHelpful, onclick: () => give(false) }));
    const share = m.suggested_action === "share_summary" ? h("button", { class: "btn small", type: "button", text: t.copy, onclick: async (e) => {
      try { await navigator.clipboard.writeText(t.summary(plan.role_title, p.percent, p.steps_done, p.steps_total)); e.target.textContent = t.copied; } catch (x) { /* clipboard blocked */ } } }) : null;
    return h("section", { class: "msg", "aria-live": "polite" }, h("p", { text: m.text }), h("div", { class: "row" }, fb, share));
  }
  async function update(order, percent) {
    try { draw(await api.updateProgress(S.profileId, { step_order: order, percent })); }
    catch (e) { root.append(errorPanel(e, () => update(order, percent))); }
  }
  function settings() {
    let styles = [...mot.styles];
    const out = h("span", { class: "small muted", role: "status" });
    const grid = h("div", { class: "choices" });
    const paint = () => grid.replaceChildren(...Object.keys(T.styles).map((k) => choice("checkbox", "mstyle", T.styles[k], T.styleHelp[k], styles.includes(k), (e) => { styles = e.target.checked ? [...styles, k].slice(0, 2) : styles.filter((x) => x !== k); paint(); }, !styles.includes(k) && styles.length >= 2)));
    paint();
    return h("details", { class: "panel" }, h("summary", { style: "cursor:pointer;font-weight:600;min-height:32px", text: t.settings }),
      h("div", { class: "stack", style: "margin-top:14px" }, grid,
        h("div", null, seg("mcheck", Object.entries(T.checkIn), mot.check_in, (v) => { mot.check_in = v; })),
        toggle(T.s1.pauseLabel, T.s1.pauseHelp, mot.paused, (v) => { mot.paused = v; }),
        h("div", { class: "row" }, h("button", { class: "btn small", type: "button", text: t.save, onclick: async () => {
          if (!styles.length) { out.textContent = T.s1.needStyle; return; }
          try { await api.setMotivation(S.profileId, { styles, check_in: mot.check_in, paused: mot.paused }); mot.styles = styles; out.textContent = t.saved; } catch (e) { out.textContent = e.message; } } }), out)));
  }
  draw(first);
  return root;
}
