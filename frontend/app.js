// STARTER. Router and empty screens only. Build each screen as a function in its own file (screens/screen1.js ...) following the brief.
import { api, ApiError } from "./api.js";
import { T } from "./strings.js";

const app = document.getElementById("app");
const state = { profileId: sessionStorage.getItem("profile_id") || null };   // store ONLY the id (rule F8)
export function setProfileId(id) { state.profileId = id; id ? sessionStorage.setItem("profile_id", id) : sessionStorage.removeItem("profile_id"); }

const screens = {   // replace each stub with the real screen, one at a time
  "1": () => "<h2>1 Welcome, consent and encouragement style</h2><p>TODO</p>",
  "2": () => "<h2>2 Your work</h2><p>TODO</p>",
  "3": () => "<h2>3 Skill evidence review</h2><p>TODO</p>",
  "4": () => "<h2>4 Role matches</h2><p>TODO</p>",
  "5": () => "<h2>5 Learning plan</h2><p>TODO</p>",
  "6": () => "<h2>6 My progress</h2><p>TODO</p>",
  "7": () => "<h2>7 Fairness check (adviser view)</h2><p>TODO</p>",
  "openness": () => "<h2>Job advert check</h2><p>TODO</p>",
};
async function route() {
  const key = (location.hash.replace("#/", "") || "1");
  try { app.innerHTML = await (screens[key] || screens["1"])(); }
  catch (e) { app.innerHTML = `<div class="error">${e instanceof ApiError ? e.message : "Something went wrong. Nothing was lost."}</div>`; }
}
window.addEventListener("hashchange", route);
(async () => {
  try { const m = await api.meta(); document.getElementById("disclaimer").textContent = m.disclaimers[0]; } catch (e) { /* shown by screens */ }
  route();
})();
