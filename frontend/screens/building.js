// The loading screens. They run the real backend calls and tick each agent row as its call returns.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S, setProfileId, resetJourney } from "../state.js";
import { h, go, errorPanel, handleError } from "../ui.js";
import { logo } from "../art.js";
import { buildBody, firstProblem } from "./wizard.js";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// rows: [[agent, what]]. tasks: [{ rows: [index...], fn }]. A short minimum per task keeps the screen readable.
function stage({ hash, title, lead, rows, tasks, done }) {
  const state = rows.map(() => "wait");
  const list = h("div", { class: "card rows" });
  const wrap = h("div", { class: "loadwrap" }, h("div", { class: "loadbox" }, logo(64), h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem;margin:16px 0 8px", text: title }), h("p", { class: "muted", text: lead }), list, h("div", { id: "load-out" }), h("p", { class: "small faint", style: "margin-top:20px", text: T.load.note })));
  const paint = () => list.replaceChildren(...rows.map(([a, w], i) => h("div", { class: "r " + state[i] }, h("span", { class: "ic", text: state[i] === "done" ? "✓" : "" }), h("div", { style: "text-align:left" }, h("b", { text: a }), h("div", { class: "small faint", text: w })))));
  const run = async () => {
    wrap.querySelector("#load-out").replaceChildren();
    state.fill("wait");
    try {
      for (const t of tasks) {
        t.rows.forEach((i) => { state[i] = "run"; }); paint();
        await Promise.all([t.fn(), sleep(450)]);
        t.rows.forEach((i) => { state[i] = "done"; }); paint();
      }
      if (location.hash === "#/" + hash) done();   // do nothing if the person already left this screen
    } catch (e) {
      const node = handleError(e, run);
      if (node) wrap.querySelector("#load-out").replaceChildren(errorPanel(e, run));
    }
  };
  paint(); queueMicrotask(run);
  return wrap;
}

export async function building1() {
  const p = firstProblem();
  if (!S.form || p) { if (p) S.flash = p.msg; go(`#/onboard/${p ? p.step : 1}`); return null; }
  const t = T.load;
  return stage({
    hash: "building", title: t.title1, lead: t.lead1, rows: t.rows1,
    tasks: [
      { rows: [0], fn: async () => {
        if (S.profileId) { try { await api.deleteProfile(S.profileId); } catch (e) { /* old profile already gone */ } }
        resetJourney();
        const profile = await api.createProfile(buildBody()); setProfileId(profile.profile_id);
      } },
      { rows: [1], fn: async () => { S.extract = await api.extract(S.profileId); } },
    ],
    done: () => go("#/3"),
  });
}
export async function building2() {
  if (!S.roleId) { go("#/4"); return null; }
  const t = T.load, hrs = S.form && parseInt(S.form.hours, 10), weekly = hrs >= 1 && hrs <= 40 ? hrs : undefined;
  return stage({
    hash: "5", title: t.title2, lead: t.lead2, rows: t.rows2,
    tasks: [
      { rows: [0, 1], fn: async () => { await api.makePlan(S.profileId, weekly ? { role_id: S.roleId, weekly_hours: weekly } : { role_id: S.roleId }); } },
      { rows: [2], fn: async () => { await api.getProgress(S.profileId); } },
    ],
    done: () => go("#/roadmap"),
  });
}
