class VariableDockComponent {
  constructor(containerElement, options = {}) {
    this.container = containerElement;

    this.onDrop = options.onDrop || (() => {});
    this.onDeleteAssignment = options.onDeleteAssignment || (() => {});

    this.config = {
      itemHeight: 70,
      baseWidth: 320,
      maxWidth: 500,
      spread: 240,
      colors: {
        zoneDefault: "#64748b",
        zoneHilighted: "rgba(0, 255, 0, 1)",
        valueMarked: "rgba(255, 0, 255, 1)"
      },
      defaultZoneName: "DÉFAUT",
      ...options.config,
    };

    this.state = {
      isVisible: false,
      data: {},
      filteredData: [],
      currentFilter: "",

      selectedIds: new Set(),

      scrollTop: 0,
      targetScrollTop: 0,
      scrollVelocity: 0,
      scrollSnapTimeout: null,

      activeItemIndex: -1,
      hoveredItem: null,

      isDragging: false,
      draggedItems: [],
      dragStartX: 0,
      dragStartY: 0,
      dragColor: "#fff",

      mouseY: -1000,
      animationFrameId: null,
    };

    this.dom = {};
    this.itemElements = [];

    this._initDOM();
    this._setupEvents();
    this._loop();
  }

  // --- API PUBLIQUE ---

  resetFilter() {
    this.filter("");
  }

  resetData() {
    this.state.data = {};
    this.state.filteredData = [];
    this.state.selectedIds.clear();
    this.resetFilter();
  }

  updateValue(key) {
    let v = this.state.data[key];
    if (v) {
      //console.log("UPDVALUE:" + key);
      const item = this.itemElements.find((e) => e.key === key);
      if (item) {
        const el = item.el;

        let zoneDefault=true;
        let zoneColor = this.config.colors.zoneDefault;
        if (!v.zone || v.zone != v.zoneparent) {
          zoneColor = this.config.colors.zoneHilighted;
          zoneDefault=false;
        }

        const statusClass = v.error
          ? "vd-status-dot vd-error"
          : "vd-status-dot";

        let e = el.querySelector(".vd-item-zone");
        if (zoneDefault)
         e.textContent = v.zone || "?";
        else
         e.textContent = (v.zone || "?") + " <= "+v.zoneparent;

        e.style.color=zoneColor;
        el.style.borderRightColor = zoneColor;


        e=item.el.querySelector(".vd-item-value");
        let s=v.value || "--";
        if (v.flags)
          s="["+v.flags+"] "+s;
        e.textContent = s;

        if (v.flags && v.flags.includes('K'))
          el.classList.add("vd-marked");
        else
          el.classList.remove("vd-marked");

        e=item.el.querySelector(".vd-status-dot");
        if (v.error)
          e.classList.add("vd-error");
        else
          e.classList.remove("vd-error");
      }
    }
  }

  isZoneInVariables(name) {
    if (name) {
      name=name.toLowerCase();
      return Object.values(this.state.data).some(v => v.zone === name);
    }
    return false;
  }

  updateData(variablesList) {
    if (Object.keys(this.state.data).length == 0) {
      console.log("DOCK: RESETDATA");
      this.resetData();

      variablesList.forEach((v) => {
        this.state.data[v.key] = v;
      });

      this.filter(this.state.currentFilter || "");
      this.showPanel();
    } else {
      console.log("DOCK: UPDATEDATA");
      variablesList.forEach((v) => {
        let vt = this.state.data[v.key];
        if (vt) {
          vt.tag = v.tag;
          vt.description = v.description;
          vt.valuestr = v.valuestr;
          vt.error = v.error;
          vt.zone = v.zone;
          vt.zoneparent = v.zoneparent;
          vt.flags = v.flags;

          this.updateValue(v.key);
        }
      });
    }
  }

  togglePanel(show) {
    if (show === undefined) show = !this.state.isVisible;

    if (this.state.isVisible === show) 
      return;

    if (show) 
      this.resetFilter();

    console.log("DOCK: TOGGLE "+show);

    this.state.isVisible = show;

    if (show) {
      //this.dom.panel.classList.remove("hidden");
      this.dom.panel.classList.add("vd-visible");
      this._updateDimensions();
      this._renderList();
      this._updateScrollPosition();
    } else {
      //this.dom.panel.classList.add("hidden");
      this.dom.panel.classList.remove("vd-visible");
      this.resetData();
    }
  }

  hidePanel() {
    console.log("HIDEPANEL");
    this.togglePanel(false);
  }

  showPanel() {
    console.log("SHOWPANEL");
    this.togglePanel(true);
  }

  _updateScrollPosition() {
    this._updateDimensions();

    const totalH = this.state.filteredData.length * this.config.itemHeight;
    this.state.targetScrollTop =
      this.state.viewHeight - this.config.itemHeight;

    this.state.targetScrollTop = Math.max(0, this.state.targetScrollTop);

    const max = (this.state.filteredData.length - 1) * this.config.itemHeight;
    if (this.state.targetScrollTop < 0) this.state.targetScrollTop = 0;
    if (this.state.targetScrollTop > max) this.state.targetScrollTop = max;

    this.state.scrollTop = this.state.targetScrollTop;
  }

  filter(query) {
    console.log("FILTER:"+query);

    let filterChanged=false;
    if (query.toLowerCase()!==this.state.currentFilter) {
      filterChanged=true;
    }

    this.state.currentFilter = query.toLowerCase();
    const term = query;

    // Filtrage
    this.state.filteredData = [];
    Object.keys(this.state.data).forEach((k) => {
      const v = this.state.data[k];
      if (!term ||
        v.key.toLowerCase().includes(term) ||
        (v.tag && v.tag.toLowerCase().includes(term)) ||
        (v.description && v.description.toLowerCase().includes(term))
      ) {
        this.state.filteredData.push(v);
      }
    });

    if (filterChanged) {
      this._renderList();

      // Si on a des données, on centre et on update le génie tout de suite
      if (this.state.filteredData.length > 0) {
        this._updateScrollPosition();

        // Force update immédiat pour éviter le saut visuel
        this._updateGenieEffect();
      }
    }
  }

  // --- PRIVE ---

  _initDOM() {
    const wrapper = document.createElement("div");
    wrapper.className = "vd-wrapper";
    wrapper.innerHTML = `
                    <svg class="vd-svg-layer"></svg>
                    <div id="vd-drag-ghost" class="vd-drag-ghost"></div>
                    
                    <div class="vd-panel" id="vd-panel">
                        <div class="vd-scroll-viewport" id="vd-viewport">
                            <div class="vd-focus-line"></div>
                            <div id="vd-list-content" class="vd-list-content"></div>
                        </div>
                    </div>
                `;

    this.container.appendChild(wrapper);

    this.dom.panel = wrapper.querySelector("#vd-panel");
    this.dom.viewport = wrapper.querySelector("#vd-viewport");
    this.dom.content = wrapper.querySelector("#vd-list-content");
    this.dom.ghost = wrapper.querySelector("#vd-drag-ghost");
  }

  _setupEvents() {
    this.dom.viewport.addEventListener("wheel", (e) => this._handleWheel(e), {
      passive: false,
    });
    window.addEventListener("resize", () => this._updateDimensions());

    document.addEventListener("mousemove", (e) =>
      this._handleGlobalMouseMove(e)
    );
    window.addEventListener("mouseup", (e) => this._endDrag(e));

    this.dom.panel.addEventListener("mouseleave", () => {
      if (!this.state.isDragging) {
        this.state.mouseY = -1000;
        this.state.hoveredItem = null;
      }
    });

    this.container.addEventListener("keydown", (e) => {
      if (!this.state.isVisible) return;
      if (e.target.tagName === "INPUT") return;

      // SUPPR
      if (e.key === "Delete" || e.key === "Backspace") {
        const toDelete = [];
        // 1. Check selection (mais seulement les items visibles/filtrés)
        if (this.state.selectedIds.size > 0) {
          this.state.selectedIds.forEach((key) => {
            // Vérifie que l'item est bien dans la liste filtrée actuelle
            const item = this.state.filteredData.find((d) => d.key === key);
            if (item) toDelete.push(item.key);
          });
        }
        // 2. Sinon check hover
        if (toDelete.length === 0 && this.state.hoveredItem) {
          // Vérifie aussi que l'item survolé est dans la liste filtrée (normalement oui)
          toDelete.push(this.state.hoveredItem.key);
        }

        if (toDelete.length > 0) {
          this.onDeleteAssignment(toDelete);
          this._clearSelection();
        }
      }

      // ESPACE
      if (e.code === "Space") {
        e.preventDefault();
        if (this.state.hoveredItem) {
          this._toggleSelection(this.state.hoveredItem.key);
        }
      }
      
      // CTRL + A
      if ((e.ctrlKey || e.metaKey) && e.key === "a") {
        e.preventDefault();
        e.stopPropagation();

        if (this.state.hoveredItem) {
          // On vérifie si tout ce qui est VISIBLE est sélectionné
          const allVisibleSelected = this.state.filteredData.every((v) =>
            this.state.selectedIds.has(v.key)
          );

          if (allVisibleSelected) {
            // Désélectionner uniquement les visibles
            this.state.filteredData.forEach((v) =>
              this.state.selectedIds.delete(v.key)
            );
          } else {
            // Sélectionner tous les visibles
            this.state.filteredData.forEach((v) =>
              this.state.selectedIds.add(v.key)
            );
          }

          this._updateSelectionVisuals();
        }
      }
    });
  }

  _renderList() {
    console.log("RENDERLIST()");
    this.dom.content.innerHTML = "";
    this.itemElements = [];

    this.state.filteredData.forEach((d, index) => {
      const el = document.createElement("div");
      el.className = "vd-item";

      let zoneColor = this.config.colors.zoneDefault;
      if (!d.zone || d.zone !== d.zoneparent) {
        zoneColor = this.config.colors.zoneHilighted;
      }

      const statusClass = d.error ? "vd-status-dot vd-error" : "vd-status-dot";

      el.style.borderRightColor = zoneColor;
      el.style.width = this.config.baseWidth + "px"; // Init width

      el.innerHTML = `
                        <div class="vd-line-primary">
                            <span class="vd-item-key">${d.key}</span>
                            <div style="flex-grow:1"></div>
                            <span class="vd-item-value">${
                              d.value || "--"
                            }</span>
                            <div class="${statusClass}"></div>
                        </div>

                        <div class="vd-line-ext">
                          <span class="vd-item-tag">${d.tag || "NOTAG"}</span>
                          <span class="vd-item-zone" style="color: ${zoneColor}">${
        d.zone
      }</span>
                        </div>

                        <div class="vd-line-secondary">
                          ${d.description || "NOLABEL"}
                        </div>
                    `;

      el.onmousedown = (e) => this._handleItemMouseDown(e, d, index, zoneColor);
      el.onmouseenter = () => {
        this.state.hoveredItem = d;
      };

      this.dom.content.appendChild(el);

      this.itemElements.push({
        el,
        key: d.key,
        index,
        color: zoneColor,
        currentW: this.config.baseWidth,
        currentShift: 0,
      });

      this.updateValue(d.key);
    });

    this._updateSelectionVisuals();

    /*
    this.dom.content.style.height = `${
      this.state.filteredData.length * this.config.itemHeight
    }px`;
    */

    // Appel immédiat pour dimensionner correctement dès le rendu
    this._updateGenieEffect();
  }

  _toggleSelection(key) {
    if (this.state.selectedIds.has(key)) this.state.selectedIds.delete(key);
    else this.state.selectedIds.add(key);
    this._updateSelectionVisuals();
  }

  _clearSelection() {
    this.state.selectedIds.clear();
    this._updateSelectionVisuals();
  }

  _updateSelectionVisuals() {
    this.itemElements.forEach((item) => {
      if (this.state.selectedIds.has(item.key)) {
        item.el.classList.add("vd-selected");
      } else {
        item.el.classList.remove("vd-selected");
      }
    });
  }

  _updateDimensions() {
    const rect = this.dom.viewport.getBoundingClientRect();
    this.state.viewHeight = rect.height;
    const centerOffset = this.state.viewHeight / 2;
    const pad = centerOffset - this.config.itemHeight / 2;
    this.dom.content.style.paddingTop = `${pad}px`;
    this.dom.content.style.paddingBottom = `${pad}px`;
  }

  _loop() {
    this._updatePhysics();
    this._updateGenieEffect();
    this.state.animationFrameId = requestAnimationFrame(() => this._loop());
  }

  _updatePhysics() {
    /*
    const diff = this.state.targetScrollTop - this.state.scrollTop;
    this.state.scrollVelocity += diff * 0.1;
    this.state.scrollVelocity *= 0.85;
    this.state.scrollTop += this.state.scrollVelocity;
    */
    this.state.scrollTop = this.state.targetScrollTop;

    const offset = this.state.viewHeight / 2 - this.config.itemHeight / 2;
    this.dom.content.style.transform = `translateY(${
      -this.state.scrollTop + offset
    }px)`;
  }

  _updateGenieEffect() {
    if (!this.state.isVisible) return;

    const focusY = this.state.scrollTop;

    const startIdx = Math.max(
      0,
      Math.floor((focusY - this.state.viewHeight) / this.config.itemHeight)
    );
    const endIdx = Math.min(
      this.itemElements.length,
      Math.ceil((focusY + this.state.viewHeight) / this.config.itemHeight)
    );

    let closestDist = Infinity;
    let closestIndex = -1;

    const lerp = (start, end, t) => start * (1 - t) + end * t;

    for (let i = startIdx; i < endIdx; i++) {
      const item = this.itemElements[i];
      const itemY = i * this.config.itemHeight;
      const dist = Math.abs(itemY - focusY);

      if (dist < closestDist) {
        closestDist = dist;
        closestIndex = i;
      }

      let factor = 0;
      if (this.state.mouseY > -100) {
        const rect = item.el.getBoundingClientRect();
        const centerY = rect.top + rect.height / 2;
        const mDist = Math.abs(this.state.mouseY - centerY);
        if (mDist < this.config.spread) {
          const x = mDist / this.config.spread;
          factor = Math.pow(Math.cos((x * Math.PI) / 2), 3);
        }
      }

      const targetW =
        this.config.baseWidth +
        (this.config.maxWidth - this.config.baseWidth) * factor;

      // Lissage
      item.currentW = lerp(item.currentW, targetW, 0.15);
      item.el.style.width = `${item.currentW}px`;

      // Active State
      if (factor > 0.9) {
        item.el.classList.add("vd-active");
      } else {
        item.el.classList.remove("vd-active");
      }
    }

    this.state.activeItemIndex = closestIndex;
  }

