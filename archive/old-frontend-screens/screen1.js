// Screen 1: welcome, consent, encouragement style.
import { api } from "../api.js";
import { T } from "../strings.js";
import { S } from "../state.js";
import { h, go, choice, seg, toggle } from "../ui.js";

export default async function screen1() {
  if (!S.meta) { try { S.meta = await api.meta(); } catch (e) { /* shown by other screens */ } }
  const t = T.s1;
  const demo = h("aside", { class: "demo-card", "aria-label": t.sampleTitle },
    h("h2", { text: t.sampleTitle }),
    h("p", { class: "quote" }, h("span", { class: "mark", text: t.sampleText[0] }), t.sampleText[1], h("span", { class: "mark", text: t.sampleText[2] }), t.sampleText[3]),
    h("div", { class: "arrows" }, t.sampleChips.map(([n, l]) => h("span", { class: "chip" }, n, h("i", { text: l })))),
    h("p", { class: "cap", text: t.sampleCaption }));

  const hint = h("p", { class: "small muted", role: "status" });
  const go2 = h("button", { class: "btn", type: "button", onclick: () => go("#/2"), text: t.start });
  const styleBoxes = [];
  const refresh = () => {
    styleBoxes.forEach(([key, input]) => { input.checked = S.styles.includes(key); input.disabled = !input.checked && S.styles.length >= 2; });
    const ok = S.consent && S.styles.length >= 1;
    go2.disabled = !ok;
    hint.textContent = !S.consent ? t.needConsent : S.styles.length < 1 ? t.needStyle : "";
  };
  const toggleStyle = (key, on) => { S.styles = on ? [...S.styles, key].slice(0, 2) : S.styles.filter((k) => k !== key); refresh(); };

  const styleGrid = h("div", { class: "choices", role: "group", "aria-labelledby": "style-h" },
    Object.keys(T.styles).map((k) => { const c = choice("checkbox", "style", T.styles[k], T.styleHelp[k], S.styles.includes(k), (e) => toggleStyle(k, e.target.checked)); styleBoxes.push([k, c.querySelector("input")]); return c; }));

  const consent = h("label", { class: "check" }, h("input", { type: "checkbox", checked: S.consent, onchange: (e) => { S.consent = e.target.checked; refresh(); } }), h("span", { text: T.consentLabel }));

  const form = h("section", { class: "card", "aria-labelledby": "style-h" },
    h("h2", { id: "style-h", text: t.styleTitle }), h("p", { class: "hint", text: t.styleHelp }), styleGrid,
    h("div", { class: "field" }, h("p", { class: "lbl", id: "ci-h", text: t.checkInTitle }), seg("checkin", Object.entries(T.checkIn), S.checkIn, (v) => { S.checkIn = v; })),
    h("div", { class: "field" }, toggle(t.pauseLabel, t.pauseHelp, S.paused, (v) => { S.paused = v; })),
    h("div", { class: "field" }, consent),
    h("div", { class: "row" }, go2, hint));
  refresh();

  return h("div", { class: "page" },
    h("section", { class: "hero" },
      h("div", { class: "head" }, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead }), h("p", { class: "small muted", text: t.privacy })),
      demo),
    form);
}
