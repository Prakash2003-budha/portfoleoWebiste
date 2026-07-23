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

/**
 * Renders a profile picture if the person has uploaded one to Cloudinary,
 * otherwise falls back to the initials badge. `sizeClass` matches the
 * existing .avatar size modifiers (e.g. "large", "xlarge").
 */
function avatarHtml(row, sizeClass) {
  const name = (row && (row.display_name || row.full_name)) || "Weirdo";
  const cls = ["avatar", sizeClass].filter(Boolean).join(" ");
  if (row && row.avatar_url) {
    return `<span class="${cls} has-photo"><img src="${esc(row.avatar_url)}" alt="${esc(name)}'s profile photo" loading="lazy"></span>`;
  }
  return `<span class="${cls}">${esc(initials(name))}</span>`;
}

function profileCardHtml(row) {
  const name = row.display_name || row.full_name || "Anonymous";
  const badge = row.is_owner ? "<span class='badge'>you</span>" : "";
  const editLink = row.is_owner
    ? "<a class='button ghost small' href='#/profile/edit'>Edit</a>"
    : "";
  return `<article class="profile-card">
    <a class="avatar-link" href="#/profile/${row.id}" aria-label="View ${esc(name)}">${avatarHtml(row)}</a>
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

  // The uploaded photo lives on the profile record, not the bare user
  // record, so fetch it too and prefer it for the navbar avatar.
  let profile = null;
  if (user) {
    try {
      profile = await api.get("/profile/me");
    } catch (err) {
      profile = null;
    }
  }

  if (user) {
    nav.innerHTML = `
      <a href="#/dashboard">Dashboard</a>
      <a href="#/profile/edit">Edit My Profile</a>
      <a href="#/profiles">View All Profiles</a>
      <a href="#/portfolio">Portfolio</a>
      <a href="#/feedback">Feedback</a>`;
    // Sign out is no longer a top-bar button. It lives in a dropdown behind
    // the user's avatar so the header stays quiet.
    actions.innerHTML = `
      <div class="user-menu" id="user-menu">
        <button type="button" class="user-menu-trigger" id="user-menu-trigger" aria-haspopup="menu" aria-expanded="false">
          ${avatarHtml({
            display_name: (profile && profile.display_name) || user.full_name,
            avatar_url: (profile && profile.avatar_url) || user.avatar_url,
          })}
          <span class="user-menu-name">${esc(user.full_name)}</span>
          <span class="caret" aria-hidden="true"></span>
        </button>
        <div class="user-menu-panel" role="menu">
          <div class="user-info">
            <strong>${esc(user.full_name)}</strong>
            <span>${esc(user.email || "Signed in")}</span>
          </div>
          <a href="#/dashboard" role="menuitem">Dashboard</a>
          <a href="#/profile/edit" role="menuitem">Edit my profile</a>
          <a href="#/portfolio" role="menuitem">My wall</a>
          <button type="button" class="signout" id="logout-link" role="menuitem">Sign out</button>
        </div>
      </div>`;

    const menu = document.getElementById("user-menu");
    const trigger = document.getElementById("user-menu-trigger");
    const closeMenu = () => {
      menu.classList.remove("open");
      trigger.setAttribute("aria-expanded", "false");
    };
    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const willOpen = !menu.classList.contains("open");
      menu.classList.toggle("open", willOpen);
      trigger.setAttribute("aria-expanded", String(willOpen));
    });
    document.addEventListener("click", (e) => {
      if (!menu.contains(e.target)) closeMenu();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeMenu();
    });

    document.getElementById("logout-link").addEventListener("click", async (e) => {
      e.preventDefault();
      closeMenu();
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

/**
 * Full-size image lightbox — used so anyone (not just the owner) can click
 * a post on a Wall and see it properly instead of just the small tile.
 */
function openLightbox(imageUrl, title, meta) {
  closeLightbox();
  const overlay = document.createElement("div");
  overlay.className = "lightbox-overlay";
  overlay.id = "lightbox-overlay";
  overlay.innerHTML = `
    <div class="lightbox-shell" role="dialog" aria-modal="true" aria-label="${esc(title || "Post")}">
      <button class="lightbox-close" type="button" aria-label="Close">&times;</button>
      <img class="lightbox-image" src="${esc(imageUrl)}" alt="${esc(title || "Untitled post")}">
      ${title || meta ? `<div class="lightbox-caption">
        ${title ? `<h3>${esc(title)}</h3>` : ""}
        ${meta ? `<span>${esc(meta)}</span>` : ""}
      </div>` : ""}
    </div>`;
  document.body.appendChild(overlay);
  document.body.classList.add("lightbox-open");

  const close = () => closeLightbox();
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  overlay.querySelector(".lightbox-close").addEventListener("click", close);
  document.addEventListener("keydown", lightboxKeyHandler);
}

function lightboxKeyHandler(e) {
  if (e.key === "Escape") closeLightbox();
}

function closeLightbox() {
  const existing = document.getElementById("lightbox-overlay");
  if (existing) existing.remove();
  document.body.classList.remove("lightbox-open");
  document.removeEventListener("keydown", lightboxKeyHandler);
}
