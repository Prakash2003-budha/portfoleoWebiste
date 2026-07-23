let activeSection = "experiences";

async function renderPortfolio(params) {
  const viewingUserId = params && params.userId;
  let user = null;

  try {
    user = await api.get("/me");
  } catch (err) {
    user = null;
  }

  let owner;
  let sections;
  let editable;
  let targetUserId;

  await window.loadPortfolioSchema();

  if (viewingUserId) {
    const data = await api.get(`/portfolio/user/${viewingUserId}`);
    owner = data.owner;
    sections = data.sections;
    editable = user && String(user.id) === String(viewingUserId);
    targetUserId = viewingUserId;
  } else {
    if (!user) {
      navigate("/login");
      return;
    }
    const profile = await api.get("/profile/me");
    owner = { ...profile, full_name: user.full_name };
    sections = (await api.get(`/portfolio/user/${user.id}`)).sections;
    editable = true;
    targetUserId = user.id;
  }

  // The visual Wall (Studio posts) is a nice-to-have alongside the structured
  // sections below — don't let a failure here break the rest of the page.
  let posts = [];
  try {
    posts = await api.get(`/posts/user/${targetUserId}`);
  } catch (err) {
    posts = [];
  }

  const tabs = Object.entries(window.getPortfolioSchema())
    .map(([key, cfg]) => 
      `<button data-section="${key}" class="${key === activeSection ? "active" : ""}">${esc(cfg.label)}</button>`
    ).join("");

  setView(`
    <section class="directory-hero">
      <span class="eyebrow">Portfolio evidence</span>
      <h1>${esc(owner.display_name || owner.full_name || "Portfolio")}.</h1>
      <p class="lede">${esc(owner.headline || "Structured evidence with space for identity.")}</p>
      ${editable ? `<div class="hero-actions"><a class="button" href="#/studio">Open the Studio</a></div>` : ""}
    </section>
    <section class="wall-section">
      <div class="section-head compact-head">
        <span class="eyebrow">Visual wall</span>
        <h2>${editable ? "Your posts" : "Their posts"}</h2>
      </div>
      ${renderWallHtml(posts, editable)}
    </section>
    <section class="portfolio-editor">
      <div class="tabs">${tabs}</div>
      <div id="section-body"></div>
    </section>
  `);

  bindWallActions(editable, targetUserId, owner.display_name || owner.full_name);

  document.querySelectorAll(".tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeSection = btn.dataset.section;
      renderSectionBody(sections, editable);
      
      // Update active tab styling
      document.querySelectorAll(".tabs button").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
    });
  });

  renderSectionBody(sections, editable);
}

function renderWallHtml(posts, editable) {
  if (!posts || posts.length === 0) {
    return `
      <div class="wall-empty">
        <p>${editable ? "No posts yet — the Studio is where you design text, shapes, images, and freehand drawings into a post." : "This person hasn't posted anything to their wall yet."}</p>
        ${editable ? `<a class="button ghost small" href="#/studio">Open the Studio</a>` : ""}
      </div>`;
  }

  const tiles = posts.map((post) => `
    <article class="wall-tile" data-id="${post.id}" data-title="${esc(post.title || "Untitled post")}" tabindex="0" role="button" aria-label="View post: ${esc(post.title || "Untitled post")}">
      <img src="${esc(post.thumbnail)}" alt="${esc(post.title || "Untitled post")}" loading="lazy">
      <div class="wall-tile-overlay">
        <span>${esc(post.title || "Untitled post")}</span>
        ${editable ? `
          <div class="wall-tile-actions">
            <a class="wall-tile-edit" href="#/studio/${post.id}" title="Edit">Edit</a>
            <button class="wall-tile-delete" type="button" data-id="${post.id}" title="Delete">Delete</button>
          </div>` : ""}
      </div>
    </article>`).join("");

  return `<div class="wall-grid">${tiles}</div>`;
}

function bindWallActions(editable, targetUserId, ownerName) {
  document.querySelectorAll(".wall-tile").forEach((tile) => {
    const openTile = (e) => {
      // Don't open the lightbox when the click landed on an edit/delete control.
      if (e.target.closest(".wall-tile-edit, .wall-tile-delete")) return;
      const img = tile.querySelector("img");
      openLightbox(img.src, tile.dataset.title, ownerName ? `by ${ownerName}` : "");
    };
    tile.addEventListener("click", openTile);
    tile.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openTile(e);
      }
    });
  });

  if (!editable) return;
  document.querySelectorAll(".wall-tile-delete").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this post? This can't be undone.")) return;
      try {
        await api.del(`/posts/${btn.dataset.id}`);
        renderPortfolio(targetUserId ? { userId: targetUserId } : {});
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

function renderSectionBody(sections, editable) {
  const cfg = window.getSectionConfig(activeSection);
  const rows = sections[activeSection] || [];
  
  const items = rows.length > 0 
    ? rows.map((row) => `
      <li>
        <div>
          <strong>${esc(row[cfg.primary])}</strong>
          <span>${esc(row[cfg.secondary] || "")}</span>
        </div>
        ${editable ? `<button class="remove-btn" data-id="${row.id}">Remove</button>` : ""}
      </li>`).join("") 
    : "<li><span>No records yet.</span></li>";

  const formHtml = editable ? `
    <form id="section-form" class="inline-form">
      ${cfg.fields.map((f) => `
        <label>
          ${esc(f.label)}${f.required ? " *" : ""}
          ${f.name === "description" || f.name === "identity_link"
            ? `<textarea name="${f.name}" rows="3" ${f.required ? "required" : ""}></textarea>`
            : `<input name="${f.name}" type="${f.type || "text"}" ${f.required ? "required" : ""}>`
          }
        </label>
      `).join("")}
      <button class="button" type="submit">Add ${esc(cfg.label.toLowerCase())} record</button>
    </form>` : "";

  document.getElementById("section-body").innerHTML = `
    <article class="detail-panel wide">
      ${formHtml}
      <h3 style="margin-top: 24px; margin-bottom: 12px; color: var(--text);">${esc(cfg.label)} Entries</h3>
      <ul class="item-list">${items}</ul>
    </article>
  `;

  if (editable) {
    document.getElementById("section-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = new FormData(e.target);
      const payload = {};
      cfg.fields.forEach((f) => (payload[f.name] = form.get(f.name)));
      
      try {
        await api.post(`/portfolio/${activeSection}`, payload);
        renderPortfolio({}); // Re-render to fetch and show new data
      } catch (err) {
        alert(err.message);
      }
    });

    document.querySelectorAll(".remove-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.del(`/portfolio/${activeSection}/${btn.dataset.id}`);
          renderPortfolio({});
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }
}