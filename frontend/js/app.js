// app.js — registers routes, then boots the app.

route("/login", renderLogin);
route("/register", renderRegister);
route("/dashboard", renderDashboard);
route("/profiles", renderProfiles);
route("/profile/edit", () => renderProfileForm());
route("/profile/:id", renderProfileDetail);
route("/portfolio", () => renderPortfolio({}));
route("/portfolio/:userId", renderPortfolio);
route("/feedback", renderFeedback);

async function boot() {
  const user = await renderTopbar();
  const path = currentPath();
  const publicPaths = ["/login", "/register", "/profiles", "/feedback"];
  const isProfileDetail = /^\/profile\/\d+$/.test(path);
  const isPortfolioView = /^\/portfolio\/\d+$/.test(path);

  if (!user && !publicPaths.includes(path) && !isProfileDetail && !isPortfolioView) {
    navigate("/login");
    return;
  }
  resolve();
}

boot();
