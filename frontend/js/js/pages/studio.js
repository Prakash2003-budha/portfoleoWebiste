// studio.js
// The "Canva-like" post editor. People express themselves visually here —
// text, shapes, images, and freehand drawing on a fixed-size canvas — instead
// of filling out education/experience forms. Built on Fabric.js (loaded from
// a CDN in index.html) so we get object selection, resize handles, and
// serialization for free.

const STUDIO_SIZE = 1080; // internal canvas resolution (square post, like an IG post)
const STUDIO_MAX_HISTORY = 30;

let studioCanvas = null;
let studioPostId = null; // set when editing an existing post
let studioHistory = [];
let studioRedoStack = [];
let studioApplyingHistory = false;
let studioTool = "select";
let studioBrushColor = "#f6c453";
let studioBrushWidth = 6;

async function renderStudio(params) {
  const user = await api.get("/me").catch(() => null);
  if (!user) {
    navigate("/login");
    return;
  }

  studioPostId = params && params.id ? params.id : null;
  let existing = null;
  if (studioPostId) {
    try {
      existing = await api.get(`/posts/${studioPostId}`);
      if (!existing.is_owner) {
        setView(`<p class="alert">You can only edit your own posts.</p>`);
        return;
      }
    } catch (err) {
      setView(`<p class="alert">${esc(err.message)}</p>`);
      return;
    }
  }

  setView(`
    <section class="studio">
      <div class="studio-topbar">
        <a class="button ghost small" href="#/portfolio">&larr; Back to my wall</a>
        <input id="studio-title" class="studio-title-input" type="text"
               placeholder="Untitled post" value="${esc(existing ? existing.title : "")}" maxlength="120">
        <div class="studio-topbar-actions">
          <button class="button ghost small" id="studio-undo" type="button" title="Undo">Undo</button>
          <button class="button ghost small" id="studio-redo" type="button" title="Redo">Redo</button>
          <button class="button small" id="studio-save" type="button">${existing ? "Save changes" : "Post it"}</button>
        </div>
      </div>
      <div id="studio-alert"></div>

      <div class="studio-body">
        <aside class="studio-tools">
          <button class="studio-tool active" data-tool="select" title="Select / move">
            <span class="studio-tool-icon">&#9995;</span><span>Select</span>
          </button>
          <button class="studio-tool" data-tool="text" title="Add text">
            <span class="studio-tool-icon">T</span><span>Text</span>
          </button>
          <button class="studio-tool" data-tool="rect" title="Add rectangle">
            <span class="studio-tool-icon">&#9634;</span><span>Rectangle</span>
          </button>
          <button class="studio-tool" data-tool="circle" title="Add circle">
            <span class="studio-tool-icon">&#9711;</span><span>Circle</span>
          </button>
          <button class="studio-tool" data-tool="triangle" title="Add triangle">
            <span class="studio-tool-icon">&#9651;</span><span>Triangle</span>
          </button>
          <button class="studio-tool" data-tool="line" title="Add line">
            <span class="studio-tool-icon">&#9585;</span><span>Line</span>
          </button>
          <button class="studio-tool" data-tool="pencil" title="Freehand pencil">
            <span class="studio-tool-icon">&#9998;</span><span>Pencil</span>
          </button>
          <button class="studio-tool" data-tool="image" title="Upload image">
            <span class="studio-tool-icon">&#128247;</span><span>Image</span>
          </button>
          <input type="file" id="studio-image-input" accept="image/*" style="display:none">
          <div class="studio-tools-divider"></div>
          <button class="studio-tool" id="studio-duplicate" type="button" title="Duplicate selection">
            <span class="studio-tool-icon">&#10064;</span><span>Duplicate</span>
          </button>
          <button class="studio-tool" id="studio-delete" type="button" title="Delete selection">
            <span class="studio-tool-icon">&#128465;</span><span>Delete</span>
          </button>
        </aside>

        <div class="studio-canvas-wrap">
          <div class="studio-canvas-frame" id="studio-canvas-frame">
            <canvas id="studio-fabric-canvas"></canvas>
          </div>
          <p class="studio-hint" id="studio-hint">Click a tool on the left to add something, then drag, resize, or double-click text to edit it.</p>
        </div>

        <aside class="studio-panel" id="studio-panel">
          <h3>Canvas</h3>
          <label class="studio-field">
            Background
            <input type="color" id="studio-bg-color" value="${existing ? "#181a20" : "#181a20"}">
          </label>
          <p class="studio-panel-empty" id="studio-panel-empty">Select something on the canvas to edit its style.</p>
          <div id="studio-object-controls" style="display:none;">
            <h3>Selection</h3>
            <label class="studio-field" id="studio-fill-row">
              Color
              <input type="color" id="studio-obj-fill" value="#f6c453">
            </label>
            <div id="studio-text-controls" style="display:none;">
              <label class="studio-field">
                Font
                <select id="studio-font-family">
                  <option value="Inter, sans-serif">Inter</option>
                  <option value="Fraunces, Georgia, serif">Fraunces</option>
                  <option value="'Playfair Display', Georgia, serif">Playfair Display</option>
                  <option value="'Bebas Neue', sans-serif">Bebas Neue</option>
                  <option value="'IBM Plex Mono', monospace">IBM Plex Mono</option>
                  <option value="Georgia, 'Times New Roman', serif">Georgia</option>
                  <option value="'Times New Roman', Times, serif">Times New Roman</option>
                  <option value="Arial, Helvetica, sans-serif">Arial</option>
                  <option value="Verdana, Geneva, sans-serif">Verdana</option>
                  <option value="'Courier New', Courier, monospace">Courier New</option>
                  <option value="'Brush Script MT', cursive">Brush Script</option>
                  <option value="Impact, 'Arial Narrow Bold', sans-serif">Impact</option>
                </select>
              </label>
              <label class="studio-field">
                Font size
                <input type="range" id="studio-font-size" min="12" max="180" value="48">
              </label>
              <label class="studio-field-row">
                <input type="checkbox" id="studio-font-bold"> Bold
              </label>
            </div>
            <div id="studio-stroke-controls" style="display:none;">
              <label class="studio-field">
                Thickness
                <input type="range" id="studio-stroke-width" min="1" max="40" value="6">
              </label>
            </div>
            <label class="studio-field">
              Opacity
              <input type="range" id="studio-opacity" min="0.1" max="1" step="0.05" value="1">
            </label>
            <div class="studio-layer-row">
              <button class="button ghost small" id="studio-forward" type="button">Forward</button>
              <button class="button ghost small" id="studio-backward" type="button">Backward</button>
            </div>
          </div>
        </aside>
      </div>
    </section>
  `);

  initStudioCanvas(existing);
}

