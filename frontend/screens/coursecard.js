// One course as an expandable card. Closed: the title, the reason it is on the path, and the headline facts.
// Open: every fact we have about it and a button to the course page. Facts come from the back end as text and are shown as text.
import { T } from "../strings.js";
import { h, num } from "../ui.js";
import { ill } from "../art.js";

export function courseCard(c, n) {
  const r = T.role, d = r.d;
  const time = c.hours ? r.time(num(c.hours)) : (c.duration_text || r.timeNone);
  const rating = c.rating != null ? r.rating(c.rating, c.rating_count) : r.noRating;
  const cost = c.cost ? r.cost(c.cost) : r.costNone;
  const cert = c.certificate === true ? r.cert.yes : c.certificate === false ? r.cert.no : r.cert.unknown;
  const level = c.level ? r.levelWord[c.level] : r.unknown;
  const more = h("span", { class: "more", text: r.more + " ▾" });
  const row = (k, v) => v ? [h("dt", { text: k }), h("dd", { text: v })] : [];
  const el = h("details", { class: "card coursecard" },
    h("summary", null, ill("course", 56),
      h("div", { class: "grow" }, h("h4", { style: "font-size:1.08rem", text: c.title }), h("div", { class: "sub", text: [r.step(n), c.provider].filter(Boolean).join(" · ") }),
        c.why ? h("p", { class: "small", style: "margin:6px 0 0" }, h("b", { text: r.why + ": " }), c.why) : null,
        c.covers && c.covers.length ? h("p", { class: "small muted", style: "margin:4px 0 0" }, h("b", { text: r.covers + ": " }), c.covers.join(", ")) : null,
        h("div", { class: "pills", style: "margin-top:8px" }, [time, rating, cost, cert].map((x) => h("span", { class: "badge", text: x })))), more),
    h("div", { class: "body" }, h("div", { class: "cdetail" }, h("dl", null,
      ...row(d.provider, c.provider), ...row(d.level, level), ...row(d.time, c.hours ? r.time(num(c.hours)) + (c.duration_text ? ` (${c.duration_text})` : "") : c.duration_text),
      ...row(d.cost, c.cost || r.unknown), ...row(d.rating, rating), ...row(d.cert, cert), ...row(d.prereq, c.prerequisites), ...row(d.topics, c.topics && c.topics.length ? c.topics.join(", ") : null))),
      c.units && c.units.length ? h("div", { class: "cdetail", style: "margin-top:10px" }, h("b", { text: d.sections }), h("ol", { style: "margin:6px 0 0;padding-left:20px" }, c.units.map((u) => h("li", { text: u })))) : null,
      c.url ? h("p", { style: "margin:14px 0 0" }, h("a", { class: "btn", href: c.url, target: "_blank", rel: "noopener noreferrer", text: r.open })) : null));
  el.addEventListener("toggle", () => { more.textContent = (el.open ? r.less : r.more) + (el.open ? " ▴" : " ▾"); });
  return el;
}