  _handleWheel(e) {
    e.preventDefault();
    this.state.targetScrollTop += e.deltaY;

    const max = (this.state.filteredData.length - 1) * this.config.itemHeight;
    if (this.state.targetScrollTop < 0) this.state.targetScrollTop = 0;
    if (this.state.targetScrollTop > max) this.state.targetScrollTop = max;

    /*
    if (this.state.scrollSnapTimeout)
      clearTimeout(this.state.scrollSnapTimeout);
    this.state.scrollSnapTimeout = setTimeout(() => {
      const snapIdx = Math.round(
        this.state.targetScrollTop / this.config.itemHeight
      );
      this.state.targetScrollTop = snapIdx * this.config.itemHeight - this.config.itemHeight / 2;
    }, 100);
    */
  }

  _handleGlobalMouseMove(e) {
    if (this.state.isDragging) {
      this._updateDrag(e);
      return;
    }
    const rect = this.dom.panel.getBoundingClientRect();
    if (e.clientX >= rect.left) {
      this.state.mouseY = e.clientY;
    } else {
      this.state.mouseY = -1000;
    }
  }

  _handleItemMouseDown(e, data, index, color) {
    if (e.button !== 0) return;

    this.state.isDragging = false;
    this.state.draggedItems = [data];

    // Gestion Drag Multiselect : si on clique sur un sélectionné, on prend tout le groupe
    // MAIS on ne prend que les visibles (filtrés)
    if (this.state.selectedIds.has(data.key)) {
      this.state.draggedItems = [];
      this.state.selectedIds.forEach((key) => {
        const item = this.state.filteredData.find((d) => d.key === key);
        if (item) this.state.draggedItems.push(item);
      });
      // Sécurité: si le groupe est vide (tout filtré), on prend juste l'item cliqué
      if (this.state.draggedItems.length === 0)
        this.state.draggedItems = [data];
    }

    this.state.dragStartX = e.clientX;
    this.state.dragStartY = e.clientY;
    this.state.dragColor = color;

    const onMove = (mv) => {
      const d = Math.hypot(
        mv.clientX - this.state.dragStartX,
        mv.clientY - this.state.dragStartY
      );
      if (d > 5 && !this.state.isDragging) {
        this._startDrag();
      }
    };

    const onUp = () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);

      if (!this.state.isDragging) {
        if (this.state.hoveredItem) {
          this._toggleSelection(this.state.hoveredItem.key);
        }
      }
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  }

  _startDrag() {
    this.state.isDragging = true;
    this.dom.panel.classList.add("vd-hidden-drag");

    const count = this.state.draggedItems.length;
    this.dom.ghost.textContent =
      count > 1 ? `${count} VARIABLES` : this.state.draggedItems[0].key;
    this.dom.ghost.style.display = "block";
    this.dom.ghost.style.borderColor = this.state.dragColor;
  }

  _updateDrag(e) {
    this.dom.ghost.style.left = e.clientX + "px";
    this.dom.ghost.style.top = e.clientY + "px";
  }

  _endDrag(e) {
    if (!this.state.isDragging) return;

    this.state.isDragging = false;
    this.dom.panel.classList.remove("vd-hidden-drag");
    this.dom.ghost.style.display = "none";

    if (this.onDrop) {
      const keys = this.state.draggedItems.map((i) => i.key);
      this.onDrop(keys, e.clientX, e.clientY);

      // Reset selection après drop
      this._clearSelection();
    }
    this.state.draggedItems = [];
  }
}

