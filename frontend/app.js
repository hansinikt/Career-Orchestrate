// Shell and router. Each screen lives in screens/ and returns a DOM node (or null after sending the person elsewhere).
import { api } from "./api.js";
import { T } from "./strings.js";
import { S, setProfileId, resetJourney } from "./state.js";
import { U, signOut, initials } from "./store.js";
import { h, spinner, handleError, go } from "./ui.js";
import { logo } from "./art.js";
import * as slots from "./slots.js";
import landing from "./screens/landing.js";
import signin from "./screens/signin.js";
import welcome from "./screens/welcome.js";
import wizard from "./screens/wizard.js";
import { building1, building2 } from "./screens/building.js";
import screen3 from "./screens/screen3.js";
import jobs from "./screens/jobs.js";
import role from "./screens/role.js";
import roadmap from "./screens/roadmap.js";
import dashboard from "./screens/dashboard.js";
import courses from "./screens/courses.js";
import course from "./screens/course.js";
import missions from "./screens/missions.js";
import certs from "./screens/certs.js";
import profile from "./screens/profile.js";
import screen7 from "./screens/screen7.js";
import screenOpenness from "./screens/screen_openness.js";

// layout: "public" (landing, sign in), "flow" (profile questions, gates, loading), "app" (the main site)
const ROUTES = {
  "": { fn: landing, layout: "public" }, features: { fn: landing, layout: "public" }, how: { fn: landing, layout: "public" }, shots: { fn: landing, layout: "public" },
  signin: { fn: signin, layout: "public" },
  welcome: { fn: welcome, layout: "flow", auth: true }, onboard: { fn: wizard, layout: "flow", auth: true }, building: { fn: building1, layout: "flow", auth: true },
  "3": { fn: screen3, layout: "flow", auth: true, need: true }, "4": { fn: () => { go("#/jobs"); return null; }, layout: "flow", auth: true, need: true }, "5": { fn: building2, layout: "flow", auth: true, need: true },
  jobs: { fn: jobs, layout: "app", auth: true, need: true, tab: "jobs" }, role: { fn: role, layout: "app", auth: true, need: true, tab: "jobs" },
  roadmap: { fn: roadmap, layout: "app", auth: true, need: true, tab: "roadmap" }, dashboard: { fn: dashboard, layout: "app", auth: true, need: true, tab: "dashboard" },
  courses: { fn: courses, layout: "app", auth: true, need: true, tab: "courses" }, course: { fn: course, layout: "app", auth: true, need: true, tab: "courses" },
  missions: { fn: missions, layout: "app", auth: true, need: true, tab: "missions" },
  certs: { fn: certs, layout: "app", auth: true, tab: "certs" }, profile: { fn: profile, layout: "app", auth: true, need: true },
  "7": { fn: screen7, layout: "app", auth: true }, openness: { fn: screenOpenness, layout: "public" },
};
const main = document.getElementById("app");
const chrome = document.getElementById("chrome");
document.getElementById("skip").textContent = T.skipLink;
let routeId = 0;

const link = (href, text, on) => h("a", { href, class: on ? "on" : null, "aria-current": on ? "page" : null, text });
const brand = () => h("a", { class: "brand", href: U.user ? "#/dashboard" : "#/" }, logo(30), h("b", { text: T.appName }));

// ---- search (pages, courses, missions) ----
const PAGES = () => [[T.nav.dashboard, "#/dashboard"], [T.nav.roadmap, "#/roadmap"], [T.nav.jobs, "#/jobs"], [T.nav.courses, "#/courses"], [T.nav.missions, "#/missions"], [T.nav.certs, "#/certs"],
  [T.menu.profile, "#/profile"], [T.menu.schedule, "#/profile/schedule"], [T.menu.encourage, "#/profile/encourage"], [T.menu.email, "#/profile/email"]];