function studioAlert(message, isError) {
  const el = document.getElementById("studio-alert");
  if (!el) return;
  el.innerHTML = message ? `<p class="${isError ? "alert" : "studio-notice"}">${esc(message)}</p>` : "";
}

function initStudioCanvas(existing) {
  if (typeof fabric === "undefined") {
    studioAlert("The drawing library failed to load. Check your internet connection and reload the page.", true);
    return;
  }

  studioCanvas = new fabric.Canvas("studio-fabric-canvas", {
    backgroundColor: "#181a20",
    preserveObjectStacking: true,
  });

  fitStudioCanvas();
  window.addEventListener("resize", fitStudioCanvas);

  studioHistory = [];
  studioRedoStack = [];

  if (existing && existing.canvas_json) {
    studioApplyingHistory = true;
    try {
      const data = typeof existing.canvas_json === "string" ? JSON.parse(existing.canvas_json) : existing.canvas_json;
      studioCanvas.loadFromJSON(data, () => {
        studioCanvas.renderAll();
        studioApplyingHistory = false;
        pushStudioHistory();
        const bgInput = document.getElementById("studio-bg-color");
        if (bgInput && studioCanvas.backgroundColor) bgInput.value = toHexColor(studioCanvas.backgroundColor);
      });
    } catch (err) {
      studioApplyingHistory = false;
      studioAlert("Couldn't load the saved design, starting from a blank canvas.", true);
    }
  } else {
    pushStudioHistory();
  }

  studioCanvas.on("object:added", onStudioCanvasChanged);
  studioCanvas.on("object:modified", onStudioCanvasChanged);
  studioCanvas.on("object:removed", onStudioCanvasChanged);
  studioCanvas.on("selection:created", updateStudioPanel);
  studioCanvas.on("selection:updated", updateStudioPanel);
  studioCanvas.on("selection:cleared", updateStudioPanel);
  studioCanvas.on("path:created", onStudioCanvasChanged);

  bindStudioToolbar();
  bindStudioPanel();
  updateStudioPanel();

  document.addEventListener("keydown", studioKeydownHandler);
}

