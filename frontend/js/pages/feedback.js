function renderFeedback() {
  setView(`
    <section class="editor-layout">
      <div>
        <span class="eyebrow">Usability testing</span>
        <h1>Tell us how the prototype feels.</h1>
        <p class="lede">This short form supports Objective 4 of the proposal: evaluating whether the system represents identity clearly while staying easy to use.</p>
      </div>
      <form id="feedback-form" class="form-card">
        <h2>Usability feedback</h2>
        <div id="feedback-alert"></div>
        <label>Your name (optional)<input name="visitor_name" placeholder="Anonymous"></label>
        <label>Clarity rating (1-5)<input name="clarity_rating" type="number" min="1" max="5" required></label>
        <label>Identity representation rating (1-5)<input name="identity_rating" type="number" min="1" max="5" required></label>
        <label>Comments<textarea name="comments" rows="5" placeholder="What worked, what felt confusing?"></textarea></label>
        <button class="button" type="submit">Submit feedback</button>
      </form>
    </section>`);

  document.getElementById("feedback-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      await api.post("/feedback", {
        visitor_name: form.get("visitor_name"),
        clarity_rating: form.get("clarity_rating"),
        identity_rating: form.get("identity_rating"),
        comments: form.get("comments"),
      });
      document.getElementById("feedback-alert").innerHTML =
        "<p class='badge'>Thanks — your feedback was saved.</p>";
      e.target.reset();
    } catch (err) {
      document.getElementById("feedback-alert").innerHTML = `<p class="alert">${esc(err.message)}</p>`;
    }
  });
}
