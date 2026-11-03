// Landing page: one trail drawn from "where you are" to a goal, then what it does, how it works, screenshots, and a final call.
// All text lives in strings.js. Motion: the trail draws once on load; sections reveal once on scroll (CSS only, switched off for reduced motion).
import { T } from "../strings.js";
import { h } from "../ui.js";
import { trail } from "../art.js";

const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export default function landing() {
  const t = T.land;
  const hero = h("section", { class: "hero" }, h("div", { class: "inner" },
    h("div", { class: "hero-copy" }, h("h1", { id: "page-title", tabindex: "-1" }, t.title[0], h("br"), t.title[1]), h("p", { class: "lead", text: t.lead }),
      h("div", { class: "row" }, h("a", { class: "btn lg", href: "#/signin", text: t.start }))),
    h("div", { class: "hero-trail", role: "img", "aria-label": t.trailAlt }, trail(t.trail))));

  // the six agents, in the order the work flows (indexes into t.feats)
  const agent = ([, title, text]) => h("li", { class: "agent rv" }, h("h3", { text: title }), h("p", { text }));
  const features = h("section", { class: "band-section", id: "features" }, h("div", { class: "inner split-head" },
    h("div", { class: "rv" }, h("h2", { text: t.agentsTitle }), h("p", { class: "lead", text: t.agentsLead })),
    h("ol", { class: "agents" }, t.feats.map(agent))));

  const how = h("section", { class: "band-section tint", id: "how" }, h("div", { class: "inner" }, h("h2", { class: "rv", text: t.howTitle }),
    h("ol", { class: "legs" }, t.how.map(([title, text], i) => h("li", { class: "leg rv", style: `--d:${i * 90}ms` }, h("span", { class: "stop", "aria-hidden": "true" }, String(i + 1)), h("h3", { text: title }), h("p", { text }))))));

  const slides = t.shots, track = h("div", { class: "car-track", tabindex: "0", role: "region", "aria-label": t.shotsTitle });
  const dots = h("div", { class: "car-dots" });
  slides.forEach(([k, title, cap], i) => {
    track.append(h("figure", { class: "car-slide" }, h("img", { src: `img/shot-${k}.jpg`, alt: title, loading: i ? "lazy" : "eager" }), h("figcaption", null, h("b", { text: title }), h("span", { text: cap }))));
    dots.append(h("button", { class: "car-dot", type: "button", "aria-label": title, onclick: () => track.scrollTo({ left: i * track.clientWidth, behavior: "smooth" }) }));
  });
  const cur = () => Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
  const sync = () => {
    [...dots.children].forEach((d, i) => d.classList.toggle("on", i === cur()));
    if (reduced()) return;
    const w = Math.max(1, track.clientWidth);   // light parallax: each picture drifts a little against its frame
    [...track.children].forEach((s, i) => s.style.setProperty("--p", ((i * w - track.scrollLeft) / w).toFixed(3)));
  };
  track.addEventListener("scroll", () => requestAnimationFrame(sync));
  const step = (d) => track.scrollTo({ left: Math.max(0, Math.min(slides.length - 1, cur() + d)) * track.clientWidth, behavior: "smooth" });
  track.addEventListener("keydown", (e) => { if (e.key === "ArrowRight") step(1); if (e.key === "ArrowLeft") step(-1); });
  queueMicrotask(sync);
  const shots = h("section", { class: "band-section", id: "shots" }, h("div", { class: "inner" }, h("h2", { class: "rv", text: t.shotsTitle }),
    h("div", { class: "car rv" }, h("div", { class: "car-frame" }, track, h("button", { class: "car-arrow left", type: "button", "aria-label": t.prev, text: "‹", onclick: () => step(-1) }),
      h("button", { class: "car-arrow right", type: "button", "aria-label": t.next, text: "›", onclick: () => step(1) })), dots)));

  const cta = h("section", { class: "cta" }, h("div", { class: "inner rv" }, h("h2", { text: t.ctaTitle }), h("p", { text: t.ctaLead }), h("a", { class: "btn white lg", href: "#/signin", text: t.start })));

  const page = h("div", { class: "land" }, hero, features, how, shots, cta);
  if (!reduced() && "IntersectionObserver" in window) {
    page.classList.add("rv-on");   // content stays visible if this never runs
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: 0.15 });
    queueMicrotask(() => page.querySelectorAll(".rv").forEach((el) => io.observe(el)));
  }
  return page;
}
