function renderRegister() {
  setView(`
    <section class="auth-layout">
      <div class="auth-copy">
        <span class="eyebrow">Join the directory</span>
        <h1>Create a profile that leaves room for the whole person.</h1>
        <p class="lede">Your account starts with a public profile draft. You can edit the headline, location, and bio after registration.</p>
      </div>
      <form id="register-form" class="form-card">
        <h2>Register</h2>
        <div id="register-alert"></div>
        <label>Full name<input name="full_name" type="text" required></label>
        <label>Email<input name="email" type="email" required></label>
        <label>Password<input name="password" type="password" minlength="6" required></label>
        <button class="button" type="submit">Create account</button>
        <p class="form-note">Already have an account? <a href="#/login">Sign in</a>.</p>
      </form>
    </section>`);

  document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      await api.post("/register", {
        full_name: form.get("full_name"),
        email: form.get("email"),
        password: form.get("password"),
      });
      await renderTopbar();
      navigate("/profile/edit");
    } catch (err) {
      document.getElementById("register-alert").innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });
}
