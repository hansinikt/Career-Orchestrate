// Three-number summary for a job: courses, hours, and weeks at the person's own weekly study time.
import { h } from "../ui.js";
import { T } from "../strings.js";
export const weeksFor = (hours, weekly) => (weekly >= 1 && hours > 0 ? Math.max(1, Math.ceil(hours / weekly)) : null);
export function timeStrip(count, hours, weekly) {
  const t = T.strip, hrs = Math.round(hours), wk = weeksFor(hrs, weekly);
  if (!count) return null;
  const cell = (big, label) => h("div", { class: "ts-cell" }, h("b", { text: String(big) }), h("span", { text: label }));
  return h("div", { class: "timestrip", role: "group", "aria-label": t.label },
    h("div", { class: "ts-row" }, cell(count, count === 1 ? t.course : t.courses), cell(hrs, t.hours), wk ? cell(wk, wk === 1 ? t.week : t.weeks) : null),
    wk ? h("p", { class: "ts-note", text: t.note(wk, weekly) }) : null);
}
