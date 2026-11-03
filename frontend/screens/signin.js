// Demo sign-in. No real account is checked yet (the backend has no accounts); the name and email are kept for this browser tab only.
import { T } from "../strings.js";
import { S } from "../state.js";
import { U, signIn } from "../store.js";
import { h, go, field } from "../ui.js";
import { logo } from "../art.js";

export default function signinScreen() {
  const t = T.auth;
  if (U.user) { go(S.profileId ? "#/dashboard" : "#/welcome"); return null; }
  let mode = "create";
  const root = h("div", { class: "auth" });
  const draw = () => {
    const name = h("input", { type: "text", id: "a-name", autocomplete: "name", maxlength: "60" });
    const email = h("input", { type: "email", id: "a-email", autocomplete: "email" });
    const pass = h("input", { type: "password", id: "a-pass", autocomplete: mode === "create" ? "new-password" : "current-password" });
    const err = h("p", { class: "err", role: "alert" });
    const submit = (e) => {
      e.preventDefault();
      const n = name.value.trim(), m = email.value.trim();
      if (mode === "create" && !n) { err.textContent = t.needName; name.focus(); return; }
      if (!/^\S+@\S+\.\S+$/.test(m)) { err.textContent = t.needEmail; email.focus(); return; }
      if (pass.value.length < 6) { err.textContent = t.needPass; pass.focus(); return; }
      signIn({ name: n || m.split("@")[0], email: m });
      go(S.profileId ? "#/dashboard" : "#/welcome");
    };
    root.replaceChildren(
      h("div", { class: "left" }, h("form", { class: "card", style: "width:100%;max-width:440px;padding:34px", onsubmit: submit, novalidate: true },
        h("h1", { id: "page-title", tabindex: "-1", style: "font-size:2rem", text: t.title }), h("p", { class: "muted", text: t.lead }),
        h("div", { class: "seg", role: "tablist", style: "width:100%" }, [["create", t.tabCreate], ["signin", t.tabSignin]].map(([id, label]) => h("label", { style: "flex:1;text-align:center" },
          h("input", { type: "radio", name: "mode", checked: mode === id, onchange: () => { mode = id; draw(); } }), h("span", { text: label })))),
        mode === "create" ? field(t.name, name) : null, field(t.email, email), field(t.password, pass), err,
        h("button", { class: "btn lg", type: "submit", style: "width:100%", text: mode === "create" ? t.create : t.signin }),
        )),
      h("div", { class: "right" }, h("div", { class: "auth-brand" }, logo(84, "#ffffff"), h("div", { class: "wordmark", text: "Career Orchestrator" }))));
  };
  draw();
  return root;
}