// Fabric canvases have a fixed internal resolution (STUDIO_SIZE) so saved
// posts are always sharp; we only scale how they're *displayed* to fit
// whatever screen the person is on.
function fitStudioCanvas() {
  if (!studioCanvas) return;
  const frame = document.getElementById("studio-canvas-frame");
  if (!frame) return;
  const available = Math.min(frame.clientWidth || 560, 640);
  const scale = available / STUDIO_SIZE;
  studioCanvas.setDimensions({ width: STUDIO_SIZE * scale, height: STUDIO_SIZE * scale });
  studioCanvas.setViewportTransform([scale, 0, 0, scale, 0, 0]);
  studioCanvas.renderAll();
}

function toHexColor(color) {
  if (!color) return "#181a20";
  if (color.startsWith("#")) return color;
  return "#181a20";
}

function pushStudioHistory() {
  if (studioApplyingHistory || !studioCanvas) return;
  studioHistory.push(JSON.stringify(studioCanvas.toJSON()));
  if (studioHistory.length > STUDIO_MAX_HISTORY) studioHistory.shift();
  studioRedoStack = [];
}

function onStudioCanvasChanged() {
  if (studioApplyingHistory) return;
  pushStudioHistory();
}

function studioUndo() {
  if (studioHistory.length < 2) return;
  studioRedoStack.push(studioHistory.pop());
  const previous = studioHistory[studioHistory.length - 1];
  studioApplyingHistory = true;
  studioCanvas.loadFromJSON(JSON.parse(previous), () => {
    studioCanvas.renderAll();
    studioApplyingHistory = false;
    updateStudioPanel();
  });
}

function studioRedo() {
  if (studioRedoStack.length === 0) return;
  const next = studioRedoStack.pop();
  studioHistory.push(next);
  studioApplyingHistory = true;
  studioCanvas.loadFromJSON(JSON.parse(next), () => {
    studioCanvas.renderAll();
    studioApplyingHistory = false;
    updateStudioPanel();
  });
}

function setStudioTool(tool) {
  studioTool = tool;
  document.querySelectorAll(".studio-tool[data-tool]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tool === tool);
  });

  studioCanvas.isDrawingMode = tool === "pencil";
  if (tool === "pencil") {
    studioCanvas.freeDrawingBrush = new fabric.PencilBrush(studioCanvas);
    studioCanvas.freeDrawingBrush.color = studioBrushColor;
    studioCanvas.freeDrawingBrush.width = studioBrushWidth;
  }

  const hint = document.getElementById("studio-hint");
  const hints = {
    select: "Click a tool on the left to add something, then drag, resize, or double-click text to edit it.",
    text: "Text added — double-click it to type, drag the corners to resize.",
    pencil: "Pencil mode: click and drag on the canvas to draw. Pick Select to stop drawing.",
    image: "Choose an image from your device to add it to the canvas.",
  };
  if (hint) hint.textContent = hints[tool] || hints.select;
}

function addStudioShape(kind) {
  const center = STUDIO_SIZE / 2;
  let obj;
  const commonStroke = { stroke: "#181a20", strokeWidth: 0 };
  if (kind === "rect") {
    obj = new fabric.Rect({ left: center - 150, top: center - 100, width: 300, height: 200, fill: studioBrushColor, rx: 12, ry: 12, ...commonStroke });
  } else if (kind === "circle") {
    obj = new fabric.Circle({ left: center - 100, top: center - 100, radius: 100, fill: studioBrushColor, ...commonStroke });
  } else if (kind === "triangle") {
    obj = new fabric.Triangle({ left: center - 100, top: center - 90, width: 200, height: 180, fill: studioBrushColor, ...commonStroke });
  } else if (kind === "line") {
    obj = new fabric.Line([center - 150, center, center + 150, center], { stroke: studioBrushColor, strokeWidth: studioBrushWidth });
  }
  if (!obj) return;
  studioCanvas.add(obj);
  studioCanvas.setActiveObject(obj);
  studioCanvas.renderAll();
  setStudioTool("select");
}

