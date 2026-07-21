// portfolio.js
// The "wall" — an Instagram/Canva-style grid of the visual posts someone has
// made in the Studio, instead of a structured evidence form (education,
// experience, skills...). Route names (#/portfolio, #/portfolio/:userId) are
// kept as-is so existing links elsewhere in the app don't break.

async function renderPortfolio(params) {
  const viewingUserId = params && params.userId;
  const user = await api.get("/me").catch(() => null);

  let owner;
  let posts;
  let editable;

  if (viewingUserId) {
    const [ownerRow, postRows] = await Promise.all([
      api.get(`/profiles/${viewingUserId}`).catch(() => null),
      api.get(`/posts/user/${viewingUserId}`),
    ]);
    owner = ownerRow;
    posts = postRows;
    editable = user && String(user.id) === String(viewingUserId);
  } else {
    if (!user) {
      navigate("/login");
      return;
    }
    const profile = await api.get("/profile/me");
    posts = await api.get(`/posts/user/${user.id}`);
    owner = { ...profile, full_name: user.full_name };
    editable = true;
  }

  const name = (owner && (owner.display_name || owner.full_name)) || "This wall";
  const heading = editable ? "Your wall." : `${name}'s wall.`;

  const grid = posts.length
    ? posts.map(postTileHtml).join("")
    : `<div class="wall-empty">
         <p>${editable ? "Nothing here yet — your first post is one click away." : "No posts here yet."}</p>
         ${editable ? '<a class="button" href="#/studio">Create your first post</a>' : ""}
       </div>`;

  setView(`
    <section class="directory-hero">
      <span class="eyebrow">Visual wall</span>
      <h1>${esc(heading)}</h1>
      <p class="lede">Express yourself the way you actually would — on a canvas, not a form. Text, shapes, photos, and freehand doodles, laid out however you like.</p>
      ${editable ? '<div class="hero-actions"><a class="button" href="#/studio">+ New post</a></div>' : ""}
    </section>
    <section class="wall-section">
      <div class="wall-grid">${grid}</div>
    </section>
  `);

  if (editable) {
    document.querySelectorAll("[data-delete-post]").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!confirm("Delete this post? This can't be undone.")) return;
        try {
          await api.del(`/posts/${btn.dataset.deletePost}`);
          renderPortfolio(params);
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }
}

function postTileHtml(post) {
  const editLink = post.is_owner
    ? `<a class="wall-tile-edit" href="#/studio/${post.id}" title="Edit">Edit</a>
       <button class="wall-tile-delete" data-delete-post="${post.id}" title="Delete">&times;</button>`
    : "";
  return `<article class="wall-tile">
    <img src="${post.thumbnail}" alt="${esc(post.title || "Untitled post")}" loading="lazy">
    <div class="wall-tile-overlay">
      <span>${esc(post.title || "Untitled post")}</span>
      <div class="wall-tile-actions">${editLink}</div>
    </div>
  </article>`;
}
