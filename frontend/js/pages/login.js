function renderLogin() {
  setView(`
    <section class="auth-layout">
      <div class="auth-copy">
        <span class="eyebrow">Welcome back</span>
        <h1>Return to your wonderfully unfinished profile.</h1>
        <p class="lede">Sign in to write reflections, shape your profile, and browse the community dashboard.</p>
      </div>
      <form id="login-form" class="form-card">
        <h2>Sign in</h2>
        <div id="login-alert"></div>
        <label>Email<input name="email" type="email" placeholder="you@example.com" required></label>
        <label>Password<input name="password" type="password" placeholder="Enter your password" required></label>
        <button class="button" type="submit">Open dashboard</button>
        <p class="form-note">New user? <a href="#/register">Open the registration form</a>.</p>
      </form>
    </section>`);

  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      await api.post("/login", { email: form.get("email"), password: form.get("password") });
      await renderTopbar();
      navigate("/dashboard");
    } catch (err) {
      if (err.data && err.data.pending_activation) {
        // The account exists but hasn't completed email activation, so the
        // login form can't succeed. Show only a button that takes the user
        // back to the OTP confirmation page.
        // Remember the email so the activation page can resend for this user.
        try {
          const fd = new FormData(e.target);
          localStorage.setItem("pfw_pending_activation_email", fd.get("email"));
        } catch (e) {
          /* ignore */
        }
        document.getElementById("login-form").innerHTML = `
          <div class="form-card status-card">
            <div class="status-details">
              <p class="status-label">Activation required</p>
              <p>${esc(err.message)}</p>
            </div>
            <div class="status-actions">
              <a class="button" href="#/activate">Enter activation code</a>
            </div>
          </div>`;
      } else {
        document.getElementById("login-alert").innerHTML = `<p class="alert">${esc(err.message)}</p>`;
      }
    }
  });
}