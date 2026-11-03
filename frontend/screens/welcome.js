// First thing after sign-in: a short hello that leads into the profile questions.
import { T } from "../strings.js";
import { U } from "../store.js";
import { h, go } from "../ui.js";
import { logo } from "../art.js";

export default function welcome() {
  const t = T.hi, first = (U.user.name || "").split(" ")[0] || U.user.name;
  const box = h("div", { class: "welcome", "aria-live": "polite" });
  const frame = (...kids) => box.replaceChildren(h("div", { class: "fade" }, ...kids));
  const quick = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const timers = [];
  const begin = () => { timers.forEach(clearTimeout); go("#/onboard/1"); };
  frame(h("h1", { id: "page-title", tabindex: "-1", text: t.hello(first) }));
  timers.push(setTimeout(() => frame(logo(64), h("h1", { id: "page-title", tabindex: "-1", style: "margin-top:14px", text: t.welcome })), quick ? 200 : 1800));
  timers.push(setTimeout(() => frame(h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem", text: t.welcome }), h("p", { class: "lead", style: "margin:22px auto 16px;max-width:30em", text: t.steps }), h("p", { class: "muted", style: "margin:0 auto 40px;max-width:30em", text: t.steps2 }),
    h("button", { class: "btn lg", type: "button", text: t.go, onclick: begin })), quick ? 400 : 4000));
  window.addEventListener("hashchange", () => timers.forEach(clearTimeout), { once: true });
  return h("div", { style: "position:relative" }, box, h("button", { class: "linkbtn", type: "button", style: "position:absolute;right:24px;bottom:24px", text: t.skip, onclick: begin }));
}
