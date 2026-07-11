async function renderActivate(params) {
  const token = params.token;
  let message = "Activating your account...";
  let title = "Account activation";
  let status = "pending";

  try {
    const result = await api.get(`/activate/${encodeURIComponent(token)}`);
    message = result.message || "Your account is now activated. You can log in.";
    title = "Activation successful";
    status = "success";
  } catch (err) {
    message = err.message || "Activation failed. Please try again or contact support.";
    title = "Activation failed";
    status = "error";
  }

  setView(`
    <section class="auth-layout">
      <div class="auth-copy">
        <span class="eyebrow">${esc(title)}</span>
        <h1>${esc(message)}</h1>
        <p class="lede">
          ${status === "success"
            ? "Your account is activated and ready to use. Continue to sign in and finish your public profile."
            : "The activation link could not be processed. Try again, or open the email and click the link once more."}
        </p>
      </div>
      <div class="form-card status-card ${status}">
        <div class="status-icon">${status === "success" ? "✔" : "⚠"}</div>
        <div class="status-details">
          <p class="status-label">${status === "success" ? "Activation complete" : "Activation issue"}</p>
          <p>${esc(message)}</p>
        </div>
        <div class="status-actions">
          <a class="button" href="#/login">Sign in</a>
          ${status === "error" ? '<a class="button ghost" href="#/register">Register again</a>' : ''}
        </div>
      </div>
    </section>`);
}
