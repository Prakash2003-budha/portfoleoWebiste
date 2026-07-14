// portfolio.js
// -------------
// This used to be a fixed tabbed "portfolio evidence" view. It's now a
// freeform canvas: a blank page where text, photos, and pulled-in
// portfolio records can be dragged, resized, and rotated anywhere — a
// poster/collage the user designs themselves, instead of a fixed template.
//
// Structured records (education, experience, skills, etc.) still live in
// the same relational tables as before — they're just authored from a
// collapsible "Manage portfolio records" panel now, and get *placed* on
// the canvas rather than always being shown in fixed tabs.

let CANVAS_STATE = null; // { canvas_width, canvas_height, background_color, elements[] }
let CANVAS_EDITABLE = false;
let CANVAS_SELECTED_ID = null;
let CANVAS_SECTIONS = null;
let CANVAS_OWNER_USER_ID = null;
let CANVAS_Z_COUNTER = 1;
let CANVAS_ADD_COUNT = 0;
let CANVAS_SAVE_TIMER = null;
let CANVAS_KEYDOWN_HANDLER = null;
let RECORDS_ACTIVE_SECTION = "education";

const CANVAS_SIZE_PRESETS = {
  portrait: { label: "Portrait poster", w: 900, h: 1200 },
  square: { label: "Square collage", w: 1000, h: 1000 },
  landscape: { label: "Landscape banner", w: 1300, h: 800 },
  a4: { label: "Tall page (A4-ish)", w: 950, h: 1343 },
};

async function renderPortfolio(params) {
  // The router only swaps #view's innerHTML, so listeners bound to
  // `document` (keyboard shortcuts) and pending timers need manual cleanup
  // whenever this page is (re)entered.
  if (CANVAS_KEYDOWN_HANDLER) {
    document.removeEventListener("keydown", CANVAS_KEYDOWN_HANDLER);
    CANVAS_KEYDOWN_HANDLER = null;
  }
  if (CANVAS_SAVE_TIMER) {
    clearTimeout(CANVAS_SAVE_TIMER);
    CANVAS_SAVE_TIMER = null;
  }

  const viewingUserId = params && params.userId;
  let user = null;
  try {
    user = await api.get("/me");
  } catch (err) {
    user = null;
  }

  await window.loadPortfolioSchema();

  let owner, sections, canvasData, editable, ownerUserId;

  if (viewingUserId) {
    const data = await api.get(`/portfolio/user/${viewingUserId}`);
    owner = data.owner;
    sections = data.sections;
    editable = !!(user && String(user.id) === String(viewingUserId));
    ownerUserId = viewingUserId;
    canvasData = await api.get(`/canvas/user/${viewingUserId}`);
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
    ownerUserId = user.id;
    canvasData = await api.get("/canvas/me");
  }

  CANVAS_STATE = {
    canvas_width: canvasData.canvas_width,
    canvas_height: canvasData.canvas_height,
    background_color: canvasData.background_color || "#ffffff",
    elements: Array.isArray(canvasData.elements) ? canvasData.elements : [],
  };
  CANVAS_EDITABLE = editable;
  CANVAS_SELECTED_ID = null;
  CANVAS_SECTIONS = sections;
  CANVAS_OWNER_USER_ID = ownerUserId;
  CANVAS_Z_COUNTER = 1 + CANVAS_STATE.elements.reduce((m, e) => Math.max(m, e.z || 0), 0);
  CANVAS_ADD_COUNT = CANVAS_STATE.elements.length;

  setView(`
    <section class="directory-hero">
      <span class="eyebrow">${editable ? "Your canvas" : "Personal canvas"}</span>
      <h1>${esc(owner.display_name || owner.full_name || "Portfolio")}.</h1>
      <p class="lede">${esc(owner.headline || "A freeform space to arrange the evidence and the person behind it.")}</p>
      ${!editable ? "<p class=\"lede\" style=\"color:var(--muted)\">You're viewing this canvas read-only.</p>" : ""}
    </section>
    <section class="canvas-page">
      ${editable ? canvasToolbarHtml() : ""}
      <div class="canvas-stage-wrap${editable ? "" : " canvas-readonly"}" id="canvas-stage-wrap">
        <div class="canvas-stage" id="canvas-stage"></div>
      </div>
      ${editable ? recordsPanelHtml() : ""}
    </section>
  `);

  renderStage();
  wireStageBackgroundClick();

  if (editable) {
    wireToolbar();
    wireRecordsPanel();
    wireKeyboard();
  }
}

