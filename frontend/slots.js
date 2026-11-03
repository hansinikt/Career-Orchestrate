// DATA SLOTS. Every list and number a screen shows comes from a function in this file.
// Screens never invent data. When the backend adds an endpoint, change ONLY the body of the matching function.
//
// Shapes the backend should return (the screens already draw them; empty list = empty state):
//   courses():   [{ order, title, sub, text, hours, url, provider, duration, cost, percent, hasCourse, skill_name }]   <- built from GET /plan and GET /progress (exists today)
//   missions():  [{ id, title, source, brief, status: "open"|"done"|"locked" }]                                        <- NO endpoint yet (returns [] unless config DEMO_EXTRAS)
//   questions(): [{ id, text, options: [string], answer_index?: number }]                                                <- NO endpoint yet (returns [] unless config DEMO_EXTRAS)
//   certificates and proofs are kept on this device until the backend has upload endpoints.
import { api, ApiError } from "./api.js";
import { S } from "./state.js";
import { T } from "./strings.js";
import { U, saveExtras } from "./store.js";

const DEMO = !!window.DEMO_EXTRAS;
const quiet = (e, codes) => e instanceof ApiError && codes.includes(e.code);

export async function plan() {
  if (!S.profileId) return null;
  try { return await api.getPlan(S.profileId); }
  catch (e) { if (quiet(e, ["NO_ACTIVE_PLAN", "SKILLS_NOT_CONFIRMED"])) return null; throw e; }
}
export async function progress() {
  if (!S.profileId) return null;
  try { return await api.getProgress(S.profileId); }
  catch (e) { if (quiet(e, ["NO_ACTIVE_PLAN", "SKILLS_NOT_CONFIRMED"])) return null; throw e; }
}
export function courseRows(p, prog) {
  if (!p) return [];
  const pct = new Map(((prog && prog.steps) || []).map((s) => [s.order, s.percent]));
  return p.steps.map((st) => {
    const r = st.status === "resource_found" ? st.resource : null;
    return {
      order: st.order, skill_name: st.skill_name, hasCourse: !!r,
      title: r ? r.title : st.skill_name, sub: `${T.crs.step(st.order)} · ${st.skill_name}`, text: st.rationale,
      hours: st.est_hours, url: r ? r.url : null, provider: r ? r.provider : null, duration: r ? r.duration_text : null, cost: r ? r.cost : null,
      percent: pct.has(st.order) ? pct.get(st.order) : 0,
    };
  });
}
export async function missions() {
  if (!DEMO) return [];   // TODO(backend): GET /profiles/{id}/missions
  const base = [
    { id: "m1", title: "List five things you would keep private", source: "Step 1", brief: "Write five examples and say why each is private.", status: "open" },
    { id: "m2", title: "Write a one-page note for new joiners", source: "Step 1", brief: "One page, plain words.", status: "open" },
    { id: "m3", title: "Summarise your records process", source: "Step 2", brief: "One paragraph.", status: "locked" },
  ];
  return base.map((m) => (U.x.proofs[m.id] ? Object.assign({}, m, { status: "done" }) : m));
}
export function todayMission(list) { return list.find((m) => m.status === "open") || null; }
export async function questions() {
  if (!DEMO) return [];   // TODO(backend): GET /profiles/{id}/skillcheck
  return [{ id: "q1", text: "A colleague asks for a copy of another person's record. What do you do first?", options: ["Share it with the whole team", "Ask the person who owns the record before sharing", "Keep a copy on your own computer", "Send it to whoever asks first"], answer_index: 1 }];
}
export function saveProof(id, file) {   // TODO(backend): POST /profiles/{id}/missions/{mid}/proof (multipart)
  U.x.proofs[id] = { name: file.name, at: new Date().toISOString().slice(0, 10) }; saveExtras();
}
export function addCertificate(c) { U.x.certs.push(Object.assign({ id: "c" + Date.now(), added: new Date().toISOString().slice(0, 10) }, c)); saveExtras(); }
export function removeCertificate(id) { U.x.certs = U.x.certs.filter((c) => c.id !== id); saveExtras(); }
// Plain text CVs are read in the browser. PDF and Word need a backend reader (TODO(backend): POST /cv/read).
export async function readCv(file) {
  const ok = /\.(txt|md)$/i.test(file.name) || file.type === "text/plain";
  if (!ok) return null;
  const text = await file.text();
  const lines = text.split(/\r?\n/).map((l) => l.replace(/^[\s\-*•\d.)]+/, "").trim()).filter((l) => l.length >= 10);
  return lines.slice(0, 5).map((l) => l.slice(0, 1000));
}
// What the roadmap boxes and dashboard tiles say under the heading. Fallbacks when the backend has nothing yet.
export function roadmapItems(courses, missionList, questionList) {
  const c = courses[0], m = todayMission(missionList) || missionList[0], q = questionList[0];
  return [
    { key: "courses", kind: "course", title: T.nav.courses, sub: c ? c.title : T.road.fallback.courses, text: T.road.text.courses, href: "#/courses" },
    { key: "missions", kind: "mission", title: T.nav.missions, sub: m ? m.title : T.road.fallback.missions, text: T.road.text.missions, href: "#/missions" },
    { key: "skillcheck", kind: "check", title: T.nav.skillcheck, sub: q ? q.text.slice(0, 40) + (q.text.length > 40 ? "…" : "") : T.road.fallback.skillcheck, text: T.road.text.skillcheck, href: "#/skillcheck" },
    { key: "certs", kind: "cert", title: T.nav.certs, sub: T.road.fallback.certs, text: T.road.text.certs, href: "#/certs" },
  ];
}
