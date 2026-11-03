// In-memory screen state. Only the profile id is kept in the browser's storage (rule F8).
function read() { try { return sessionStorage.getItem("profile_id"); } catch (e) { return null; } }
export const S = {
  profileId: read(),
  meta: null,
  // screen 1
  styles: [], checkIn: "weekly", paused: false, consent: true,
  // screen 2
  form: null,
  // screen 3
  extract: null, decisions: {}, added: [],
  // screen 4 and 5
  roleId: null, changeRole: false,
  // one-time message shown at the top of the next screen
  flash: null,
};
export function setProfileId(id) {
  S.profileId = id || null;
  try { id ? sessionStorage.setItem("profile_id", id) : sessionStorage.removeItem("profile_id"); } catch (e) { /* storage blocked: fine */ }
}
export function resetJourney() { S.extract = null; S.decisions = {}; S.added = []; S.roleId = null; }
