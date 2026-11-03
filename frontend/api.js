// THE ONLY FILE THAT TALKS TO THE BACKEND. Screens call these functions and never use fetch directly.
// Field names are defined by contracts/v2/models.py. Do not rename, add or remove fields here.
const BASE = window.API_BASE || "/api/v1";
const TIMEOUT_MS = 15000;

export class ApiError extends Error {
  // code: one of the contract codes (VALIDATION_ERROR, FORBIDDEN_FIELD, NOT_FOUND, CONSENT_REQUIRED, SKILLS_NOT_CONFIRMED, NO_ACTIVE_PLAN, INTERNAL)
  // or the client-only codes NETWORK and TIMEOUT.
  constructor(code, message, details, status) { super(message); this.code = code; this.details = details || null; this.status = status || 0; }
}

async function call(method, path, body) {
  const ctl = new AbortController(); const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  let res;
  try {
    res = await fetch(BASE + path, { method, headers: body === undefined ? {} : { "Content-Type": "application/json" },
                                     body: body === undefined ? undefined : JSON.stringify(body), signal: ctl.signal });
  } catch (e) {
    throw e.name === "AbortError" ? new ApiError("TIMEOUT", "The server took too long to answer. Please try again.")
                                  : new ApiError("NETWORK", "Cannot reach the server. Check that the backend is running.");
  } finally { clearTimeout(timer); }
  if (res.status === 204) return null;
  let data = null; try { data = await res.json(); } catch (e) { /* not JSON */ }
  if (!res.ok) {
    const err = data && data.error ? data.error : { code: "INTERNAL", message: "Something went wrong. Nothing was lost. Try again." };
    throw new ApiError(err.code, err.message, err.details, res.status);
  }
  return data;
}

const P = (id) => `/profiles/${encodeURIComponent(id)}`;
export const api = {
  health:            ()            => call("GET", "/health"),
  meta:              ()            => call("GET", "/meta"),
  roles:             ()            => call("GET", "/roles"),                       // { roles: [...] }
  skills:            ()            => call("GET", "/skills"),                      // { skills: [...] }
  demoPersonas:      ()            => call("GET", "/demo/personas"),               // { synthetic: true, personas: [...] }
  createProfile:     (body)        => call("POST", "/profiles", body),             // body: ProfileCreate
  getProfile:        (id)          => call("GET", P(id)),
  deleteProfile:     (id)          => call("DELETE", P(id)),                       // returns null
  extract:           (id)          => call("POST", P(id) + "/extract"),            // ExtractResponse
  confirm:           (id, body)    => call("POST", P(id) + "/confirm", body),      // body: ConfirmRequest
  recommendations:   (id)          => call("GET", P(id) + "/recommendations"),
  rolePath:          (id, roleId)  => call("GET", P(id) + `/paths/${encodeURIComponent(roleId)}`),     // RolePathResponse: courses for one job option, simplest first
  makePlan:          (id, body)    => call("POST", P(id) + "/plan", body),         // body: { role_id, weekly_hours? }
  getPlan:           (id)          => call("GET", P(id) + "/plan"),
  setMotivation:     (id, body)    => call("PUT", P(id) + "/motivation", body),    // body: { styles, check_in, paused }
  getProgress:       (id)          => call("GET", P(id) + "/progress"),
  updateProgress:    (id, body)    => call("POST", P(id) + "/progress", body),     // body: { step_order, percent, hours_logged? }
  messageFeedback:   (id, mid, ok) => call("POST", P(id) + `/messages/${encodeURIComponent(mid)}/feedback`, { helpful: ok }), // returns null
  readinessCheck:    (text)        => call("POST", "/readiness/check", { text }),
  startAudit:        (id, canary)  => call("POST", P(id) + "/audit", { canary: !!canary }),
  getAudit:          (aid)         => call("GET", `/audits/${encodeURIComponent(aid)}`),
  reviewAudit:       (aid, body)   => call("POST", `/audits/${encodeURIComponent(aid)}/review`, body), // body: { reviewer, decision, note? }
  getTrace:          (id)          => call("GET", P(id) + "/trace"),               // { steps: [{ step, agent, mode, input_summary, output_summary, stopped_at_gate }] }
  getMarket:         (id)          => call("GET", P(id) + "/market"),              // { held, next_skills, roles_in_catalogue, source_note }
  scout:             (id)          => call("POST", P(id) + "/scout"),              // Course Scout proposals; nothing changes until approved
  scoutApprove:      (id, choices) => call("POST", P(id) + "/scout/approve", { choices }), // choices: [{ order, resource_id }] -> PlanResponse
  getMissions:       (id)          => call("GET", P(id) + "/missions"),
  startMission:      (id, mid)     => call("POST", P(id) + `/missions/${encodeURIComponent(mid)}/start`),
  declineMission:    (id, mid)     => call("POST", P(id) + `/missions/${encodeURIComponent(mid)}/decline`),   // { missions, message|null }
  reopenMission:     (id, mid)     => call("POST", P(id) + `/missions/${encodeURIComponent(mid)}/reopen`),
  chapters:          (id, order)   => call("GET", P(id) + `/steps/${order}/chapters`),                      // { chapters, percent, source: "chapters"|"manual", next_message }
  tickChapter:       (id, order, chapter_id, done) => call("POST", P(id) + `/steps/${order}/chapters`, { chapter_id, done }),
  parseCv:           (text)        => call("POST", "/cv/parse", { text }),
  cvFile:            (name, b64)   => call("POST", "/cv/file", { file_name: name, content_base64: b64 }),   // PDF or Word (.docx) to { text, truncated, pages }
  putBackground:     (id, body)    => call("PUT", P(id) + "/background", body),
  getBackground:     (id)          => call("GET", P(id) + "/background"),
  getCv:             (id)          => call("GET", P(id) + "/cv"),                                              // { file_name, text, sections }
  uploadProof:       (id, mid, body) => call("POST", P(id) + `/missions/${encodeURIComponent(mid)}/proof`, body), // body: { file_name, content_base64, note? }
};
