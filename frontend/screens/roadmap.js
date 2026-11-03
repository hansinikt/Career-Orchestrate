// The roadmap: a winding road with one illustrated box per part of the app. Each box opens that part.
import { T } from "../strings.js";
import { h } from "../ui.js";
import { ill, roadSvg } from "../art.js";
import * as slots from "../slots.js";

const W = 1440, CENTRE = 410, AMP = 80;
const PX = [170, 445, 720, 995, 1270];
const roadY = (x) => CENTRE - AMP * Math.cos(Math.PI * (x - 170) / 275);

export default async function roadmap() {
  const [plan, prog, miss, qs] = await Promise.all([slots.plan(), slots.progress(), slots.missions(), slots.questions()]);
  const items = slots.roadmapItems(slots.courseRows(plan, prog), miss, qs, plan);
  const pts = []; for (let x = -20; x <= W + 20; x += 10) pts.push([x, Math.round(roadY(x) * 10) / 10]);
  const pct = (x) => `${(x / W * 100).toFixed(3)}%`;
  const road = h("div", { class: "road" }, roadSvg(pts));
  items.forEach((it, i) => {
    const x = PX[i], y = roadY(x), above = y < CENTRE;
    road.append(h("div", { class: "pin", style: `left:${pct(x)};top:${Math.round(y - 58)}px`, "aria-hidden": "true" }, h("b", { text: String(i + 1) })));
    road.append(h("a", { class: "card rbox", href: it.href, style: `left:${pct(x)};top:${Math.round(above ? y - 58 - 18 - 132 : y + 52)}px${i === 0 ? ";border:2px solid var(--brand)" : ""}`, "aria-label": `${i + 1}. ${it.title}: ${it.sub}` },
      ill(it.kind, 62), h("div", null, h("h3", { text: it.title }), h("div", { class: "sub", text: it.sub }), h("small", { class: "muted", text: it.text }), h("span", { class: "open", text: T.road.open(it.title) + " ›" }))));
  });
  return h("div", { class: "roadwrap" },
    h("div", { class: "roadhead row between" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: T.road.title(plan && plan.role_title) }), h("p", { text: T.road.lead })), h("a", { class: "btn", href: "#/dashboard", text: T.road.toDash })),
    road);
}
