/* ============================================================
   Locadora — interações do front-end (sem framework)
   Tema, sidebar mobile, menu do usuário, popover de status,
   toasts e helpers de gráfico (Chart.js).
   ============================================================ */
(function () {
  "use strict";

  // ---------- Tema ----------
  var THEME_KEY = "locadora-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    document.dispatchEvent(new CustomEvent("locadora:themechange", { detail: theme }));
  }

  function toggleTheme() {
    var atual = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    applyTheme(atual === "dark" ? "light" : "dark");
  }

  // ---------- Sidebar mobile ----------
  function setupNav() {
    var shell = document.getElementById("app-shell");
    if (!shell) return;
    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-nav-toggle]")) {
        shell.classList.toggle("nav-open");
      } else if (e.target.closest(".nav-overlay") || e.target.closest(".nav__item")) {
        shell.classList.remove("nav-open");
      }
    });
  }

  // ---------- Menu do usuário ----------
  function setupUserMenu() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-user-toggle]");
      var menus = document.querySelectorAll(".user.is-open");
      menus.forEach(function (m) {
        if (!btn || m !== btn.closest(".user")) m.classList.remove("is-open");
      });
      if (btn) btn.closest(".user").classList.toggle("is-open");
    });
  }

  // ---------- Toggle de tema (botões) ----------
  function setupThemeToggle() {
    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-theme-toggle]")) toggleTheme();
    });
  }

  // ---------- Popover de status (mostra campos de manutenção) ----------
  function setupStatusFields() {
    document.addEventListener("change", function (e) {
      var sel = e.target.closest("select[data-status-select]");
      if (!sel) return;
      var panel = sel.closest(".popover__panel") || sel.closest("form");
      if (!panel) return;
      var extra = panel.querySelector("[data-manut-fields]");
      if (extra) extra.style.display = sel.value === "manutencao" ? "" : "none";
    });
  }

  // ---------- Toasts ----------
  function initToasts(scope) {
    (scope || document).querySelectorAll(".toast:not([data-bound])").forEach(function (t) {
      t.setAttribute("data-bound", "1");
      var hide = function () {
        t.classList.add("is-hiding");
        setTimeout(function () { t.remove(); }, 320);
      };
      var close = t.querySelector(".toast__close");
      if (close) close.addEventListener("click", hide);
      setTimeout(hide, 5000);
    });
  }

  // ---------- Gráficos (Chart.js, com tema) ----------
  var registry = [];

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  // Registra um construtor de gráfico que será (re)desenhado a cada troca de tema.
  window.Locadora = {
    cssVar: cssVar,
    chart: function (build) {
      var instance = null;
      var render = function () {
        if (typeof Chart === "undefined") return;
        if (instance) instance.destroy();
        instance = build(cssVar);
      };
      registry.push(render);
      // Chart.js é carregado com defer; aguarda ficar disponível.
      (function wait(tries) {
        if (typeof Chart !== "undefined") { render(); return; }
        if (tries > 0) setTimeout(function () { wait(tries - 1); }, 100);
      })(50);
    },
  };

  document.addEventListener("locadora:themechange", function () {
    registry.forEach(function (render) { render(); });
  });

  // ---------- Boot ----------
  document.addEventListener("DOMContentLoaded", function () {
    setupNav();
    setupUserMenu();
    setupThemeToggle();
    setupStatusFields();
    initToasts(document);
  });

  // Toasts trocados via HTMX (swap OOB do #toast-container).
  document.body.addEventListener("htmx:afterSettle", function (e) {
    initToasts(e.target);
    initToasts(document.getElementById("toast-container"));
  });
})();
