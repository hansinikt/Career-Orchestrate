// DATA SLOTS. Every list and number a screen shows comes from a function in this file.
// Screens never invent data. When the backend adds an endpoint, change ONLY the body of the matching function.
//
// Shapes the backend should return (the screens already draw them; empty list = empty state):
//   courses():   [{ order, title, sub, text, hours, url, provider, duration, cost, percent, hasCourse, skill_name }]   <- built from GET /plan and GET /progress (exists today)
//   missions():  [{ id, title, source, brief, status: "open"|"done"|"locked" }]                                        <- GET /profiles/{id}/missions (exists)
//   proofs are saved on the server (POST /missions/{id}/proof). Certificates are kept on this device until the backend has an endpoint.
import { api, ApiError } from "./api.js";
import { S } from "./state.js";
import { T } from "./strings.js";
import { U, saveExtras } from "./store.js";

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
// CVs: .txt and .md are read in the browser. PDF and Word (.docx) are sent to POST /cv/file, which returns their text. The text is then read by POST /cv/parse.
// Returns the text, or null for a file type we do not accept. Throws an ApiError with a plain message when the server cannot read the file.
export async function readCvText(file) {
  if (/\.(txt|md)$/i.test(file.name) || file.type === "text/plain") return (await file.text()).slice(0, 20000);
  if (!/\.(pdf|docx?)$/i.test(file.name)) return null;
  if (file.size > 2000000) throw new ApiError("VALIDATION_ERROR", T.wiz.s1.cvTooBig, null, 422);
  const buf = new Uint8Array(await file.arrayBuffer()); let bin = ""; for (let i = 0; i < buf.length; i += 8192) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 8192));
  return (await api.cvFile(file.name, btoa(bin))).text;
}
// What the roadmap boxes and dashboard tiles say under the heading, and whether each part is finished.
export function roadmapItems(courses, missionList, planInfo, prog) {
  const c = courses[0], m = todayMission(missionList) || missionList[0];
  return [
    { key: "jobs", kind: "goal", title: T.nav.jobs, sub: planInfo ? planInfo.role_title : T.road.fallback.jobs, href: "#/jobs", done: !!planInfo },
    { key: "courses", kind: "course", title: T.nav.courses, sub: c ? c.title : T.road.fallback.courses, href: "#/courses", done: !!(prog && prog.percent >= 100) },
    { key: "missions", kind: "mission", title: T.nav.missions, sub: m ? m.title : T.road.fallback.missions, href: "#/missions", done: missionList.length > 0 && missionList.every((x) => x.status === "done") },
    { key: "certs", kind: "cert", title: T.nav.certs, sub: T.road.fallback.certs, href: "#/certs", done: false },
  ];
}
// The courses of the role the person chose (empty when there is no plan yet or the role has no course data). Never throws, so pages can fall back.
export async function chosenCourses(p) {
  if (!p || !p.role_id) return [];
  try { return await roleCourses(p.role_id); } catch (e) { return []; }
}
// Courses for one job option, simplest first. The back end (engine/paths.py) chooses and orders them; this only reshapes them for the screen.
export async function rolePath(roleId) {
  if (!S.profileId) return { courses: [], requirements: [] };
  const r = await api.rolePath(S.profileId, roleId);
  return { requirements: r.requirements, courses: r.courses.map((c) => ({ resource_id: c.resource_id, title: c.title, provider: c.provider, level: c.level, duration_text: c.duration_text, hours: c.est_hours, cost: c.cost,
    rating: c.rating, rating_count: c.rating_count, certificate: c.certificate, prerequisites: c.prerequisites, url: c.url, why: c.why, covers: c.covers, units: c.units || [], topics: c.topics || [], verified: c.verification_status === "verified" })) };
}
export async function roleCourses(roleId) { return (await rolePath(roleId)).courses; }

// Hours a week the person said they can study (from the profile), or null.
export async function weeklyHours() {
  if (!S.profileId) return null;
  try { const p = await api.getProfile(S.profileId); const w = p.preferences && p.preferences.weekly_hours; return w >= 1 ? w : null; } catch (e) { return null; }
}