function addStudioText() {
  const textbox = new fabric.Textbox("Say something", {
    left: STUDIO_SIZE / 2 - 220,
    top: STUDIO_SIZE / 2 - 40,
    width: 440,
    fontSize: 48,
    fontFamily: "Inter, sans-serif",
    fill: "#f7f3ea",
    fontWeight: 700,
  });
  studioCanvas.add(textbox);
  studioCanvas.setActiveObject(textbox);
  studioCanvas.renderAll();
  setStudioTool("select");
  textbox.enterEditing();
  textbox.selectAll();
}

function handleStudioImageFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    fabric.Image.fromURL(e.target.result, (img) => {
      const maxDim = STUDIO_SIZE * 0.7;
      const scale = Math.min(maxDim / img.width, maxDim / img.height, 1);
      img.set({
        left: (STUDIO_SIZE - img.width * scale) / 2,
        top: (STUDIO_SIZE - img.height * scale) / 2,
        scaleX: scale,
        scaleY: scale,
      });
      studioCanvas.add(img);
      studioCanvas.setActiveObject(img);
      studioCanvas.renderAll();
      setStudioTool("select");
    });
  };
  reader.readAsDataURL(file);
}

function bindStudioToolbar() {
  document.querySelectorAll(".studio-tool[data-tool]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tool = btn.dataset.tool;
      if (tool === "text") {
        addStudioText();
      } else if (["rect", "circle", "triangle", "line"].includes(tool)) {
        addStudioShape(tool);
      } else if (tool === "image") {
        document.getElementById("studio-image-input").click();
      } else {
        setStudioTool(tool);
      }
    });
  });

  document.getElementById("studio-image-input").addEventListener("change", (e) => {
    handleStudioImageFile(e.target.files[0]);
    e.target.value = "";
  });

  document.getElementById("studio-duplicate").addEventListener("click", () => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    active.clone((cloned) => {
      cloned.set({ left: (active.left || 0) + 24, top: (active.top || 0) + 24 });
      studioCanvas.add(cloned);
      studioCanvas.setActiveObject(cloned);
      studioCanvas.renderAll();
    });
  });

  document.getElementById("studio-delete").addEventListener("click", removeStudioSelection);

  document.getElementById("studio-undo").addEventListener("click", studioUndo);
  document.getElementById("studio-redo").addEventListener("click", studioRedo);

  document.getElementById("studio-bg-color").addEventListener("input", (e) => {
    studioCanvas.backgroundColor = e.target.value;
    studioCanvas.renderAll();
    pushStudioHistory();
  });

  document.getElementById("studio-save").addEventListener("click", saveStudioPost);
}

function removeStudioSelection() {
  const active = studioCanvas.getActiveObject();
  if (!active) return;
  if (active.type === "activeSelection") {
    active.forEachObject((obj) => studioCanvas.remove(obj));
  } else {
    studioCanvas.remove(active);
  }
  studioCanvas.discardActiveObject();
  studioCanvas.renderAll();
}

function studioKeydownHandler(e) {
  const active = studioCanvas && studioCanvas.getActiveObject();
  const isEditingText = active && active.isEditing;
  if (isEditingText) return;

  if ((e.key === "Delete" || e.key === "Backspace") && active) {
    e.preventDefault();
    removeStudioSelection();
  } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !e.shiftKey) {
    e.preventDefault();
    studioUndo();
  } else if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === "y" || (e.key.toLowerCase() === "z" && e.shiftKey))) {
    e.preventDefault();
    studioRedo();
  }
}

