document.addEventListener("DOMContentLoaded", () => {
  const DEBUG = true;
  const debugOutput = document.getElementById("debugOutput");
  const clearDebugBtn = document.getElementById("clearDebugBtn");

  // Mark globally so we can confirm script load from console
  window.NamecardOCR_LOADED = true;
  window.NamecardOCR_Debug = { version: "debug-20250221a" };
  
  function log(...args) {
    const msg = args.map(a => {
      if (typeof a === "object") {
        try { return JSON.stringify(a); } catch { return String(a); }
      }
      return String(a);
    }).join(" ");
    
    if (DEBUG) console.log("[NamecardOCR]", ...args);
    
    // Also output to visible debug area
    if (debugOutput) {
      const time = new Date().toLocaleTimeString();
      debugOutput.textContent += `[${time}] ${msg}\n`;
      debugOutput.scrollTop = debugOutput.scrollHeight;
    }
  }
  
  if (clearDebugBtn) {
    clearDebugBtn.addEventListener("click", () => {
      if (debugOutput) debugOutput.textContent = "";
    });
  }
  
  log("Script loaded, initializing...");

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const analyzeBtnText = document.getElementById("analyzeBtnText");
  const statusEl = document.getElementById("status");
  const resultsEl = document.getElementById("results");
  const previewArea = document.getElementById("previewArea");
  const previewImage = document.getElementById("previewImage");
  const selectionCanvas = document.getElementById("selectionCanvas");
  const selectionBoxes = document.getElementById("selectionBoxes");
  const selectionList = document.getElementById("selectionList");
  const selectionCount = document.getElementById("selectionCount");
  const clearSelectionsBtn = document.getElementById("clearSelectionsBtn");
  const modeButtons = document.querySelectorAll(".mode-btn");

  // Debug: check if all elements are found
  log("Elements found:", {
    dropzone: !!dropzone,
    fileInput: !!fileInput,
    analyzeBtn: !!analyzeBtn,
    analyzeBtnText: !!analyzeBtnText,
    statusEl: !!statusEl,
    resultsEl: !!resultsEl,
    previewArea: !!previewArea,
    previewImage: !!previewImage,
    selectionCanvas: !!selectionCanvas,
    selectionBoxes: !!selectionBoxes,
    selectionList: !!selectionList,
    selectionCount: !!selectionCount,
    clearSelectionsBtn: !!clearSelectionsBtn,
    modeButtons: modeButtons.length
  });

  let selectedFile = null;
  let lastJobId = null;
  let currentMode = "auto"; // "auto" or "manual"
  let selections = []; // Array of {x, y, w, h} in image coordinates
  let isDrawing = false;
  let startX = 0, startY = 0;
  let currentRect = null;
  let imageScaleX=1;
		let imageScaleY=1;
  // ===== Mode Switching =====
  modeButtons.forEach((btn, idx) => {
    log(`Setting up mode button ${idx}:`, btn.getAttribute("data-mode"));
    btn.addEventListener("click", () => {
      log("Mode button clicked:", btn.getAttribute("data-mode"));
      modeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const newMode = btn.getAttribute("data-mode");
      const wasAuto = (currentMode === "auto");
      currentMode = newMode;
      log(`Mode changed: wasAuto=${wasAuto}, currentMode=${currentMode}, hasFile=${!!selectedFile}`);
      
      // If switching TO manual mode and we already have a file, show the preview
      if (currentMode === "manual" && selectedFile && wasAuto) {
        log("Switching to manual with existing file, calling showPreview");
        showPreview(selectedFile);
      }
      
      updateUI();
    });
  });

  function updateUI() {
    log(`updateUI called: mode=${currentMode}, hasFile=${!!selectedFile}`);
    if (currentMode === "manual") {
      if (analyzeBtnText) analyzeBtnText.textContent = "Crop & OCR Selected Regions";
      // Note: previewArea display is controlled by showPreview() after image loads
    } else {
      if (analyzeBtnText) analyzeBtnText.textContent = "Auto Analyze";
      if (previewArea) previewArea.style.display = "none";
    }
    updateAnalyzeButton();
  }

  function updateAnalyzeButton() {
    log("updateAnalyzeButton:", { mode: currentMode, hasFile: !!selectedFile, selections: selections.length });
    if (currentMode === "auto") {
      analyzeBtn.disabled = !selectedFile;
    } else {
      // Manual mode: need file AND at least one selection
      analyzeBtn.disabled = !selectedFile || selections.length === 0;
    }
  }

  // ===== File Selection =====
  function setStatus(msg) {
    log("Status:", msg);
    if (statusEl) statusEl.textContent = msg || "";
  }

  function onFileSelected(file) {
    log("onFileSelected called:", file ? file.name : "null");
    selectedFile = file;
    selections = [];
    renderSelections();
    
    if (file && currentMode === "manual") {
      log("File selected in manual mode, calling showPreview");
      showPreview(file);
    } else {
      log(`Not showing preview: file=${!!file}, mode=${currentMode}`);
      if (previewArea) previewArea.style.display = "none";
    }
    
    setStatus(selectedFile ? `Selected: ${selectedFile.name}` : "");
    updateAnalyzeButton();
  }

  function showPreview(file) {
    log("showPreview called:", file ? file.name : "null");
    
    if (!file) {
      log("showPreview: no file, hiding preview");
      if (previewArea) previewArea.style.display = "none";
      return;
    }
    
    if (!previewArea || !previewImage) {
      log("ERROR: previewArea or previewImage not found!");
      setStatus("Error: Preview elements not found");
      return;
    }
    
    setStatus(`Loading preview: ${file.name}...`);
    
    const reader = new FileReader();
    reader.onerror = (err) => {
      log("FileReader error:", err);
      setStatus(`Error loading file: ${file.name}`);
      previewArea.style.display = "none";
    };
    reader.onload = (e) => {
      log("FileReader onload, data length:", e.target.result.length);
      previewImage.onload = () => {
        log("Image loaded:", previewImage.naturalWidth, "x", previewImage.naturalHeight);
        setupCanvas();
        previewArea.style.display = "block";
        log("Preview area displayed");
        setStatus(`Selected: ${file.name} (${previewImage.naturalWidth}×${previewImage.naturalHeight}px) - Draw rectangles to select cards`);
      };
      previewImage.onerror = (imgErr) => {
        log("Image load error:", imgErr);
        setStatus(`Error displaying image: ${file.name}`);
        previewArea.style.display = "none";
      };
      previewImage.src = e.target.result;
      log("Image src set");
    };
    log("Starting to read file as DataURL");
    reader.readAsDataURL(file);
  }

  if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("bg-gray-100");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("bg-gray-100");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      log("File dropped");
      dropzone.classList.remove("bg-gray-100");
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      log("Dropped file:", f ? f.name : "none");
      if (f) onFileSelected(f);
    });
  } else {
    log("WARNING: dropzone element not found");
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const f = fileInput.files && fileInput.files[0];
      log("File input changed:", f ? f.name : "none");
      if (f) onFileSelected(f);
    });
  } else {
    log("WARNING: fileInput element not found");
  }

  // ===== Canvas Setup & Drawing =====
  function setupCanvas() {
    const displayWidth = previewImage.clientWidth;
    const displayHeight = previewImage.clientHeight;
    const naturalWidth = previewImage.naturalWidth;
    const naturalHeight = previewImage.naturalHeight;
    log("setupCanvas:", { displayWidth, displayHeight, naturalWidth, naturalHeight });
    
    selectionCanvas.width = displayWidth;
    selectionCanvas.height = displayHeight;
    selectionCanvas.style.width = displayWidth + "px";
    selectionCanvas.style.height = displayHeight + "px";
    
				imageScaleX = naturalWidth / displayWidth;
			 imageScaleY = naturalHeight / displayHeight;

log("Scale factors:", { imageScaleX, imageScaleY });
    
    // Clear any existing selections display
    selectionBoxes.innerHTML = "";
    renderSelections();
  }

  // Handle window resize
  window.addEventListener("resize", () => {
    if (previewImage.src && currentMode === "manual") {
      setTimeout(setupCanvas, 100);
    }
  });

  function getCanvasCoords(e) {
    const rect = selectionCanvas.getBoundingClientRect();
    let clientX, clientY;
    if (e.touches && e.touches.length > 0) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  }

  selectionCanvas.addEventListener("mousedown", startDraw);
  selectionCanvas.addEventListener("touchstart", startDraw, { passive: false });

  function startDraw(e) {
    if (currentMode !== "manual") return;
    e.preventDefault();
    isDrawing = true;
    const coords = getCanvasCoords(e);
    startX = coords.x;
    startY = coords.y;
    currentRect = { x: startX, y: startY, w: 0, h: 0 };
  }

  document.addEventListener("mousemove", draw);
  document.addEventListener("touchmove", draw, { passive: false });

  function draw(e) {
    if (!isDrawing || currentMode !== "manual") return;
    e.preventDefault();
    const coords = getCanvasCoords(e);
    const x = Math.min(startX, coords.x);
    const y = Math.min(startY, coords.y);
    const w = Math.abs(coords.x - startX);
    const h = Math.abs(coords.y - startY);
    currentRect = { x, y, w, h };
    drawCanvas();
  }

  document.addEventListener("mouseup", endDraw);
  document.addEventListener("touchend", endDraw);

  function endDraw(e) {
    if (!isDrawing) return;
    isDrawing = false;
    
    if (currentRect && currentRect.w > 20 && currentRect.h > 20) {
      // Convert to image coordinates
      const imgRect = {
        x: Math.round(currentRect.x * imageScaleX),
        y: Math.round(currentRect.y * imageScaleY),
        w: Math.round(currentRect.w * imageScaleX),
        h: Math.round(currentRect.h * imageScaleY)
      };
						log("開開心心")
						log("Rect display->image:", {
									displayRect: currentRect,
									imageRect: imgRect,
									natural: { w: previewImage.naturalWidth, h: previewImage.naturalHeight },
									display: { w: previewImage.clientWidth, h: previewImage.clientHeight },
									imageScaleX, imageScaleY
							});
      selections.push(imgRect);
      renderSelections();
      updateAnalyzeButton();
    }
    
    currentRect = null;
    drawCanvas();
  }

  function drawCanvas() {
    const ctx = selectionCanvas.getContext("2d");
    ctx.clearRect(0, 0, selectionCanvas.width, selectionCanvas.height);
    
    // Draw current rectangle being drawn
    if (currentRect && currentRect.w > 0 && currentRect.h > 0) {
      ctx.strokeStyle = "#28a745";
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
      ctx.setLineDash([]);
      ctx.fillStyle = "rgba(40, 167, 69, 0.2)";
      ctx.fillRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
    }
  }

  function renderSelections() {
    // Update count
    selectionCount.textContent = selections.length;
    log("renderSelections:", selections);
    
    // Render visual boxes on image
    selectionBoxes.innerHTML = "";
    selections.forEach((sel, idx) => {
      // Convert back to display coordinates
      const displayX = sel.x / imageScaleX;
      const displayY = sel.y / imageScaleY;
      const displayW = sel.w / imageScaleX;
      const displayH = sel.h / imageScaleY;
      
      const box = document.createElement("div");
      box.className = "selection-box";
      box.style.left = displayX + "px";
      box.style.top = displayY + "px";
      box.style.width = displayW + "px";
      box.style.height = displayH + "px";
      box.innerHTML = `
        <span class="box-label">${idx + 1}</span>
        <button class="box-delete" data-idx="${idx}">×</button>
      `;
      box.querySelector(".box-delete").addEventListener("click", (e) => {
        e.stopPropagation();
        removeSelection(idx);
      });
      selectionBoxes.appendChild(box);
    });
    
    // Render list
    selectionList.innerHTML = "";
    if (selections.length === 0) {
      selectionList.innerHTML = `<div class="text-muted p-3 text-center">尚未選取任何區域</div>`;
    } else {
      selections.forEach((sel, idx) => {
        const item = document.createElement("div");
        item.className = "selection-item";
        item.innerHTML = `
          <span>區域 ${idx + 1}: ${sel.w}×${sel.h}px</span>
          <button class="btn btn-outline-danger btn-sm" data-idx="${idx}">刪除</button>
        `;
        item.querySelector("button").addEventListener("click", () => removeSelection(idx));
        selectionList.appendChild(item);
      });
    }
  }

  function removeSelection(idx) {
    selections.splice(idx, 1);
    renderSelections();
    updateAnalyzeButton();
  }

		if (clearSelectionsBtn) {
				clearSelectionsBtn.addEventListener("click", () => {
						selections = [];
						renderSelections();
						updateAnalyzeButton();
				});
		} else {
				log("WARNING: clearSelectionsBtn element not found");
		}

  // ===== Analyze / Results =====
  function escapeHtml(s) {
    return (s || "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[c]));
  }

  function renderResults(jobId, cards) {
    resultsEl.innerHTML = "";
    if (!cards || !cards.length) {
      resultsEl.innerHTML = `<div class="alert alert-warning">No cards detected.</div>`;
      return;
    }

    const container = document.createElement("div");
    container.className = "row";

    cards.forEach((card, idx) => {
      const fields = card.fields || {};
      const col = document.createElement("div");
      col.className = "col-12 col-lg-6 mb-4";
      col.innerHTML = `
        <div class="card border-0 shadow">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="fw-bold">Card ${idx + 1}</div>
              <button class="btn btn-success btn-sm" data-action="confirm">Confirm</button>
            </div>
            <img src="${escapeHtml(card.image_url)}" class="img-fluid rounded border mb-3" alt="card"/>
            <div class="row g-2">
              ${inputRow("name", "Name", fields.name)}
              ${inputRow("job_title", "Job Title", fields.job_title)}
              ${inputRow("email", "Email", fields.email)}
              ${inputRow("mobile", "Mobile", fields.mobile)}
              ${inputRow("phone", "Phone", fields.phone)}
              ${inputRow("company_name", "Company", fields.company_name)}
              ${inputRow("company_phone", "Company Phone", fields.company_phone)}
              ${inputRow("address", "Address", fields.address)}
              ${inputRow("website", "Website", fields.website)}
            </div>
            <div class="mt-2 text-muted small">filename: ${escapeHtml(card.filename)}</div>
            <div class="mt-2" data-role="msg"></div>
          </div>
        </div>
      `;

      function inputRow(key, label, value) {
        return `
          <div class="col-12">
            <label class="form-label mb-1">${escapeHtml(label)}</label>
            <input class="form-control form-control-sm" data-field="${escapeHtml(key)}" value="${escapeHtml(value || "")}" />
          </div>
        `;
      }

      col.querySelector('[data-action="confirm"]').addEventListener("click", async () => {
        const msg = col.querySelector('[data-role="msg"]');
        msg.innerHTML = "";

        const payloadFields = {};
        col.querySelectorAll("[data-field]").forEach((el) => {
          payloadFields[el.getAttribute("data-field")] = el.value;
        });

        try {
          msg.innerHTML = `<div class="text-muted">Saving...</div>`;
          const resp = await fetch("/namecard_ocr/confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_id: jobId, filename: card.filename, fields: payloadFields }),
          });
          const data = await resp.json();
          if (!data.ok) {
            msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">${escapeHtml(data.error || "Save failed")}</div>`;
            return;
          }
          msg.innerHTML = `<div class="alert alert-success py-2 mb-0">Saved (customer_uid=${escapeHtml(String(data.customer_uid))}, created=${escapeHtml(String(data.created))})</div>`;
        } catch (e) {
          msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">Save failed: ${escapeHtml(String(e))}</div>`;
        }
      });

      container.appendChild(col);
    });

    resultsEl.appendChild(container);
  }

  analyzeBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    
    analyzeBtn.disabled = true;
    resultsEl.innerHTML = "";
    
    const fd = new FormData();
    fd.append("file", selectedFile);
    
    let endpoint = "/namecard_ocr/analyze";
    
    if (currentMode === "manual") {
      if (selections.length === 0) {
        setStatus("Please select at least one region");
        analyzeBtn.disabled = false;
        return;
      }
      setStatus(`Processing ${selections.length} selected region(s)...`);
      fd.append("mode", "manual");
      fd.append("selections", JSON.stringify(selections));
      endpoint = "/namecard_ocr/analyze_manual";
    } else {
      setStatus("Analyzing... (auto segmenting + OCR)");
    }
				
				if (currentMode === "manual") {
					log("POST analyze_manual payload:", {
							endpoint,
							selections,
							selections_json: JSON.stringify(selections).slice(0, 200) + "..."
					});
			}
				
				

    try {
      const resp = await fetch(endpoint, { method: "POST", body: fd });
      const data = await resp.json();
      if (!data.ok) {
        setStatus(`Error: ${data.error || "unknown"}`);
        updateAnalyzeButton();
        return;
      }
      lastJobId = data.job_id;
      setStatus(`Done. job_id=${data.job_id}, found ${data.cards.length} card(s)`);
      renderResults(data.job_id, data.cards);
      
      // Clear selections after successful processing
      if (currentMode === "manual") {
        selections = [];
        renderSelections();
      }
    } catch (e) {
      setStatus(`Error: ${String(e)}`);
    } finally {
      updateAnalyzeButton();
    }
  });

  // Initial UI setup
  updateUI();
  
  log("Initialization complete. Current mode:", currentMode);
  log("Ready! Select a file and click '手動框選' to see the preview.");
})();