// ---------------------------------------------------------------------
// Toolbar
// ---------------------------------------------------------------------

function canvasToolbarHtml() {
  const cur = CANVAS_STATE;
  const matched = Object.entries(CANVAS_SIZE_PRESETS).find(
    ([, p]) => p.w === cur.canvas_width && p.h === cur.canvas_height
  );
  const options = Object.entries(CANVAS_SIZE_PRESETS)
    .map(
      ([key, p]) =>
        `<option value="${key}" ${matched && matched[0] === key ? "selected" : ""}>${esc(p.label)} (${p.w}×${p.h})</option>`
    )
    .join("");

  return `
    <div class="canvas-toolbar">
      <button class="button small" id="add-text-btn" type="button">+ Text</button>
      <label class="button small ghost file-btn">+ Photo<input type="file" id="add-photo-input" accept="image/*"></label>
      <div class="canvas-menu" id="add-data-menu">
        <button class="button small ghost" id="add-data-btn" type="button">+ From portfolio ▾</button>
        <div class="canvas-menu-panel" id="add-data-panel"></div>
      </div>
      <div class="divider"></div>
      <select id="canvas-size-select" title="Canvas size">${options}</select>
      <input type="color" id="canvas-bg-input" value="${cur.background_color}" title="Canvas background">
      <div class="divider"></div>
      <button class="button small ghost" id="canvas-clear-btn" type="button">Clear</button>
      <button class="button small" id="canvas-save-btn" type="button">Save</button>
      <span class="canvas-status saved" id="canvas-status"><span class="dot"></span><span id="canvas-status-text">Saved</span></span>
    </div>`;
}

function wireToolbar() {
  document.getElementById("add-text-btn").addEventListener("click", addTextElement);

  document.getElementById("add-photo-input").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    if (file.size > 8 * 1024 * 1024) {
      alert("Please choose an image under 8MB.");
      return;
    }
    try {
      const { dataUrl, width, height } = await resizeImageFile(file);
      addPhotoElement(dataUrl, width, height);
    } catch (err) {
      alert("Could not read that image.");
    }
  });

  const menuBtn = document.getElementById("add-data-btn");
  const menuWrap = document.getElementById("add-data-menu");
  menuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    menuWrap.classList.toggle("open");
  });
  document.addEventListener("click", () => menuWrap.classList.remove("open"));
  buildAddDataMenu();

  const sizeSelect = document.getElementById("canvas-size-select");
  sizeSelect.addEventListener("change", () => {
    const preset = CANVAS_SIZE_PRESETS[sizeSelect.value];
    if (!preset) return;
    CANVAS_STATE.canvas_width = preset.w;
    CANVAS_STATE.canvas_height = preset.h;
    markDirty();
    renderStage();
  });

  const bgInput = document.getElementById("canvas-bg-input");
  bgInput.addEventListener("input", () => {
    CANVAS_STATE.background_color = bgInput.value;
    markDirty();
    renderStage();
  });

  document.getElementById("canvas-clear-btn").addEventListener("click", () => {
    if (CANVAS_STATE.elements.length && !confirm("Remove everything from this canvas?")) return;
    CANVAS_STATE.elements = [];
    CANVAS_SELECTED_ID = null;
    markDirty();
    renderStage();
  });

  document.getElementById("canvas-save-btn").addEventListener("click", saveCanvas);
}

