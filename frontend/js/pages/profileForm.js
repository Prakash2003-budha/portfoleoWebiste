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
        <div id="avatar-alert"></div>
        <div class="avatar-uploader">
          <div class="avatar-uploader-preview" id="avatar-preview">
            ${avatarHtml({ display_name: profile.display_name || user.full_name, avatar_url: profile.avatar_url }, "large")}
          </div>
          <div class="avatar-uploader-controls">
            <label class="button ghost small avatar-upload-btn" for="avatar-input">
              ${profile.avatar_url ? "Change photo" : "Upload photo"}
            </label>
            <input type="file" id="avatar-input" accept="image/png,image/jpeg,image/webp,image/gif" style="display:none">
            <span class="avatar-uploader-hint">PNG, JPG, WEBP, or GIF. Up to 5MB — everyone browsing the directory will see this.</span>
          </div>
        </div>
        <label>Display name<input name="display_name" value="${esc(profile.display_name || user.full_name)}" required></label>
        <label>Headline<input name="headline" value="${esc(profile.headline || "")}" maxlength="180" required></label>
        <label>Location<input name="location" value="${esc(profile.location || "")}"></label>
        <label>Bio<textarea name="bio" rows="7">${esc(profile.bio || "")}</textarea></label>
        <button class="button" type="submit">Save profile</button>
      </form>
    </section>`);

  document.getElementById("avatar-input").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const avatarAlert = document.getElementById("avatar-alert");
    avatarAlert.innerHTML = `<p class="loading-state small">Uploading photo…</p>`;

    const formData = new FormData();
    formData.append("avatar", file);

    try {
      const response = await fetch(`${window.PFW_API_BASE || "http://127.0.0.1:5000/api"}/profile/me/avatar`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error((data && data.error) || `Upload failed (${response.status})`);
      }
      avatarAlert.innerHTML = "";
      document.getElementById("avatar-preview").innerHTML = avatarHtml(
        { display_name: document.querySelector('[name="display_name"]').value, avatar_url: data.avatar_url },
        "large"
      );
      document.querySelector(".avatar-upload-btn").textContent = "Change photo";
    } catch (err) {
      avatarAlert.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    } finally {
      e.target.value = "";
    }
  });

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
