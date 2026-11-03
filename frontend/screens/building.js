// The loading screens. They run the real backend calls and tick each agent row as its call returns.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S, setProfileId, resetJourney } from "../state.js";
import { h, go, errorPanel, handleError } from "../ui.js";
import { logo } from "../art.js";
import { buildBody, backgroundBody, firstProblem } from "./wizard.js";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// rows: [[agent, what]]. tasks: [{ rows: [index], min, fn }], one agent per task. Agents show one at a time and slide to the next when done.
function stage({ hash, title, lead, rows, tasks, done }) {
  const dots = h("div", { class: "agent-dots", "aria-hidden": "true" }, tasks.map(() => h("span", { class: "ad" })));
  const stageBox = h("div", { class: "agent-stage", "aria-live": "polite" });
  const wrap = h("div", { class: "loadwrap" }, h("div", { class: "loadbox" }, logo(64), h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem;margin:16px 0 8px", text: title }), h("p", { class: "muted", text: lead }), dots, stageBox, h("div", { id: "load-out" }), h("p", { class: "small faint", style: "margin-top:20px", text: T.load.note })));
  const card = (i, st) => { const [a, w] = rows[tasks[i].rows[0]]; return h("div", { class: "card agentcard " + st }, h("span", { class: "ic", text: st === "done" ? "✓" : "" }), h("div", { style: "text-align:left" }, h("small", { class: "faint", text: T.load.agentOf(i + 1, tasks.length) }), h("h3", { style: "margin:2px 0", text: a }), h("div", { class: "small muted", text: w }))); };
  const show = (i, st) => { stageBox.replaceChildren(card(i, st)); [...dots.children].forEach((d, j) => d.className = "ad" + (j < i || (j === i && st === "done") ? " done" : j === i ? " on" : "")); };
  const run = async () => {
    wrap.querySelector("#load-out").replaceChildren();
    try {
      for (let i = 0; i < tasks.length; i++) {
        show(i, "run");
        await Promise.all([tasks[i].fn(), sleep(tasks[i].min || 1500)]);
        show(i, "done"); await sleep(450);
      }
      if (location.hash === "#/" + hash) done();   // do nothing if the person already left this screen
    } catch (e) {
      const node = handleError(e, run);
      if (node) wrap.querySelector("#load-out").replaceChildren(errorPanel(e, run));
    }
  };
  queueMicrotask(run);
  return wrap;
}

export async function building1() {
  const p = firstProblem();
  if (!S.form || p) { if (p) S.flash = p.msg; go(`#/onboard/${p ? p.step : 1}`); return null; }
  const t = T.load;
  return stage({
    hash: "building", title: t.title1, lead: t.lead1, rows: t.rows1,
    tasks: [
      { rows: [0], min: 900, fn: async () => {
        if (S.profileId) { try { await api.deleteProfile(S.profileId); } catch (e) { /* old profile already gone */ } }
        resetJourney();
        const profile = await api.createProfile(buildBody()); setProfileId(profile.profile_id);
        await api.putBackground(S.profileId, backgroundBody());
      } },
      { rows: [1], min: 4000, fn: async () => { S.extract = await api.extract(S.profileId); } },
      // The skills we found are added to the profile (the separate "check your skills" screen was removed). Skills the person typed themselves were already theirs.
      { rows: [2], min: 1500, fn: async () => { await api.confirm(S.profileId, { decisions: S.extract.suggestions.map((x) => ({ suggestion_id: x.suggestion_id, action: "accept" })), added_skills: [] }); } },
    ],
    done: () => go("#/jobs"),
  });
}
export async function building2() {
  if (!S.roleId) { go("#/jobs"); return null; }
  const t = T.load, hrs = S.form && parseInt(S.form.hours, 10), weekly = hrs >= 1 && hrs <= 40 ? hrs : undefined;
  let pending = null;   // one plan call shared by the first two agents
  const once = () => pending || (pending = api.makePlan(S.profileId, weekly ? { role_id: S.roleId, weekly_hours: weekly } : { role_id: S.roleId }).catch((e) => { pending = null; throw e; }));
  return stage({
    hash: "5", title: t.title2, lead: t.lead2, rows: t.rows2,
    tasks: [
      { rows: [0], min: 1800, fn: once },
      { rows: [1], min: 2200, fn: once },
      { rows: [2], min: 1800, fn: async () => { await api.getProgress(S.profileId); } },
    ],
    done: () => go("#/roadmap"),
  });
}
