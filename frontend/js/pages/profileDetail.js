async function renderProfileDetail(params) {
  const row = await api.get(`/profiles/${params.id}`);
  const action = row.is_owner
    ? "<a class='button' href='#/profile/edit'>Edit profile</a>"
    : "<a class='button ghost' href='#/profiles'>Back to directory</a>";

  setView(`
    <section class="profile-page">
      <div class="profile-banner">
        <div class="avatar xlarge">${esc(initials(row.display_name || row.full_name))}</div>
        <span class="eyebrow">Public profile</span>
        <h1>${esc(row.display_name || row.full_name)}</h1>
        <p class="lede">${esc(row.headline || "A portfolio still becoming itself.")}</p>
        <div class="hero-actions">${action}<a class="button ghost" href="#/profiles">Browse more</a></div>
      </div>
      <div class="detail-grid">
        <article class="detail-panel"><span>Location</span><p>${esc(row.location || "Not shared yet")}</p></article>
        <article class="detail-panel wide"><span>About</span><p>${esc(row.bio || "This person has not written a bio yet.")}</p></article>
      </div>
      <div class="hero-actions">
        <a class="button ghost" href="#/portfolio/${row.user_id}">View full portfolio evidence</a>
      </div>
    </section>`);
}
