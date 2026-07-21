// ui.js
// Small render helpers shared across pages. Kept framework-free on purpose
// so the whole frontend stays a plain HTML/CSS/JS deliverable.

function esc(value) {
  const div = document.createElement("div");
  div.textContent = value === null || value === undefined ? "" : String(value);
  return div.innerHTML;
}

function initials(name) {
  const parts = String(name || "W")
    .split(" ")
    .filter(Boolean)
    .map((p) => p[0].toUpperCase());
  return parts.slice(0, 2).join("") || "W";
}

function profileCardHtml(row) {
  const name = row.display_name || row.full_name || "Anonymous";
  const badge = row.is_owner ? "<span class='badge'>you</span>" : "";
  const editLink = row.is_owner
    ? "<a class='button ghost small' href='#/profile/edit'>Edit</a>"
    : "";
  return `<article class="profile-card">
    <a class="avatar" href="#/profile/${row.id}" aria-label="View ${esc(name)}">${esc(initials(name))}</a>
    <div class="profile-card-copy">
      <div class="title-row"><h3>${esc(name)}</h3>${badge}</div>
      <p class="headline">${esc(row.headline || "Still shaping a public headline.")}</p>
      <p>${esc(row.bio || "This profile is waiting for a few honest lines.")}</p>
      <div class="meta-row">
        <span>${esc(row.location || "Somewhere strange")}</span>
        <div class="card-actions">${editLink}<a class="button small" href="#/profile/${row.id}">View Profile</a></div>
      </div>
    </div>
  </article>`;
}

async function renderTopbar() {
  const nav = document.getElementById("topnav");
  const actions = document.getElementById("top-actions");
  let user = null;
  try {
    user = await api.get("/me");
  } catch (err) {
    user = null;
  }

  if (user) {
    nav.innerHTML = `
      <a href="#/dashboard">Dashboard</a>
      <a href="#/profile/edit">Edit My Profile</a>
      <a href="#/profiles">View All Profiles</a>
      <a href="#/portfolio">My Wall</a>
      <a href="#/studio" class="nav-cta">+ New Post</a>
      <a href="#/feedback">Feedback</a>`;
    actions.innerHTML = `
      <span class="user-label">${esc(user.full_name)}</span>
      <a class="button ghost small" href="#" id="logout-link">Sign out</a>`;
    document.getElementById("logout-link").addEventListener("click", async (e) => {
      e.preventDefault();
      await api.post("/logout");
      navigate("/login");
      renderTopbar();
    });
  } else {
    nav.innerHTML = `
      <a href="#/register">Register New User</a>
      <a href="#/login">Login</a>
      <a href="#/profiles">View Profiles</a>`;
    actions.innerHTML = `
      <a class="button ghost small" href="#/login">Sign in</a>
      <a class="button small" href="#/register">Register New User</a>`;
  }
  return user;
}

function setView(html) {
  document.getElementById("view").innerHTML = html;
}
