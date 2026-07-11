let PORTFOLIO_SCHEMA = null;
let activeSection = "education";

const PORTFOLIO_STYLES = `
.item-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.item-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: var(--panel-soft);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 10px 14px;
}

.item-list li strong {
  display: block;
}

.item-list li span {
  color: var(--muted);
  font-size: 0.9em;
}

.item-list .remove-btn {
  background: none;
  border: 1px solid var(--line);
  color: var(--rose);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
}

.inline-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.inline-form input,
.inline-form select,
.inline-form textarea {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--panel);
  color: var(--text);
}

.inline-form button {
  grid-column: 1 / -1;
}

.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tabs button {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--panel-soft);
  color: var(--text);
  cursor: pointer;
}

.tabs button.active {
  background: var(--accent-strong);
  color: #10201a;
  border-color: transparent;
}
`;

async function loadPortfolioSchema() {
  if (!PORTFOLIO_SCHEMA) {
    PORTFOLIO_SCHEMA = await api.get("/portfolio/schema");
  }
  return PORTFOLIO_SCHEMA;
}

function getSectionConfig(section) {
  return PORTFOLIO_SCHEMA ? PORTFOLIO_SCHEMA[section] : null;
}

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
    .map(
      ([key, cfg]) =>
        `<button data-section="${key}" class="${key === activeSection ? "active" : ""}">${esc(cfg.label)}</button>`
    )
    .join("");

  setView(`
    <section class="directory-hero">
      <span class="eyebrow">Portfolio evidence</span>
      <h1>${esc(owner.display_name || owner.full_name || "Portfolio")}.</h1>
      <p class="lede">${esc(owner.headline || "Structured evidence with space for identity.")}</p>
    </section>
    <section class="portfolio-editor">
      <div class="tabs">${tabs}</div>
      <div id="section-body"></div>
    </section>`);

  document.querySelectorAll(".tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeSection = btn.dataset.section;
      renderSectionBody(sections, editable);
      document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b === btn));
    });
  });

  renderSectionBody(sections, editable);
}

function renderSectionBody(sections, editable) {
  const cfg = window.getSectionConfig(activeSection);
  const rows = sections[activeSection] || [];
  const items =
    rows
      .map(
        (row) => `<li>
        <div>
          <strong>${esc(row[cfg.primary])}</strong>
          <span>${esc(row[cfg.secondary] || "")}</span>
        </div>
        ${editable ? `<button class="remove-btn" data-id="${row.id}">Remove</button>` : ""}
      </li>`
      )
      .join("") || "<li>No records yet.</li>";

  const formHtml = editable
    ? `<form id="section-form" class="inline-form">
        ${cfg.fields
          .map(
            (f) =>
              `<label>${esc(f.label)}${f.required ? " *" : ""}
                ${
                  f.name === "description" || f.name === "identity_link"
                    ? `<textarea name="${f.name}" rows="2" ${f.required ? "required" : ""}></textarea>`
                    : `<input name="${f.name}" type="${f.type || "text"}" ${f.required ? "required" : ""}>`
                }
              </label>`
          )
          .join("")}
        <button class="button" type="submit">Add ${esc(cfg.label.toLowerCase())} record</button>
      </form>`
    : "";

  document.getElementById("section-body").innerHTML = `
    <article class="detail-panel wide">
      <span>${esc(cfg.label)}</span>
      <ul class="item-list">${items}</ul>
    </article>
    ${formHtml}`;

  if (editable) {
    document.getElementById("section-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = new FormData(e.target);
      const payload = {};
      cfg.fields.forEach((f) => (payload[f.name] = form.get(f.name)));
      try {
        await api.post(`/portfolio/${activeSection}`, payload);
        renderPortfolio({});
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
