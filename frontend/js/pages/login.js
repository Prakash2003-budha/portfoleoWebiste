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
        <label>Email<input name="email" type="email" value="sujit@example.com" required></label>
        <label>Password<input name="password" type="password" value="password123" required></label>
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
      document.getElementById("login-alert").innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });
}
