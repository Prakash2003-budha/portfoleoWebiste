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
        <label>Confirm password<input name="confirm_password" type="password" minlength="6" required></label>
        <button class="button" type="submit">Create account</button>
        <p class="form-note">Already have an account? <a href="#/login">Sign in</a>.</p>
      </form>
    </section>`);

  document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const submitBtn = e.target.querySelector("button[type=submit]");
    const alertEl = document.getElementById("register-alert");

    // Clear previous alert states
    alertEl.innerHTML = "";

    const password = form.get("password");
    const confirmPassword = form.get("confirm_password");

    // Client-side validation: Check if passwords match
    if (password !== confirmPassword) {
      alertEl.innerHTML = `<p class="alert">Passwords do not match. Please try again.</p>`;
      
      // Clear password fields to allow user re-entry
      e.target.querySelector("input[name=password]").value = "";
      e.target.querySelector("input[name=confirm_password]").value = "";
      e.target.querySelector("input[name=password]").focus();
      return;
    }

    // Guard against double-clicks firing two overlapping /register requests.
    if (submitBtn.disabled) return;
    submitBtn.disabled = true;
    submitBtn.textContent = "Creating account…";

    try {
      await api.post("/register", {
        full_name: form.get("full_name"),
        email: form.get("email"),
        password: password,
      });
      // Covers both a brand-new registration and the "already registered but
      // never activated" case, which now also returns success and resends a code.
      navigate("/activate");
    } catch (err) {
      alertEl.innerHTML = `<p class="alert">${esc(err.message)}</p>`;
      submitBtn.disabled = false;
      submitBtn.textContent = "Create account";
    }
  });
}