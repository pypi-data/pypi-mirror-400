// src/core/BaseMapRenderer.ts
var BaseMapRenderer = class {
  model;
  el;
  map = null;
  mapContainer = null;
  lastProcessedCallId = 0;
  pendingCalls = [];
  eventQueue = [];
  isMapReady = false;
  methodHandlers = /* @__PURE__ */ new Map();
  modelListeners = [];
  constructor(model, el) {
    this.model = model;
    this.el = el;
  }
  /**
   * Create the map container element.
   */
  createMapContainer() {
    this.el.style.width = "100%";
    this.el.style.display = "block";
    const container = document.createElement("div");
    container.style.width = this.model.get("width") || "100%";
    container.style.height = this.model.get("height") || "400px";
    container.style.position = "relative";
    container.style.minWidth = "200px";
    this.el.appendChild(container);
    this.mapContainer = container;
    return container;
  }
  /**
   * Set up model trait listeners.
   */
  setupModelListeners() {
    const onJsCallsChange = () => this.processJsCalls();
    const onCenterChange = () => this.onCenterChange();
    const onZoomChange = () => this.onZoomChange();
    const onStyleChange = () => this.onStyleChange();
    this.model.on("change:_js_calls", onJsCallsChange);
    this.model.on("change:center", onCenterChange);
    this.model.on("change:zoom", onZoomChange);
    this.model.on("change:style", onStyleChange);
    this.modelListeners.push(
      () => this.model.off("change:_js_calls", onJsCallsChange),
      () => this.model.off("change:center", onCenterChange),
      () => this.model.off("change:zoom", onZoomChange),
      () => this.model.off("change:style", onStyleChange)
    );
  }
  /**
   * Remove model trait listeners.
   */
  removeModelListeners() {
    this.modelListeners.forEach((unsubscribe) => unsubscribe());
    this.modelListeners = [];
  }
  /**
   * Register a method handler.
   */
  registerMethod(name, handler) {
    this.methodHandlers.set(name, handler);
  }
  /**
   * Execute a method by name.
   */
  executeMethod(method, args, kwargs) {
    const handler = this.methodHandlers.get(method);
    if (handler) {
      try {
        handler(args, kwargs);
      } catch (error) {
        console.error(`Error executing method ${method}:`, error);
      }
    } else {
      console.warn(`Unknown method: ${method}`);
    }
  }
  /**
   * Process queued JavaScript calls from Python.
   */
  processJsCalls() {
    const calls = this.model.get("_js_calls") || [];
    const newCalls = calls.filter((call) => call.id > this.lastProcessedCallId);
    for (const call of newCalls) {
      if (this.isMapReady) {
        this.executeMethod(call.method, call.args, call.kwargs);
      } else {
        this.pendingCalls.push(call);
      }
      this.lastProcessedCallId = call.id;
    }
  }
  /**
   * Process pending calls after map is ready.
   */
  processPendingCalls() {
    for (const call of this.pendingCalls) {
      this.executeMethod(call.method, call.args, call.kwargs);
    }
    this.pendingCalls = [];
  }
  /**
   * Send an event to Python.
   */
  sendEvent(type, data) {
    const event = {
      type,
      data,
      timestamp: Date.now()
    };
    this.eventQueue.push(event);
    this.model.set("_js_events", [...this.eventQueue]);
    this.model.save_changes();
  }
  /**
   * Restore persisted state (layers, sources) from model.
   */
  restoreState() {
    const sources = this.model.get("_sources") || {};
    for (const [sourceId, sourceConfig] of Object.entries(sources)) {
      this.executeMethod("addSource", [sourceId], sourceConfig);
    }
    const layers = this.model.get("_layers") || {};
    for (const [layerId, layerConfig] of Object.entries(layers)) {
      this.executeMethod("addLayer", [], layerConfig);
    }
  }
  /**
   * Get the map instance.
   */
  getMap() {
    return this.map;
  }
  /**
   * Check if map is ready.
   */
  getIsMapReady() {
    return this.isMapReady;
  }
  /**
   * Get the model.
   */
  getModel() {
    return this.model;
  }
};

