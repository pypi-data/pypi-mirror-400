// src/cesium/index.ts
import "cesium/Build/Cesium/Widgets/widgets.css";

// src/cesium/CesiumRenderer.ts
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

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

// src/cesium/CesiumRenderer.ts
var CesiumRenderer = class extends BaseMapRenderer {
  viewer = null;
  methodHandlers = {};
  imageryLayers = /* @__PURE__ */ new Map();
  tilesets = /* @__PURE__ */ new Map();
  dataSources = /* @__PURE__ */ new Map();
  constructor(model, el) {
    super(model, el);
    this.registerDefaultMethods();
  }
  /**
   * Register a method handler.
   */
  registerMethod(name, handler) {
    this.methodHandlers[name] = handler;
  }
  /**
   * Register default method handlers.
   */
  registerDefaultMethods() {
    this.registerMethod("addBasemap", this.handleAddBasemap.bind(this));
    this.registerMethod("addImageryLayer", this.handleAddImageryLayer.bind(this));
    this.registerMethod("removeImageryLayer", this.handleRemoveImageryLayer.bind(this));
    this.registerMethod("setTerrain", this.handleSetTerrain.bind(this));
    this.registerMethod("removeTerrain", this.handleRemoveTerrain.bind(this));
    this.registerMethod("add3DTileset", this.handleAdd3DTileset.bind(this));
    this.registerMethod("remove3DTileset", this.handleRemove3DTileset.bind(this));
    this.registerMethod("addGeoJSON", this.handleAddGeoJSON.bind(this));
    this.registerMethod("removeDataSource", this.handleRemoveDataSource.bind(this));
    this.registerMethod("flyTo", this.handleFlyTo.bind(this));
    this.registerMethod("zoomTo", this.handleZoomTo.bind(this));
    this.registerMethod("setCamera", this.handleSetCamera.bind(this));
    this.registerMethod("resetView", this.handleResetView.bind(this));
    this.registerMethod("setVisibility", this.handleSetVisibility.bind(this));
    this.registerMethod("setOpacity", this.handleSetOpacity.bind(this));
  }
  /**
   * Initialize the Cesium viewer.
   */
  async initialize() {
    const accessToken = this.model.get("access_token") || "";
    const center = this.model.get("center") || [0, 0];
    const zoom = this.model.get("zoom") || 2;
    if (accessToken) {
      Cesium.Ion.defaultAccessToken = accessToken;
    }
    const container = document.createElement("div");
    container.style.width = "100%";
    container.style.height = "100%";
    this.el.appendChild(container);
    const height = this.zoomToHeight(zoom);
    this.viewer = new Cesium.Viewer(container, {
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      animation: false,
      timeline: false,
      fullscreenButton: false,
      vrButton: false,
      selectionIndicator: false,
      infoBox: false
    });
    this.viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(center[0], center[1], height)
    });
    const jsCalls = this.model.get("_js_calls");
    if (jsCalls && jsCalls.length > 0) {
      for (const call of jsCalls) {
        await this.executeMethod(call);
      }
    }
    this.model.on("change:_js_calls", () => {
      this.handleJsCallsChange();
    });
    this.model.on("change:center", () => {
      const newCenter = this.model.get("center");
      if (this.viewer) {
        const currentHeight = this.viewer.camera.positionCartographic.height;
        this.viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(newCenter[0], newCenter[1], currentHeight)
        });
      }
    });
  }
  /**
   * Convert zoom level to camera height.
   */
  zoomToHeight(zoom) {
    return 4e7 / Math.pow(2, zoom);
  }
  /**
   * Handle JS calls change.
   */
  handleJsCallsChange() {
    const jsCalls = this.model.get("_js_calls");
    if (jsCalls && jsCalls.length > 0) {
      const lastCall = jsCalls[jsCalls.length - 1];
      this.executeMethod(lastCall);
    }
  }
  /**
   * Execute a method from Python.
   */
  async executeMethod(call) {
    const { method, args, kwargs } = call;
    const handler = this.methodHandlers[method];
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
  // -------------------------------------------------------------------------
  // Basemap/Imagery Handlers
  // -------------------------------------------------------------------------
  handleAddBasemap(args, kwargs) {
    if (!this.viewer) return;
    const url = args[0];
    const name = kwargs.name || "basemap";
    const imageryProvider = new Cesium.UrlTemplateImageryProvider({
      url
    });
    const layer = this.viewer.imageryLayers.addImageryProvider(imageryProvider);
    this.imageryLayers.set(name, layer);
  }
  handleAddImageryLayer(args, kwargs) {
    if (!this.viewer) return;
    const url = kwargs.url;
    const name = kwargs.name || `imagery-${this.imageryLayers.size}`;
    const alpha = kwargs.alpha ?? 1;
    let imageryProvider;
    if (kwargs.type === "wms") {
      imageryProvider = new Cesium.WebMapServiceImageryProvider({
        url,
        layers: kwargs.layers,
        parameters: kwargs.parameters
      });
    } else if (kwargs.type === "wmts") {
      imageryProvider = new Cesium.WebMapTileServiceImageryProvider({
        url,
        layer: kwargs.layer,
        style: kwargs.style || "default",
        tileMatrixSetID: kwargs.tileMatrixSetID
      });
    } else if (kwargs.type === "arcgis") {
      imageryProvider = new Cesium.ArcGisMapServerImageryProvider({
        url
      });
    } else {
      imageryProvider = new Cesium.UrlTemplateImageryProvider({
        url
      });
    }
    const layer = this.viewer.imageryLayers.addImageryProvider(imageryProvider);
    layer.alpha = alpha;
    this.imageryLayers.set(name, layer);
  }
  handleRemoveImageryLayer(args, kwargs) {
    if (!this.viewer) return;
    const [name] = args;
    const layer = this.imageryLayers.get(name);
    if (layer) {
      this.viewer.imageryLayers.remove(layer);
      this.imageryLayers.delete(name);
    }
  }
  // -------------------------------------------------------------------------
  // Terrain Handlers
  // -------------------------------------------------------------------------
  handleSetTerrain(args, kwargs) {
    if (!this.viewer) return;
    const url = kwargs.url;
    const requestVertexNormals = kwargs.requestVertexNormals !== false;
    const requestWaterMask = kwargs.requestWaterMask !== false;
    if (url === "cesium-world-terrain" || !url) {
      this.viewer.scene.setTerrain(
        Cesium.Terrain.fromWorldTerrain({
          requestVertexNormals,
          requestWaterMask
        })
      );
    } else {
      Cesium.CesiumTerrainProvider.fromUrl(url, {
        requestVertexNormals,
        requestWaterMask
      }).then((terrainProvider) => {
        if (this.viewer) {
          this.viewer.terrainProvider = terrainProvider;
        }
      });
    }
  }
  handleRemoveTerrain(args, kwargs) {
    if (!this.viewer) return;
    this.viewer.terrainProvider = new Cesium.EllipsoidTerrainProvider();
  }
  // -------------------------------------------------------------------------
  // 3D Tiles Handlers
  // -------------------------------------------------------------------------
  async handleAdd3DTileset(args, kwargs) {
    if (!this.viewer) return;
    const url = kwargs.url;
    const name = kwargs.name || `tileset-${this.tilesets.size}`;
    const maximumScreenSpaceError = kwargs.maximumScreenSpaceError ?? 16;
    try {
      let tileset;
      if (typeof url === "number" || typeof url === "string" && /^\d+$/.test(url)) {
        tileset = await Cesium.Cesium3DTileset.fromIonAssetId(
          parseInt(url),
          {
            maximumScreenSpaceError
          }
        );
      } else {
        tileset = await Cesium.Cesium3DTileset.fromUrl(url, {
          maximumScreenSpaceError
        });
      }
      this.viewer.scene.primitives.add(tileset);
      this.tilesets.set(name, tileset);
      if (kwargs.flyTo !== false) {
        this.viewer.zoomTo(tileset);
      }
    } catch (error) {
      console.error("Error loading 3D Tileset:", error);
    }
  }
  handleRemove3DTileset(args, kwargs) {
    if (!this.viewer) return;
    const [name] = args;
    const tileset = this.tilesets.get(name);
    if (tileset) {
      this.viewer.scene.primitives.remove(tileset);
      this.tilesets.delete(name);
    }
  }
  // -------------------------------------------------------------------------
  // GeoJSON Handlers
  // -------------------------------------------------------------------------
  async handleAddGeoJSON(args, kwargs) {
    if (!this.viewer) return;
    const data = kwargs.data;
    const name = kwargs.name || `geojson-${this.dataSources.size}`;
    const clampToGround = kwargs.clampToGround !== false;
    const stroke = kwargs.stroke || "#3388ff";
    const strokeWidth = kwargs.strokeWidth ?? 2;
    const fill = kwargs.fill || "rgba(51, 136, 255, 0.5)";
    try {
      const dataSource = await Cesium.GeoJsonDataSource.load(data, {
        stroke: Cesium.Color.fromCssColorString(stroke),
        strokeWidth,
        fill: Cesium.Color.fromCssColorString(fill),
        clampToGround
      });
      await this.viewer.dataSources.add(dataSource);
      this.dataSources.set(name, dataSource);
      if (kwargs.flyTo !== false) {
        this.viewer.zoomTo(dataSource);
      }
    } catch (error) {
      console.error("Error loading GeoJSON:", error);
    }
  }
  handleRemoveDataSource(args, kwargs) {
    if (!this.viewer) return;
    const [name] = args;
    const dataSource = this.dataSources.get(name);
    if (dataSource) {
      this.viewer.dataSources.remove(dataSource);
      this.dataSources.delete(name);
    }
  }
  // -------------------------------------------------------------------------
  // Camera Handlers
  // -------------------------------------------------------------------------
  handleFlyTo(args, kwargs) {
    if (!this.viewer) return;
    const lng = args[0];
    const lat = args[1];
    const height = kwargs.height || this.zoomToHeight(kwargs.zoom || 10);
    const heading = kwargs.heading || 0;
    const pitch = kwargs.pitch || -90;
    const roll = kwargs.roll || 0;
    const duration = kwargs.duration ?? 2;
    this.viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(lng, lat, height),
      orientation: {
        heading: Cesium.Math.toRadians(heading),
        pitch: Cesium.Math.toRadians(pitch),
        roll: Cesium.Math.toRadians(roll)
      },
      duration
    });
  }
  handleZoomTo(args, kwargs) {
    if (!this.viewer) return;
    const target = kwargs.target;
    if (target) {
      const dataSource = this.dataSources.get(target);
      if (dataSource) {
        this.viewer.zoomTo(dataSource);
        return;
      }
      const tileset = this.tilesets.get(target);
      if (tileset) {
        this.viewer.zoomTo(tileset);
        return;
      }
    }
  }
  handleSetCamera(args, kwargs) {
    if (!this.viewer) return;
    const lng = kwargs.longitude || 0;
    const lat = kwargs.latitude || 0;
    const height = kwargs.height || 1e7;
    const heading = kwargs.heading || 0;
    const pitch = kwargs.pitch || -90;
    const roll = kwargs.roll || 0;
    this.viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(lng, lat, height),
      orientation: {
        heading: Cesium.Math.toRadians(heading),
        pitch: Cesium.Math.toRadians(pitch),
        roll: Cesium.Math.toRadians(roll)
      }
    });
  }
  handleResetView(args, kwargs) {
    if (!this.viewer) return;
    this.viewer.camera.flyHome(kwargs.duration ?? 2);
  }
  // -------------------------------------------------------------------------
  // Layer Management Handlers
  // -------------------------------------------------------------------------
  handleSetVisibility(args, kwargs) {
    if (!this.viewer) return;
    const [name, visible] = args;
    const imageryLayer = this.imageryLayers.get(name);
    if (imageryLayer) {
      imageryLayer.show = visible;
      return;
    }
    const tileset = this.tilesets.get(name);
    if (tileset) {
      tileset.show = visible;
      return;
    }
    const dataSource = this.dataSources.get(name);
    if (dataSource) {
      dataSource.show = visible;
      return;
    }
  }
  handleSetOpacity(args, kwargs) {
    if (!this.viewer) return;
    const [name, opacity] = args;
    const imageryLayer = this.imageryLayers.get(name);
    if (imageryLayer) {
      imageryLayer.alpha = opacity;
      return;
    }
  }
  // -------------------------------------------------------------------------
  // Cleanup
  // -------------------------------------------------------------------------
  destroy() {
    if (this.viewer) {
      this.viewer.destroy();
      this.viewer = null;
    }
    this.imageryLayers.clear();
    this.tilesets.clear();
    this.dataSources.clear();
    super.destroy();
  }
};

// src/cesium/index.ts
var renderer = null;
function render({ model, el }) {
  renderer = new CesiumRenderer(model, el);
  renderer.initialize().catch((error) => {
    console.error("Failed to initialize Cesium viewer:", error);
  });
  return () => {
    if (renderer) {
      renderer.destroy();
      renderer = null;
    }
  };
}
var index_default = { render };
export {
  index_default as default,
  render
};
