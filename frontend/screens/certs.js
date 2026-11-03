// Certifications: what the person has earned. Kept on this device until the backend has an upload endpoint.
import { T } from "../strings.js";
import { U } from "../store.js";
import { h, crumb, field, emptyState, trash } from "../ui.js";
import { ill } from "../art.js";
import * as slots from "../slots.js";

export default async function certs() {
  const t = T.cert;
  const root = h("div", { class: "page" });
  let adding = false, err = null;
  const draw = () => {
    const list = U.x.certs;
    const grid = list.length ? h("div", { class: "grid g3" }, list.map((c) => h("div", { class: "card", style: "text-align:center" }, h("div", { style: "display:flex;justify-content:center" }, ill("cert", 64)), h("h4", { text: c.name }),
      c.fileName ? h("small", { class: "faint", text: c.fileName }) : null, h("div", { class: "sub", text: t.added(c.added) }),
      h("div", { class: "row", style: "justify-content:center" }, c.link ? h("a", { class: "btn ghost small", href: c.link, target: "_blank", rel: "noopener noreferrer", text: t.open }) : null,
        trash(t.remove, () => { slots.removeCertificate(c.id); draw(); }))))) : emptyState("cert", t.emptyTitle, t.emptyText);
    let form = null;
    if (adding) {
      const name = h("input", { type: "text", id: "ct-name", maxlength: "100" }), file = h("input", { type: "file", id: "ct-file", accept: ".pdf,.png,.jpg,.jpeg" }), link = h("input", { type: "text", id: "ct-link", placeholder: "https://" });
      form = h("form", { class: "card", onsubmit: (e) => {
        e.preventDefault();
        if (!name.value.trim()) { err = t.needName; draw(); return; }
        const l = link.value.trim(); if (l && !/^https:\/\//i.test(l)) { err = t.badLink; draw(); return; }
        slots.addCertificate({ name: name.value.trim(), link: l || null, fileName: file.files[0] ? file.files[0].name : null }); adding = false; err = null; draw();
      } }, err ? h("p", { class: "err", role: "alert", text: err }) : null, field(t.name, name), field(t.file, file), field(t.link, link), h("div", { class: "row" }, h("button", { class: "btn", type: "submit", text: t.save }), h("button", { class: "btn ghost", type: "button", text: T.back, onclick: () => { adding = false; err = null; draw(); } })));
    }
    root.replaceChildren(crumb(t.crumb), h("div", { class: "head" }, h("div", null, h("h1", { id: "page-title", tabindex: "-1", text: t.title }), h("p", { class: "lead", text: t.lead })), adding ? null : h("button", { class: "btn org", type: "button", text: t.add, onclick: () => { adding = true; draw(); } })), ...(form ? [form] : []), grid);
  };
  draw();
  return root;
}
