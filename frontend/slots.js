// DATA SLOTS. Every list and number a screen shows comes from a function in this file.
// Screens never invent data. When the backend adds an endpoint, change ONLY the body of the matching function.
//
// Shapes the backend should return (the screens already draw them; empty list = empty state):
//   courses():   [{ order, title, sub, text, hours, url, provider, duration, cost, percent, hasCourse, skill_name }]   <- built from GET /plan and GET /progress (exists today)
//   missions():  [{ id, title, source, brief, status: "open"|"done"|"locked" }]                                        <- GET /profiles/{id}/missions (exists)
//   questions(): [{ id, text, options: [string], answer_index?: number }]                                                <- NO endpoint yet (returns [] unless config DEMO_EXTRAS)
//   proofs are saved on the server (POST /missions/{id}/proof). Certificates are kept on this device until the backend has an endpoint.
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
  if (!S.profileId) return [];
  try {
    const r = await api.getMissions(S.profileId);
    return r.missions.map((m) => ({ id: m.mission_id, title: m.title, source: m.source, brief: m.brief, status: m.status, percent: m.percent, chapter_title: m.chapter_title, proof_name: m.proof_name }));
  } catch (e) { if (quiet(e, ["NO_ACTIVE_PLAN", "SKILLS_NOT_CONFIRMED"])) return []; throw e; }
}
export function todayMission(list) { return list.find((m) => m.status === "open") || null; }
export async function questions() {
  if (!DEMO) return [];   // TODO(backend): GET /profiles/{id}/skillcheck
  return [{ id: "q1", text: "A colleague asks for a copy of another person's record. What do you do first?", options: ["Share it with the whole team", "Ask the person who owns the record before sharing", "Keep a copy on your own computer", "Send it to whoever asks first"], answer_index: 1 }];
}
export async function saveProof(id, file) {
  if (file.size > 2000000) throw new ApiError("VALIDATION_ERROR", T.mis.tooBig, null, 422);
  const buf = new Uint8Array(await file.arrayBuffer()); let bin = ""; for (let i = 0; i < buf.length; i += 8192) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 8192));
  await api.uploadProof(S.profileId, id, { file_name: file.name, content_base64: btoa(bin) });
}
export async function startMission(id) { await api.startMission(S.profileId, id); }
export async function reopenMission(id) { await api.reopenMission(S.profileId, id); }
export async function declineMission(id) { const r = await api.declineMission(S.profileId, id); return r.message; }   // the encouragement text, or null when messages are paused
export function addCertificate(c) { U.x.certs.push(Object.assign({ id: "c" + Date.now(), added: new Date().toISOString().slice(0, 10) }, c)); saveExtras(); }
export function removeCertificate(id) { U.x.certs = U.x.certs.filter((c) => c.id !== id); saveExtras(); }
// Plain text CVs (.txt, .md) are read in the browser, then sent as text to POST /cv/parse. PDF and Word return null (not supported yet).
export async function readCvText(file) {
  const ok = /\.(txt|md)$/i.test(file.name) || file.type === "text/plain";
  if (!ok) return null;
  return (await file.text()).slice(0, 20000);
}
// What the roadmap boxes and dashboard tiles say under the heading. Fallbacks when the backend has nothing yet.
export function roadmapItems(courses, missionList, questionList, planInfo) {
  const c = courses[0], m = todayMission(missionList) || missionList[0], q = questionList[0];
  return [
    { key: "jobs", kind: "goal", title: T.nav.jobs, sub: planInfo ? planInfo.role_title : T.road.fallback.jobs, text: T.road.text.jobs, href: "#/jobs" },
    { key: "courses", kind: "course", title: T.nav.courses, sub: c ? c.title : T.road.fallback.courses, text: T.road.text.courses, href: "#/courses" },
    { key: "missions", kind: "mission", title: T.nav.missions, sub: m ? m.title : T.road.fallback.missions, text: T.road.text.missions, href: "#/missions" },
    { key: "skillcheck", kind: "check", title: T.nav.skillcheck, sub: q ? q.text.slice(0, 40) + (q.text.length > 40 ? "…" : "") : T.road.fallback.skillcheck, text: T.road.text.skillcheck, href: "#/skillcheck" },
    { key: "certs", kind: "cert", title: T.nav.certs, sub: T.road.fallback.certs, text: T.road.text.certs, href: "#/certs" },
  ];
}
// Courses for one job option, simplest first. The Course Scout (back end) chooses and orders them; this screen only draws what it gets.
// Shape of each item: { resource_id, title, provider, level: "beginner"|"intermediate"|"advanced"|null, duration_text, cost, rating, rating_count,
//   certificate: true|false|null, prerequisites, url, why, covers: [skill names], verified: boolean }
// TODO(backend): GET /profiles/{id}/paths/{role_id}. Until it exists the list is empty and the role page shows the "being prepared" state.
export async function roleCourses(roleId) {
  return [];
}
