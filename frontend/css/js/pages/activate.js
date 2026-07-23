async function renderActivate(params) {
  const code = params.token ? decodeURIComponent(params.token) : "";

  function renderForm() {
    setView(`
      <section class="auth-layout">
        <div class="auth-copy">
          <span class="eyebrow">Activate your account</span>
          <h1>Enter the one-time activation code from your email.</h1>
          <p class="lede">A code was emailed to you after registration. Paste it here to complete activation.</p>
        </div>
        <form id="activate-form" class="form-card">
          <h2>Activation code</h2>
          <div id="activate-alert"></div>
          <label>Code<input name="code" type="text" inputmode="numeric" maxlength="6" minlength="6" value="${esc(code)}" required></label>
          <button class="button" type="submit">Activate account</button>
          <p class="form-note">If you did not receive the email, check your spam folder or try registering again.</p>
        </form>
      </section>`);
  }

  async function activateAccount(codeValue) {
    const result = await api.post("/activate", { code: codeValue });
    setView(`
      <section class="auth-layout">
        <div class="auth-copy">
          <span class="eyebrow">Activation successful</span>
          <h1>Your account is activated.</h1>
          <p class="lede">You can now sign in and continue building your profile.</p>
        </div>
        <div class="form-card status-card success">
          <div class="status-icon">✔</div>
          <div class="status-details">
            <p class="status-label">Activation complete</p>
            <p>${esc(result.message || "Your account is now activated. You can log in.")}</p>
          </div>
          <div class="status-actions">
            <a class="button" href="#/login">Sign in</a>
          </div>
        </div>
      </section>`);
  }

  renderForm();

  const form = document.getElementById("activate-form");
  const alertContainer = document.getElementById("activate-alert");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertContainer.innerHTML = "";
    const codeValue = form.code.value.trim();
    try {
      await activateAccount(codeValue);
    } catch (err) {
      alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });

  if (code) {
    try {
      await activateAccount(code);
    } catch (err) {
      alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  }
}
