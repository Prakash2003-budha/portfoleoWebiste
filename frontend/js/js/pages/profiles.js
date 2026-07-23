async function renderProfiles() {
  const rows = await api.get("/profiles");
  let user = null;
  try {
    user = await api.get("/me");
  } catch (err) {
    user = null;
  }
  const cards = rows.map(profileCardHtml).join("") || "<p class='empty'>No profiles have been created yet.</p>";
  const cta = user
    ? "<a class='button' href='#/profile/edit'>Create or edit my profile</a>"
    : "<a class='button' href='#/register'>Register your profile</a>";

  setView(`
    <section class="directory-hero">
      <span class="eyebrow">Profile directory</span>
      <h1>Browse the people behind the portfolios.</h1>
      <p class="lede">Every profile has room for skills, identity, place, contradictions, and the quietly interesting bits.</p>
      <div class="hero-actions">${cta}<a class="button ghost" href="#/dashboard">Dashboard</a></div>
    </section>
    <section class="profiles-section">
      <div class="section-head">
        <span class="eyebrow">Community profiles</span>
        <h2>Other people's pages</h2>
      </div>
      <div class="profile-grid">${cards}</div>
    </section>`);
}