const app = {
  canvas: null,
  ctx: null,
  pollingInterval: null,
  config: {
    colors: {
      zoneViewOkFill: "rgba(34, 197, 94, 0.4)",
      //zoneViewOkStroke: "rgba(32, 220, 32, 1)",
      zoneViewOkStroke: "rgba(220, 220, 220, 1)",
      zoneViewErrorFill: "rgba(239, 68, 68, 0.5)",
      //zoneViewErrorStroke: "rgba(220, 32, 32, 1)",
      zoneViewErrorStroke: "rgba(220, 220, 220, 1)",
      zoneViewAltFill: "rgba(100, 116, 139, 0.6)",
      zoneViewAltStroke: "rgba(255, 255, 255, 0.9)",
      zoneActiveFill: "rgba(59, 130, 246, 0.5)",
      zoneActiveStroke: "rgba(37, 99, 235, 1)",
      zoneInactiveFill: "rgba(34, 197, 94, 0.5)",
      //zoneInactiveStroke: "rgba(22, 163, 74, 1)",     
      zoneInactiveStroke: "rgba(255, 255, 255, 0.9)",
      zoneHilightedStroke: "rgba(0, 255, 0)",      
      zoneHilightedFill: "rgba(0, 255, 0, 0.5)",      

      vertexFill: "rgba(255, 255, 255, 1)",
      vertexStroke: "rgba(37, 99, 235, 1)",
      snapHighlight: "rgba(16, 185, 129, 1)",
      labelFill: "rgba(30, 41, 59, 0.6)",
      deviceLabelFill: "rgba(208, 215, 14, 0.8)",
      deviceLabelSelectedFill: "rgba(55, 107, 220, 0.85)",
      deviceLabelNoZoneFill: "rgba(251, 139, 139, 0.85)",
      deviceDotFill: "rgba(208, 215, 14, 1)",
      deviceDotTagFill: "rgba(236, 100, 16, 1)",
      deviceDotSelectedFill: "rgba(37, 99, 235, 1)",
      deviceDotTagErrorFill: "rgba(220, 38, 38, 1)",
      deviceDotStroke: "rgba(255, 255, 255, 1)",
      deviceTextSelected: "rgba(255, 255, 255, 1)",
      deviceText: "rgba(32, 32, 32, 1)",
      valueFill: "rgba(75, 85, 99, 0.9)",
      valueStroke: "rgba(255,255,255,0.5)",
      valueSelectedFill: "rgba(59, 130, 246, 0.4)",
      valueSelectedStroke: "rgba(37, 99, 235, 1)",
      valueErrorFill: "rgba(220, 38, 38, 0.9)",
      valueText: "rgba(255, 255, 255, 1)",
      selboxStroke: "rgba(244, 224, 10, 1.9)",
      selboxFill: "rgba(244, 224, 10, 0.25)",
      floorplanBoxStroke: "#e5f50bff",
      floorplanHandleFill: "#e5f50bff",
    },

    apiBaseUrl: "http://{interface}:{port}/api/v1",
    apiKeyZones: "zones",
    apiKeyFloors: "floorplan",
    apiKeyValues: "values",
    apiKeyDevices: "devices",
    vertexRadius: 5,
    hitTolerance: 10,
    snapDistance: 10,
    maxHistory: 20,
  },

  state: {
    mode: "view",
    action: "idle",
    view: { x: 0, y: 0, scale: 1, rotation: 0 },
    floors: [],
    activeFloorId: null,
    saveDataPending: false,
    zones: [],
    selectedZoneIds: [],
    availableZoneNames: [],
    zoneStatusMap: {},
    values: [],
    selectedValueIds: [],
    availableValueKeys: [],
    valuesByKey: {},
    valuesDataCache: {},
    allValuesData: [],
    devices: [],
    selectedDeviceIds: [],
    availableDeviceKeys: [],
    allDevicesData: [],
    devicesDataCache: {},
    dockVariables: null,
    history: [],
    future: [],
    hoveredVertexIndex: -1,
    draggingVertexIndex: -1,
    isSpacePressed: false,
    coupledVertices: [],
    snappedPoint: null,
    lastMouse: { x: 0, y: 0 },
    lastMousePrevious: { x: 0, y: 0 },
    clickStartMouse: { x: 0, y: 0 },
    dragOffset: { x: 0, y: 0 },
    startDragBg: null,
    hoveredCropEdge: null,
    draggingCropEdge: null,
    editingValueId: null,
    visibleModalKeys: [],
    selectionStart: null,
    selectionEnd: null,
    searchQuery: "",
  },

  init: function () {
    this.canvas = document.getElementById("mainCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.resize();
    window.addEventListener("resize", () => this.resize());
    this.setupEvents();
    this.setupPanelDrag();
    this.setStatus("view", "Chargement...");
    Promise.all([
      this.loadZones(),
      this.loadFloors(),
      this.loadValues(),
      this.loadDevices(),
    ]).then((results) => {
      const floorsLoaded = results[1];
      if (!floorsLoaded || this.state.floors.length === 0) {
        this.createDefaultFloor();
        this.setMode("background");
        this.showToast("Bienvenue. Configurez le plan de fond.");
      } else {
        if (!this.state.activeFloorId && this.state.floors.length > 0)
          this.state.activeFloorId = this.state.floors[0].id;
        const active = this.getActiveFloor();
        if (active && active.imgData) this.loadBackgroundImage(active.imgData);
        this.setMode("view");
      }
      this.updateFloorSelectorUI();
      this.fetchAvailableMetadata();
      this.saveState();
      this.startPolling();
    });
    requestAnimationFrame(() => this.loop());
  },

  // --- HELPERS ---
  resize: function () {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.render();
  },

  setStatus: function (mode, text) {
    const el = document.getElementById("status-text");
    if (el)
      /*
      el.textContent = `${
        mode === "view" ? "VUE" : mode === "background" ? "FOND" : "ÉDITION"
      } : ${text}`;
      */
      el.textContent = `${text}`;
  },

  setupPanelDrag: function () {
    const panel = document.getElementById("prop-panel");
    const header = document.getElementById("prop-header");
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;
    header.addEventListener("mousedown", (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      const rect = panel.getBoundingClientRect();
      panel.style.right = "auto";
      panel.style.left = rect.left + "px";
      panel.style.top = rect.top + "px";
      initialLeft = rect.left;
      initialTop = rect.top;
    });
    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      e.preventDefault();
      panel.style.left = initialLeft + e.clientX - startX + "px";
      panel.style.top = initialTop + e.clientY - startY + "px";
    });
    window.addEventListener("mouseup", () => {
      isDragging = false;
    });
  },

  getActiveFloor: function () {
    return this.state.floors.find((f) => f.id === this.state.activeFloorId);
  },

  onUpdateSelectedZones: function () {
    const container = document.getElementById("missing-zones-container");
    if (container) {
      if (this.state.selectedZoneIds.length) container.classList.add("hidden");
      else container.classList.remove("hidden");
    }
  },

  onUpdateSelectedDevicesValues: function(values) {
    if (this.isMode("edit-devices") && values.length>0) {
      if (this.state.selectedDeviceIds.length>0) {
          console.log("onUpdateSelectedDevicesValues()");
          this.state.dockVariables.updateData(values);
          this.state.dockVariables.filter(this.state.searchQuery);
        }
    }
    else {
      this.state.resetData();
    }
  },

  onDropVariables: function(keys, x, y) {
    const worldPos = this.screenToWorld(x, y);
    const zone=this.getZoneAt(worldPos);

    if (zone) {
      this.saveValuesZones(keys, zone.name);
    }
  },

  onResetVariablesZone : function(keys) {
      this.saveValuesZones(keys, null);
  },

  onUpdateSelectedDevices: function () {
    console.log("onUpdateSelectedDevices()");
    const container = document.getElementById("missing-devices-container");
    if (container) {
      if (this.state.selectedDeviceIds.length > 0) {
        container.classList.add("hidden");
        if (!this.state.dockVariables) {
          this.state.dockVariables = new VariableDockComponent(document.body, {
            onDrop: (keys, x, y) => this.onDropVariables(keys, x, y),
            onDeleteAssignment: (keys) => this.onResetVariablesZone(keys)
          });
        }

        this.state.dockVariables.hidePanel();
        this.state.dockVariables.resetData();
        //this.state.dockVariables.showPanel();
        this.pollSelectedDevicesValues();
      } else {
        container.classList.remove("hidden");
        if (this.state.dockVariables) {
          this.state.dockVariables.hidePanel();
        }
      }
    }
  },

  // --- RENDER ---
  render: function () {
    const ctx = this.ctx;
    const canvas = this.canvas;
    const v = this.state.view;
    const search = this.state.searchQuery.toLowerCase();

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.translate(v.x, v.y);
    ctx.rotate((v.rotation * Math.PI) / 180);
    ctx.scale(v.scale, v.scale);

    const worldPos = this.screenToWorld(
      this.state.lastMouse.x,
      this.state.lastMouse.y
    );
    const hoveredDevice = this.getDeviceAt(worldPos);

    // Floor
    const floor = this.getActiveFloor();
    if (floor) {
      const useProcessed =
        (floor.invert ||
          floor.removeBg ||
          floor.cropTop > 0 ||
          floor.cropBottom > 0 ||
          floor.cropLeft > 0 ||
          floor.cropRight > 0) &&
        floor.processedCanvas;
      const img = useProcessed ? floor.processedCanvas : floor.img;
      if (floor.isLoaded && img) {
        ctx.save();
        ctx.globalAlpha = floor.opacity;
        ctx.translate(floor.x, floor.y);
        ctx.scale(floor.scale, floor.scale);
        ctx.rotate((floor.rotation * Math.PI) / 180);
        const w = img.width;
        const h = img.height;
        ctx.drawImage(img, -w / 2, -h / 2);
        if (this.state.mode === "background") {
          ctx.strokeStyle = this.config.colors.floorplanBoxStroke;
          ctx.lineWidth = 2 / floor.scale;
          ctx.setLineDash([5, 5]);
          ctx.strokeRect(-w / 2, -h / 2, w, h);
          ctx.setLineDash([]);
          ctx.fillStyle = this.config.colors.floorplanHandleFill;
          const s = 8 / floor.scale;
          ctx.fillRect(-s / 2, -h / 2 - s / 2, s, s);
          ctx.fillRect(-s / 2, h / 2 - s / 2, s, s);
          ctx.fillRect(-w / 2 - s / 2, -s / 2, s, s);
          ctx.fillRect(w / 2 - s / 2, -s / 2, s, s);
        }
        ctx.restore();
      }
    }

    // Zones
    this.state.zones
      .filter((z) => z.floorId === this.state.activeFloorId)
      .forEach((z) => {
        const sel = this.state.selectedZoneIds.includes(z.id);

        let fill, stroke;
        if (this.state.mode === "view") {
          const status = this.getZonePollStatus(z.name);
          const error = status && status.error;

          if (error === true) {
            fill = this.config.colors.zoneViewErrorFill;
            stroke = this.config.colors.zoneViewErrorStroke;
          } else if (error === false) {
            fill = this.config.colors.zoneViewOkFill;
            stroke = this.config.colors.zoneViewOkStroke;
          } else {
            fill = this.config.colors.zoneViewAltFill;
            stroke = this.config.colors.zoneViewAltStroke;
          }
        } else if (
          this.state.mode === "background" ||
          this.state.mode === "edit-devices"
        ) {
          fill = this.config.colors.zoneViewAltFill;
          stroke = this.config.colors.zoneViewAltStroke;

          if (this.state.dockVariables && this.state.dockVariables.isZoneInVariables(z.name)) {
            stroke = this.config.colors.zoneHilightedStroke;        
            fill = this.config.colors.zoneHilightedFill;        
          }
        } else {
          fill = sel
            ? this.config.colors.zoneActiveFill
            : this.config.colors.zoneInactiveFill;
          stroke = sel
            ? this.config.colors.zoneActiveStroke
            : this.config.colors.zoneInactiveStroke;
        }

        ctx.beginPath();
        if (z.points.length > 0) {
          ctx.moveTo(z.points[0].x, z.points[0].y);
          for (let i = 1; i < z.points.length; i++)
            ctx.lineTo(z.points[i].x, z.points[i].y);
        }
        ctx.closePath();
        ctx.fillStyle = fill;
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 2 / v.scale;
        ctx.fill();
        ctx.stroke();

        if (z.name) {
          const c = this.getCentroid(z.points);
          ctx.font = `bold ${14 / v.scale}px Arial`;
          const m = ctx.measureText(z.name);
          const w = m.width;
          const h = 12 / v.scale;
          const p = 6 / v.scale;
          ctx.fillStyle = this.config.colors.labelFill;
          ctx.beginPath();
          ctx.roundRect(
            c.x - w / 2 - p,
            c.y - h / 2 - p,
            w + p * 2,
            h + p * 2,
            4 / v.scale
          );
          ctx.fill();
          ctx.fillStyle = "#ffffff";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(z.name, c.x, c.y);
        }
        if (sel && this.state.mode === "edit-zones") {
          const r = this.config.vertexRadius / v.scale;
          z.points.forEach((p, idx) => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
            ctx.fillStyle =
              this.state.hoveredVertexIndex === idx
                ? "#bfdbfe"
                : this.config.colors.vertexFill;
            ctx.strokeStyle = this.config.colors.vertexStroke;
            ctx.lineWidth = 2 / v.scale;
            ctx.fill();
            ctx.stroke();
          });
        }
      });

    // Devices
    if (
      this.state.mode === "edit-devices" ||
      this.state.mode === "edit-zones" ||
      this.state.mode === "background" ||
      this.state.mode === "view"
    ) {
      this.state.devices
        .filter((d) => d.floorId === this.state.activeFloorId)
        .forEach((device) => {
          if (search) {
            if (!device.key.includes(search)) return;
          }

          const sel = this.state.selectedDeviceIds.includes(device.id);
          const hovered = hoveredDevice && device.id == hoveredDevice.id;
          const status = this.getDevicePollStatus(device.key);
          const error = status && status.error;

          let txt = device.key;
          if (hovered) {
            if (status) {
              txt += " (";
              txt += status.model ? status.model : status.class;
              if (status.version) txt += " v" + status.version;
              txt += ")";
            }
          } else {
            if (status) {
              txt += " (";
              txt += status.model;
              txt += ")";
            }
          }

          const fs = 12 / v.scale;
          const lh = fs * 1.2;
          const p = 6 / v.scale;
          ctx.font = `${fs}px monospace`;
          const m = ctx.measureText(txt);
          let tw = m.width;
          let th = fs;

          const idM = ctx.measureText(txt);
          tw = Math.max(tw, idM.width);
          th = fs * 2.2;

          let bg = this.config.colors.deviceLabelFill;
          if (!device.zone) bg = this.config.colors.deviceLabelNoZoneFill;
          if (sel) bg = this.config.colors.deviceLabelSelectedFill;

          if (sel) ctx.strokeStyle = this.config.colors.deviceTextSelected;
          else ctx.strokeStyle = this.config.colors.deviceText;
          ctx.lineWidth = 1 / v.scale;

          const h = 8;
          const hmargin = 4;

          if (this.state.mode === "edit-devices" || hovered || search) {
            ctx.fillStyle = bg;
            ctx.beginPath();
            ctx.rect(device.x, device.y - h, tw + hmargin * 2 + h, 2 * h);
            ctx.fill();

            if (sel) ctx.fillStyle = this.config.colors.deviceTextSelected;
            else {
              ctx.fillStyle = this.config.colors.deviceText;
            }
            ctx.textAlign = "left";
            ctx.textBaseline = "middle";
            ctx.font = `${fs}px monospace`;
            ctx.fillText(txt, device.x + h + hmargin, device.y);
          }

          bg = this.config.colors.deviceDotFill;
          if (sel) bg = this.config.colors.deviceDotSelectedFill;
          ctx.fillStyle = bg;
          ctx.strokeStyle = this.config.colors.deviceDotStroke;

          ctx.beginPath();
          ctx.arc(device.x, device.y, h * 1.1, 0, Math.PI * 2, false);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = this.config.colors.deviceDotTagFill;
          if (error) ctx.fillStyle = this.config.colors.deviceDotTagErrorFill;
          ctx.strokeStyle = ctx.fillStyle;
          ctx.beginPath();
          ctx.arc(device.x, device.y, h * 0.7, 0, Math.PI * 2, false);
          ctx.fill();
          ctx.stroke();
        });
    }

    // Values
    if (this.state.mode === "edit-zones" || this.state.mode === "view") {
      this.state.values
        .filter((v) => v.floorId === this.state.activeFloorId)
        .forEach((val) => {
          if (search) {
            if (!val.key.includes(search)) return;
          }
          const sel = this.state.selectedValueIds.includes(val.id);
          const data = this.state.valuesDataCache[val.key] || {
            valuestr: "---",
            error: false,
          };
          let txt = data.valuestr;
          if (this.state.mode === "edit-zones" && !val.key) txt = "No Key";

          const hasId = !!val.identifier;
          const fs = 12 / v.scale;
          const lh = fs * 1.2;
          const p = 6 / v.scale;
          ctx.font = `bold ${fs}px monospace`;
          const m = ctx.measureText(txt);
          let tw = m.width;
          let th = fs;

          if (hasId) {
            const idM = ctx.measureText(val.identifier);
            tw = Math.max(tw, idM.width);
            th = fs * 2.2;
          }

          let bg = this.config.colors.valueFill;
          if (data.error) bg = this.config.colors.valueErrorFill;
          if (sel && this.state.mode === "edit-zones")
            bg = this.config.colors.valueSelectedFill;

          ctx.fillStyle = bg;
          ctx.beginPath();
          ctx.roundRect(
            val.x - tw / 2 - p,
            val.y - th / 2 - p,
            tw + p * 2,
            th + p * 2,
            4 / v.scale
          );
          ctx.fill();

          if (this.state.mode === "edit-zones") {
            ctx.strokeStyle = sel
              ? this.config.colors.valueSelectedStroke
              : this.config.colors.valueStroke;
            ctx.lineWidth = 1 / v.scale;
            ctx.stroke();
          }

          ctx.fillStyle = this.config.colors.valueText;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          if (hasId) {
            ctx.fillText(val.identifier, val.x, val.y - lh / 2);
            ctx.font = `${fs}px monospace`;
            ctx.fillText(txt, val.x, val.y + lh / 2);
          } else {
            ctx.fillText(txt, val.x, val.y);
          }
        });
    }

    if (this.state.snappedPoint) {
      const p = this.state.snappedPoint;
      const r = (this.config.vertexRadius + 4) / v.scale;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.strokeStyle = this.config.colors.snapHighlight;
      ctx.lineWidth = 3 / v.scale;
      ctx.stroke();
    }

    // Box Selection
    if (
      this.state.action === "selecting_box" &&
      this.state.selectionStart &&
      this.state.selectionEnd
    ) {
      const r = this.getBoxFromPoints(
        this.state.selectionStart,
        this.state.selectionEnd
      );
      ctx.fillStyle = this.config.colors.selboxFill;
      ctx.strokeStyle = this.config.colors.selboxStroke;
      ctx.lineWidth = 1 / v.scale;
      ctx.beginPath();
      ctx.roundRect(r.x, r.y, r.w, r.h, 3);
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  },

  // --- DATA ---

  mapDevicesToZones: function () {
    this.state.devices.forEach((device) => {
      const pt = { x: device.x, y: device.y };
      const zone = this.getZoneAt(pt, device.floorId);

      device.zone = null;
      if (zone) {
        if (zone.floorId == device.floorId) device.zone = zone.name;
      }
    });
  },

  mapZones: function () {
    this.mapDevicesToZones();
  },

  signalDataChange: function () {
    //console.log("Signal DATA change!");
    this.state.saveDataPending = true;
    const btnSave = document.getElementById("btn-save");
    if (btnSave && this.state.mode != "view")
      btnSave.classList.remove("opacity-50", "cursor-not-allowed");
  },

  saveData: function (force) {
    if (this.state.mode === "view") {
      this.showToast("Sauvegarde impossible en mode Vue", true);
      return;
    }

    if (force || this.state.saveDataPending) {
      this.saveZones();
      this.saveFloors();
      this.saveValues();
      this.saveDevices();
      this.state.saveDataPending = false;

      fetch(`${this.config.apiBaseUrl}/save`).catch(() => {});

      const btnSave = document.getElementById("btn-save");
      if (btnSave) btnSave.classList.add("opacity-50", "cursor-not-allowed");
    }

    this.showToast("Sauvegarde Complète");
  },
  saveZones: function () {
    const p = { zones: this.state.zones };
    fetch(
      `${this.config.apiBaseUrl}/storeuserdata?key=${this.config.apiKeyZones}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
      }
    ).catch(() =>
      localStorage.setItem(this.config.apiKeyZones, JSON.stringify(p))
    );
  },
  saveFloors: function () {
    const p = {
      floors: this.state.floors,
      activeFloorId: this.state.activeFloorId,
    };
    fetch(
      `${this.config.apiBaseUrl}/storeuserdata?key=${this.config.apiKeyFloors}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
      }
    ).catch(() =>
      localStorage.setItem(this.config.apiKeyFloors, JSON.stringify(p))
    );
  },
  saveValues: function () {
    const p = { values: this.state.values };
    fetch(
      `${this.config.apiBaseUrl}/storeuserdata?key=${this.config.apiKeyValues}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
      }
    ).catch(() =>
      localStorage.setItem(this.config.apiKeyValues, JSON.stringify(p))
    );
  },

  saveValuesZones: function(keys, zone) {
    let data = {};
    keys.forEach((k) => {
      data[k]=zone;
    });

    //console.log(data);

    fetch(`${this.config.apiBaseUrl}/setzone`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    .then(()=>{
      this.pollSelectedDevicesValues();
    })
    .catch(() => {})
  },

  saveDevicesZones: function () {
    this.mapDevicesToZones();

    let data = {};
    this.state.devices.forEach((device) => {
      data[device.key] = device.zone ? device.zone : null;
    });

    //console.log(data);

    fetch(`${this.config.apiBaseUrl}/setzone`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    .then(()=>{
      this.pollSelectedDevicesValues();
    })
    .catch(() => {})
  },

  saveDevices: function () {
    const p = { devices: this.state.devices };
    fetch(
      `${this.config.apiBaseUrl}/storeuserdata?key=${this.config.apiKeyDevices}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
      }
    ).catch(() =>
      localStorage.setItem(this.config.apiKeyDevices, JSON.stringify(p))
    );

    this.saveDevicesZones();
  },

  loadZones: function () {
    return fetch(
      `${this.config.apiBaseUrl}/getuserdata?key=${this.config.apiKeyZones}`
    )
      .then((r) => r.json())
      .then((d) => {
        if (d && d.zones) {
          this.state.zones = d.zones;
          return true;
        }
        return false;
      })
      .catch(() => {
        const l = localStorage.getItem(this.config.apiKeyZones);
        if (l) {
          this.state.zones = JSON.parse(l).zones;
          return true;
        }
        return false;
      });
  },

  loadFloors: function () {
    return fetch(
      `${this.config.apiBaseUrl}/getuserdata?key=${this.config.apiKeyFloors}`
    )
      .then((r) => r.json())
      .then((d) => {
        if (d && d.floors) {
          //this.state.floors = d.floors;
          // SANITIZE: Reset image objects to avoid "drawImage called on non-object" error
          this.state.floors = d.floors.map((f) => ({
            ...f,
            img: null,
            processedCanvas: null,
            isLoaded: false,
          }));
          this.state.activeFloorId = d.activeFloorId;
          return true;
        }
        return false;
      })
      .catch(() => {
        const l = localStorage.getItem(this.config.apiKeyFloors);
        if (l) {
          const d = JSON.parse(l);
          // SANITIZE: Reset image objects to avoid "drawImage called on non-object" error
          this.state.floors = d.floors.map((f) => ({
            ...f,
            img: null,
            processedCanvas: null,
            isLoaded: false,
          }));
          this.state.activeFloorId = d.activeFloorId;
          return true;
        }
        return false;
      });
  },

  loadValues: function () {
    return fetch(
      `${this.config.apiBaseUrl}/getuserdata?key=${this.config.apiKeyValues}`
    )
      .then((r) => r.json())
      .then((d) => {
        if (d && d.values) {
          this.state.values = d.values;
          return true;
        }
        return false;
      })
      .catch(() => {
        const l = localStorage.getItem(this.config.apiKeyValues);
        if (l) {
          this.state.values = JSON.parse(l).values;
          return true;
        }
        return false;
      });
  },

  loadDevices: function () {
    return fetch(
      `${this.config.apiBaseUrl}/getuserdata?key=${this.config.apiKeyDevices}`
    )
      .then((r) => r.json())
      .then((d) => {
        if (d && d.devices) {
          this.state.devices = d.devices;
          return true;
        }
        return false;
      })
      .catch(() => {
        const l = localStorage.getItem(this.config.apiKeyDevices);
        if (l) {
          this.state.devices = JSON.parse(l).devices;
          return true;
        }
        return false;
      });
  },

  fetchAvailableMetadata: function () {
    fetch(`${this.config.apiBaseUrl}/getzones`)
      .then((r) => r.json())
      .then((d) => {
        if (d.data) this.state.availableZoneNames = d.data.map((i) => i.zone);
      })
      .catch(() => {});

    fetch(`${this.config.apiBaseUrl}/getalldevices`)
      .then((r) => r.json())
      .then((d) => {
        if (d.data) {
          this.state.allDevicesData = d.data;
          this.state.availableDeviceKeys = d.data.map((i) => i.key || i);
          d.data.forEach((d) => {
            if (d.key) this.state.devicesDataCache[d.key] = d;
          });
        }
      })
      .catch(() => {});

    fetch(`${this.config.apiBaseUrl}/getvalues`)
      .then((r) => r.json())
      .then((d) => {
        if (d.data) {
          this.state.allValuesData = d.data;
          this.state.availableValueKeys = d.data.map((i) => i.key || i);
          this.state.valuesByKey[i.key] = d.data;
        }
      })
      .catch(() => {});
  },

  startPolling: function () {
    if (this.pollingInterval) return;
    this.pollData();
    this.pollingInterval = setInterval(() => this.pollData(), 5000);
  },

  stopPolling: function () {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  },

  pollZones: function () {
    fetch(`${this.config.apiBaseUrl}/getzones`)
      .then((r) => r.json())
      .then((d) => {
        if (d.data) {
          this.state.zoneStatusMap = {};
          d.data.forEach((i) => {
            if (i.zone) this.state.zoneStatusMap[i.zone.toLowerCase()] = i;
          });
        }
      })
      .catch(() => {});
  },

  pollDevices: function () {
    fetch(`${this.config.apiBaseUrl}/getalldevices`)
      .then((r) => r.json())
      .then((d) => {
        if (d.data) {
          this.state.deviceStatusMap = {};
          d.data.forEach((i) => {
            if (i.key) this.state.deviceStatusMap[i.key.toLowerCase()] = i;
          });
        }
      })
      .catch(() => {});
  },

  pollValues: function () {
    const pk = this.state.values
      .filter((v) => v.floorId === this.state.activeFloorId && v.key)
      .map((v) => v.key);

    const mk = !document
      .getElementById("value-selector-modal")
      .classList.contains("hidden")
      ? this.state.visibleModalKeys
      : [];

    const uk = [...new Set([...pk, ...mk])];
    if (uk.length > 0) {
      const p = uk.join(",");
      fetch(`${this.config.apiBaseUrl}/getvalues?key=${encodeURIComponent(p)}`)
        .then((r) => r.json())
        .then((d) => {
          if (d.data) {
            d.data.forEach((v) => {
              if (v.key)
                this.state.valuesDataCache[v.key] = {
                  valuestr: v.valuestr,
                  error: v.error,
                };
            });
            if (mk.length > 0) this.updateValuesTableRows();
            this.render();
          }
        })
        .catch(() => {});
    }
  },

  pollSelectedDevicesValues: function () {
    let keys = [];
    this.state.devices
      .filter((d) => this.state.selectedDeviceIds.includes(d.id))
      .forEach((d) => {
        keys.push(d.key);
      });

    if (keys.length > 0) {
      const p = keys.join(",");
      fetch(
        `${this.config.apiBaseUrl}/getdevicevalues?device=${encodeURIComponent(p)}`
      )
        .then((r) => r.json())
        .then((d) => {
          if (d.data) {
            this.onUpdateSelectedDevicesValues(d.data);
          }
        })
        .catch(() => {});
    }
  },

  pollData: function () {
    this.pollZones();
    this.pollDevices();
    this.pollValues();
    this.pollSelectedDevicesValues();

    /*
    if (this.state.mode === "edit-zones") 
      this.updateMissingZonesUI();
    */

    this.render();
  },

  showToast: function (msg) {
    const t = document.getElementById("status-text");
    t.textContent = msg;
    setTimeout(() => (t.textContent = "Prêt"), 3000);
  },

  getZonePollStatus(name) {
    if (name && this.state.zoneStatusMap) {
      name = name.toLowerCase();
      if (this.state.zoneStatusMap.hasOwnProperty(name))
        return this.state.zoneStatusMap[name];
    }
    return null;
  },
  getDevicePollStatus(key) {
    if (key && this.state.deviceStatusMap) {
      key = key.toLowerCase();
      if (this.state.deviceStatusMap.hasOwnProperty(key))
        return this.state.deviceStatusMap[key];
    }
    return null;
  },

  // --- FLOOR MGMT ---
  createDefaultFloor: function () {
    const newFloor = {
      id: "floor_" + Date.now(),
      name: "Plan Principal",
      img: null,
      imgData: null,
      isLoaded: false,
      x: 0,
      y: 0,
      scale: 1,
      opacity: 0.5,
      rotation: 0,
      invert: false,
      removeBg: false,
      cropTop: 0,
      cropBottom: 0,
      cropLeft: 0,
      cropRight: 0,
    };
    this.state.floors.push(newFloor);
    this.state.activeFloorId = newFloor.id;
    this.signalDataChange();
  },
  addFloor: function () {
    this.saveState();
    const newFloor = {
      id: "floor_" + Date.now(),
      name: "Nouveau Plan",
      img: null,
      imgData: null,
      isLoaded: false,
      x: 0,
      y: 0,
      scale: 1,
      opacity: 0.5,
      rotation: 0,
      invert: false,
      removeBg: false,
      cropTop: 0,
      cropBottom: 0,
      cropLeft: 0,
      cropRight: 0,
    };
    this.state.floors.push(newFloor);
    this.switchFloor(newFloor.id);
    this.signalDataChange();
    this.setStatus("background", "Nouveau plan créé");
  },
  deleteCurrentFloor: function () {
    if (this.state.floors.length <= 1) {
      this.showToast("Impossible de supprimer le dernier plan", true);
      return;
    }
    if (!confirm("Supprimer ce plan et toutes ses zones ?")) return;
    this.saveState();
    this.state.zones = this.state.zones.filter(
      (z) => z.floorId !== this.state.activeFloorId
    );
    this.state.values = this.state.values.filter(
      (v) => v.floorId !== this.state.activeFloorId
    );
    this.state.devices = this.state.devices.filter(
      (f) => f.id !== this.state.activeFloorId
    );
    this.state.floors = this.state.floors.filter(
      (f) => f.id !== this.state.activeFloorId
    );
    let nextIndex = Math.min(0, this.state.floors.length - 1);
    this.switchFloor(this.state.floors[nextIndex].id);
    this.signalDataChange();
    this.setStatus("background", "Plan supprimé");
  },

  switchFloor: function (floorId) {
    this.state.activeFloorId = floorId;
    this.state.selectedZoneIds = [];
    this.state.selectedValueIds = [];
    this.state.selectedDeviceIds = [];
    this.updateFloorSelectorUI();
    this.updatePropPanel();
    const floor = this.getActiveFloor();
    if (floor && floor.imgData && !floor.isLoaded) {
      this.loadBackgroundImage(floor.imgData);
    } else if (floor && floor.isLoaded) {
      this.processActiveFloorImage();
    }
    this.onUpdateSelectedZones();
    this.updateMissingZonesUI();
    this.onUpdateSelectedDevices();
    this.updateMissingDevicesUI();
    this.render();
  },
  updateFloorSelectorUI: function () {
    const select = document.getElementById("floor-selector");
    select.innerHTML = "";
    this.state.floors.forEach((f) => {
      const opt = document.createElement("option");
      opt.value = f.id;
      opt.textContent = f.name;
      opt.selected = f.id === this.state.activeFloorId;
      select.appendChild(opt);
    });
  },
  updateCurrentFloorName: function (name) {
    const floor = this.getActiveFloor();
    if (floor) {
      floor.name = name;
      this.signalDataChange();
      this.updateFloorSelectorUI();
    }
  },
  updateBgOpacity: function (val) {
    const floor = this.getActiveFloor();
    if (floor) {
      floor.opacity = parseFloat(val);
      this.signalDataChange();
      this.render();
    }
  },
  rotateBg: function (angle) {
    this.saveState();
    const floor = this.getActiveFloor();
    if (floor) {
      floor.rotation = (floor.rotation + angle) % 360;
      this.signalDataChange();
      this.render();
    }
  },
  handleImageUpload: function (input) {
    if (input.files && input.files[0]) {
      const file = input.files[0];
      //console.log(`Loading image {file}`);

      const reader = new FileReader();
      reader.onload = (e) => {
        this.saveState();
        const result = e.target.result;
        const floor = this.getActiveFloor();
        if (floor) {
          floor.imgData = result;
          this.loadBackgroundImage(result);
          this.signalDataChange();
          this.setStatus("background", "Image chargée.");
        }
      };
      reader.readAsDataURL(file);
    }
  },
  loadBackgroundImage: function (url) {
    const img = new Image();
    if (url.startsWith("http")) {
      img.crossOrigin = "Anonymous";
    }
    img.src = url;
    img.onload = () => {
      const floor = this.getActiveFloor();
      if (floor) {
        floor.img = img;
        floor.isLoaded = true;
        this.processActiveFloorImage();
      }
    };
  },
  processActiveFloorImage: function () {
    const floor = this.getActiveFloor();
    if (!floor || !floor.img) return;
    try {
      const tempCanvas = document.createElement("canvas");
      const ctx = tempCanvas.getContext("2d");
      const cTop = floor.cropTop || 0;
      const cBottom = floor.cropBottom || 0;
      const cLeft = floor.cropLeft || 0;
      const cRight = floor.cropRight || 0;
      const w = floor.img.width;
      const h = floor.img.height;
      const sw = Math.max(1, w - cLeft - cRight);
      const sh = Math.max(1, h - cTop - cBottom);
      tempCanvas.width = sw;
      tempCanvas.height = sh;
      ctx.drawImage(floor.img, cLeft, cTop, sw, sh, 0, 0, sw, sh);
      const imageData = ctx.getImageData(0, 0, sw, sh);
      const data = imageData.data;
      const invert = floor.invert || false;
      const removeBg = floor.removeBg || false;
      if (invert || removeBg) {
        for (let i = 0; i < data.length; i += 4) {
          if (invert) {
            data[i] = 255 - data[i];
            data[i + 1] = 255 - data[i + 1];
            data[i + 2] = 255 - data[i + 2];
          }
          if (removeBg) {
            if (data[i] > 230 && data[i + 1] > 230 && data[i + 2] > 230) {
              data[i + 3] = 0;
            }
          }
        }
        ctx.putImageData(imageData, 0, 0);
      }
      floor.processedCanvas = tempCanvas;
    } catch (e) {
      floor.processedCanvas = null;
    }
    this.render();
  },
  updateFloorImageProcessing: function () {
    const floor = this.getActiveFloor();
    if (!floor) return;
    floor.invert = document.getElementById("img-invert").checked;
    floor.removeBg = document.getElementById("img-transparent").checked;
    floor.cropTop =
      parseInt(document.getElementById("crop-top").value, 10) || 0;
    floor.cropBottom =
      parseInt(document.getElementById("crop-bottom").value, 10) || 0;
    floor.cropLeft =
      parseInt(document.getElementById("crop-left").value, 10) || 0;
    floor.cropRight =
      parseInt(document.getElementById("crop-right").value, 10) || 0;
    this.processActiveFloorImage();
    this.saveState();
  },
  stripImages: function (floors) {
    const clone = JSON.parse(JSON.stringify(floors));
    clone.forEach((f) => delete f.processedCanvas);
    return clone;
  },

  // --- VALUE SELECTOR ---
  openValueSelector: function (targetId = null) {
    this.state.editingValueId =
      targetId ||
      (this.state.selectedValueIds.length === 1
        ? this.state.selectedValueIds[0]
        : null);
    if (!this.state.editingValueId) return;
    document.getElementById("value-selector-modal").classList.remove("hidden");
    document.getElementById("value-search-input").value = "";
    this.filterValuesList("");
    setTimeout(() => document.getElementById("value-search-input").focus(), 50);
  },
  closeValueSelector: function () {
    document.getElementById("value-selector-modal").classList.add("hidden");
    this.state.editingValueId = null;
    this.state.visibleModalKeys = [];
  },
  filterValuesList: function (q) {
    const terms = q
      .toLowerCase()
      .split(" ")
      .filter((t) => t.length);
    const tbody = document.getElementById("values-table-body");
    tbody.innerHTML = "";
    const filtered = this.state.allValuesData
      .filter((v) => {
        const txt = `${v.key} ${v.tag || ""} ${v.description || ""} ${
          v.zone || ""
        }`.toLowerCase();
        return terms.every((t) => txt.includes(t));
      })
      .slice(0, 64);
    this.state.visibleModalKeys = filtered.map((v) => v.key);
    this.renderValuesTable(filtered);
    this.pollData();
  },
  renderValuesTable: function (items) {
    const tbody = document.getElementById("values-table-body");
    tbody.innerHTML = "";
    items.forEach((v) => {
      const live = this.state.valuesDataCache[v.key] || {
        valuestr: v.valuestr || "-",
        error: v.error,
      };
      const tr = document.createElement("tr");
      tr.className =
        "hover:bg-purple-50 cursor-pointer border-b border-slate-50 transition-colors";
      tr.setAttribute("data-key", v.key);
      tr.innerHTML = `<td class="font-mono font-bold text-purple-700">${
        v.key
      }</td><td class="text-right font-mono ${
        live.error ? "text-red-600" : "text-slate-600"
      }">${live.valuestr}</td><td class="text-slate-600">${
        v.description || ""
      }</td><td class="text-xs text-slate-500">${
        v.tag || "-"
      }</td><td class="text-xs text-slate-500">${v.zone || "-"}</td>`;
      tr.onclick = () => {
        if (this.state.editingValueId) {
          const val = this.state.values.find(
            (x) => x.id === this.state.editingValueId
          );
          if (val) {
            val.key = v.key;
            this.saveValues();
            this.updatePropPanel();
          }
        }
        this.closeValueSelector();
        this.render();
      };
      tbody.appendChild(tr);
    });
    document.getElementById(
      "values-count-info"
    ).textContent = `${items.length} affichées (Filtrage local)`;
  },
  updateValuesTableRows: function () {
    const rows = document.querySelectorAll("#values-table-body tr");
    rows.forEach((tr) => {
      const key = tr.getAttribute("data-key");
      if (key && this.state.valuesDataCache[key]) {
        const data = this.state.valuesDataCache[key];
        tr.cells[1].textContent = data.valuestr;
        tr.cells[1].className = `text-right font-mono ${
          data.error ? "text-red-600" : "text-slate-600"
        }`;
      }
    });
  },

  // SELECTION
  selectAllZones: function () {
    this.state.zones.forEach((z) => {
      if (!this.state.selectedZoneIds.includes(z.id))
        this.state.selectedZoneIds.push(z.id);
    });

    this.onUpdateSelectedZones();
  },
  selectAllValues: function () {
    this.state.values.forEach((v) => {
      if (!this.state.selectedValueIds.includes(v.id))
        this.state.selectedValueIds.push(v.id);
    });
  },
  selectAllDevices: function () {
    this.state.devices.forEach((v) => {
      if (!this.state.selectedDeviceIds.includes(v.id)) {
        this.state.selectedDeviceIds.push(v.id);
      }
    });

    this.onUpdateSelectedDevices();
  },
  selectAll: function () {
    if (this.state.mode === "edit-zones") {
      this.selectAllZones();
      this.selectAllValues();
    }

    if (this.state.mode === "edit-devices") {
      this.selectAllDevices();
    }
  },

  // REMAPING
  //mapValuesToInheritedZone: function() { this.state.values.forEach(v => { if(1) this.state.selectedValueIds.push(v.id); }); },
  //remapZones: function() { this.mapValuesToInheritedZones()},

  isMode: function (mode) {
    if (this.state.mode === mode) return true;
    return false;
  },

  isModeEdit: function (mode) {
    if (this.state.mode.startsWith("edit-")) return true;
    return false;
  },

  isModeBackground: function (mode) {
    return this.isMode("background");
  },

  // --- UI ACTIONS ---
  setMode: function (mode) {
    if (this.state.mode !== mode) {
      this.mapZones();

      if (this.isModeEdit()) {
        this.saveData(false);
      }

      if (this.isModeBackground()) this.saveFloors();
    }
    this.state.mode = mode;
    this.state.action = "idle";

    if (mode !== "edit-zones") {
      this.state.selectedZoneIds = [];
      this.state.selectedValueIds = [];
      this.onUpdateSelectedZones();
    }

    if (mode !== "edit-devices") {
      this.state.selectedDeviceIds = [];
      this.onUpdateSelectedDevices();
      if (this.state.dockVariables)
        this.state.dockVariables.hidePanel();     
    }

    this.state.snappedPoint = null;
    document
      .getElementById("btn-view")
      .classList.toggle("active", mode === "view");
    document
      .getElementById("btn-edit-zones")
      .classList.toggle("active", mode === "edit-zones");
    document
      .getElementById("btn-edit-devices")
      .classList.toggle("active", mode === "edit-devices");
    document
      .getElementById("btn-bg")
      .classList.toggle("active", mode === "background");
    document
      .getElementById("edit-tools")
      .classList.toggle("hidden", mode !== "edit-zones");

    document.getElementById("btn-add-zone").classList.remove("active");
    document.getElementById("btn-add-value").classList.remove("active");

    const btnSave = document.getElementById("btn-save");
    if (mode === "view" || !this.state.saveDataPending)
      btnSave.classList.add("opacity-50", "cursor-not-allowed");
    else btnSave.classList.remove("opacity-50", "cursor-not-allowed");

    const dot = document.getElementById("status-dot");
    dot.className = `w-2 h-2 rounded-full ${
      mode === "edit-zones"
        ? "bg-blue-500"
        : mode === "background"
        ? "bg-purple-500"
        : "bg-green-500"
    }`;
    this.setStatus(
      mode,
      mode === "view"
        ? "VIEW"
        : mode === "edit-zones"
        ? "ZONE"
        : mode === "edit-devices"
        ? "DEVICES"
        : "PLAN"
    );

    if (mode === "view" || mode === "edit-zones" || mode == "edit-devices")
      this.startPolling();
    else this.stopPolling();

    this.updateUIForMode();
    this.updateMissingZonesUI();
    this.updateMissingDevicesUI();
    this.updatePropPanel();
    this.render();
  },

  activateZoneTool: function () {
    if (this.state.mode !== "edit-zones") return;
    const isPlacing = this.state.action === "placing_zone";
    this.state.action = isPlacing ? "idle" : "placing_zone";
    document
      .getElementById("btn-add-zone")
      .classList.toggle("active", !isPlacing);
    document.getElementById("btn-add-value").classList.remove("active");
    if (!isPlacing) {
      this.state.selectedZoneIds = [];
      this.state.selectedValueIds = [];
      this.onUpdateSelectedZones();

      this.updatePropPanel();
      this.setStatus("edit-zones", "Cliquez pour poser une zone");
    } else {
      this.setStatus("edit-zones", "Mode Édition");
    }
  },
  activateValueTool: function () {
    if (this.state.mode !== "edit-zones") return;
    const isPlacing = this.state.action === "placing_value";
    this.state.action = isPlacing ? "idle" : "placing_value";
    document.getElementById("btn-add-zone").classList.remove("active");
    document
      .getElementById("btn-add-value")
      .classList.toggle("active", !isPlacing);
    if (!isPlacing) {
      this.state.selectedZoneIds = [];
      this.state.selectedValueIds = [];
      this.onUpdateSelectedZones();

      this.updatePropPanel();
      this.setStatus("edit-zones", "Cliquez pour placer une valeur");
    } else {
      this.setStatus("edit-zones", "Mode Édition");
    }
  },
  updatePropPanel: function () {
    const panel = document.getElementById("prop-panel");
    const bgProps = document.getElementById("bg-props");
    const zoneProps = document.getElementById("zone-props");
    const title = document.getElementById("prop-title");
    const singleZone = document.getElementById("single-zone-inputs");
    const singleValue = document.getElementById("single-value-inputs");
    const multiInfo = document.getElementById("multi-zone-info");
    panel.classList.add("hidden");
    bgProps.classList.add("hidden");
    zoneProps.classList.add("hidden");
    if (this.state.mode === "background") {
      panel.classList.remove("hidden");
      bgProps.classList.remove("hidden");
      title.textContent = "Plan de Fond";
      const floor = this.getActiveFloor();
      if (floor) {
        document.getElementById("bg-opacity").value = floor.opacity;
        document.getElementById("floor-name").value = floor.name;
        document.getElementById("img-invert").checked = floor.invert;
        document.getElementById("img-transparent").checked = floor.removeBg;
        document.getElementById("crop-top").value = Math.floor(
          floor.cropTop || 0
        );
        document.getElementById("crop-bottom").value = Math.floor(
          floor.cropBottom || 0
        );
        document.getElementById("crop-left").value = Math.floor(
          floor.cropLeft || 0
        );
        document.getElementById("crop-right").value = Math.floor(
          floor.cropRight || 0
        );
      }
    } else if (this.state.mode === "edit-zones") {
      if (
        this.state.selectedZoneIds.length > 0 ||
        this.state.selectedValueIds.length > 0
      ) {
        panel.classList.remove("hidden");
        zoneProps.classList.remove("hidden");
        singleZone.classList.add("hidden");
        singleValue.classList.add("hidden");
        multiInfo.classList.add("hidden");
        if (
          this.state.selectedValueIds.length === 1 &&
          this.state.selectedZoneIds.length === 0
        ) {
          title.textContent = "Propriétés Valeur";
          singleValue.classList.remove("hidden");
          const val = this.state.values.find(
            (v) => v.id === this.state.selectedValueIds[0]
          );
          document.getElementById("value-key").value = val ? val.key : "";
          document.getElementById("value-identifier").value =
            val.identifier || "";
        } else if (
          this.state.selectedZoneIds.length === 1 &&
          this.state.selectedValueIds.length === 0
        ) {
          title.textContent = "Propriétés Zone";
          singleZone.classList.remove("hidden");
          const zone = this.state.zones.find(
            (z) => z.id === this.state.selectedZoneIds[0]
          );
          document.getElementById("zone-name").value = zone ? zone.name : "";
          const datalist = document.getElementById("zone-suggestions");
          datalist.innerHTML = "";
          const usedNames = this.state.zones.map((z) => z.name.toLowerCase());
          this.state.availableZoneNames.forEach((name) => {
            if (!usedNames.includes(name.toLowerCase())) {
              const option = document.createElement("option");
              option.value = name;
              datalist.appendChild(option);
            }
          });
        } else {
          title.textContent = "Sélection Multiple";
          multiInfo.classList.remove("hidden");
        }
      }
    }
  },
  clearZoneNameInput: function () {
    const input = document.getElementById("zone-name");
    input.value = "";
    input.focus();
    this.updateSelectedZoneName("");
  },
  updateSelectedZoneName: function (name) {
    if (this.state.selectedZoneIds.length === 1) {
      const zone = this.state.zones.find(
        (z) => z.id === this.state.selectedZoneIds[0]
      );
      if (zone) {
        zone.name = name;
        this.signalDataChange();
        this.updateMissingZonesUI();
      }
    }
  },
  updateSelectedValueKey: function (key) {
    if (this.state.selectedValueIds.length === 1) {
      const val = this.state.values.find(
        (v) => v.id === this.state.selectedValueIds[0]
      );
      if (val) {
        val.key = key;
        this.signalDataChange();
      }
    }
  },
  updateSelectedValueIdentifier: function (id) {
    if (this.state.selectedValueIds.length === 1) {
      const val = this.state.values.find(
        (v) => v.id === this.state.selectedValueIds[0]
      );
      if (val) {
        val.identifier = id;
        this.render();
      }
    }
  },
  deleteSelection: function () {
    this.saveState();

    if (this.state.mode === "edit-zones") {
      if (this.state.selectedZoneIds.length > 0) {
        this.signalDataChange();
        this.state.zones = this.state.zones.filter(
          (z) => !this.state.selectedZoneIds.includes(z.id)
        );
        this.state.selectedZoneIds = [];
        this.onUpdateSelectedZones();
      }

      if (this.state.selectedValueIds.length > 0) {
        this.signalDataChange();
        this.state.values = this.state.values.filter(
          (v) => !this.state.selectedValueIds.includes(v.id)
        );
        this.state.selectedValueIds = [];
      }
    }

    if (this.state.mode === "edit-devices") {
      if (this.state.selectedDeviceIds.length > 0) {
        this.signalDataChange();
        this.state.devices = this.state.devices.filter(
          (v) => !this.state.selectedDeviceIds.includes(v.id)
        );
        this.state.selectedDeviceIds = [];
        this.onUpdateSelectedDevices();
      }
    }

    this.updatePropPanel();
    this.updateMissingZonesUI();
    this.updateMissingDevicesUI();
  },

  duplicateSelectedZone: function () {
    if (
      this.state.selectedZoneIds.length === 0 &&
      this.state.selectedValueIds.length === 0
    )
      return;
    this.saveState();
    const newSelZones = [],
      newSelVals = [];
    this.state.zones
      .filter((z) => this.state.selectedZoneIds.includes(z.id))
      .forEach((z) => {
        const newId =
          "zone_" + Date.now() + Math.random().toString(16).slice(2);
        const newPoints = z.points.map((p) => ({ x: p.x + 20, y: p.y + 20 }));
        this.state.zones.push({
          id: newId,
          name: z.name,
          points: newPoints,
          floorId: z.floorId,
        });
        newSelZones.push(newId);
        this.signalDataChange();
      });
    this.state.values
      .filter((v) => this.state.selectedValueIds.includes(v.id))
      .forEach((v) => {
        const newId = "val_" + Date.now() + Math.random().toString(16).slice(2);
        this.state.values.push({
          id: newId,
          key: v.key,
          identifier: v.identifier,
          x: v.x + 20,
          y: v.y + 20,
          floorId: v.floorId,
        });
        newSelVals.push(newId);
        this.signalDataChange();
      });
    this.state.selectedZoneIds = newSelZones;
    this.state.selectedValueIds = newSelVals;
    this.onUpdateSelectedZones();

    this.updatePropPanel();
  },
  createZoneAt: function (p) {
    this.saveState();
    const s = 150,
      id = "zone_" + Date.now();
    const pts = [
      { x: p.x, y: p.y },
      { x: p.x + s, y: p.y },
      { x: p.x + s, y: p.y + s },
      { x: p.x, y: p.y + s },
    ];
    this.state.zones.push({
      id,
      name: "",
      points: pts,
      floorId: this.state.activeFloorId,
    });
    this.state.selectedZoneIds = [id];
    this.state.selectedValueIds = [];
    this.state.action = "idle";
    document.getElementById("btn-add-zone").classList.remove("active");
    this.onUpdateSelectedZones();
    this.updatePropPanel();
    this.signalDataChange();
  },
  createValueAt: function (p) {
    this.saveState();
    const id = "val_" + Date.now();
    this.state.values.push({
      id,
      x: p.x,
      y: p.y,
      key: "",
      identifier: "",
      floorId: this.state.activeFloorId,
    });
    this.state.selectedValueIds = [id];
    this.state.selectedZoneIds = [];
    this.state.action = "idle";
    document.getElementById("btn-add-value").classList.remove("active");
    this.onUpdateSelectedZones();
    this.updatePropPanel();
    this.setStatus("edit-zones", "Valeur ajoutée.");
    this.openValueSelector(id);
    this.signalDataChange();
  },
  /*
  createDeviceAt: function (p) {
    this.saveState();
    const id = "device_" + Date.now();
    this.state.devices.push({
      id,
      x: p.x,
      y: p.y,
      key: "",
      identifier: "",
      floorId: this.state.activeFloorId,
      zone: "",
    });
    this.state.selectedDeviceIds = [id];
    this.state.action = "idle";
    this.signalDataChange();
  },
  */

  // --- ZONES MISSING UI ---
  updateMissingZonesUI: function () {
    const search = this.state.searchQuery.toLowerCase();
    const container = document.getElementById("missing-zones-container");
    container.innerHTML = "";
    if (this.state.mode !== "edit-zones") return;

    const usedNames = this.state.zones.map((z) => z.name.toLowerCase());
    const missing = this.state.availableZoneNames
      .sort()
      .filter(
        (name) =>
          !usedNames.includes(name.toLowerCase()) &&
          (!search || name.includes(search))
      );
    if (missing.length === 0) return;
    missing.forEach((name) => {
      const btn = document.createElement("div");
      btn.className = "zone-tag-btn pointer-events-auto";
      btn.innerHTML = `<i class="fa-solid fa-plus mr-1 text-xs text-white-400"></i> ${name}`;
      btn.onclick = () => this.createZoneFromTag(name);
      container.appendChild(btn);
    });
  },
  updateMissingDevicesUI: function () {
    const search = this.state.searchQuery.toLowerCase();
    const container = document.getElementById("missing-devices-container");
    container.innerHTML = "";
    if (this.state.mode !== "edit-devices") return;
    const usedKeys = this.state.devices.map((z) => z.key.toLowerCase());
    const missing = this.state.availableDeviceKeys
      .sort()
      .filter(
        (key) =>
          !usedKeys.includes(key.toLowerCase()) &&
          (!search || key.includes(search))
      );

    if (missing.length === 0) return;

    missing.forEach((key) => {
      const btn = document.createElement("div");
      btn.className = "device-tag-btn pointer-events-auto";
      btn.innerHTML = `<i class="fa-solid fa-plus mr-1 text-xs text-white-400"></i> ${key}`;
      btn.onclick = () => this.createDeviceFromTag(key);
      container.appendChild(btn);
    });
  },

  createZoneFromTag: function (name) {
    this.saveState();
    const centerScreen = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    };
    const worldPos = this.screenToWorld(centerScreen.x, centerScreen.y);
    const size = 150;
    let bestPos = worldPos;
    let found = false;
    const offsetStep = size + 20;
    const activeZones = this.state.zones.filter(
      (z) => z.floorId === this.state.activeFloorId
    );
    for (let r = 0; r < 5 && !found; r++) {
      for (let x = -r; x <= r; x++) {
        for (let y = -r; y <= r; y++) {
          const testPos = {
            x: worldPos.x + x * offsetStep,
            y: worldPos.y + y * offsetStep,
          };
          const testRect = { x: testPos.x, y: testPos.y, w: size, h: size };
          let collision = false;
          for (const z of activeZones) {
            let minX = Infinity,
              maxX = -Infinity,
              minY = Infinity,
              maxY = -Infinity;
            z.points.forEach((p) => {
              if (p.x < minX) minX = p.x;
              if (p.x > maxX) maxX = p.x;
              if (p.y < minY) minY = p.y;
              if (p.y > maxY) maxY = p.y;
            });
            if (
              testRect.x < maxX &&
              testRect.x + testRect.w > minX &&
              testRect.y < maxY &&
              testRect.y + testRect.h > minY
            ) {
              collision = true;
              break;
            }
          }
          if (!collision) {
            bestPos = testPos;
            found = true;
            break;
          }
        }
        if (found) break;
      }
    }
    const points = [
      { x: bestPos.x, y: bestPos.y },
      { x: bestPos.x + size, y: bestPos.y },
      { x: bestPos.x + size, y: bestPos.y + size },
      { x: bestPos.x, y: bestPos.y + size },
    ];
    const id = "zone_" + Date.now();
    this.state.zones.push({
      id,
      name: name,
      points,
      floorId: this.state.activeFloorId,
    });
    this.state.selectedZoneIds = [id];
    this.onUpdateSelectedZones();
    this.updatePropPanel();
    this.signalDataChange();
    this.setStatus("edit-zones", `Zone "${name}" ajoutée.`);
    this.updateMissingZonesUI();
  },

  createDeviceFromTag: function (name) {
    this.saveState();
    const centerScreen = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    };
    const worldPos = this.screenToWorld(centerScreen.x, centerScreen.y);
    const size = 50;
    let bestPos = worldPos;
    let found = false;
    const offsetStep = size + 20;
    const activeDevices = this.state.devices.filter(
      (d) => d.floorId === this.state.activeFloorId
    );

    /*
    for (let r = 0; r < 5 && !found; r++) {
      for (let x = -r; x <= r; x++) {
        for (let y = -r; y <= r; y++) {
          const testPos = {
            x: worldPos.x + x * offsetStep,
            y: worldPos.y + y * offsetStep,
          };
          const testRect = { x: testPos.x, y: testPos.y, w: size, h: size };
          let collision = false;
          for (const d of activeDevices) {
            let minX = Infinity,
              maxX = -Infinity,
              minY = Infinity,
              maxY = -Infinity;
            d.points.forEach((p) => {
              if (p.x < minX) minX = p.x;
              if (p.x > maxX) maxX = p.x;
              if (p.y < minY) minY = p.y;
              if (p.y > maxY) maxY = p.y;
            });
            if (
              testRect.x < maxX &&
              testRect.x + testRect.w > minX &&
              testRect.y < maxY &&
              testRect.y + testRect.h > minY
            ) {
              collision = true;
              break;
            }
          }
          if (!collision) {
            bestPos = testPos;
            found = true;
            break;
          }
        }
        if (found) break;
      }
    }
    */

    const id = "device_" + Date.now();
    this.state.devices.push({
      id,
      x: bestPos.x,
      y: bestPos.y,
      key: name,
      floorId: this.state.activeFloorId,
      zone: "",
    });
    this.state.selectedDeviceIds = [id];
    this.onUpdateSelectedDevices();

    this.signalDataChange();
    this.setStatus("edit-devices", `Device "${name}" ajouté.`);
    this.updateMissingDevicesUI();
    //this.state.action = "idle";
  },

  // --- MATH & EVENTS ---
  screenToWorld: function (sx, sy) {
    const v = this.state.view;
    let x = sx - this.canvas.width / 2;
    let y = sy - this.canvas.height / 2;
    x -= v.x;
    y -= v.y;
    const rad = (-v.rotation * Math.PI) / 180;
    return {
      x: (x * Math.cos(rad) - y * Math.sin(rad)) / v.scale,
      y: (x * Math.sin(rad) + y * Math.cos(rad)) / v.scale,
    };
  },
  dist: function (p1, p2) {
    return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
  },
  projectPointOnSegment: function (p, v, w) {
    const l2 = this.dist(v, w) ** 2;
    if (l2 == 0) return v;
    let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    t = Math.max(0, Math.min(1, t));
    return { x: v.x + t * (w.x - v.x), y: v.y + t * (w.y - v.y) };
  },
  distToSegment: function (p, v, w) {
    return this.dist(p, this.projectPointOnSegment(p, v, w));
  },
  getCentroid: function (points) {
    let area = 0,
      cx = 0,
      cy = 0;
    for (let i = 0; i < points.length; i++) {
      const j = (i + 1) % points.length;
      const p1 = points[i],
        p2 = points[j];
      const f = p1.x * p2.y - p2.x * p1.y;
      area += f;
      cx += (p1.x + p2.x) * f;
      cy += (p1.y + p2.y) * f;
    }
    if (Math.abs(area) < 1e-6) {
      let x = 0,
        y = 0;
      for (let p of points) {
        x += p.x;
        y += p.y;
      }
      return { x: x / points.length, y: y / points.length };
    }
    area *= 3;
    return { x: cx / area, y: cy / area };
  },
  isPointInPoly: function (p, polygon) {
    let isInside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      if (
        polygon[i].y > p.y !== polygon[j].y > p.y &&
        p.x <
          ((polygon[j].x - polygon[i].x) * (p.y - polygon[i].y)) /
            (polygon[j].y - polygon[i].y) +
            polygon[i].x
      ) {
        isInside = !isInside;
      }
    }
    return isInside;
  },
  getZoneAt: function (worldPos, floorId = null) {
    const activeZones = this.state.zones.filter(
      (z) => z.floorId === (floorId ? floorId : this.state.activeFloorId)
    );
    for (let i = activeZones.length - 1; i >= 0; i--) {
      if (this.isPointInPoly(worldPos, activeZones[i].points))
        return activeZones[i];
    }
    return null;
  },
  getVertexAt: function (worldPos, zone) {
    const tolerance = this.config.hitTolerance / this.state.view.scale;
    for (let i = 0; i < zone.points.length; i++) {
      if (this.dist(worldPos, zone.points[i]) <= tolerance) return i;
    }
    return -1;
  },
  getEdgeAt: function (worldPos, zone) {
    const tolerance = this.config.hitTolerance / this.state.view.scale;
    for (let i = 0; i < zone.points.length; i++) {
      if (
        this.distToSegment(
          worldPos,
          zone.points[i],
          zone.points[(i + 1) % zone.points.length]
        ) <= tolerance
      )
        return i;
    }
    return -1;
  },
  getValueAt: function (worldPos, floorId = null) {
    const activeValues = this.state.values.filter(
      (v) => v.floorId === (floorId ? floorId : this.state.activeFloorId)
    );
    const w = 80 / this.state.view.scale;
    const h = 30 / this.state.view.scale;
    for (let i = activeValues.length - 1; i >= 0; i--) {
      const v = activeValues[i];
      if (
        Math.abs(worldPos.x - v.x) < w / 2 &&
        Math.abs(worldPos.y - v.y) < h / 2
      )
        return activeValues[i];
    }
    return null;
  },

  getDeviceAt: function (worldPos, floorId = null) {
    const activeDevices = this.state.devices.filter(
      (v) => v.floorId === (floorId ? floorId : this.state.activeFloorId)
    );
    const w = 80 / this.state.view.scale;
    const h = 30 / this.state.view.scale;
    for (let i = activeDevices.length - 1; i >= 0; i--) {
      const d = activeDevices[i];
      if (
        Math.abs(worldPos.x - d.x) < w / 2 &&
        Math.abs(worldPos.y - d.y) < h / 2
      )
        return activeDevices[i];
    }
    return null;
  },

  getBgHandleAt: function (worldPos) {
    const floor = this.getActiveFloor();
    if (!floor || !floor.processedCanvas) return null;
    const dx = worldPos.x - floor.x;
    const dy = worldPos.y - floor.y;
    const rad = (-floor.rotation * Math.PI) / 180;
    const lx = dx * Math.cos(rad) - dy * Math.sin(rad);
    const ly = dx * Math.sin(rad) + dy * Math.cos(rad);
    const w = floor.processedCanvas.width;
    const h = floor.processedCanvas.height;
    const halfW = w / 2;
    const halfH = h / 2;
    const tol = 10 / this.state.view.scale / floor.scale;
    if (Math.abs(ly - -halfH) < tol && lx >= -halfW && lx <= halfW)
      return "top";
    if (Math.abs(ly - halfH) < tol && lx >= -halfW && lx <= halfW)
      return "bottom";
    if (Math.abs(lx - -halfW) < tol && ly >= -halfH && ly <= halfH)
      return "left";
    if (Math.abs(lx - halfW) < tol && ly >= -halfH && ly <= halfH)
      return "right";
    return null;
  },

  getBestSnap: function (pos, excludeZoneIds = []) {
    const snapThreshold = this.config.snapDistance / this.state.view.scale;
    let bestDist = snapThreshold;
    let bestPoint = null;
    const activeZones = this.state.zones.filter(
      (z) => z.floorId === this.state.activeFloorId
    );
    activeZones.forEach((z) => {
      if (excludeZoneIds.includes(z.id)) return;
      z.points.forEach((p) => {
        const d = this.dist(pos, p);
        if (d < bestDist) {
          bestDist = d;
          bestPoint = { x: p.x, y: p.y };
        }
      });
      for (let i = 0; i < z.points.length; i++) {
        const p1 = z.points[i];
        const p2 = z.points[(i + 1) % z.points.length];
        const proj = this.projectPointOnSegment(pos, p1, p2);
        const d = this.dist(pos, proj);
        if (d < bestDist) {
          bestDist = d;
          bestPoint = proj;
        }
      }
    });
    return bestPoint;
  },
  snapZoneVertices: function (zoneIds) {
    const movingZones = this.state.zones.filter((z) => zoneIds.includes(z.id));
    let snappedCount = 0;
    movingZones.forEach((zone) => {
      zone.points.forEach((p, index) => {
        const snapTarget = this.getBestSnap(p, zoneIds);
        if (snapTarget) {
          zone.points[index] = { x: snapTarget.x, y: snapTarget.y };
          this.signalDataChange();
          snappedCount++;
        }
      });
    });
    if (snappedCount > 0) {
      this.render();
      this.setStatus("edit-zones", `Alignement magnétique appliqué.`);
    }
  },
  getBoxFromPoints: function (p1, p2) {
    return {
      x: Math.min(p1.x, p2.x),
      y: Math.min(p1.y, p2.y),
      w: Math.abs(p1.x - p2.x),
      h: Math.abs(p1.y - p2.y),
    };
  },
  applyBoxSelection: function (isAdditive) {
    const rect = this.getBoxFromPoints(
      this.state.selectionStart,
      this.state.selectionEnd
    );

    const hitZoneIds = [];
    const hitValueIds = [];
    const hitDeviceIds = [];

    if (this.state.mode === "edit-zones") {
      this.state.zones
        .filter((z) => z.floorId === this.state.activeFloorId)
        .forEach((z) => {
          if (
            z.points.some(
              (p) =>
                p.x >= rect.x &&
                p.x <= rect.x + rect.w &&
                p.y >= rect.y &&
                p.y <= rect.y + rect.h
            )
          )
            hitZoneIds.push(z.id);
        });

      this.state.values
        .filter((v) => v.floorId === this.state.activeFloorId)
        .forEach((v) => {
          if (
            v.x >= rect.x &&
            v.x <= rect.x + rect.w &&
            v.y >= rect.y &&
            v.y <= rect.y + rect.h
          )
            hitValueIds.push(v.id);
        });
    }

    if (this.state.mode === "edit-devices") {
      this.state.devices
        .filter((d) => d.floorId === this.state.activeFloorId)
        .forEach((d) => {
          if (
            d.x >= rect.x &&
            d.x <= rect.x + rect.w &&
            d.y >= rect.y &&
            d.y <= rect.y + rect.h
          )
            hitDeviceIds.push(d.id);
        });
    }

    if (isAdditive) {
      hitZoneIds.forEach((id) => {
        if (!this.state.selectedZoneIds.includes(id))
          this.state.selectedZoneIds.push(id);
      });
      hitValueIds.forEach((id) => {
        if (!this.state.selectedValueIds.includes(id))
          this.state.selectedValueIds.push(id);
      });
      hitDeviceIds.forEach((id) => {
        if (!this.state.selectedDeviceIds.includes(id)) {
          this.state.selectedDeviceIds.push(id);
        }
      });

      this.onUpdateSelectedZones();
      this.onUpdateSelectedDevices();
    } else {
      this.state.selectedZoneIds = hitZoneIds;
      this.state.selectedValueIds = hitValueIds;
      this.state.selectedDeviceIds = hitDeviceIds;
      this.onUpdateSelectedZones();
      this.onUpdateSelectedDevices();
    }
    this.updatePropPanel();
  },

  // SEARCHBAR
  // Méthode appelée à chaque frappe
  handleGlobalSearch: function (query) {
    this.state.searchQuery = query.toLowerCase().trim();
    this.render(); // On redessine pour appliquer le filtre visuellement

    // Si vous avez une liste HTML (ex: liste de zones manquantes),
    // appelez aussi sa fonction de mise à jour ici :
    this.updateMissingZonesUI();
    this.updateMissingDevicesUI();
    if (this.state.dockVariables)
      this.state.dockVariables.filter(this.state.searchQuery);
  },

  // Méthode pour effacer la recherche
  clearGlobalSearch: function () {
    this.state.searchQuery = "";
    const input = document.getElementById("global-search-input");
    input.value = "";
    input.blur(); // Enlever le focus

    // Optionnel : Masquer la barre si elle est vide
    document.getElementById("global-search-container").classList.add("hidden");

    this.render();
    this.updateMissingZonesUI();
    this.updateMissingDevicesUI();
    if (this.state.dockVariables) this.state.dockVariables.resetFilter();
  },

  // Méthode pour afficher/masquer la barre selon le mode
  updateUIForMode: function () {
    const searchContainer = document.getElementById("global-search-container");

    /*
    
    // Exemple : Afficher la barre seulement en mode 'view' ou 'edit'
    if (this.state.mode === 'edit-zones' || this.state.mode === 'edit-devices') {
        searchContainer.classList.remove('hidden');
    } else {
        searchContainer.classList.add('hidden');
    }
        */
  },

  // --- UNDO/REDO ---
  saveState: function () {
    const snapshot = {
      zones: JSON.parse(JSON.stringify(this.state.zones)),
      floors: JSON.parse(JSON.stringify(this.state.floors)),
      activeFloorId: this.state.activeFloorId,
      values: JSON.parse(JSON.stringify(this.state.values)),
    };
    this.state.history.push(snapshot);
    if (this.state.history.length > this.config.maxHistory)
      this.state.history.shift();
    this.state.future = [];
    this.updateMissingZonesUI();
  },
  undo: function () {
    if (this.state.history.length === 0) return;
    const currentSnapshot = {
      zones: JSON.parse(JSON.stringify(this.state.zones)),
      floors: this.stripImages(this.state.floors),
      activeFloorId: this.state.activeFloorId,
      values: JSON.parse(JSON.stringify(this.state.values)),
    };
    this.state.future.push(currentSnapshot);
    this.restoreState(this.state.history.pop());
    this.setStatus(this.state.mode, "Annuler (Undo)");
  },
  redo: function () {
    if (this.state.future.length === 0) return;
    const currentSnapshot = {
      zones: JSON.parse(JSON.stringify(this.state.zones)),
      floors: this.stripImages(this.state.floors),
      activeFloorId: this.state.activeFloorId,
      values: JSON.parse(JSON.stringify(this.state.values)),
    };
    this.state.history.push(currentSnapshot);
    this.restoreState(this.state.future.pop());
    this.setStatus(this.state.mode, "Rétablir (Redo)");
  },
  restoreState: function (snapshot) {
    this.state.zones = JSON.parse(JSON.stringify(snapshot.zones));
    this.state.floors = JSON.parse(JSON.stringify(snapshot.floors));
    this.state.activeFloorId = snapshot.activeFloorId;
    this.state.values = JSON.parse(JSON.stringify(snapshot.values || []));
    const floor = this.getActiveFloor();
    if (floor && floor.imgData) this.loadBackgroundImage(floor.imgData);
    this.updateFloorSelectorUI();
    this.state.selectedZoneIds = [];
    this.state.selectedValueIds = [];
    this.onUpdateSelectedZones();
    this.updatePropPanel();
    this.updateMissingZonesUI();
    this.render();
  },

  setupEvents: function () {
    const c = this.canvas;
    window.addEventListener("keydown", (e) => {
      const isCtrl = e.ctrlKey || e.metaKey;
      const isShift = e.shiftKey;

      if (e.target.tagName === "INPUT") {
        if (["Escape", "F6", "F7", "F3"].indexOf(e.key) < 0) return; // No shortcuts when typing
      }

      if (e.key === "/" || e.key == "F3") {
        // On vérifie si on n'est pas déjà dans un input pour ne pas gêner la saisie
        if (
          document.activeElement.tagName !== "INPUT" &&
          document.activeElement.tagName !== "TEXTAREA"
        ) {
          e.preventDefault(); // Empêche d'écrire le "/"

          // Si la barre est masquée, on l'affiche (selon votre logique de vue)
          const searchContainer = document.getElementById(
            "global-search-container"
          );
          if (searchContainer.classList.contains("hidden")) {
            searchContainer.classList.remove("hidden");
          }

          const input = document.getElementById("global-search-input");
          input.focus();
          input.select(); // Sélectionne tout le texte existant
        }
      }

      // Fermer la recherche avec ECHAP
      if (e.key === "Escape") {
        let input = document.getElementById("global-search-input");
        if (document.activeElement === input) {
          input.blur();
          app.clearGlobalSearch(); // Optionnel : effacer ou juste quitter
          return;
        }

        input = document.getElementById("value-selector-modal");
        if (document.activeElement === input) {
          if (e.target.tagName === "INPUT") {
            e.preventDefault();
            app.closeValueSelector();

            // TODO: seulement si on est dans le panel value
            this.deleteSelection();
            return;
          }
        }

        if (this.isModeEdit()) {
          this.state.selectedZoneIds = [];
          this.state.selectedValueIds = [];
          this.state.selectedDeviceIds = [];
          this.onUpdateSelectedZones();
          this.onUpdateSelectedDevices();
        }
      }

      if (e.code === "Space") {
        this.state.isSpacePressed = true;
        c.style.cursor = "grab";
      }
      if (e.key === "F6") {
        e.preventDefault();
        if (this.state.mode === "edit-zones") this.setMode("edit-devices");
        else this.setMode("edit-zones");
      }
      if (e.key === "F7") {
        e.preventDefault();
        this.setMode("view");
      }
      if (
        (e.key === "v" || e.key === "V") &&
        this.state.mode === "edit-zones"
      ) {
        e.preventDefault();
        this.activateValueTool();
        if (this.state.selectedValueIds.length === 1)
          this.openValueSelector(this.state.selectedValueIds[0]);
        else if (this.state.selectedZoneIds.length === 1) {
          const z = this.state.zones.find(
            (z) => z.id === this.state.selectedZoneIds[0]
          );
          const wPos = this.screenToWorld(
            this.state.lastMouse.x,
            this.state.lastMouse.y
          );
          this.createValueAt(wPos);
          const newValId = this.state.selectedValueIds[0];
          this.openValueSelector(newValId, z.name);
        } else
          this.createValueAt(
            this.screenToWorld(this.state.lastMouse.x, this.state.lastMouse.y)
          );
        return;
      }
      if (
        (e.key === "z" || e.key === "Z") &&
        this.state.mode === "edit-zones"
      ) {
        e.preventDefault();
        this.createZoneAt(
          this.screenToWorld(this.state.lastMouse.x, this.state.lastMouse.y)
        );
        return;
      }
      if (e.key === "PageDown") {
        e.preventDefault();
        if (this.state.floors.length > 1) {
          const idx = this.state.floors.findIndex(
            (f) => f.id === this.state.activeFloorId
          );
          const next = (idx + 1) % this.state.floors.length;
          this.switchFloor(this.state.floors[next].id);
        }
        return;
      }
      if (e.key === "PageUp") {
        e.preventDefault();
        if (this.state.floors.length > 1) {
          const idx = this.state.floors.findIndex(
            (f) => f.id === this.state.activeFloorId
          );
          const prev =
            (idx - 1 + this.state.floors.length) % this.state.floors.length;
          this.switchFloor(this.state.floors[prev].id);
        }
        return;
      }
      if (isCtrl && e.key === "s") {
        e.preventDefault();
        this.saveData(false);
      }
      if (isCtrl && e.key === "z") {
        e.preventDefault();
        this.undo();
      }
      if (isCtrl && e.key === "y") {
        e.preventDefault();
        this.redo();
      }

      if (this.state.mode === "edit-zones") {
        if (isCtrl && e.key === "a") {
          e.preventDefault();
          this.selectAll();
        }
        if (isCtrl && e.key === "d") {
          e.preventDefault();
          this.duplicateSelectedZone();
        }
        if (e.key === "Delete") {
          e.preventDefault();
          this.deleteSelection();
        }
      }

      if (this.state.mode === "edit-devices") {
        if (isCtrl && e.key === "a") {
          console.log("APP: CTRL+A");
          e.preventDefault();
          this.selectAll();
        }
        if (e.key === "Delete") {
          e.preventDefault();
          this.deleteSelection();
        }
      }
    });
    window.addEventListener("keyup", (e) => {
      if (e.code === "Space") {
        this.state.isSpacePressed = false;
        if (this.state.action !== "panning") c.style.cursor = "default";
      }
    });
    c.addEventListener("mousemove", (e) => {
      const rect = c.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const worldPos = this.screenToWorld(mx, my);
      this.state.lastMouse = { x: mx, y: my };

      if (this.state.action === "dragging_selection") {
        const dx = worldPos.x - this.state.dragOffset.x;
        const dy = worldPos.y - this.state.dragOffset.y;

        if (this.state.mode === "edit-zones") {
          this.state.selectedZoneIds.forEach((id) => {
            const z = this.state.zones.find((x) => x.id === id);
            if (z) {
              z.points = z.points.map((p) => ({ x: p.x + dx, y: p.y + dy }));
              this.signalDataChange();
            }
          });

          this.state.selectedValueIds.forEach((id) => {
            const v = this.state.values.find((x) => x.id === id);
            if (v) {
              v.x += dx;
              v.y += dy;
              this.signalDataChange();
            }
          });
        }

        if (this.state.mode === "edit-devices") {
          this.state.dockVariables.hidePanel();
          this.state.selectedDeviceIds.forEach((id) => {
            const d = this.state.devices.find((x) => x.id === id);
            if (d) {
              d.x += dx;
              d.y += dy;
              this.signalDataChange();
            }
          });
        }

        this.state.dragOffset = worldPos;
        return;
      }

      if (this.state.isSpacePressed || this.state.action === "panning")
        c.style.cursor = this.state.action === "panning" ? "grabbing" : "grab";
      else if (
        this.state.mode === "edit-zones" &&
        this.state.action === "idle"
      ) {
        if (this.getValueAt(worldPos)) c.style.cursor = "move";
        else if (
          this.state.selectedZoneIds.length === 1 &&
          this.getVertexAt(
            worldPos,
            this.state.zones.find((z) => z.id === this.state.selectedZoneIds[0])
          ) !== -1
        )
          c.style.cursor = "crosshair";
        else if (
          (e.ctrlKey || e.metaKey) &&
          this.state.selectedZoneIds.length === 1 &&
          this.getEdgeAt(
            worldPos,
            this.state.zones.find((z) => z.id === this.state.selectedZoneIds[0])
          ) !== -1
        )
          c.style.cursor = "copy";
        else if (this.getZoneAt(worldPos)) c.style.cursor = "move";
        else c.style.cursor = "default";
      }

      if (this.state.mode === "background") {
        const handle = this.getBgHandleAt(worldPos);
        if (handle) {
          if (handle === "left" || handle === "right")
            c.style.cursor = "col-resize";
          else c.style.cursor = "row-resize";
        } else if (
          this.state.action !== "dragging_crop_edge" &&
          this.state.action !== "dragging_bg"
        ) {
          c.style.cursor = "move";
        }
      }

      if (this.state.action === "dragging_crop_edge") {
        const floor = this.getActiveFloor();
        const deltaXScreen =
          (mx - this.state.lastMousePrevious.x) /
          this.state.view.scale /
          floor.scale;
        const deltaYScreen =
          (my - this.state.lastMousePrevious.y) /
          this.state.view.scale /
          floor.scale;
        const rad = (-floor.rotation * Math.PI) / 180;
        const dx = deltaXScreen * Math.cos(rad) - deltaYScreen * Math.sin(rad);
        const dy = deltaXScreen * Math.sin(rad) + deltaYScreen * Math.cos(rad);
        if (this.state.draggingCropEdge === "top") floor.cropTop += dy;
        if (this.state.draggingCropEdge === "bottom") floor.cropBottom -= dy;
        if (this.state.draggingCropEdge === "left") floor.cropLeft += dx;
        if (this.state.draggingCropEdge === "right") floor.cropRight -= dx;
        floor.cropTop = Math.max(0, floor.cropTop);
        floor.cropBottom = Math.max(0, floor.cropBottom);
        floor.cropLeft = Math.max(0, floor.cropLeft);
        floor.cropRight = Math.max(0, floor.cropRight);
        this.signalDataChange();
        document.getElementById("crop-top").value = Math.floor(floor.cropTop);
        document.getElementById("crop-bottom").value = Math.floor(
          floor.cropBottom
        );
        document.getElementById("crop-left").value = Math.floor(floor.cropLeft);
        document.getElementById("crop-right").value = Math.floor(
          floor.cropRight
        );
        this.processActiveFloorImage();
      } else if (
        this.state.action === "dragging_vertex" &&
        this.state.selectedZoneIds.length === 1
      ) {
        const zone = this.state.zones.find(
          (z) => z.id === this.state.selectedZoneIds[0]
        );
        if (zone) {
          let targetPos = { x: worldPos.x, y: worldPos.y };
          this.state.snappedPoint = null;
          const snap = this.getBestSnap(worldPos, this.state.selectedZoneIds);
          if (snap) {
            targetPos = snap;
            this.state.snappedPoint = snap;
          }
          zone.points[this.state.draggingVertexIndex] = targetPos;
          this.signalDataChange();
        }
        return;
      } else if (this.state.action === "dragging_bg") {
        const deltaX = (mx - this.state.startDragBg.mx) / this.state.view.scale;
        const deltaY = (my - this.state.startDragBg.my) / this.state.view.scale;
        const floor = this.getActiveFloor();
        floor.x = this.state.startDragBg.imgX + deltaX;
        floor.y = this.state.startDragBg.imgY + deltaY;
        this.signalDataChange();
        return;
      }

      if (this.state.action === "panning") {
        const dx = mx - this.state.lastMousePrevious.x;
        const dy = my - this.state.lastMousePrevious.y;
        const rad = (-this.state.view.rotation * Math.PI) / 180;
        this.state.view.x += dx * Math.cos(rad) - dy * Math.sin(rad);
        this.state.view.y += dx * Math.sin(rad) + dy * Math.cos(rad);
      }

      // CURSOR
      this.state.lastMousePrevious = { x: mx, y: my };
      if (!this.state.isSpacePressed && this.state.action === "idle") {
        let cursor = "default";

        if (this.state.mode === "edit-zones") {
          if (this.state.selectedZoneIds.length === 1) {
            const zone = this.state.zones.find(
              (z) => z.id === this.state.selectedZoneIds[0]
            );
            if (this.getVertexAt(worldPos, zone) !== -1) cursor = "crosshair";
            else if (
              (e.ctrlKey || e.metaKey) &&
              this.getEdgeAt(worldPos, zone) !== -1
            )
              cursor = "copy";
          }

          if (cursor === "default" && this.getZoneAt(worldPos)) cursor = "move";
        } else if (this.state.mode === "edit-devices") {
          if (this.getDeviceAt(worldPos)) cursor = "move";
        } else if (this.state.mode === "background") cursor = "move";
        else if (this.state.mode === "view") {
          const zone = this.getZoneAt(worldPos);
          const device = this.getDeviceAt(worldPos);
          cursor = zone || device ? "pointer" : "default";
        }

        if (this.state.mode !== "background") {
          const handle = this.getBgHandleAt(worldPos);
          if (handle) {
            if (handle === "left" || handle === "right") cursor = "col-resize";
            else cursor = "row-resize";
          }
        }

        c.style.cursor = cursor;
      }

      if (this.state.action === "selecting_box") {
        this.state.selectionEnd = worldPos;
      }
    });

    c.addEventListener("mousedown", (e) => {
      const rect = c.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const worldPos = this.screenToWorld(mx, my);
      const isShift = e.shiftKey;
      const isCtrl = e.ctrlKey || e.metaKey;

      this.state.lastMouse = { x: mx, y: my };
      this.state.lastMousePrevious = { x: mx, y: my };
      this.state.clickStartMouse = { x: mx, y: my };
      if (e.button === 1 || this.state.isSpacePressed) {
        this.state.action = "panning";
        c.style.cursor = "grabbing";
        return;
      }
      if (this.state.mode === "view" && e.button === 0) {
        this.state.action = "panning";
        c.style.cursor = "grabbing";
        return;
      }
      if (this.state.mode === "background" && e.button === 0) {
        const handle = this.getBgHandleAt(worldPos);
        if (handle) {
          this.saveState();
          this.state.action = "dragging_crop_edge";
          this.state.draggingCropEdge = handle;
          return;
        }
        this.saveState();
        this.state.action = "dragging_bg";
        const floor = this.getActiveFloor();
        this.state.startDragBg = {
          mx: mx,
          my: my,
          imgX: floor.x,
          imgY: floor.y,
        };
        return;
      }
      if (this.state.mode === "edit-devices") {
        const clickedDevice = this.getDeviceAt(worldPos);
        if (clickedDevice) {
          const isSel = this.state.selectedDeviceIds.includes(clickedDevice.id);

          if (!isCtrl && !isSel) {
            this.state.selectedDeviceIds = [];
          }

          if (!this.state.selectedDeviceIds.includes(clickedDevice.id)) {
            this.state.selectedDeviceIds.push(clickedDevice.id);
            this.onUpdateSelectedDevices();
          }
          else if (isCtrl) {
            this.state.selectedDeviceIds = this.state.selectedDeviceIds.filter(
              (id) => id !== clickedDevice.id
            );
            this.onUpdateSelectedDevices();
          }

          this.saveState();
          this.state.action = "dragging_selection";
          this.state.dragOffset = worldPos;
          return;
        }

        if (isShift) {
          const zone = this.getZoneAt(worldPos);
          if (zone) {
            const name = zone.name;
            this.state.devices
              .filter((d) => d.zone === zone.name)
              .forEach((d) => {
                if (!this.state.selectedDeviceIds.includes(d.id))
                  this.state.selectedDeviceIds.push(d.id);
              });

            this.onUpdateSelectedDevices();
            return;
          }
        }

        if (!e.ctrlKey && !e.metaKey) {
          this.state.selectedDeviceIds = [];
          this.onUpdateSelectedDevices();
        }
        // Box Selection Start
        if (!clickedDevice && this.state.selectedZoneIds.length === 0) {
          this.state.selectionStart = worldPos;
          this.state.selectionEnd = worldPos;
          this.state.action = "selecting_box";
        }
      }

      if (this.state.mode === "edit-zones") {
        if (this.state.action === "placing_zone") {
          this.createZoneAt(worldPos);
          return;
        }
        if (this.state.action === "placing_value") {
          this.createValueAt(worldPos);
          return;
        }

        const clickedVal = this.getValueAt(worldPos);
        if (clickedVal) {
          const isCtrl = e.ctrlKey || e.metaKey;
          const isSel = this.state.selectedValueIds.includes(clickedVal.id);

          if (!isCtrl && !isSel) {
            this.state.selectedZoneIds = [];
            if (!this.state.selectedValueIds.includes(clickedVal.id))
              this.state.selectedValueIds = [];
          }

          if (!this.state.selectedValueIds.includes(clickedVal.id))
            this.state.selectedValueIds.push(clickedVal.id);
          else if (isCtrl)
            this.state.selectedValueIds = this.state.selectedValueIds.filter(
              (id) => id !== clickedVal.id
            );

          this.updatePropPanel();
          this.saveState();
          this.state.action = "dragging_selection";
          this.state.dragOffset = worldPos;
          return;
        }

        if (this.state.selectedZoneIds.length === 1) {
          const zone = this.state.zones.find(
            (z) => z.id === this.state.selectedZoneIds[0]
          );
          const vIndex = this.getVertexAt(worldPos, zone);
          if (vIndex !== -1) {
            this.saveState();
            this.state.action = "dragging_vertex";
            this.state.draggingVertexIndex = vIndex;
            return;
          }
          if (e.ctrlKey || e.metaKey) {
            const edgeIndex = this.getEdgeAt(worldPos, zone);
            if (edgeIndex !== -1) {
              this.saveState();
              const p1 = zone.points[edgeIndex];
              const p2 = zone.points[(edgeIndex + 1) % zone.points.length];
              const newPoint = this.projectPointOnSegment(worldPos, p1, p2);
              zone.points.splice(edgeIndex + 1, 0, newPoint);
              this.signalDataChange();
              this.state.action = "dragging_vertex";
              this.state.draggingVertexIndex = edgeIndex + 1;
              this.setStatus("edit-zones", "Point ajouté sur la ligne");
              return;
            }
          }
        }

        const clickedZone = this.getZoneAt(worldPos);
        if (clickedZone) {
          const isCtrl = e.ctrlKey || e.metaKey;
          const isSel = this.state.selectedZoneIds.includes(clickedZone.id);

          if (!isCtrl && !isSel) {
            this.state.selectedValueIds = [];
            if (!this.state.selectedZoneIds.includes(clickedZone.id))
              this.state.selectedZoneIds = [];
            this.onUpdateSelectedZones();
          }

          if (!this.state.selectedZoneIds.includes(clickedZone.id))
            this.state.selectedZoneIds.push(clickedZone.id);
          else if (isCtrl)
            this.state.selectedZoneIds = this.state.selectedZoneIds.filter(
              (id) => id !== clickedZone.id
            );

          this.onUpdateSelectedZones();
          this.updatePropPanel();
          this.saveState();
          this.state.action = "dragging_selection";
          this.state.dragOffset = worldPos;
          return;
        }

        if (!e.ctrlKey && !e.metaKey) {
          this.state.selectedZoneIds = [];
          this.state.selectedValueIds = [];
          this.onUpdateSelectedZones();
          this.updatePropPanel();
        }
        // Box Selection Start
        if (
          !clickedVal &&
          !clickedZone &&
          this.state.selectedZoneIds.length === 0
        ) {
          this.state.selectionStart = worldPos;
          this.state.selectionEnd = worldPos;
          this.state.action = "selecting_box";
        }
      }
    });
    c.addEventListener("mouseup", (e) => {
      const rect = c.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      if (this.state.mode === "view" && this.state.action === "panning") {
        const dist = Math.sqrt(
          (mx - this.state.clickStartMouse.x) ** 2 +
            (my - this.state.clickStartMouse.y) ** 2
        );

        if (dist < 5) {
          const d = this.getDeviceAt(this.screenToWorld(mx, my));
          if (d) {
            const data = this.state.devicesDataCache[d.key];
            window.open(
              "/devicevalues?device=" + encodeURIComponent(d.key),
              "_blank"
            );
          } else {
            const z = this.getZoneAt(this.screenToWorld(mx, my));
            if (z) {
              window.open(
                "/zonevalues?zone=" + encodeURIComponent(z.name),
                "_blank"
              );
            }
          }
        }
      }
      if (this.state.action === "dragging_selection") {
        //console.log("END DRAG");

        if (this.state.selectedZoneIds.length > 0) {
          this.snapZoneVertices(this.state.selectedZoneIds);
        }

        this.saveDevicesZones();

        if (this.isMode("edit-devices")) {
          if (this.state.selectedDeviceIds.length > 0) {
            this.pollSelectedDevicesValues();
          }
        }
      }
      if (this.state.action === "dragging_crop_edge") 
        this.saveData();

      // Box Selection End
      if (this.state.action === "selecting_box") {
        this.applyBoxSelection(e.ctrlKey || e.metaKey);
        this.state.selectionStart = null;
        this.state.selectionEnd = null;
        this.state.action = "idle";
        this.render(); // Clear box
      } else if (
        !["placing_zone", "placing_value"].includes(this.state.action)
      ) {
        this.state.action = "idle";
        this.state.draggingVertexIndex = -1;
        this.state.snappedPoint = null;
        this.state.draggingCropEdge = null;
        c.style.cursor = this.state.isSpacePressed ? "grab" : "default";
      }
    });
    c.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        if (this.state.mode === "background") {
          this.saveState();
          const d = -e.deltaY * 0.001,
            f = this.getActiveFloor();
          f.scale = Math.min(Math.max(0.1, f.scale + d), 5);
          this.render();
          return;
        }

        const d = -e.deltaY * 0.001;
        this.state.view.scale = Math.min(
          Math.max(0.1, this.state.view.scale + d),
          10
        );
      },
      { passive: false }
    );

    c.addEventListener("contextmenu", (e) => e.preventDefault());
    c.addEventListener("dblclick", (e) => {
      if (this.state.mode !== "edit-zones") return;
      if (this.state.selectedValueIds.length === 1) {
        this.openValueSelector(this.state.selectedValueIds[0]);
        return;
      }
      if (this.state.selectedZoneIds.length === 1) {
        const wPos = this.screenToWorld(
            e.clientX - c.getBoundingClientRect().left,
            e.clientY - c.getBoundingClientRect().top
          ),
          z = this.state.zones.find(
            (x) => x.id === this.state.selectedZoneIds[0]
          );
        const vi = this.getVertexAt(wPos, z);
        if (vi !== -1 && z.points.length > 3) {
          this.saveState();
          z.points.splice(vi, 1);
          this.signalDataChange();
          return;
        }
        const ei = this.getEdgeAt(wPos, z);
        if (ei !== -1) {
          this.saveState();
          z.points.splice(ei + 1, 0, { x: wPos.x, y: wPos.y });
          this.signalDataChange();
        }
      }
    });
  },

  loop: function () {
    this.render();
    requestAnimationFrame(() => this.loop());
  },
};

window.onload = () => app.init();