function buildAddDataMenu() {
  const panel = document.getElementById("add-data-panel");
  if (!panel) return;
  const schema = window.getPortfolioSchema() || {};
  let html = "";

  Object.entries(schema).forEach(([key, cfg]) => {
    const rows = (CANVAS_SECTIONS && CANVAS_SECTIONS[key]) || [];
    if (!rows.length) return;
    html += `<div class="canvas-menu-group-label">${esc(cfg.label)}</div>`;
    rows.forEach((row) => {
      html += `<button type="button" class="canvas-menu-item" data-section="${key}" data-id="${row.id}">
        ${esc(row[cfg.primary] || "")}${row[cfg.secondary] ? `<small>${esc(row[cfg.secondary])}</small>` : ""}
      </button>`;
    });
  });

  panel.innerHTML =
    html || `<p class="canvas-menu-empty">No portfolio records yet — add some in the panel below, then drag them in here.</p>`;

  panel.querySelectorAll(".canvas-menu-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      const section = btn.dataset.section;
      const rows = (CANVAS_SECTIONS && CANVAS_SECTIONS[section]) || [];
      const row = rows.find((r) => String(r.id) === btn.dataset.id);
      if (row) addDataElement(section, row);
    });
  });
}

// ---------------------------------------------------------------------
// Adding elements
// ---------------------------------------------------------------------

function newId() {
  return "el_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function nextZ() {
  CANVAS_Z_COUNTER += 1;
  return CANVAS_Z_COUNTER;
}

function prevZ() {
  const min = CANVAS_STATE.elements.reduce((m, e) => Math.min(m, e.z || 1), 1);
  return min - 1;
}

function cascadeOffset() {
  return (CANVAS_ADD_COUNT % 6) * 22;
}

function addTextElement() {
  const off = cascadeOffset();
  const el = {
    id: newId(),
    type: "text",
    x: 40 + off,
    y: 40 + off,
    width: 240,
    height: 90,
    rotation: 0,
    z: nextZ(),
    text: "Double-click to edit this text",
    style: { fontSize: 18, color: "#1a1a1a", background: "transparent", bold: false, align: "left" },
  };
  CANVAS_STATE.elements.push(el);
  CANVAS_ADD_COUNT++;
  CANVAS_SELECTED_ID = el.id;
  markDirty();
  renderStage();
}

function fitBox(w, h, max) {
  if (w <= max && h <= max) return { w, h };
  const scale = max / Math.max(w, h);
  return { w: Math.round(w * scale), h: Math.round(h * scale) };
}

function addPhotoElement(dataUrl, w, h) {
  const box = fitBox(w, h, 300);
  const off = cascadeOffset();
  const el = {
    id: newId(),
    type: "photo",
    x: 60 + off,
    y: 60 + off,
    width: box.w,
    height: box.h,
    rotation: 0,
    z: nextZ(),
    src: dataUrl,
    style: { borderRadius: 0 },
  };
  CANVAS_STATE.elements.push(el);
  CANVAS_ADD_COUNT++;
  CANVAS_SELECTED_ID = el.id;
  markDirty();
  renderStage();
}

function addDataElement(section, row) {
  const cfg = window.getSectionConfig(section);
  if (!cfg) return;
  const off = cascadeOffset();
  const el = {
    id: newId(),
    type: "data",
    x: 80 + off,
    y: 80 + off,
    width: 260,
    height: 100,
    rotation: 0,
    z: nextZ(),
    title: row[cfg.primary] || "",
    subtitle: row[cfg.secondary] || "",
    style: { fontSize: 15, color: "#1a1a1a", background: "#f4f1ea", align: "left" },
  };
  CANVAS_STATE.elements.push(el);
  CANVAS_ADD_COUNT++;
  CANVAS_SELECTED_ID = el.id;
  markDirty();
  renderStage();
  document.getElementById("add-data-menu")?.classList.remove("open");
}

function deleteElement(id) {
  CANVAS_STATE.elements = CANVAS_STATE.elements.filter((e) => e.id !== id);
  if (CANVAS_SELECTED_ID === id) CANVAS_SELECTED_ID = null;
  markDirty();
  renderStage();
}

// ---------------------------------------------------------------------
// Image handling — downscale in-browser before it's ever sent anywhere,
// since photos are stored inline as base64 data URLs.
// ---------------------------------------------------------------------

