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
          <div id="resend-section" class="resend-section">
            <!-- Resend UI injected by script -->
          </div>
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
  const resendSection = document.getElementById("resend-section");

  // Helper to start a client-side countdown and disable the resend button
  function startCooldown(btn, seconds) {
    let remaining = seconds;
    btn.disabled = true;
    btn.textContent = `Resend available in ${remaining}s`;
    const iv = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(iv);
        btn.disabled = false;
        btn.textContent = `Resend code`;
      } else {
        btn.textContent = `Resend available in ${remaining}s`;
      }
    }, 1000);
  }

  // Render resend UI: either use stored pending email or show an input
  (function renderResendUi() {
    const storedEmail = localStorage.getItem("pfw_pending_activation_email");
    if (storedEmail) {
      resendSection.innerHTML = `
        <p class="form-note">Didn't get the code? Resend to <strong>${esc(storedEmail)}</strong>.</p>
        <button id="resend-btn" class="button secondary">Resend code</button>
      `;
      const btn = document.getElementById("resend-btn");
      // Check server for remaining cooldown and start it if needed
      (async function () {
        try {
          const status = await api.get(`/activation-status?email=${encodeURIComponent(storedEmail)}`);
          if (status && status.retry_after && status.retry_after > 0) {
            startCooldown(btn, status.retry_after);
          }
        } catch (e) {
          // ignore status errors
        }
      })();
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          const res = await api.post("/resend-activation", { email: storedEmail });
          alertContainer.innerHTML = `<p class="notice">${esc(res.message || 'Activation code sent.')}</p>`;
          startCooldown(btn, res.retry_after || 60);
        } catch (err) {
          const retry = err.data && err.data.retry_after ? err.data.retry_after : null;
          if (retry) {
            startCooldown(btn, retry);
          }
          btn.disabled = false;
          alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
        }
      });
    } else {
      resendSection.innerHTML = `
        <p class="form-note">Didn't get the code? Enter your email to resend the activation code.</p>
        <label>Email<input id="resend-email" type="email" required></label>
        <button id="resend-btn" class="button secondary">Resend code</button>
      `;
      const btn = document.getElementById("resend-btn");
      const input = document.getElementById("resend-email");
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        const mail = input.value.trim();
        if (!mail) return; 
        btn.disabled = true;
        try {
          const res = await api.post("/resend-activation", { email: mail });
          // remember the email for future visits
          localStorage.setItem("pfw_pending_activation_email", mail);
          alertContainer.innerHTML = `<p class="notice">${esc(res.message || 'Activation code sent.')}</p>`;
          startCooldown(btn, res.retry_after || 60);
        } catch (err) {
          const retry = err.data && err.data.retry_after ? err.data.retry_after : null;
          if (retry) {
            startCooldown(btn, retry);
          }
          btn.disabled = false;
          alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
        }
      });
    }
  })();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertContainer.innerHTML = "";
    const codeValue = form.code.value.trim();
    try {
      await activateAccount(codeValue);
      // activation succeeded; remove any stored pending email
      localStorage.removeItem("pfw_pending_activation_email");
    } catch (err) {
      alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });

  if (code) {
    try {
      await activateAccount(code);
      localStorage.removeItem("pfw_pending_activation_email");
    } catch (err) {
      alertContainer.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  }
}
