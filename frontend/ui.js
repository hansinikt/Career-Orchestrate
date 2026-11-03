// Small DOM helpers. Everything is built with createElement/textContent, so worker and API text is never parsed as HTML (rule F13).
import { ApiError } from "./api.js";
import { T } from "./strings.js";
import { S, setProfileId } from "./state.js";
import { ill } from "./art.js";

const PROPS = new Set(["checked", "disabled", "selected", "required", "open", "multiple"]);
export function h(tag, props, ...kids) {
  const el = document.createElement(tag);
  let value;
  for (const [k, v] of Object.entries(props || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k === "value") value = v;
    else if (PROPS.has(k)) el[k] = !!v;
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2).toLowerCase(), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  const add = (c) => {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) c.forEach(add);
    else el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  };
  kids.forEach(add);
  if (value !== undefined) el.value = value;
  return el;
}
export const go = (hash) => { location.hash = hash; };
export const spinner = (msg) => h("div", { class: "spinner", role: "status", "aria-label": msg || T.loading });

export function errorPanel(err, retry) {
  const msg = err instanceof ApiError ? err.message : "Something went wrong. Nothing was lost.";
  const fields = err && err.details && Array.isArray(err.details.errors) ? err.details.errors : [];
  return h("div", { class: "errorbox", role: "alert" },
    h("h2", { text: T.errorTitle }),
    h("p", { text: msg }),
    fields.length ? h("ul", null, fields.slice(0, 5).map((f) => h("li", { text: typeof f === "string" ? f : [(f.loc || []).join("."), f.msg].filter(Boolean).join(": ") }))) : null,
    retry ? h("button", { class: "btn", type: "button", onclick: retry, text: T.errorTryAgain }) : null);
}
// Returns a node to show, or null when we have sent the person to the right screen (section 8 of the brief).
export function handleError(err, retry) {
  const code = err instanceof ApiError ? err.code : "INTERNAL";
  const redirect = (hash, msg) => { S.flash = msg; go(hash); return null; };
  if (code === "CONSENT_REQUIRED") return redirect("#/onboard/9", err.message);
  if (code === "SKILLS_NOT_CONFIRMED") return redirect("#/3", err.message);
  if (code === "NO_ACTIVE_PLAN") return redirect("#/jobs", err.message);
  if (code === "NOT_FOUND") { setProfileId(null); return redirect("#/onboard", err.message); }
  return errorPanel(err, retry);
}

export function pageHead(title, lead, tag) {
  return h("div", { class: "head col" }, tag ? h("span", { class: "tag", text: tag }) : null, h("h1", { id: "page-title", tabindex: "-1", text: title }), lead ? h("p", { class: "lead", text: lead }) : null);
}
const GLYPH = { strong_fit: "●", bridgeable: "◐", stretch: "○" };
export const bandChip = (band) => h("span", { class: "band " + band }, h("span", { class: "g", "aria-hidden": "true" }), T.bands[band] || band);
export const levelWord = (n) => T.levels[n] != null ? T.levels[n] : String(n);
export const num = (x) => String(Math.round(Number(x) * 10) / 10); // display only: 24.0 shows as 24
export const field = (label, control, opts = {}) => h("div", { class: "field" }, h("label", { for: control.id }, label, opts.req ? h("span", { class: "req", "aria-hidden": "true", text: " *" }) : null), opts.hint ? h("p", { class: "hint", text: opts.hint }) : null, control, opts.after);
// A bold question with a short line under it saying what to enter. req adds the red asterisk.
export const ask = (label, hint, control, opts = {}) => h("div", { class: "field q" }, h(opts.forId !== "none" && (opts.forId || control.id) ? "label" : "p", { class: "qt", for: opts.forId !== "none" ? (opts.forId || control.id || null) : null }, label, opts.req ? h("span", { class: "req", "aria-hidden": "true", text: " *" }) : null), hint ? h("p", { class: "hint", text: hint }) : null, control);
export function choice(type, name, title, help, checked, onchange, disabled) {
  const input = h("input", { type, name, checked, disabled, onchange });
  return h("label", { class: "choice" }, input, h("span", { class: "box" }, h("b", { text: title }), help ? h("small", { text: help }) : null));
}
export function seg(name, options, current, onchange) {
  return h("div", { class: "seg", role: "radiogroup" }, options.map(([val, label]) =>
    h("label", null, h("input", { type: "radio", name, value: String(val), checked: String(val) === String(current), onchange: () => onchange(val) }), h("span", { text: label }))));
}
export function toggle(label, help, checked, onchange) {
  const input = h("input", { type: "checkbox", checked, onchange: (e) => onchange(e.target.checked) });
  return h("label", { class: "toggle" }, input, h("span", { class: "sw" }), h("span", null, h("b", { text: label }), help ? h("small", { class: "faint", text: " " + help }) : null));
}

// ---- v3 helpers ----
export function bar(percent, label) {   // percent: number 0..100, or null/undefined for an empty bar
  const p = typeof percent === "number" ? Math.max(0, Math.min(100, Math.round(percent))) : 0;
  return h("div", { class: "bar", role: "progressbar", "aria-valuenow": String(p), "aria-valuemin": "0", "aria-valuemax": "100", "aria-label": label || "Progress" }, h("i", { style: `width:${p}%` }));
}
export function emptyState(kind, title, text, action, tight) {
  return h("div", { class: "empty" + (tight ? " tight" : "") }, ill(kind, 64), h("h3", { text: title }), text ? h("p", { text }) : null, action || null);
}
// The one card pattern: illustration, heading, orange subheading, one line of text, optional action.
export function itemCard({ kind, size = 56, title, sub, text, href, action, tag, children }) {
  const body = h("div", { class: "grow" }, h("h4", { text: title }), sub ? h("div", { class: "sub", text: sub }) : null, text ? h("p", { text }) : null, tag || null, children || null);
  const inner = [ill(kind, size), body, action || null];
  return href ? h("a", { class: "card item", href }, inner) : h("div", { class: "card item" }, inner);
}
export const crumb = (text) => h("div", { class: "crumb", text });
export function pills(name, options, selected, onchange, multi = true) {
  return h("div", { class: "pills", role: "group" }, options.map((o) => h("label", { class: "pill" },
    h("input", { type: multi ? "checkbox" : "radio", name, value: o, checked: selected.includes(o), onchange: (e) => onchange(o, e.target.checked) }), h("span", { text: o }))));
}

// A small trash-bin button that replaces a text "Remove" link. The label stays for screen readers and the hover tip.
export function trash(label, onclick) {
  const b = h("button", { class: "trash", type: "button", "aria-label": label, title: label, onclick });
  b.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>';
  return b;
}
