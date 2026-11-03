// Small illustrations. Static markup written here (never built from user or API text), parsed with DOMParser.
const B = "#1f6f5f", O = "#c47a12";
const KINDS = {
  course: ["#f6e9cf", O, (f) => `<path d="M10 20c8-4 16-4 22 2v26c-6-6-14-6-22-2z" fill="#fff" stroke="${f}" stroke-width="2.5"/><path d="M54 20c-8-4-16-4-22 2v26c6-6 14-6 22-2z" fill="#fff" stroke="${f}" stroke-width="2.5"/><circle cx="32" cy="12" r="5" fill="${f}"/>`],
  mission: ["#e3f3e8", "#2f8a4f", (f) => `<rect x="16" y="12" width="32" height="42" rx="4" fill="#fff" stroke="${f}" stroke-width="2.5"/><rect x="24" y="8" width="16" height="8" rx="3" fill="${f}"/><path d="M23 28l3 3 6-6M23 40l3 3 6-6" stroke="${f}" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M36 29h7M36 41h7" stroke="${f}" stroke-width="2.5" stroke-linecap="round"/>`],
  check: ["#e2e9ef", "#44607a", (f) => `<circle cx="32" cy="32" r="20" fill="#fff" stroke="${f}" stroke-width="2.5"/><path d="M26 27c0-8 12-8 12 0 0 5-6 5-6 10" stroke="${f}" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="32" cy="44" r="2.4" fill="${f}"/>`],
  cert: ["#fff2cc", "#c78a00", (f) => `<path d="M24 38l-5 16 13-6 13 6-5-16" fill="${f}" opacity=".85"/><circle cx="32" cy="27" r="16" fill="#fff" stroke="${f}" stroke-width="2.5"/><path d="M25 27l5 5 9-10" stroke="${f}" stroke-width="3" fill="none" stroke-linecap="round"/>`],
  skills: ["#dcebe5", B, (f) => `<rect x="14" y="18" width="36" height="30" rx="4" fill="#fff" stroke="${f}" stroke-width="2.5"/><path d="M21 30h22M21 38h14" stroke="${f}" stroke-width="3" stroke-linecap="round"/><circle cx="48" cy="46" r="9" fill="${f}"/><path d="M44 46l3 3 6-6" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round"/>`],
  goal: ["#fff2cc", "#c78a00", (f) => `<circle cx="32" cy="34" r="20" fill="#fff" stroke="${f}" stroke-width="2.5"/><circle cx="32" cy="34" r="11" fill="none" stroke="${f}" stroke-width="2.5"/><circle cx="32" cy="34" r="3.5" fill="${f}"/>`],
  cv: ["#dcebe5", B, (f) => `<rect x="14" y="8" width="36" height="46" rx="4" fill="#fff" stroke="${f}" stroke-width="2.5"/><circle cx="32" cy="22" r="5" fill="${f}"/><path d="M22 38c2-6 18-6 20 0M22 46h20" stroke="${f}" stroke-width="2.5" fill="none" stroke-linecap="round"/>`],
};
function parse(str) { return document.importNode(new DOMParser().parseFromString(str, "image/svg+xml").documentElement, true); }
export function ill(kind, size = 60) {
  const k = KINDS[kind] || KINDS.course;
  const svg = parse(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 64 64" class="ill" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="31" fill="${k[0]}"/>${k[2](k[1])}</svg>`);
  return svg;
}
export function logo(size = 30, ink = B) {
  return parse(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M5 25C11 25 10 12 16 12S21 22 27 7" fill="none" stroke="${ink}" stroke-width="2.6" stroke-linecap="round"/><circle cx="5" cy="25" r="3" fill="#fcfdfb" stroke="${ink}" stroke-width="2.2"/><circle cx="27" cy="7" r="3.4" fill="#f0a02b"/></svg>`);
}
// The hero trail: one path, four stops. Positions are in a 640x420 box; labels are HTML so they stay sharp and readable.
export const TRAIL_STOPS = [[50, 350], [210, 230], [380, 290], [560, 110]];
export function trail(labels) {
  const svg = parse(`<svg xmlns="http://www.w3.org/2000/svg" class="trail-svg" viewBox="0 0 640 420" aria-hidden="true" focusable="false"><path class="t-ghost" d="M50 350C120 350 130 230 210 230S300 290 380 290S470 110 560 110" fill="none"/><path class="t-draw" pathLength="1" d="M50 350C120 350 130 230 210 230S300 290 380 290S470 110 560 110" fill="none"/>${TRAIL_STOPS.map(([x, y], i) => `<circle class="t-stop s${i}" cx="${x}" cy="${y}" r="${i === 0 ? 11 : 9}"/>`).join("")}</svg>`);
  const wrap = document.createElement("div"); wrap.className = "trail"; wrap.append(svg);
  TRAIL_STOPS.forEach(([x, y], i) => { const l = document.createElement("span"); l.className = `t-label s${i}`; l.textContent = labels[i]; l.style.left = `${x / 6.4}%`; l.style.top = `${y / 4.2}%`; wrap.append(l); });
  return wrap;
}
// The winding road. Same wave the pins sit on (see roadmap.js).
export function roadSvg(pts) {
  const d = pts.map((p) => p.join(",")).join(" ");
  return parse(`<svg xmlns="http://www.w3.org/2000/svg" class="path" viewBox="0 0 1440 690" preserveAspectRatio="none" aria-hidden="true" focusable="false"><polyline points="${d}" fill="none" stroke="#cfe0d7" stroke-width="64" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/><polyline points="${d}" fill="none" stroke="#1f6f5f" stroke-width="3" stroke-dasharray="14 14" vector-effect="non-scaling-stroke"/></svg>`);
}
export function gaugeSvg(percent) {
  // percent: number 0..100 or null. null draws the empty track only.
  const track = "M30 130 A100 100 0 0 1 230 130";
  let fill = "";
  if (typeof percent === "number" && percent > 0) {
    const a = Math.PI * (1 - Math.min(100, percent) / 100);
    const x = 130 + 100 * Math.cos(a), y = 130 - 100 * Math.sin(a);
    fill = `<path d="M30 130 A100 100 0 0 1 ${x.toFixed(1)} ${y.toFixed(1)}" fill="none" stroke="${B}" stroke-width="22" stroke-linecap="round"/>`;
  }
  return parse(`<svg xmlns="http://www.w3.org/2000/svg" class="gauge" width="250" height="140" viewBox="0 0 260 150" aria-hidden="true" focusable="false"><path d="${track}" fill="none" stroke="#e6e9ef" stroke-width="22" stroke-linecap="round"/>${fill}</svg>`);
}