function resizeImageFile(file, maxDim = 1100, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        if (width > maxDim || height > maxDim) {
          const scale = maxDim / Math.max(width, height);
          width = Math.round(width * scale);
          height = Math.round(height * scale);
        }
        const canvasEl = document.createElement("canvas");
        canvasEl.width = width;
        canvasEl.height = height;
        const ctx = canvasEl.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        const isPng = file.type === "image/png";
        const dataUrl = canvasEl.toDataURL(isPng ? "image/png" : "image/jpeg", quality);
        resolve({ dataUrl, width, height });
      };
      img.onerror = reject;
      img.src = reader.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ---------------------------------------------------------------------
// Rendering the stage + elements
// ---------------------------------------------------------------------

function findEl(id) {
  return CANVAS_STATE.elements.find((e) => e.id === id);
}

function renderStage() {
  const stage = document.getElementById("canvas-stage");
  if (!stage) return;
  stage.style.width = CANVAS_STATE.canvas_width + "px";
  stage.style.height = CANVAS_STATE.canvas_height + "px";
  stage.style.background = CANVAS_STATE.background_color;

  const sorted = [...CANVAS_STATE.elements].sort((a, b) => (a.z || 0) - (b.z || 0));
  stage.innerHTML = sorted.length
    ? sorted.map(elementHtml).join("")
    : `<p class="canvas-empty-hint">${
        CANVAS_EDITABLE
          ? "Empty canvas — add text, photos, or portfolio records from the toolbar above, then drag them anywhere."
          : "This canvas is empty."
      }</p>`;

  if (CANVAS_EDITABLE) {
    stage.querySelectorAll(".canvas-el").forEach(wireElement);
  }
}

function elementInnerHtml(el) {
  const st = el.style || {};
  if (el.type === "photo") {
    return `<img src="${el.src}" style="border-radius:${st.borderRadius || 0}px" draggable="false">`;
  }
  if (el.type === "data") {
    return `<div class="data-block" style="background:${st.background || "transparent"}; color:${
      st.color || "#1a1a1a"
    }; font-size:${st.fontSize || 15}px; text-align:${st.align || "left"};">
      <strong>${esc(el.title || "")}</strong>
      ${el.subtitle ? `<span>${esc(el.subtitle)}</span>` : ""}
    </div>`;
  }
  return `<div class="text-block" style="background:${st.background || "transparent"}; color:${
    st.color || "#1a1a1a"
  }; font-size:${st.fontSize || 18}px; font-weight:${st.bold ? 800 : 400}; text-align:${
    st.align || "left"
  };">${esc(el.text || "")}</div>`;
}

function elementToolbarHtml(el) {
  const st = el.style || {};
  if (el.type === "photo") {
    return `<div class="canvas-el-toolbar">
      <button type="button" data-action="radius" data-val="0">Square</button>
      <button type="button" data-action="radius" data-val="16">Round</button>
      <button type="button" data-action="radius" data-val="9999">Circle</button>
      <button type="button" data-action="front">Front</button>
      <button type="button" data-action="back">Back</button>
      <button type="button" class="danger" data-action="delete">Delete</button>
    </div>`;
  }
  const boldClass = st.bold ? " active" : "";
  return `<div class="canvas-el-toolbar">
    <select data-action="fontsize">
      ${[12, 14, 16, 18, 22, 28, 36, 48]
        .map((sz) => `<option value="${sz}" ${(st.fontSize || 18) == sz ? "selected" : ""}>${sz}px</option>`)
        .join("")}
    </select>
    <input type="color" data-action="color" value="${st.color || "#1a1a1a"}" title="Text color">
    <input type="color" data-action="bg" value="${
      st.background && st.background !== "transparent" ? st.background : "#ffffff"
    }" title="Background color">
    <button type="button" data-action="bgclear">No bg</button>
    ${el.type === "text" ? `<button type="button" class="${boldClass}" data-action="bold">B</button>` : ""}
    <button type="button" data-action="align" data-val="left">L</button>
    <button type="button" data-action="align" data-val="center">C</button>
    <button type="button" data-action="align" data-val="right">R</button>
    <button type="button" data-action="front">Front</button>
    <button type="button" data-action="back">Back</button>
    <button type="button" class="danger" data-action="delete">Delete</button>
  </div>`;
}