// src/core/StateManager.ts
var StateManager = class {
  model;
  constructor(model) {
    this.model = model;
  }
  /**
   * Add a layer to the state.
   */
  addLayer(layerId, config) {
    const layers = this.model.get("_layers") || {};
    const layerState = {
      id: config.id,
      type: config.type,
      source: config.source,
      paint: config.paint,
      layout: config.layout,
      visible: true,
      opacity: 1
    };
    this.model.set("_layers", { ...layers, [layerId]: layerState });
    this.model.save_changes();
  }
  /**
   * Remove a layer from the state.
   */
  removeLayer(layerId) {
    const layers = { ...this.model.get("_layers") };
    delete layers[layerId];
    this.model.set("_layers", layers);
    this.model.save_changes();
  }
  /**
   * Update layer visibility.
   */
  setLayerVisibility(layerId, visible) {
    const layers = { ...this.model.get("_layers") };
    if (layers[layerId]) {
      layers[layerId] = { ...layers[layerId], visible };
      this.model.set("_layers", layers);
      this.model.save_changes();
    }
  }
  /**
   * Update layer opacity.
   */
  setLayerOpacity(layerId, opacity) {
    const layers = { ...this.model.get("_layers") };
    if (layers[layerId]) {
      layers[layerId] = { ...layers[layerId], opacity };
      this.model.set("_layers", layers);
      this.model.save_changes();
    }
  }
  /**
   * Get layer state.
   */
  getLayer(layerId) {
    return this.model.get("_layers")?.[layerId];
  }
  /**
   * Get all layers.
   */
  getLayers() {
    return this.model.get("_layers") || {};
  }
  /**
   * Add a source to the state.
   */
  addSource(sourceId, config) {
    const sources = this.model.get("_sources") || {};
    const sourceState = {
      type: config.type,
      data: config.data,
      url: config.url,
      tiles: config.tiles,
      tileSize: config.tileSize,
      attribution: config.attribution
    };
    this.model.set("_sources", { ...sources, [sourceId]: sourceState });
    this.model.save_changes();
  }
  /**
   * Remove a source from the state.
   */
  removeSource(sourceId) {
    const sources = { ...this.model.get("_sources") };
    delete sources[sourceId];
    this.model.set("_sources", sources);
    this.model.save_changes();
  }
  /**
   * Get source state.
   */
  getSource(sourceId) {
    return this.model.get("_sources")?.[sourceId];
  }
  /**
   * Get all sources.
   */
  getSources() {
    return this.model.get("_sources") || {};
  }
  /**
   * Add a control to the state.
   */
  addControl(controlId, type, position, options) {
    const controls = this.model.get("_controls") || {};
    const controlState = {
      type,
      position,
      options
    };
    this.model.set("_controls", { ...controls, [controlId]: controlState });
    this.model.save_changes();
  }
  /**
   * Remove a control from the state.
   */
  removeControl(controlId) {
    const controls = { ...this.model.get("_controls") };
    delete controls[controlId];
    this.model.set("_controls", controls);
    this.model.save_changes();
  }
  /**
   * Get control state.
   */
  getControl(controlId) {
    return this.model.get("_controls")?.[controlId];
  }
  /**
   * Get all controls.
   */
  getControls() {
    return this.model.get("_controls") || {};
  }
};