function bindStudioPanel() {
  document.getElementById("studio-obj-fill").addEventListener("input", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    if (active.type === "line") {
      active.set("stroke", e.target.value);
    } else {
      active.set("fill", e.target.value);
    }
    studioCanvas.renderAll();
  });
  document.getElementById("studio-obj-fill").addEventListener("change", pushStudioHistory);

  document.getElementById("studio-font-family").addEventListener("change", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active || active.type !== "textbox") return;
    active.set("fontFamily", e.target.value);
    studioCanvas.renderAll();
    pushStudioHistory();
  });

  document.getElementById("studio-font-size").addEventListener("input", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active || active.type !== "textbox") return;
    active.set("fontSize", parseInt(e.target.value, 10));
    studioCanvas.renderAll();
  });
  document.getElementById("studio-font-size").addEventListener("change", pushStudioHistory);

  document.getElementById("studio-font-bold").addEventListener("change", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active || active.type !== "textbox") return;
    active.set("fontWeight", e.target.checked ? 700 : 400);
    studioCanvas.renderAll();
    pushStudioHistory();
  });

  document.getElementById("studio-stroke-width").addEventListener("input", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    active.set("strokeWidth", parseInt(e.target.value, 10));
    studioCanvas.renderAll();
  });
  document.getElementById("studio-stroke-width").addEventListener("change", pushStudioHistory);

  document.getElementById("studio-opacity").addEventListener("input", (e) => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    active.set("opacity", parseFloat(e.target.value));
    studioCanvas.renderAll();
  });
  document.getElementById("studio-opacity").addEventListener("change", pushStudioHistory);

  document.getElementById("studio-forward").addEventListener("click", () => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    studioCanvas.bringForward(active);
    pushStudioHistory();
  });
  document.getElementById("studio-backward").addEventListener("click", () => {
    const active = studioCanvas.getActiveObject();
    if (!active) return;
    studioCanvas.sendBackwards(active);
    pushStudioHistory();
  });
}

function updateStudioPanel() {
  const active = studioCanvas && studioCanvas.getActiveObject();
  const controls = document.getElementById("studio-object-controls");
  const empty = document.getElementById("studio-panel-empty");
  if (!controls || !empty) return;

  if (!active) {
    controls.style.display = "none";
    empty.style.display = "block";
    return;
  }

  controls.style.display = "block";
  empty.style.display = "none";

  const isText = active.type === "textbox";
  const isLine = active.type === "line";
  document.getElementById("studio-text-controls").style.display = isText ? "block" : "none";
  document.getElementById("studio-stroke-controls").style.display = isLine ? "block" : "none";

  document.getElementById("studio-obj-fill").value = toHexColor(isLine ? active.stroke : active.fill);
  document.getElementById("studio-opacity").value = active.opacity != null ? active.opacity : 1;
  if (isText) {
    document.getElementById("studio-font-family").value = active.fontFamily || "Inter, sans-serif";
    document.getElementById("studio-font-size").value = active.fontSize || 48;
    document.getElementById("studio-font-bold").checked = (active.fontWeight || 400) >= 700;
  }
  if (isLine) {
    document.getElementById("studio-stroke-width").value = active.strokeWidth || 6;
  }
}

async function saveStudioPost() {
  if (!studioCanvas) return;
  const title = (document.getElementById("studio-title").value || "Untitled post").trim();
  const canvasJson = JSON.stringify(studioCanvas.toJSON());
  const thumbnail = studioCanvas.toDataURL({ format: "png", quality: 0.85, multiplier: 1 / (studioCanvas.getZoom() || 1) });

  const payload = { title, canvas_json: canvasJson, thumbnail, width: STUDIO_SIZE, height: STUDIO_SIZE };
  const saveBtn = document.getElementById("studio-save");
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving…";

  try {
    if (studioPostId) {
      await api.put(`/posts/${studioPostId}`, payload);
    } else {
      const result = await api.post("/posts", payload);
      studioPostId = result.id;
    }
    navigate("/portfolio");
  } catch (err) {
    studioAlert(err.message, true);
    saveBtn.disabled = false;
    saveBtn.textContent = studioPostId ? "Save changes" : "Post it";
  }
}

// Clean up global listeners when navigating away so they don't pile up
// across visits to the studio page (the router just swaps #view innerHTML,
// it doesn't tear down JS state for us).
function teardownStudio() {
  window.removeEventListener("resize", fitStudioCanvas);
  document.removeEventListener("keydown", studioKeydownHandler);
  studioCanvas = null;
}