function elementHtml(el) {
  const rot = el.rotation || 0;
  const style = `left:${el.x}px; top:${el.y}px; width:${el.width}px; height:${el.height}px; transform: rotate(${rot}deg); z-index:${el.z || 1};`;
  const selected = el.id === CANVAS_SELECTED_ID ? " selected" : "";
  const inner = elementInnerHtml(el);
  const handles = CANVAS_EDITABLE
    ? `<div class="rotate-handle" data-role="rotate"></div>
       <div class="resize-handle br" data-role="resize"></div>
       ${elementToolbarHtml(el)}`
    : "";
  return `<div class="canvas-el${selected}" data-id="${el.id}" data-type="${el.type}" style="${style}">
    <div class="canvas-el-inner">${inner}</div>
    ${handles}
  </div>`;
}

// ---------------------------------------------------------------------
// Selection, drag, resize, rotate, inline text editing
// ---------------------------------------------------------------------

function selectElement(id) {
  CANVAS_SELECTED_ID = id;
  document.querySelectorAll(".canvas-el").forEach((n) => n.classList.toggle("selected", n.dataset.id === id));
}

function deselectAll() {
  CANVAS_SELECTED_ID = null;
  document.querySelectorAll(".canvas-el").forEach((n) => n.classList.remove("selected"));
}

function wireStageBackgroundClick() {
  const stage = document.getElementById("canvas-stage");
  if (!stage) return;
  stage.addEventListener("pointerdown", (e) => {
    if (e.target === stage) deselectAll();
  });
}

function startDrag(e, node, el) {
  e.preventDefault();
  const handle = e.currentTarget;
  const startX = e.clientX;
  const startY = e.clientY;
  const origX = el.x;
  const origY = el.y;
  let moved = false;
  handle.setPointerCapture(e.pointerId);

  function onMove(ev) {
    const dx = ev.clientX - startX;
    const dy = ev.clientY - startY;
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) moved = true;
    el.x = Math.round(origX + dx);
    el.y = Math.round(origY + dy);
    node.style.left = el.x + "px";
    node.style.top = el.y + "px";
  }
  function onUp() {
    handle.releasePointerCapture(e.pointerId);
    handle.removeEventListener("pointermove", onMove);
    handle.removeEventListener("pointerup", onUp);
    if (moved) markDirty();
  }
  handle.addEventListener("pointermove", onMove);
  handle.addEventListener("pointerup", onUp);
}

function startResize(e, node, el) {
  e.preventDefault();
  e.stopPropagation();
  const handle = e.currentTarget;
  const startX = e.clientX;
  const startY = e.clientY;
  const origW = el.width;
  const origH = el.height;
  handle.setPointerCapture(e.pointerId);

  function onMove(ev) {
    const dx = ev.clientX - startX;
    const dy = ev.clientY - startY;
    el.width = Math.max(24, Math.round(origW + dx));
    el.height = Math.max(24, Math.round(origH + dy));
    node.style.width = el.width + "px";
    node.style.height = el.height + "px";
  }
  function onUp() {
    handle.releasePointerCapture(e.pointerId);
    handle.removeEventListener("pointermove", onMove);
    handle.removeEventListener("pointerup", onUp);
    markDirty();
  }
  handle.addEventListener("pointermove", onMove);
  handle.addEventListener("pointerup", onUp);
}

function startRotate(e, node, el) {
  e.preventDefault();
  e.stopPropagation();
  const handle = e.currentTarget;
  handle.setPointerCapture(e.pointerId);

  function onMove(ev) {
    const rect = node.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const angle = Math.atan2(ev.clientY - cy, ev.clientX - cx) * (180 / Math.PI) + 90;
    el.rotation = Math.round(angle);
    node.style.transform = `rotate(${el.rotation}deg)`;
  }
  function onUp() {
    handle.releasePointerCapture(e.pointerId);
    handle.removeEventListener("pointermove", onMove);
    handle.removeEventListener("pointerup", onUp);
    markDirty();
  }
  handle.addEventListener("pointermove", onMove);
  handle.addEventListener("pointerup", onUp);
}

function placeCaretAtEnd(el) {
  el.focus();
  if (typeof window.getSelection !== "undefined" && typeof document.createRange !== "undefined") {
    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }
}

