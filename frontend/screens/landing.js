// Landing page: who we are, what it does, a demo button. Marketing copy lives in strings.js.
import { T } from "../strings.js";
import { h, bar } from "../ui.js";
import { ill } from "../art.js";

export default function landing() {
  const t = T.land;
  const feat = ([kind, title, text, example]) => {
    const tryBox = h("div", { class: "try", hidden: true, role: "status", text: example });
    const btn = h("button", { class: "linkbtn", type: "button", "aria-expanded": "false", text: t.tryIt, onclick: () => { tryBox.hidden = !tryBox.hidden; btn.setAttribute("aria-expanded", String(!tryBox.hidden)); } });
    return h("article", { class: "card feat" }, ill(kind, 60), h("h3", { text: title }), h("p", { text }), h("div", { style: "margin-top:10px" }, btn), tryBox);
  };
  const hero = h("section", { class: "hero" }, h("div", { class: "inner" },
    h("div", null, h("h1", { id: "page-title", tabindex: "-1" }, t.title[0], h("br"), t.title[1]), h("p", { class: "lead", text: t.lead }),
      h("div", { class: "row" }, h("a", { class: "btn lg", href: "#/signin", text: t.start }), h("a", { class: "btn ghost lg", href: "#/signin", text: t.demo }))),
    h("div", { class: "demo-card", "aria-hidden": "true" },
      h("div", { class: "row between" }, h("b", { text: t.cardMission }), h("span", { class: "st amber", text: t.cardDue })),
      h("div", { class: "mission-box" }, h("small", { text: t.cardTag }), h("div", { class: "t", text: t.cardTitle }), h("span", { class: "btn org small", text: t.cardBtn })),
      h("small", { class: "faint", text: t.cardBar }), h("div", { style: "margin-top:8px" }, bar(0)))));

  const features = h("section", { class: "band-section", id: "features", style: "background:#fff" }, h("div", { class: "inner" },
    h("h2", { style: "text-align:center", text: t.featTitle }), h("p", { class: "lead", style: "text-align:center;margin:12px auto 36px", text: t.featLead }),
    h("div", { class: "grid g3" }, t.feats.map(feat))));

  const how = h("section", { class: "band-section", id: "how" }, h("div", { class: "inner" }, h("h2", { text: t.howTitle }),
    h("div", { class: "steps4", style: "margin-top:30px" }, t.how.map(([title, text], i) => h("div", null, h("div", { class: "n", text: String(i + 1) }), h("h4", { text: title }), h("p", { text }))))));

  const shots = h("section", { class: "band-section", style: "background:#fff" }, h("div", { class: "inner" }, h("h2", { text: t.shotsTitle, style: "text-align:center;margin-bottom:30px" }),
    h("div", { class: "shots" }, t.shots.map(([k, cap]) => h("figure", { class: "shot", style: "margin:0" }, h("img", { src: `img/shot-${k}.png`, alt: cap, loading: "lazy", style: "width:100%;display:block" }), h("figcaption", { class: "cap", text: cap }))))));

  const fair = h("section", { class: "band-section", id: "fairness" }, h("div", { class: "inner", style: "display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:center" },
    h("div", null, h("h2", { text: t.fairTitle }), h("p", { class: "lead", style: "margin-top:14px", text: t.fairLead })),
    h("div", { class: "card" }, h("b", { text: t.fairCard }), h("div", { class: "small muted", text: t.fairVariants }),
      h("div", { class: "row" }, ["A29", "A42", "A50", "A58", "P5", "P25"].map((v) => h("span", { class: "st blue", text: v }))), h("small", { text: t.fairLine }))));

  const cta = h("section", { class: "cta" }, h("h2", { text: t.ctaTitle }), h("p", { text: t.ctaLead }), h("a", { class: "btn white lg", href: "#/signin", text: t.demo }));
  return h("div", null, hero, features, how, shots, fair, cta);
}
