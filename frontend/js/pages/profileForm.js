async function renderProfileForm(error) {
  const user = await api.get("/me");
  const profile = (await api.get("/profile/me")) || {};
  const alert = error ? `<p class="alert">${esc(error)}</p>` : "";
  const viewLink = profile.id
    ? `<a class="button ghost" href="#/profile/${profile.id}">View My Current Profile</a>`
    : "";

  setView(`
    <section class="editor-layout">
      <div>
        <span class="eyebrow">Profile portal</span>
        <h1>Create your public profile.</h1>
        <p class="lede">This is the page other people see in the directory. Keep it clear, personal, and unmistakably yours.</p>
        <div class="hero-actions">
          <a class="button ghost" href="#/profiles">View Created Profiles</a>
          ${viewLink}
        </div>
      </div>
      <form id="profile-form" class="form-card">
        <h2>Profile details</h2>
        ${alert}
        <label>Display name<input name="display_name" value="${esc(profile.display_name || user.full_name)}" required></label>
        <label>Headline<input name="headline" value="${esc(profile.headline || "")}" maxlength="180" required></label>
        <label>Location<input name="location" value="${esc(profile.location || "")}"></label>
        <label>Bio<textarea name="bio" rows="7">${esc(profile.bio || "")}</textarea></label>
        <button class="button" type="submit">Save profile</button>
      </form>
    </section>`);

  document.getElementById("profile-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      const result = await api.put("/profile/me", {
        display_name: form.get("display_name"),
        headline: form.get("headline"),
        location: form.get("location"),
        bio: form.get("bio"),
      });
      navigate(`/profile/${result.id}`);
    } catch (err) {
      renderProfileForm(err.message);
    }
  });
}