function handleToolbarAction(e, id) {
  const action = e.target.dataset.action;
  if (!action) return;
  const el = findEl(id);
  if (!el) return;
  el.style = el.style || {};

  switch (action) {
    case "fontsize":
      el.style.fontSize = parseInt(e.target.value, 10);
      break;
    case "color":
      el.style.color = e.target.value;
      break;
    case "bg":
      el.style.background = e.target.value;
      break;
    case "bgclear":
      el.style.background = "transparent";
      break;
    case "bold":
      el.style.bold = !el.style.bold;
      break;
    case "align":
      el.style.align = e.target.dataset.val;
      break;
    case "radius":
      el.style.borderRadius = parseInt(e.target.dataset.val, 10);
      break;
    case "front":
      el.z = nextZ();
      break;
    case "back":
      el.z = prevZ();
      break;
    case "delete":
      deleteElement(id);
      return;
    default:
      return;
  }
  markDirty();
  renderStage();
}

function wireElement(node) {
  const id = node.dataset.id;
  const type = node.dataset.type;
  const inner = node.querySelector(".canvas-el-inner");

  inner.addEventListener("pointerdown", (e) => {
    const el = findEl(id);
    if (!el) return;
    if (type === "text") {
      const textEl = inner.querySelector(".text-block");
      if (textEl && textEl.isContentEditable) {
        e.stopPropagation();
        return; // let the browser place the text cursor instead of dragging
      }
    }
    selectElement(id);
    startDrag(e, node, el);
  });

  if (type === "text") {
    const textEl = inner.querySelector(".text-block");
    node.addEventListener("dblclick", (e) => {
      e.stopPropagation();
      textEl.contentEditable = "true";
      placeCaretAtEnd(textEl);
    });
    textEl.addEventListener("blur", () => {
      textEl.contentEditable = "false";
      const el = findEl(id);
      if (el) {
        el.text = textEl.innerText;
        markDirty();
      }
    });
  }

  const resizeHandle = node.querySelector('[data-role="resize"]');
  if (resizeHandle) resizeHandle.addEventListener("pointerdown", (e) => startResize(e, node, findEl(id)));

  const rotateHandle = node.querySelector('[data-role="rotate"]');
  if (rotateHandle) rotateHandle.addEventListener("pointerdown", (e) => startRotate(e, node, findEl(id)));

  const toolbar = node.querySelector(".canvas-el-toolbar");
  if (toolbar) {
    toolbar.addEventListener("pointerdown", (e) => e.stopPropagation());
    toolbar.addEventListener("click", (e) => handleToolbarAction(e, id));
    toolbar.addEventListener("input", (e) => handleToolbarAction(e, id));
    toolbar.addEventListener("change", (e) => handleToolbarAction(e, id));
  }
}

function wireKeyboard() {
  CANVAS_KEYDOWN_HANDLER = (e) => {
    if (!CANVAS_SELECTED_ID) return;
    const active = document.activeElement;
    if (active && active.isContentEditable) return;
    if (active && ["INPUT", "TEXTAREA", "SELECT"].includes(active.tagName)) return;
    if (e.key === "Delete" || e.key === "Backspace") {
      e.preventDefault();
      deleteElement(CANVAS_SELECTED_ID);
    }
  };
  document.addEventListener("keydown", CANVAS_KEYDOWN_HANDLER);
}

// ---------------------------------------------------------------------
// Saving
// ---------------------------------------------------------------------

function markDirty() {
  const status = document.getElementById("canvas-status");
  const text = document.getElementById("canvas-status-text");
  if (status) {
    status.classList.remove("saved");
    status.classList.add("dirty");
  }
  if (text) text.textContent = "Unsaved changes…";
  if (CANVAS_SAVE_TIMER) clearTimeout(CANVAS_SAVE_TIMER);
  CANVAS_SAVE_TIMER = setTimeout(saveCanvas, 1800);
}

