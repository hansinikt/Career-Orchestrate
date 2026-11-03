// Demo account and the profile answers that have no backend field yet (schedule, tools, languages, email time ...).
// Kept in sessionStorage so a page refresh on stage does not lose the sign-in. It is cleared when the tab closes.
// ASSUMPTION for the team: rule F8 said "only profile_id in storage". This adds the demo user and these extras until the backend has accounts.
const K_USER = "co_user", K_X = "co_extras";
const rd = (k) => { try { return JSON.parse(sessionStorage.getItem(k)); } catch (e) { return null; } };
const wr = (k, v) => { try { v == null ? sessionStorage.removeItem(k) : sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage blocked: fine */ } };

export const blankExtras = () => ({
  industry: "", phone: "", tools: [], certsHeld: [{ name: "", issuer: "" }], eduList: [{ level: "bachelor", field: "", institution: "" }], goalText: "", langs: [], situation: "", situations: [], barriers: [], cvNote: "",
  best: [], schedule: {}, formats: [], mail: true, mailTime: "07:30", step: 1,
  certs: [],      // certificates the person added: { id, name, link, fileName, added }
  proofs: {},     // mission proof: { [missionId]: { name, at } }
});
export const U = { user: rd(K_USER), x: Object.assign(blankExtras(), rd(K_X) || {}) };
export const saveExtras = () => wr(K_X, U.x);
export function signIn(user) { U.user = { name: user.name, email: user.email }; wr(K_USER, U.user); }
export function signOut() { U.user = null; U.x = blankExtras(); wr(K_USER, null); wr(K_X, null); }
export const initials = (name) => (name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
