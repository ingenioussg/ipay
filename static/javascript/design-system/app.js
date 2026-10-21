/* iPay front-end behaviour, shared by every page.
   Every failed request opens an animated error modal; successes show a toast.
   Server contract: errors reply 4xx/5xx with JSON {title, message, errors{field: text}};
   successes send HX-Trigger {"toast": {message, variant}} or HX-Location. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ICONS = {
    error: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
    success: '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    warning: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  };
  const svg = (n) => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n]}</svg>`;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------- theme: system -> light -> dark ---------- */
  const applyTheme = (t) => {
    const dark = t === "dark" || (t === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  };
  const theme = () => { try { return localStorage.getItem("theme") || "system"; } catch { return "system"; } };
  function cycleTheme() {
    const order = ["system", "light", "dark"];
    const next = order[(order.indexOf(theme()) + 1) % order.length];
    try { localStorage.setItem("theme", next); } catch {}
    applyTheme(next);
    toast(`Theme: ${next}`, "info", 1600);
  }
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => applyTheme(theme()));

  /* ---------- modals (animated open and close) ---------- */
  function closeModal(dlg, value = "cancel") {
    if (!dlg?.open || dlg.classList.contains("is-closing")) return;
    let finished = false;
    const done = () => { if (finished) return; finished = true; dlg.classList.remove("is-closing"); dlg.close(value); };
    if (reduced()) return done();
    dlg.classList.add("is-closing");
    dlg.addEventListener("animationend", done, { once: true });
    setTimeout(done, 450);
  }

  function modal({ title, message = "", errors = [], variant = "info", confirmText = "OK", cancelText = null }) {
    const dlg = $("#app-modal");
    if (!dlg) { alert(`${title}\n${message}`); return Promise.resolve(true); }
    const icon = { error: "error", success: "success", confirm: "warning" }[variant] || "info";
    dlg.dataset.variant = variant;
    dlg.innerHTML = `<form method="dialog">
      <div class="modal-body">
        <div class="modal-icon">${svg(icon)}</div>
        <div><div class="modal-title" id="app-modal-title">${esc(title)}</div>
        ${message ? `<p class="modal-message">${esc(message)}</p>` : ""}</div>
        ${errors.length ? `<ul class="modal-list">${errors.map((e) => `<li>${esc(e)}</li>`).join("")}</ul>` : ""}
      </div>
      <div class="modal-actions">
        ${cancelText ? `<button class="btn" value="cancel">${esc(cancelText)}</button>` : ""}
        <button class="btn ${variant === "confirm" ? "btn-primary" : "btn-primary"}" value="ok" autofocus>${esc(confirmText)}</button>
      </div></form>`;
    return new Promise((resolve) => {
      dlg.addEventListener("close", () => resolve(dlg.returnValue === "ok"), { once: true });
      if (dlg.open) dlg.close();
      dlg.showModal();
    });
  }

  // Buttons in a method="dialog" form close with the animation instead of instantly.
  document.addEventListener("submit", (e) => {
    const form = e.target;
    if (form.method === "dialog" && form.closest("dialog.modal")) { e.preventDefault(); closeModal(form.closest("dialog"), e.submitter?.value || "cancel"); }
  });
  document.addEventListener("cancel", (e) => { if (e.target.matches?.("dialog.modal")) { e.preventDefault(); closeModal(e.target); } }, true);
  document.addEventListener("click", (e) => { if (e.target.matches?.("dialog.modal")) closeModal(e.target); });

  /* ---------- toasts ---------- */
  function toast(message, variant = "success", life = 4000) {
    const stack = $("#toasts");
    if (!stack || !message) return;
    const el = document.createElement("div");
    el.className = "toast";
    el.dataset.variant = variant;
    el.setAttribute("role", variant === "error" ? "alert" : "status");
    el.style.setProperty("--life", `${life}ms`);
    el.innerHTML = `<span class="t-icon">${svg(variant === "error" ? "error" : variant === "info" ? "info" : "success")}</span>
      <div class="t-msg">${esc(message)}</div>
      <button class="btn btn-ghost btn-sm btn-icon" type="button" aria-label="Dismiss">${svg("x")}</button><span class="t-bar"></span>`;
    let gone = false;
    const leave = () => {
      if (gone) return; gone = true;
      el.classList.add("is-leaving");
      setTimeout(() => el.remove(), reduced() ? 0 : 260);
    };
    let timer = setTimeout(leave, life);
    const bar = el.querySelector(".t-bar");
    el.addEventListener("mouseenter", () => { clearTimeout(timer); bar.style.animationPlayState = "paused"; });
    el.addEventListener("mouseleave", () => { timer = setTimeout(leave, 1500); bar.style.animationPlayState = "running"; });
    el.querySelector("button").addEventListener("click", leave);
    stack.appendChild(el);
  }

  /* ---------- request progress bar ---------- */
  let pending = 0;
  const bar = () => $("#progress");
  function progressStart() { pending++; const p = bar(); if (!p) return; p.classList.remove("is-done"); requestAnimationFrame(() => p.classList.add("is-active")); }
  function progressDone() { pending = Math.max(0, pending - 1); if (pending) return; const p = bar(); if (!p) return; p.classList.remove("is-active"); p.classList.add("is-done"); }

  /* ---------- form field errors ---------- */
  function clearFieldErrors(form) {
    form?.querySelectorAll(".field.has-error").forEach((f) => { f.classList.remove("has-error"); f.querySelector("[aria-invalid]")?.removeAttribute("aria-invalid"); });
  }
  function showFieldErrors(form, errors) {
    if (!form) return;
    for (const [name, text] of Object.entries(errors)) {
      const input = form.querySelector(`[name="${CSS.escape(name)}"]`);
      const field = input?.closest(".field");
      input?.setAttribute("aria-invalid", "true");
      if (!field) continue;
      field.classList.add("has-error");
      let t = field.querySelector(".error-text");
      if (!t) { t = document.createElement("div"); t.className = "error-text"; field.appendChild(t); }
      t.textContent = text;
    }
  }

  /* ---------- htmx wiring ---------- */
  if (window.htmx) {
    htmx.config.globalViewTransitions = true;
    htmx.config.scrollBehavior = "smooth";
  }
  const csrf = () => $("#csrf")?.dataset.token || "";
  document.addEventListener("htmx:configRequest", (e) => { e.detail.headers["X-CSRF-Token"] = csrf(); });
  document.addEventListener("htmx:beforeRequest", (e) => { progressStart(); clearFieldErrors(e.detail.elt.closest?.("form")); });
  document.addEventListener("htmx:afterRequest", () => progressDone());
  document.addEventListener("htmx:responseError", (e) => {
    const xhr = e.detail.xhr;
    let p;
    try { p = JSON.parse(xhr.responseText); } catch { p = { title: `Error ${xhr.status}`, message: "The server sent an unexpected reply. Nothing was saved." }; }
    const form = e.detail.elt.closest?.("form");
    showFieldErrors(form, p.errors || {});
    modal({ title: p.title || "Something went wrong", message: p.message, errors: Object.values(p.errors || {}), variant: "error", confirmText: "Got it" })
      .then(() => form?.querySelector('[aria-invalid="true"]')?.focus());
    if (xhr.status === 401) setTimeout(() => location.assign("/login"), 1400);
  });
  document.addEventListener("htmx:sendError", () => modal({ title: "Can't reach the server", message: "Check your connection and try again. Nothing was saved.", variant: "error", confirmText: "OK" }));
  document.addEventListener("htmx:confirm", (e) => {
    if (!e.detail.question) return;
    e.preventDefault();
    modal({ title: e.detail.question, variant: "confirm", confirmText: "Continue", cancelText: "Cancel" }).then((ok) => ok && e.detail.issueRequest(true));
  });
  document.addEventListener("toast", (e) => toast(e.detail.message, e.detail.variant));

  /* ---------- page behaviours ---------- */
  function syncReveals(root = document) {
    root.querySelectorAll("[data-reveal]").forEach((sec) => {
      const on = !!document.getElementById(sec.dataset.reveal)?.checked;
      sec.classList.toggle("is-open", on);
      sec.inert = !on;
    });
  }
  function countUp(root = document) {
    root.querySelectorAll("[data-count]").forEach((el) => {
      const end = Number(el.dataset.count);
      delete el.dataset.count;
      if (!Number.isFinite(end)) return;
      const fmt = new Intl.NumberFormat();
      if (reduced()) { el.textContent = fmt.format(end); return; }
      const t0 = performance.now(), dur = 700;
      const step = (t) => { const k = Math.min(1, (t - t0) / dur); el.textContent = fmt.format(Math.round(end * (1 - (1 - k) ** 3))); if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    });
  }
  function flushFlashes(root = document) {
    root.querySelectorAll("[data-flash]").forEach((el) => { toast(el.dataset.flash, el.dataset.variant || "success"); el.remove(); });
  }
  function init(root = document) { syncReveals(root); countUp(root); flushFlashes(root); $(".app")?.classList.remove("nav-open"); }

  document.addEventListener("change", (e) => { if (e.target.matches?.('input[type="checkbox"]')) syncReveals(); });
  document.addEventListener("click", (e) => {
    const t = e.target.closest?.("[data-action]");
    if (!t) return;
    const a = t.dataset.action;
    if (a === "nav-toggle") $(".app")?.classList.toggle("nav-open");
    else if (a === "nav-close") $(".app")?.classList.remove("nav-open");
    else if (a === "theme") cycleTheme();
    else if (a === "open-modal") document.getElementById(t.dataset.target)?.showModal();
    else if (a === "close-modal") closeModal(t.closest("dialog"));
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") $(".app")?.classList.remove("nav-open"); });
  document.addEventListener("htmx:afterSettle", () => init());
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init()); else init();

  window.iPay = { modal, toast, closeModal };
})();