// src/leaflet/LeafletRenderer.ts
var LeafletRenderer = class extends BaseMapRenderer {
  stateManager;
  layersMap = new globalThis.Map();
  markersMap = new globalThis.Map();
  popupsMap = new globalThis.Map();
  controlsMap = new globalThis.Map();
  resizeObserver = null;
  constructor(model, el) {
    super(model, el);
    this.stateManager = new StateManager(model);
    this.registerMethods();
  }
  /**
   * Initialize the Leaflet map.
   */
  async initialize() {
    this.createMapContainer();
    this.map = this.createMap();
    this.setupModelListeners();
    this.setupMapEvents();
    this.setupResizeObserver();
    this.processJsCalls();
    this.isMapReady = true;
    this.processPendingCalls();
  }
  /**
   * Set up resize observer.
   */
  setupResizeObserver() {
    if (!this.mapContainer || !this.map) return;
    this.resizeObserver = new ResizeObserver(() => {
      if (this.map) {
        this.map.invalidateSize();
      }
    });
    this.resizeObserver.observe(this.mapContainer);
    this.resizeObserver.observe(this.el);
  }
  /**
   * Create the Leaflet map instance.
   */
  createMap() {
    const center = this.model.get("center");
    const zoom = this.model.get("zoom");
    const map = index_default.map(this.mapContainer, {
      center: [center[1], center[0]],
      // Convert [lng, lat] to [lat, lng]
      zoom,
      zoomControl: false,
      // We'll add controls manually
      attributionControl: false
    });
    return map;
  }
  /**
   * Set up map event listeners.
   */
  setupMapEvents() {
    if (!this.map) return;
    this.map.on("click", (e) => {
      this.model.set("clicked", {
        lng: e.latlng.lng,
        lat: e.latlng.lat,
        point: [e.containerPoint.x, e.containerPoint.y]
      });
      this.sendEvent("click", {
        lngLat: [e.latlng.lng, e.latlng.lat],
        point: [e.containerPoint.x, e.containerPoint.y]
      });
      this.model.save_changes();
    });
    this.map.on("moveend", () => {
      if (!this.map) return;
      const center = this.map.getCenter();
      const bounds = this.map.getBounds();
      const zoom = this.map.getZoom();
      this.model.set("current_center", [center.lng, center.lat]);
      this.model.set("current_zoom", zoom);
      this.model.set("current_bounds", [
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
      ]);
      this.model.save_changes();
      this.sendEvent("moveend", {
        center: [center.lng, center.lat],
        zoom,
        bounds: [
          bounds.getWest(),
          bounds.getSouth(),
          bounds.getEast(),
          bounds.getNorth()
        ]
      });
    });
    this.map.on("zoomend", () => {
      if (!this.map) return;
      this.sendEvent("zoomend", { zoom: this.map.getZoom() });
    });
  }
  /**
   * Register all method handlers.
   */
  registerMethods() {
    this.registerMethod("setCenter", this.handleSetCenter.bind(this));
    this.registerMethod("setZoom", this.handleSetZoom.bind(this));
    this.registerMethod("flyTo", this.handleFlyTo.bind(this));
    this.registerMethod("fitBounds", this.handleFitBounds.bind(this));
    this.registerMethod("addTileLayer", this.handleAddTileLayer.bind(this));
    this.registerMethod("removeTileLayer", this.handleRemoveTileLayer.bind(this));
    this.registerMethod("addGeoJSON", this.handleAddGeoJSON.bind(this));
    this.registerMethod("removeGeoJSON", this.handleRemoveGeoJSON.bind(this));
    this.registerMethod("removeLayer", this.handleRemoveLayer.bind(this));
    this.registerMethod("setVisibility", this.handleSetVisibility.bind(this));
    this.registerMethod("setOpacity", this.handleSetOpacity.bind(this));
    this.registerMethod("addBasemap", this.handleAddBasemap.bind(this));
    this.registerMethod("addControl", this.handleAddControl.bind(this));
    this.registerMethod("removeControl", this.handleRemoveControl.bind(this));
    this.registerMethod("addMarker", this.handleAddMarker.bind(this));
    this.registerMethod("removeMarker", this.handleRemoveMarker.bind(this));
  }
  // -------------------------------------------------------------------------
  // Map navigation handlers
  // -------------------------------------------------------------------------
  handleSetCenter(args, kwargs) {
    if (!this.map) return;
    const [lng, lat] = args;
    this.map.setView([lat, lng], this.map.getZoom());
  }
  handleSetZoom(args, kwargs) {
    if (!this.map) return;
    const [zoom] = args;
    this.map.setZoom(zoom);
  }
  handleFlyTo(args, kwargs) {
    if (!this.map) return;
    const [lng, lat] = args;
    const zoom = kwargs.zoom;
    const duration = kwargs.duration || 2e3;
    const options = {
      duration: duration / 1e3
      // Leaflet uses seconds
    };
    if (zoom !== void 0) {
      this.map.flyTo([lat, lng], zoom, options);
    } else {
      this.map.flyTo([lat, lng], this.map.getZoom(), options);
    }
  }
  handleFitBounds(args, kwargs) {
    if (!this.map) return;
    const [bounds] = args;
    const padding = kwargs.padding || 50;
    const duration = kwargs.duration || 1e3;
    const leafletBounds = index_default.latLngBounds(
      [bounds[1], bounds[0]],
      // Southwest: [lat, lng]
      [bounds[3], bounds[2]]
      // Northeast: [lat, lng]
    );
    this.map.fitBounds(leafletBounds, {
      padding: [padding, padding],
      animate: true,
      duration: duration / 1e3
    });
  }
  // -------------------------------------------------------------------------
  // Tile layer handlers
  // -------------------------------------------------------------------------
  handleAddTileLayer(args, kwargs) {
    if (!this.map) return;
    const [url] = args;
    const name = kwargs.name || `tiles-${Date.now()}`;
    const attribution = kwargs.attribution || "";
    const minZoom = kwargs.minZoom || 0;
    const maxZoom = kwargs.maxZoom || 22;
    const opacity = kwargs.opacity || 1;
    const tileLayer = index_default.tileLayer(url, {
      attribution,
      minZoom,
      maxZoom,
      opacity
    });
    tileLayer.addTo(this.map);
    this.layersMap.set(name, tileLayer);
  }
  handleRemoveTileLayer(args, kwargs) {
    if (!this.map) return;
    const [name] = args;
    const layer = this.layersMap.get(name);
    if (layer) {
      this.map.removeLayer(layer);
      this.layersMap.delete(name);
    }
  }
  // -------------------------------------------------------------------------
  // Basemap handlers
  // -------------------------------------------------------------------------
  handleAddBasemap(args, kwargs) {
    if (!this.map) return;
    const [url] = args;
    const name = kwargs.name || "basemap";
    const attribution = kwargs.attribution || "";
    const existingLayer = this.layersMap.get(`basemap-${name}`);
    if (existingLayer) {
      this.map.removeLayer(existingLayer);
    }
    const tileLayer = index_default.tileLayer(url, {
      attribution,
      maxZoom: 22
    });
    tileLayer.addTo(this.map);
    tileLayer.bringToBack();
    this.layersMap.set(`basemap-${name}`, tileLayer);
  }
  // -------------------------------------------------------------------------
  // GeoJSON handlers
  // -------------------------------------------------------------------------
  handleAddGeoJSON(args, kwargs) {
    if (!this.map) return;
    const geojson = kwargs.data;
    const name = kwargs.name;
    const style = kwargs.style;
    const fitBounds = kwargs.fitBounds !== false;
    const geoJsonLayer = index_default.geoJSON(geojson, {
      style: (feature) => {
        if (style) {
          return style;
        }
        const geomType = feature?.geometry?.type || "Point";
        return this.getDefaultStyle(geomType);
      },
      pointToLayer: (feature, latlng) => {
        const s = style || this.getDefaultStyle("Point");
        return index_default.circleMarker(latlng, s);
      }
    });
    geoJsonLayer.addTo(this.map);
    this.layersMap.set(name, geoJsonLayer);
    if (fitBounds && kwargs.bounds) {
      const bounds = kwargs.bounds;
      const leafletBounds = index_default.latLngBounds(
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
      );
      this.map.fitBounds(leafletBounds, { padding: [50, 50] });
    } else if (fitBounds) {
      const layerBounds = geoJsonLayer.getBounds();
      if (layerBounds.isValid()) {
        this.map.fitBounds(layerBounds, { padding: [50, 50] });
      }
    }
  }
  handleRemoveGeoJSON(args, kwargs) {
    if (!this.map) return;
    const [name] = args;
    const layer = this.layersMap.get(name);
    if (layer) {
      this.map.removeLayer(layer);
      this.layersMap.delete(name);
    }
  }
  getDefaultStyle(geometryType) {
    const defaults = {
      Point: {
        radius: 8,
        fillColor: "#3388ff",
        color: "#ffffff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      },
      MultiPoint: {
        radius: 8,
        fillColor: "#3388ff",
        color: "#ffffff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      },
      LineString: {
        color: "#3388ff",
        weight: 3,
        opacity: 0.8
      },
      MultiLineString: {
        color: "#3388ff",
        weight: 3,
        opacity: 0.8
      },
      Polygon: {
        fillColor: "#3388ff",
        color: "#0000ff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.5
      },
      MultiPolygon: {
        fillColor: "#3388ff",
        color: "#0000ff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.5
      }
    };
    return defaults[geometryType] || defaults.Point;
  }
  // -------------------------------------------------------------------------
  // Layer handlers
  // -------------------------------------------------------------------------
  handleRemoveLayer(args, kwargs) {
    if (!this.map) return;
    const [layerId] = args;
    const layer = this.layersMap.get(layerId);
    if (layer) {
      this.map.removeLayer(layer);
      this.layersMap.delete(layerId);
    }
    this.stateManager.removeLayer(layerId);
  }
  handleSetVisibility(args, kwargs) {
    if (!this.map) return;
    const [layerId, visible] = args;
    const layer = this.layersMap.get(layerId);
    if (layer) {
      if (visible) {
        this.map.addLayer(layer);
      } else {
        this.map.removeLayer(layer);
      }
    }
  }
  handleSetOpacity(args, kwargs) {
    if (!this.map) return;
    const [layerId, opacity] = args;
    const layer = this.layersMap.get(layerId);
    if (layer && "setOpacity" in layer) {
      layer.setOpacity(opacity);
    } else if (layer && "setStyle" in layer) {
      layer.setStyle({ opacity, fillOpacity: opacity * 0.6 });
    }
  }
  // -------------------------------------------------------------------------
  // Control handlers
  // -------------------------------------------------------------------------
  handleAddControl(args, kwargs) {
    if (!this.map) return;
    const [controlType] = args;
    const position = this.convertPosition(kwargs.position);
    let control = null;
    switch (controlType) {
      case "zoom":
      case "navigation":
        control = index_default.control.zoom({ position });
        break;
      case "scale":
        control = index_default.control.scale({ position, imperial: false });
        break;
      case "attribution":
        control = index_default.control.attribution({ position });
        break;
      case "layers":
        const baseLayers = {};
        const overlays = {};
        this.layersMap.forEach((layer, name) => {
          if (name.startsWith("basemap-")) {
            baseLayers[name.replace("basemap-", "")] = layer;
          } else {
            overlays[name] = layer;
          }
        });
        control = index_default.control.layers(baseLayers, overlays, { position, collapsed: kwargs.collapsed !== false });
        break;
    }
    if (control) {
      control.addTo(this.map);
      this.controlsMap.set(controlType, control);
      this.stateManager.addControl(controlType, controlType, position, kwargs);
    }
  }
  handleRemoveControl(args, kwargs) {
    if (!this.map) return;
    const [controlType] = args;
    const control = this.controlsMap.get(controlType);
    if (control) {
      this.map.removeControl(control);
      this.controlsMap.delete(controlType);
      this.stateManager.removeControl(controlType);
    }
  }
  convertPosition(position) {
    const positionMap = {
      "top-left": "topleft",
      "top-right": "topright",
      "bottom-left": "bottomleft",
      "bottom-right": "bottomright",
      topleft: "topleft",
      topright: "topright",
      bottomleft: "bottomleft",
      bottomright: "bottomright"
    };
    return positionMap[position || "top-right"] || "topright";
  }
  // -------------------------------------------------------------------------
  // Marker handlers
  // -------------------------------------------------------------------------
  handleAddMarker(args, kwargs) {
    if (!this.map) return;
    const [lng, lat] = args;
    const id = kwargs.id || `marker-${Date.now()}`;
    const popup = kwargs.popup;
    const marker = index_default.marker([lat, lng]);
    if (popup) {
      marker.bindPopup(popup);
    }
    marker.addTo(this.map);
    this.markersMap.set(id, marker);
  }
  handleRemoveMarker(args, kwargs) {
    if (!this.map) return;
    const [id] = args;
    const marker = this.markersMap.get(id);
    if (marker) {
      marker.remove();
      this.markersMap.delete(id);
    }
  }
  // -------------------------------------------------------------------------
  // Trait change handlers
  // -------------------------------------------------------------------------
  onCenterChange() {
    if (this.map && this.isMapReady) {
      const center = this.model.get("center");
      this.map.setView([center[1], center[0]], this.map.getZoom());
    }
  }
  onZoomChange() {
    if (this.map && this.isMapReady) {
      const zoom = this.model.get("zoom");
      this.map.setZoom(zoom);
    }
  }
  onStyleChange() {
  }
  // -------------------------------------------------------------------------
  // Cleanup
  // -------------------------------------------------------------------------
  destroy() {
    this.removeModelListeners();
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
    this.markersMap.forEach((marker) => marker.remove());
    this.markersMap.clear();
    this.popupsMap.forEach((popup) => popup.remove());
    this.popupsMap.clear();
    this.layersMap.forEach((layer) => {
      if (this.map) {
        this.map.removeLayer(layer);
      }
    });
    this.layersMap.clear();
    this.controlsMap.forEach((control) => {
      if (this.map) {
        this.map.removeControl(control);
      }
    });
    this.controlsMap.clear();
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    if (this.mapContainer) {
      this.mapContainer.remove();
      this.mapContainer = null;
    }
  }
};

// src/leaflet/index.ts
function render({ model, el }) {
  if (el._leafletRenderer) {
    el._leafletRenderer.destroy();
    delete el._leafletRenderer;
  }
  const renderer = new LeafletRenderer(model, el);
  el._leafletRenderer = renderer;
  renderer.initialize().catch((error) => {
    console.error("Failed to initialize Leaflet map:", error);
  });
  return () => {
    if (el._leafletRenderer) {
      el._leafletRenderer.destroy();
      delete el._leafletRenderer;
    }
  };
}
var index_default = { render };
export {
  LeafletRenderer,
  index_default as default
};
