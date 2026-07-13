let activeSection = "education";

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

  await window.loadPortfolioSchema();

  if (viewingUserId) {
    const data = await api.get(`/portfolio/user/${viewingUserId}`);
    owner = data.owner;
    sections = data.sections;
    editable = user && String(user.id) === String(viewingUserId);
  } else {
    if (!user) {
      navigate("/login");
      return;
    }
    const profile = await api.get("/profile/me");
    const data = await api.get("/portfolio/me");
    owner = { ...profile, full_name: user.full_name };
    sections = data.sections;
    editable = true;
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
    </section>
    <section class="portfolio-editor">
      <div class="tabs">${tabs}</div>
      <div id="section-body"></div>
    </section>
  `);

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