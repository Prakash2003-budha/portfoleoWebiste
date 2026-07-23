async function renderDashboard() {
  const data = await api.get("/dashboard");
  const reflections = await api.get("/reflections");
  const user = data.user;
  const profile = data.profile || {};
  const myProfileUrl = profile.id ? `#/profile/${profile.id}` : "#/profile/edit";

  const cards = data.recent_profiles.map(profileCardHtml).join("") || "<p class='empty'>No profiles yet.</p>";
  const entriesHtml =
    reflections
      .slice(0, 5)
      .map(
        (entry) => `<article class="note-card">
        <span>${esc(entry.mood || "Reflection")}</span>
        <h3>${esc(entry.title)}</h3>
        <p>${esc(entry.body)}</p>
      </article>`
      )
      .join("") ||
    "<article class='note-card'><span>Empty journal</span><h3>No reflections yet</h3><p>Add your first note from the form.</p></article>";

  setView(`
    <section class="dashboard-hero">
      <div>
        <span class="eyebrow">Dashboard</span>
        <h1>Hello, ${esc(user.full_name)}.</h1>
        <p class="lede">Manage your public profile, write reflections, and discover other people building weirdly honest portfolios.</p>
        <div class="hero-actions">
          <a class="button" href="#/profile/edit">Edit my profile</a>
          <a class="button ghost" href="${myProfileUrl}">View my profile</a>
          <a class="button ghost" href="#/profiles">Browse profiles</a>
        </div>
      </div>
      <aside class="profile-summary">
        ${avatarHtml({ display_name: profile.display_name || user.full_name, avatar_url: profile.avatar_url }, "large")}
        <h2>${esc(profile.display_name || user.full_name)}</h2>
        <p>${esc(profile.headline || "Your public headline is ready for editing.")}</p>
      </aside>
    </section>`);
  // NOTE: rest of the view is appended below to keep the hero clean.
  document.getElementById("view").insertAdjacentHTML("beforeend", `
    <section class="stats-grid">
      <article class="stat-card"><span>${esc(data.profile_count)}</span><p>Public profiles</p></article>
      <article class="stat-card"><span>${esc(data.reflection_count)}</span><p>Your reflections</p></article>
      <article class="stat-card"><span>Place</span><p>${esc(profile.location || "Add your location")}</p></article>
    </section>
    <section class="quick-actions">
      <a class="action-tile" href="#/studio"><strong>Open the Studio</strong><span>Design a new post with text, shapes, images, and freehand drawing.</span></a>
      <a class="action-tile" href="#/portfolio"><strong>View My Wall</strong><span>See every post you've made, laid out as a visual grid.</span></a>
      <a class="action-tile" href="#/profile/edit"><strong>Edit My Profile</strong><span>Change your name, headline, location, and bio.</span></a>
      <a class="action-tile" href="#/profiles"><strong>View Created Profiles</strong><span>Browse profiles created by all registered users.</span></a>
    </section>
    <section class="workbench">
      <form id="reflection-form" class="form-card compact">
        <h2>New reflection</h2>
        <div id="reflection-alert"></div>
        <label>Title<input name="title" required></label>
        <label>Entry<textarea name="body" rows="5" required></textarea></label>
        <label>Mood<input name="mood" placeholder="Focused, curious, chaotic"></label>
        <button class="button" type="submit">Save reflection</button>
      </form>
      <div>
        <div class="section-head compact-head">
          <span class="eyebrow">Recent notes</span>
          <h2>Your diary stream</h2>
        </div>
        <div class="note-list">${entriesHtml}</div>
      </div>
    </section>
    <section class="profiles-section">
      <div class="section-head">
        <span class="eyebrow">Community</span>
        <h2>Newest profiles</h2>
      </div>
      <div class="profile-grid">${cards}</div>
    </section>`);

  document.getElementById("reflection-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      await api.post("/reflections", {
        title: form.get("title"),
        body: form.get("body"),
        mood: form.get("mood"),
      });
      renderDashboard();
    } catch (err) {
      document.getElementById("reflection-alert").innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });
}