function searchBox() {
  const input = h("input", { type: "search", "aria-label": T.search.label, placeholder: T.search.placeholder, autocomplete: "off" });
  const out = h("div", { class: "results", hidden: true, role: "listbox" });
  let extra = null;
  const load = async () => {
    if (extra) return extra; extra = [];
    try {
      const p = await slots.plan(); const rc = await slots.chosenCourses(p);
      if (rc.length) rc.forEach((c) => extra.push([c.title, "#/courses", T.nav.courses]));
      else slots.courseRows(p, null).forEach((r) => extra.push([r.title, `#/course/${r.order}`, T.nav.courses]));
      (await slots.missions()).forEach((m) => extra.push([m.title, "#/missions", T.nav.missions]));
    } catch (e) { /* search still works for pages */ }
    return extra;
  };
  const show = async () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { out.hidden = true; return; }
    const all = PAGES().map(([t, href]) => [t, href, T.search.pages]).concat(await load());
    const hits = all.filter(([t]) => t.toLowerCase().includes(q)).slice(0, 8);
    out.replaceChildren(...(hits.length ? hits.map(([t, href, kind]) => h("a", { href, role: "option", onclick: () => { out.hidden = true; input.value = ""; } }, t, h("small", { text: kind }))) : [h("div", { class: "small faint", style: "padding:10px 12px", text: T.search.none })]));
    out.hidden = false;
  };
  input.addEventListener("input", show);
  input.addEventListener("keydown", (e) => { if (e.key === "Escape") { out.hidden = true; input.blur(); } });
  document.addEventListener("click", (e) => { if (!wrap.contains(e.target)) out.hidden = true; });
  const wrap = h("div", { class: "search" }, input, out);
  return wrap;
}
// ---- profile menu ----
function meMenu() {
  const dd = h("div", { class: "dd", hidden: true, role: "menu" },
    h("div", { class: "who" }, h("b", { text: U.user.name }), h("span", { text: U.user.email })),
    h("a", { href: "#/profile", role: "menuitem", text: T.menu.profile }), h("a", { href: "#/profile/schedule", role: "menuitem", text: T.menu.schedule }),
    h("a", { href: "#/certs", role: "menuitem", text: T.menu.certs }), h("a", { href: "#/profile/encourage", role: "menuitem", text: T.menu.encourage }),
    h("a", { href: "#/profile/email", role: "menuitem", text: T.menu.email }), h("hr"),
    h("button", { type: "button", role: "menuitem", text: T.menu.logout, onclick: () => { signOut(); setProfileId(null); resetJourney(); S.form = null; go("#/"); } }));
  const btn = h("button", { type: "button", "aria-haspopup": "menu", "aria-expanded": "false", onclick: () => { dd.hidden = !dd.hidden; btn.setAttribute("aria-expanded", String(!dd.hidden)); } },
    h("span", { class: "av", text: initials(U.user.name) }), h("b", { text: U.user.name.split(" ")[0] }), h("span", { "aria-hidden": "true", text: "▾" }));
  const wrap = h("div", { class: "me" }, btn, dd);
  document.addEventListener("click", (e) => { if (!wrap.contains(e.target)) { dd.hidden = true; btn.setAttribute("aria-expanded", "false"); } });
  wrap.addEventListener("keydown", (e) => { if (e.key === "Escape") { dd.hidden = true; btn.focus(); } });
  dd.addEventListener("click", (e) => { if (e.target.closest("a")) dd.hidden = true; });
  return wrap;
}
function drawChrome(r) {
  let inner;
  if (r.layout === "public" || !U.user) {
    inner = [brand(), h("nav", { class: "nav", "aria-label": "Main" }, link("#/features", T.pub.features), link("#/how", T.pub.how), link("#/shots", T.pub.shots)),
      h("div", { class: "grow" }), U.user ? meMenu() : h("a", { class: "btn small", href: "#/signin", text: T.pub.signin })];
  } else if (r.layout === "flow") {
    inner = [brand(), h("div", { class: "grow" }), meMenu()];
  } else {
    const tabs = [["dashboard", T.nav.dashboard], ["roadmap", T.nav.roadmap], ["jobs", T.nav.jobs], ["courses", T.nav.courses], ["missions", T.nav.missions], ["certs", T.nav.certs]];
    inner = [brand(), h("nav", { class: "nav", "aria-label": "Main" }, tabs.map(([k, t]) => link(`#/${k}`, t, r.tab === k))), h("div", { class: "grow" }), searchBox(), meMenu()];
  }
  chrome.replaceChildren(h("div", { class: "top-in" }, inner));
}
async function route() {
  const my = ++routeId;
  const parts = location.hash.replace(/^#\/?/, "").split("/");
  const key = parts[0] in ROUTES ? parts[0] : "";
  const arg = parts[1] || null;
  const r = ROUTES[key];
  if (r.auth && !U.user) { go("#/signin"); return; }
  if (r.need && !S.profileId) { go("#/onboard"); return; }
  drawChrome(r);
  main.replaceChildren(spinner(T.loading));
  let node;
  try { node = await r.fn(arg, key); } catch (e) { node = handleError(e, route); }
  if (my !== routeId || !node) return;
  const flash = S.flash ? h("div", { class: "page", style: "padding-bottom:0" }, h("div", { class: "note warn", role: "status", text: S.flash })) : null; S.flash = null;
  main.replaceChildren(...(flash ? [flash, node] : [node]));
  const anchor = ["features", "how", "shots"].includes(key) ? document.getElementById(key) : null;
  if (anchor) anchor.scrollIntoView(); else window.scrollTo(0, 0);
  const t = document.getElementById("page-title"); if (t && !anchor) t.focus({ preventScroll: true });
}
window.addEventListener("hashchange", route);
(async () => {
  try { S.meta = await api.meta(); } catch (e) { /* the screens show connection problems */ }
  route();
})();