async function saveCanvas() {
  if (CANVAS_SAVE_TIMER) {
    clearTimeout(CANVAS_SAVE_TIMER);
    CANVAS_SAVE_TIMER = null;
  }
  const status = document.getElementById("canvas-status");
  const text = document.getElementById("canvas-status-text");
  if (text) text.textContent = "Saving…";
  try {
    await api.put("/canvas/me", {
      canvas_width: CANVAS_STATE.canvas_width,
      canvas_height: CANVAS_STATE.canvas_height,
      background_color: CANVAS_STATE.background_color,
      elements: CANVAS_STATE.elements,
    });
    if (status) {
      status.classList.remove("dirty");
      status.classList.add("saved");
    }
    if (text) text.textContent = "Saved";
  } catch (err) {
    if (text) text.textContent = "Save failed — " + err.message;
  }
}

// ---------------------------------------------------------------------
// Records panel — still the relational education/experience/skills/etc.
// data, just tucked into a collapsible drawer under the canvas now.
// ---------------------------------------------------------------------

function recordsPanelHtml() {
  const schema = window.getPortfolioSchema() || {};
  const tabs = Object.entries(schema)
    .map(
      ([key, cfg]) =>
        `<button type="button" data-section="${key}" class="${key === RECORDS_ACTIVE_SECTION ? "active" : ""}">${esc(cfg.label)}</button>`
    )
    .join("");
  return `
    <details class="detail-panel wide" id="records-panel">
      <summary style="cursor:pointer; font-weight:900;">Manage portfolio records (education, experience, skills…)</summary>
      <div class="tabs" style="margin-top:16px;">${tabs}</div>
      <div id="records-section-body"></div>
    </details>`;
}

function wireRecordsPanel() {
  const panel = document.getElementById("records-panel");
  if (!panel) return;
  panel.querySelectorAll(".tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      RECORDS_ACTIVE_SECTION = btn.dataset.section;
      panel.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b === btn));
      renderRecordsSectionBody();
    });
  });
  renderRecordsSectionBody();
}

function renderRecordsSectionBody() {
  const cfg = window.getSectionConfig(RECORDS_ACTIVE_SECTION);
  const rows = (CANVAS_SECTIONS && CANVAS_SECTIONS[RECORDS_ACTIVE_SECTION]) || [];
  const items = rows.length
    ? rows
        .map(
          (row) => `
      <li>
        <div><strong>${esc(row[cfg.primary])}</strong><span>${esc(row[cfg.secondary] || "")}</span></div>
        <button class="remove-btn" data-id="${row.id}" type="button">Remove</button>
      </li>`
        )
        .join("")
    : "<li><span>No records yet.</span></li>";

  const formHtml = `
    <form id="records-form" class="inline-form">
      ${cfg.fields
        .map(
          (f) => `
        <label>
          ${esc(f.label)}${f.required ? " *" : ""}
          ${
            f.name === "description" || f.name === "identity_link"
              ? `<textarea name="${f.name}" rows="3" ${f.required ? "required" : ""}></textarea>`
              : `<input name="${f.name}" type="${f.type || "text"}" ${f.required ? "required" : ""}>`
          }
        </label>`
        )
        .join("")}
      <button class="button" type="submit">Add ${esc(cfg.label.toLowerCase())} record</button>
    </form>`;

  document.getElementById("records-section-body").innerHTML = `
    ${formHtml}
    <h3 style="margin-top:24px; margin-bottom:12px; color: var(--text);">${esc(cfg.label)} entries</h3>
    <ul class="item-list">${items}</ul>`;

  document.getElementById("records-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {};
    cfg.fields.forEach((f) => (payload[f.name] = form.get(f.name)));
    try {
      await api.post(`/portfolio/${RECORDS_ACTIVE_SECTION}`, payload);
      await refreshSections();
    } catch (err) {
      alert(err.message);
    }
  });

  document.querySelectorAll("#records-section-body .remove-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await api.del(`/portfolio/${RECORDS_ACTIVE_SECTION}/${btn.dataset.id}`);
        await refreshSections();
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

async function refreshSections() {
  const data = CANVAS_OWNER_USER_ID
    ? await api.get(`/portfolio/user/${CANVAS_OWNER_USER_ID}`)
    : await api.get("/portfolio/me");
  CANVAS_SECTIONS = data.sections;
  renderRecordsSectionBody();
  buildAddDataMenu();
}
