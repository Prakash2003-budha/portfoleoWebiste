// app.js — registers routes, then boots the app.

route("/login", renderLogin);
route("/register", renderRegister);
route("/activate", renderActivate);
route("/activate/:token", renderActivate);
route("/dashboard", renderDashboard);
route("/profiles", renderProfiles);
route("/profile/edit", () => renderProfileForm());
route("/profile/:id", renderProfileDetail);
route("/portfolio", () => renderPortfolio({}));
route("/portfolio/:userId", renderPortfolio);
route("/studio", () => renderStudio({}));
route("/studio/:id", renderStudio);
route("/feedback", renderFeedback);

async function boot() {
  const user = await renderTopbar();
  const path = currentPath();
  const publicPaths = ["/login", "/register", "/activate", "/profiles", "/feedback"];
  const isProfileDetail = /^\/profile\/\d+$/.test(path);
  const isPortfolioView = /^\/portfolio\/\d+$/.test(path);
  const isActivation = /^\/activate(\/[A-Za-z0-9_-]+)?$/.test(path);

  if (!user && !publicPaths.includes(path) && !isProfileDetail && !isPortfolioView && !isActivation) {
    navigate("/login");
    return;
  }
  resolve();
}

boot();
