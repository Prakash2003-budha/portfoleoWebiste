// Mirrors backend/routes/portfolio_routes.py SECTIONS, plus display labels
// and the input fields needed to add a new record in each section.
const PORTFOLIO_SECTIONS = {
  education: {
    label: "Education",
    primary: "institution",
    secondary: "qualification",
    fields: [
      { name: "institution", label: "Institution", required: true },
      { name: "qualification", label: "Qualification", required: true },
      { name: "start_year", label: "Start year", type: "number" },
      { name: "end_year", label: "End year", type: "number" },
    ],
  },
  experiences: {
    label: "Experience",
    primary: "title",
    secondary: "organization",
    fields: [
      { name: "title", label: "Title", required: true },
      { name: "organization", label: "Organization", required: true },
      { name: "description", label: "Description" },
      { name: "start_date", label: "Start date", type: "date" },
      { name: "end_date", label: "End date", type: "date" },
    ],
  },
  skills: {
    label: "Skills",
    primary: "name",
    secondary: "category",
    fields: [
      { name: "name", label: "Skill", required: true },
      { name: "category", label: "Category" },
      { name: "confidence_level", label: "Confidence (1-5)", type: "number" },
    ],
  },
  achievements: {
    label: "Achievements",
    primary: "title",
    secondary: "description",
    fields: [
      { name: "title", label: "Title", required: true },
      { name: "description", label: "Description" },
      { name: "achieved_on", label: "Date", type: "date" },
    ],
  },
  identity_traits: {
    label: "Identity traits",
    primary: "trait_name",
    secondary: "description",
    fields: [
      { name: "trait_name", label: "Trait", required: true },
      { name: "trait_type", label: "Type (strength/weakness/personality)" },
      { name: "description", label: "Description" },
    ],
  },
  habits: {
    label: "Habits",
    primary: "name",
    secondary: "identity_link",
    fields: [
      { name: "name", label: "Habit", required: true },
      { name: "frequency", label: "Frequency" },
      { name: "identity_link", label: "How it connects to identity" },
    ],
  },
};

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

  const tabs = Object.entries(PORTFOLIO_SECTIONS)
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
  const cfg = PORTFOLIO_SECTIONS[activeSection];
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
