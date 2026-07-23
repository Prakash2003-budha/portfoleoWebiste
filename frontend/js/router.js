// router.js
// Tiny hash router: no build step, no framework. Routes are registered as
// exact strings or with a ":param" segment, e.g. "/profile/:id".

const routes = [];

function route(pattern, handler) {
  const paramNames = [];
  const regex = new RegExp(
    "^" +
      pattern
        .split("/")
        .map((segment) => {
          if (segment.startsWith(":")) {
            paramNames.push(segment.slice(1));
            return "([^/]+)";
          }
          return segment.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        })
        .join("/") +
      "$"
  );
  routes.push({ regex, paramNames, handler });
}

function currentPath() {
  const hash = window.location.hash.slice(1);
  return hash || "/dashboard";
}

async function resolve() {
  if (typeof studioCanvas !== "undefined" && studioCanvas && typeof teardownStudio === "function") {
    teardownStudio();
  }
  const path = currentPath();
  if (typeof highlightActiveNav === "function") highlightActiveNav();
  for (const r of routes) {
    const match = path.match(r.regex);
    if (match) {
      const params = {};
      r.paramNames.forEach((name, i) => (params[name] = match[i + 1]));
      const view = document.getElementById("view");
      view.innerHTML = '<p class="loading-state">Loading…</p>';
      try {
        await r.handler(params);
      } catch (err) {
        view.innerHTML = `<p class="alert">${err.message}</p>`;
      }
      return;
    }
  }
  document.getElementById("view").innerHTML = "<p class='alert'>Page not found.</p>";
}

function navigate(path) {
  window.location.hash = path;
}

window.addEventListener("hashchange", resolve);
