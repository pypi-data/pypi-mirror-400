ws_url = ws_url.replace("http://", "ws://").replace("https://", "wss://");

let url = ws_url + "/ws?" + params.toString();

let canvas = document.getElementById("layout_canvas");
let context = canvas.getContext("2d");

let message = document.getElementById("message");

let socket = new WebSocket(url);
socket.binaryType = "blob";
let initialized = false;
let editing_waypoints = false;
let waypoints = []; // Client-side waypoints storage in LAYOUT coordinates
let waypointsMeta = {};

// Waypoint editing constants and state (in LAYOUT coordinates)
let START_WAYPOINT = { x: 0, y: 0 };
let STOP_WAYPOINT = { x: 100, y: 30 }; // Changed to layout coords (micrometers, typically)
const START_DIRECTION = "horizontal";
let BEND_RADIUS = 10; // Minimum bend radius in layout units (micrometers)
let currentDirection = START_DIRECTION;
let ghostPoint = null; // For preview line (in layout coordinates)

// Conversion state
let pendingCoordConversion = null; // Stores callback for coordinate conversion
let coordConversionQueue = []; // Queue for coordinate conversion requests

const categoryList = document.getElementById("rdbCategoryOptions");
const cellList = document.getElementById("rdbCellOptions");
cellList.selectedIndex = -1;
categoryList.selectedIndex = -1;

const rdbCategory = document.getElementById("rdbCategory");
const rdbCell = document.getElementById("rdbCell");

const rdbItems = document.getElementById("rdbItems");

let hoverTimer = null;
let hoverTip = true;

// Show/hide waypoint editor info toast
function updateWaypointToast() {
  const toast = document.getElementById("waypoint-toast");
  if (toast) {
    toast.style.display = editing_waypoints ? "block" : "none";
  }
}

async function initializeWebSocket() {
  await new Promise((resolve) => {
    //  Installs a handler called when the connection is established
    socket.onopen = function (evt) {
      let ev = {
        msg: "initialize",
        width: canvas.width,
        height: canvas.height,
      };
      socket.send(JSON.stringify(ev));
      resolve(); // Resolve the promise when the WebSocket is ready
    };
  });

  // Call resizeCanvas the first time
  resizeCanvas();
}

//  Installs a handler for the messages delivered by the web socket
socket.onmessage = async function (evt) {
  let data = evt.data;
  if (typeof data === "string") {
    js = JSON.parse(data);
    if (js.msg == "coord") {
      await setCoordinates(js.x, js.y);
    } else if (js.msg == "initialized") {
      initialized = true;
    } else if (js.msg == "loaded") {
      showLayers(js.layers);
      showMenu(js.modes, js.annotations);
      showCells(js.hierarchy, js.ci);
    } else if (js.msg == "reloaded") {
      showLayers(js.layers);
      showCells(js.hierarchy, js.ci);
    } else if (js.msg == "layer-u") {
      updateLayerImages(js.layers);
    } else if (js.msg == "metainfo") {
      updateMetaInfo(js.metainfo);
    } else if (js.msg == "rdbinfo") {
      updateRdbTab(js.rdbinfo);
    } else if (js.msg == "error") {
      alert(js.details);
    } else if (js.msg == "rdb-items") {
      await updateRdbItems(js.items);
    } else if (js.msg == "moved-instances") {
      // Send message to parent window (existing functionality)
      if (window.parent) {
        let msg = {
          command: "Placement",
          data: {
            coords: js.coords,
            filename: js.filename,
          },
        };
        console.log(`Sending message: ${JSON.stringify(msg)}`);
        window.parent.postMessage(msg, "*");
      }

      // Also send message to VSCode extension
      sendMessageToVSCode({
        type: "instanceMoved",
        message: "Layout instances have been moved",
        coords: js.coords,
        filename: js.filename,
        timestamp: new Date().toISOString(),
      });
    } else if (js.msg == "instance_info") {
      await drawInstToolTip({
        name: js.name,
        cell_name: js.cell_name,
        bbox: js.bbox,
      });
      hoverTip = true;
    } else if (js.msg == "layout-coords" || js.msg == "canvas-coords") {
      // Handle coordinate conversion response
      if (coordConversionQueue.length > 0) {
        const callback = coordConversionQueue.shift();
        if (callback && js.coords) {
          callback(js.coords);
        }
      }
    }
  } else if (initialized) {
    //  incoming blob messages are paint events
    createImageBitmap(data).then(function (image) {
      context.drawImage(image, 0, 0);
      // Redraw waypoints on top of the server-rendered image
      if (editing_waypoints && waypoints.length > 0) {
        drawWaypoints();
      }
    });
  }
};

socket.onclose = (evt) => console.log(`Closed ${evt.code}`);

function mouseEventToJSON(canvas, type, evt) {
  let rect = canvas.getBoundingClientRect();
  let x = evt.clientX - rect.left;
  let y = evt.clientY - rect.top;
  let keys = 0;
  if (evt.shiftKey) {
    keys += 1;
  }
  if (evt.ctrlKey) {
    keys += 2;
  }
  if (evt.altKey) {
    keys += 4;
  }
  return { msg: type, x: x, y: y, b: evt.buttons, k: keys };
}

function sendMouseEvent(canvas, type, evt) {
  if (socket.readyState == WebSocket.OPEN /*OPEN*/) {
    let ev = mouseEventToJSON(canvas, type, evt);
    socket.send(JSON.stringify(ev));
  }
}

function sendHoverInfo(canvas, type, evt) {
  if (socket.readyState == WebSocket.OPEN) {
    let rect = canvas.getBoundingClientRect();
    let x = evt.clientX - rect.left;
    let y = evt.clientY - rect.top;
    socket.send(JSON.stringify({ msg: "hover", x: x, y: y }));
    console.log({ msg: "hover", x: x, y: y });
  }
}

function sendWheelEvent(canvas, type, evt) {
  if (socket.readyState == WebSocket.OPEN /*OPEN*/) {
    let ev = mouseEventToJSON(canvas, type, evt);
    ev.dx = evt.deltaX;
    ev.dy = evt.deltaY;
    ev.dm = evt.deltaMode;
    socket.send(JSON.stringify(ev));
  }
}

function sendKeyEvent(canvas, type, evt) {
  if (socket.readyState == WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        msg: type,
        k: evt.keyCode,
        cc: evt.key.charCodeAt(0),
        key: evt.key,
        b: evt.buttons,
      }),
    );
  }
}

let lastCanvasWidth = 0;
let lastCanvasHeight = 0;

function resizeCanvas() {
  let view = document.getElementById("layout-view");
  let w = canvas.clientWidth;
  let h = canvas.clientHeight;

  view.height = view.parentElement.clientHeight;

  if (lastCanvasWidth !== w || lastCanvasHeight !== h) {
    lastCanvasWidth = w;
    lastCanvasHeight = h;

    canvas.width = w;
    canvas.height = h;

    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ msg: "resize", width: w, height: h }));
    } else if (socket.readyState === WebSocket.CONNECTING) {
    } else {
      console.error(socket.readyState);
    }
  }
}

initializeWebSocket();

setInterval(resizeCanvas, 10); // Call resizeCanvas every 10ms

window.addEventListener("resize", function () {
  if (initialized) {
    resizeCanvas();
  }
});

// Listen for messages from parent window (for iframe embedding)
window.addEventListener("message", function (event) {
  console.log("received message: ", event.data);
  // Optional: Add origin validation here for security
  // if (event.origin !== 'http://localhost:8000') return;

  // Handle start-waypoint-editor command from parent
  if (event.data) {
    let msg;
    if (typeof event.data === "string") {
      msg = JSON.parse(event.data);
    } else {
      msg = event.data;
    }
    if (msg.command === "startWaypoints") {
      const data = msg.data;
      const start = data.start || { x: 0, y: 0 };
      const stop = data.stop || { x: 100, y: 30 };
      const radius = data.radius !== undefined ? data.radius : 10;
      startWaypointEditor(start, stop, radius, data.meta);
    }
  }
});

window.addEventListener("keydown", (ev) => {
  if (ev.key === "l") {
    editing_waypoints = !editing_waypoints;
    if (!editing_waypoints) {
      // Clear waypoints when exiting editing mode
      clearWaypoints();
    } else {
      // Reset to initial state when entering editing mode
      waypoints = [];
      waypointsMeta = {};
      currentDirection = START_DIRECTION;
      ghostPoint = null;
    }

    // Update button appearance
    const waypointBtn = document.getElementById("tool-waypoint");
    if (waypointBtn) {
      if (editing_waypoints) {
        waypointBtn.classList.add("active");
        waypointBtn.setAttribute("title", "Exit Waypoint Editing (L)");
        waypointBtn.setAttribute(
          "data-bs-original-title",
          "Exit Waypoint Editing (L)",
        );
      } else {
        waypointBtn.classList.remove("active");
        waypointBtn.setAttribute("title", "Waypoint Editing (L)");
        waypointBtn.setAttribute(
          "data-bs-original-title",
          "Waypoint Editing (L)",
        );
      }
    }

    updateWaypointToast();
    console.log(`EditingWaypoints: ${editing_waypoints}`);
  } else if (ev.key === "c" && editing_waypoints) {
    // Clear waypoints when 'c' is pressed in editing mode
    clearWaypoints();
    console.log("Waypoints cleared");
  } else if (ev.key === "Escape" && editing_waypoints) {
    // Exit editing mode on Escape
    editing_waypoints = false;
    updateWaypointToast();
    clearWaypoints();
    console.log("Exited waypoint editing mode");
  }
});

let xCoord = document.getElementById("x-coord");
let yCoord = document.getElementById("y-coord");

//  Updates the Menu (modified to update toolbar with server modes)
function showMenu(modes, annotations) {
  console.log("Server provided modes:", modes);

  // Update toolbar buttons to use actual server modes
  // Find move-related mode from server
  const moveMode = modes.find((m) => m.toLowerCase().includes("move"));
  if (moveMode) {
    const moveBtn = document.getElementById("tool-move");
    if (moveBtn) {
      moveBtn.onclick = function () {
        selectTool(moveMode);
      };
    }
  }

  // Find ruler-related modes from server
  const rulerMode = modes.find((m) => m.toLowerCase().includes("ruler"));
  if (rulerMode) {
    const rulerBtn = document.getElementById("tool-ruler");
    if (rulerBtn) {
      rulerBtn.onclick = function () {
        selectTool(rulerMode);
      };
    }
  }

  let index = 0;

  annotations.forEach(function (a) {
    let option = document.createElement("option");
    option.value = index;
    option.text = a;
    index += 1;
  });
}

function selectCell(cell_index) {
  socket.send(
    JSON.stringify({
      msg: "ci-s",
      ci: cell_index,
      "zoom-fit": true,
    }),
  );
}

function selectCellByName(cell_name) {
  let currentURL = new URL(window.location.href);
  currentURL.searchParams.set("cell", cell_name);
  window.history.replaceState({}, "", currentURL.toString());
  socket.send(
    JSON.stringify({
      msg: "cell-s",
      cell: cell_name,
      "zoom-fit": true,
    }),
  );
}

//  Updates the layer list
function showCells(cells, current_index) {
  let layerElement = document.getElementById("cells-tab-pane");
  layerElement.replaceChildren();
  appendCells(layerElement, cells, current_index);
}

//  create table rows for each layer
function appendCells(parentelement, cells, current_index, addpaddings = false) {
  let lastelement = null;

  cells.forEach(function (c, i) {
    let cellRow = document.createElement("div");
    cellRow.className = "row mx-0";
    parentelement.appendChild(cellRow);
    if (c.children.length > 0) {
      let accordion = document.createElement("div");

      if (addpaddings) {
        accordion.className = "accordion accordion-flush px-2";
      } else {
        accordion.className = "accordion accordion-flush ps-2 pe-0";
      }
      accordion.id = "cellgroup-" + c.id;

      cellRow.appendChild(accordion);

      accordion_item = document.createElement("div");
      accordion_item.className = "accordion-item";
      accordion.appendChild(accordion_item);

      accordion_header = document.createElement("div");
      accordion_header.className = "accordion-header d-flex flex-row";
      accordion_item.appendChild(accordion_header);

      accordion_header_button = document.createElement("button");
      accordion_header_button.className =
        "accordion-button collapsed p-0 w-auto border-bottom";
      accordion_header_button.setAttribute("type", "button");
      accordion_header_button.setAttribute("data-bs-toggle", "collapse");
      accordion_header_button.setAttribute(
        "data-bs-target",
        "#collapseGroup" + c.id,
      );
      accordion_header_button.setAttribute("aria-expanded", "false");
      accordion_header_button.setAttribute(
        "aria-controls",
        "collapseGroup" + c.id,
      );
      let cell_name_button = document.createElement("input");
      cell_name_button.className = "btn-check";
      cell_name_button.setAttribute("type", "radio");
      cell_name_button.setAttribute("name", "option-base");
      cell_name_button.id = "cell-" + c.id;
      cell_name_button.setAttribute("autocomplete", "off");
      if (c.id == current_index) {
        cell_name_button.setAttribute("checked", "");
      }
      cell_name_button.addEventListener("change", function () {
        selectCellByName(c.name);
      });
      let cell_name = document.createElement("label");
      cell_name.innerHTML = c.name;
      cell_name.className = "btn btn-dark w-100 text-start p-0";
      cell_name.setAttribute("for", "cell-" + c.id);
      accordion_row = document.createElement("div");
      accordion_row.className = "mx-0 border-bottom flex-grow-1";
      accordion_row.appendChild(cell_name_button);
      accordion_row.appendChild(cell_name);
      accordion_header.appendChild(accordion_row);

      accordion_header.appendChild(accordion_header_button);

      accordion_collapse = document.createElement("div");
      accordion_collapse.className = "accordion-collapse collapse";
      accordion_collapse.setAttribute("data-bs-parent", "#" + accordion.id);
      accordion_collapse.id = "collapseGroup" + c.id;
      accordion_item.appendChild(accordion_collapse);

      accordion_body = document.createElement("div");
      accordion_body.className = "accordion-body p-0";
      accordion_collapse.appendChild(accordion_body);

      appendCells(accordion_body, c.children, current_index, true);
      lastelement = accordion;
    } else {
      let cell_name_button = document.createElement("input");
      cell_name_button.className = "btn-check";
      cell_name_button.setAttribute("type", "radio");
      cell_name_button.setAttribute("name", "option-base");
      cell_name_button.id = "cell-" + c.id;
      cell_name_button.setAttribute("autocomplete", "off");
      cell_name_button.addEventListener("change", function () {
        selectCellByName(c.name);
      });
      if (c.id == current_index) {
        cell_name_button.setAttribute("checked", "");
      }
      let cell_name = document.createElement("label");
      cell_name.innerHTML = c.name;
      cell_name.className = "btn btn-dark text-start p-0";
      cell_name.setAttribute("for", "cell-" + c.id);
      accordion_row = document.createElement("div");
      accordion_row = document.createElement("row");
      accordion_row.className = "row mx-0";
      accordion_row.appendChild(cell_name_button);
      accordion_row.appendChild(cell_name);

      let accordion = document.createElement("div");
      if (addpaddings) {
        accordion.className = "accordion accordion-flush ps-2 pe-0";
      } else {
        accordion.className = "accordion accordion-flush px-0";
      }
      accordion.id = "cellgroup-" + c.id;
      cellRow.appendChild(accordion);

      accordion_item = document.createElement("div");
      accordion_item.className = "accordion-item";
      accordion.appendChild(accordion_item);

      accordion_header = document.createElement("div");
      accordion_header.className = "accordion-header";
      accordion_item.appendChild(accordion_header);
      accordion_header.appendChild(accordion_row);

      lastelement = accordion;
    }
  });

  if (addpaddings && lastelement) {
    lastelement.classList.add("pb-2");
  }
}
//  Updates the layer list
function showLayers(layers) {
  // Store layers globally for bulk operations
  globalLayers = layers;

  let layerElement = document.getElementById("layers-tab-pane");
  let layerButtons = document.getElementById("layer-buttons");

  let layerSwitch = document.getElementById("layerEmptySwitch");
  let layerNumberSwitch = document.getElementById("layerNumberSwitch");

  let layerTable =
    document.getElementById("table-layer") || document.createElement("div");
  layerTable.id = "table-layer";
  layerTable.className = "container-fluid text-left px-0 pb-2";
  layerTable.replaceChildren();
  layerElement.replaceChildren(layerButtons, layerTable);

  appendLayers(
    layerTable,
    layers,
    (addempty = !layerSwitch.checked),
    (addpaddings = true),
    (showLayerNumbers = layerNumberSwitch.checked),
  );
  for (let i = 0; i < 2; i++) {
    const switchElement = [layerSwitch, layerNumberSwitch][i];
    switchElement.addEventListener("change", function () {
      layerTable.replaceChildren();
      appendLayers(
        layerTable,
        globalLayers,
        (addempty = !layerSwitch.checked),
        (addpaddings = true),
        (showLayerNumbers = layerNumberSwitch.checked),
      );
    });
  }
}
//  create table rows for each layer
function appendLayers(
  parentelement,
  layers,
  addempty = false,
  addpaddings = false,
  showLayerNumbers = false,
) {
  let lastelement = null;

  layers.forEach(function (l, i) {
    if (addempty || !l.empty) {
      let layerRow = document.createElement("div");
      layerRow.className = "row mx-0";
      parentelement.appendChild(layerRow);
      if ("children" in l) {
        let accordion = document.createElement("div");

        if (addpaddings) {
          accordion.className = "accordion accordion-flush px-2";
        } else {
          accordion.className = "accordion accordion-flush ps-2 pe-0";
        }
        accordion.id = "layergroup-" + l.id;

        layerRow.appendChild(accordion);

        accordion_item = document.createElement("div");
        accordion_item.className = "accordion-item";
        accordion.appendChild(accordion_item);

        accordion_header = document.createElement("div");
        accordion_header.className = "accordion-header d-flex flex-row";
        accordion_item.appendChild(accordion_header);

        accordion_header_button = document.createElement("button");
        accordion_header_button.className =
          "accordion-button collapsed p-0 flex-grow-1";
        accordion_header_button.setAttribute("type", "button");
        accordion_header_button.setAttribute("data-bs-toggle", "collapse");
        accordion_header_button.setAttribute(
          "data-bs-target",
          "#collapseGroup" + l.id,
        );
        accordion_header_button.setAttribute("aria-expanded", "false");
        accordion_header_button.setAttribute(
          "aria-controls",
          "collapseGroup" + l.id,
        );
        let img_cont = document.createElement("div");
        img_cont.className = "col-auto p-0 align-items-center";
        let layer_image = document.createElement("img");
        layer_image.src = "data:image/png;base64," + l.img;
        // layer_image.style = "max-width: 100%;";
        layer_image.id = "layer-img-" + l.id;
        layer_image.className = "layer-img";

        function click_layer_img() {
          l.v = !l.v;
          let ev = { msg: "layer-v", id: l.id, value: l.v };
          socket.send(JSON.stringify(ev));
        }

        layer_image.addEventListener("click", click_layer_img);
        layer_image.addEventListener("contextmenu", function (event) {
          event.preventDefault();
          event.stopPropagation();
          showLayerContextMenu(event, l.id);
        });

        img_cont.appendChild(layer_image);
        let layer_name = document.createElement("div");
        layer_name.textContent = l.name;
        layer_name.className = "col text-nowrap r-text";
        let layer_source = document.createElement("div");
        layer_source.textContent = l.s;
        layer_source.className = "col-auto text-nowrap r-text";
        accordion_row = document.createElement("div");
        accordion_row.className =
          "row mx-0 flex-nowrap justify-content-center align-items-center";
        accordion_row.addEventListener("contextmenu", function (event) {
          event.preventDefault();
          event.stopPropagation();
          showLayerContextMenu(event, l.id);
        });
        accordion_header.insertBefore(img_cont, accordion_header.firstChild);
        accordion_row.appendChild(layer_name);
        accordion_row.appendChild(layer_source);
        accordion_header_button.appendChild(accordion_row);

        accordion_header.appendChild(accordion_header_button);

        accordion_collapse = document.createElement("div");
        accordion_collapse.className = "accordion-collapse collapse";
        accordion_collapse.setAttribute("data-bs-parent", "#" + accordion.id);
        accordion_collapse.id = "collapseGroup" + l.id;
        accordion_item.appendChild(accordion_collapse);

        accordion_body = document.createElement("div");
        accordion_body.className = "accordion-body p-0";
        accordion_collapse.appendChild(accordion_body);

        appendLayers(accordion_body, l.children, (addempty = addempty));
        lastelement = accordion;
      } else {
        let img_cont = document.createElement("div");
        img_cont.className = "col-auto p-0";
        let layer_image = document.createElement("img");
        layer_image.src = "data:image/png;base64," + l.img;
        // layer_image.style = "max-width: 100%;";
        layer_image.id = "layer-img-" + l.id;
        layer_image.className = "layer-img";
        function click_layer_img() {
          l.v = !l.v;
          let ev = { msg: "layer-v", id: l.id, value: l.v };
          socket.send(JSON.stringify(ev));
        }

        layer_image.addEventListener("click", click_layer_img);
        layer_image.addEventListener("contextmenu", function (event) {
          event.preventDefault();
          event.stopPropagation();
          showLayerContextMenu(event, l.id);
        });
        img_cont.appendChild(layer_image);
        let layer_name = document.createElement("div");
        layer_name.textContent = l.name;
        layer_name.className = "col text-nowrap r-text";
        let layer_source = document.createElement("div");
        layer_source.innerHTML = String(l.s).split("@")[0];
        layer_source.className = "col-auto pe-0 text-nowrap r-text";
        accordion_row = document.createElement("row");
        accordion_row.className =
          "row mx-0 p-0 flex-nowrap justify-content-center align-items-center";
        accordion_row.addEventListener("contextmenu", function (event) {
          event.preventDefault();
          event.stopPropagation();
          showLayerContextMenu(event, l.id);
        });
        accordion_row.appendChild(img_cont);
        accordion_row.appendChild(layer_name);
        if (showLayerNumbers) {
          accordion_row.appendChild(layer_source);
        }

        let accordion = document.createElement("div");
        if (addpaddings) {
          accordion.className = "accordion accordion-flush px-2";
        } else {
          accordion.className = "accordion accordion-flush ps-2 pe-0";
        }
        accordion.id = "layergroup-" + l.id;
        layerRow.appendChild(accordion);

        accordion_item = document.createElement("div");
        accordion_item.className = "accordion-item";
        accordion.appendChild(accordion_item);

        accordion_header = document.createElement("div");
        accordion_header.className = "accordion-header";
        accordion_item.appendChild(accordion_header);
        accordion_header.appendChild(accordion_row);

        lastelement = accordion;
      }
    }
  });

  if (addpaddings && lastelement) {
    lastelement.classList.add("pb-2");
  }
}

function updateLayerImages(layers) {
  layers.forEach(function (l) {
    let layer_image = document.getElementById("layer-img-" + l.id);
    layer_image.src = "data:image/png;base64," + l.img;

    if ("children" in l) {
      updateLayerImages(l.children);
    }
  });
}

async function updateMetaInfo(metainfo) {
  const metaInfoPane = document.getElementById("metainfo-tab-pane");
  const metaInfoButton = document.getElementById("metainfo-tab");
  metaInfoPane.replaceChildren();
  let metaRow = document.createElement("div");
  metaRow.className = "row mx-0";
  metaInfoPane.appendChild(metaRow);

  let hideMeta = true;

  let entry = { index: 0 };

  for (const [key, value] of Object.entries(metainfo)) {
    metaRow.appendChild(await addAccordion(entry, key, value));
    hideMeta = false;
  }

  metaInfoButton.hidden = hideMeta;
}

async function addAccordion(entry, jsonKey, jsonValue, addpaddings = false) {
  let accordion = document.createElement("div");
  let i = entry.index;

  if (addpaddings) {
    accordion.className = "accordion accordion-flush px-2";
  } else {
    accordion.className = "accordion accordion-flush ps-2 pe-0";
  }
  accordion.id = "metaGroup" + i;

  let accordion_item = document.createElement("div");
  accordion_item.className = "accordion-item";
  accordion.appendChild(accordion_item);

  let accordion_header = document.createElement("div");
  accordion_header.className = "accordion-header d-flex flex-row";
  accordion_item.appendChild(accordion_header);

  let accordion_collapse = document.createElement("div");
  accordion_collapse.className = "accordion-collapse collapse";
  accordion_collapse.setAttribute("data-bs-parent", "#" + accordion.id);
  accordion_collapse.id = "collapseGroupMeta" + i;
  accordion_item.appendChild(accordion_collapse);

  let accordion_body = document.createElement("div");
  accordion_body.className = "accordion-body p-0";
  accordion_collapse.appendChild(accordion_body);

  entry.index += 1;

  if (typeof jsonValue === "object") {
    let accordion_header_button = document.createElement("button");
    accordion_header_button.className =
      "accordion-button collapsed p-0 w-auto border-bottom";
    accordion_header_button.setAttribute("type", "button");
    accordion_header_button.setAttribute("data-bs-toggle", "collapse");
    accordion_header_button.setAttribute(
      "data-bs-target",
      "#collapseGroupMeta" + i,
    );
    accordion_header_button.setAttribute("aria-expanded", "false");
    accordion_header_button.setAttribute(
      "aria-controls",
      "collapseGroupMeta" + i,
    );
    accordion_header_button.textContent = jsonKey;

    accordion_header.appendChild(accordion_header_button);
    for (const [key, value] of Object.entries(jsonValue)) {
      accordion_body.appendChild(await addAccordion(entry, key, value));
    }
  } else {
    accordion_body.textContent = `${jsonKey}: ${jsonValue}`;
    accordion_collapse.classList.add("show");
  }

  return accordion;
}

async function updateRdbTab(rdbinfo) {
  const rdbButton = document.getElementById("rdb-tab");
  rdbButton.hidden = false;

  categoryList.replaceChildren();
  cellList.replaceChildren();

  for (const [category, id] of Object.entries(rdbinfo.categories)) {
    opt = document.createElement("option");
    opt.value = id;
    opt.textContent = category;
    categoryList.appendChild(opt);
  }
  for (const [cell, id] of Object.entries(rdbinfo.cells)) {
    opt = document.createElement("option");
    opt.value = id;
    opt.textContent = cell;
    cellList.appendChild(opt);
  }
}

function categoryFocus(event) {
  categoryList.hidden = false;
}
function categoryFocusOut(event) {
  if (event.relatedTarget != categoryList) {
    categoryList.hidden = true;
  }
}
function cellFocus(event) {
  cellList.hidden = false;
}
function cellFocusOut(event) {
  if (event.relatedTarget != cellList) {
    cellList.hidden = true;
  }
}

async function filterCategories(input) {
  let value = input.value;
  if (value === "") {
    categoryList.options.selectedIndex = -1;
    for (let i = 0; i < categoryList.options.length; i++) {
      let option = categoryList.options[i];
      option.hidden = false;
    }
  } else {
    let regex = new RegExp(input.value, "i");
    let selected = false;
    for (let i = 0; i < categoryList.options.length; i++) {
      let option = categoryList.options[i];
      if (regex.test(option.text)) {
        option.hidden = false;
        if (option.text === input.value) {
          selected = true;
          categoryList.options.selectedIndex = i;
        }
      } else {
        option.hidden = true;
      }
      if (!selected) {
        categoryList.options.selectedIndex = -1;
      }
    }
  }
}
async function selectCategory(event) {
  let index = event.target.selectedIndex;
  if (index >= 0) {
    let option = event.target.options[index];
    rdbCategory.value = option.text;
  }
  await sendRdbCategoryAndCell();
}
async function filterCells(input) {
  let value = input.value;
  if (value === "") {
    cellList.options.selectedIndex = -1;
    for (let i = 0; i < cellList.options.length; i++) {
      let option = cellList.options[i];
      option.hidden = false;
    }
  } else {
    let regex = new RegExp(input.value, "i");
    let selected = false;
    for (let i = 0; i < cellList.options.length; i++) {
      let option = cellList.options[i];
      if (regex.test(option.text)) {
        option.hidden = false;
        if (option.text === input.value) {
          selected = true;
          cellList.options.selectedIndex = i;
        }
      } else {
        option.hidden = true;
      }
      if (!selected) {
        cellList.options.selectedIndex = -1;
      }
    }
  }
}
async function selectCell(event) {
  let index = event.target.selectedIndex;
  if (index >= 0) {
    let option = event.target.options[index];
    rdbCell.value = option.text;
  }
  await sendRdbCategoryAndCell();
}

async function updateRdbItems(items) {
  rdbItems.replaceChildren();

  for (const [id, tags] of Object.entries(items)) {
    let option = document.createElement("option");
    option.value = id;
    option.text = tags;
    rdbItems.appendChild(option);
  }
}

async function setCoordinates(x, y) {
  // console.log({"x": x, "y": y})
  xCoord.textContent = x.toFixed(3);
  yCoord.textContent = y.toFixed(3);
}

async function requestItemDrawings() {
  let json = { msg: "rdb-selected", items: {} };
  for (let i = 0; i < rdbItems.options.length; i++) {
    json.items[i] = rdbItems.options[i].selected;
  }
  socket.send(JSON.stringify(json));
}

async function sendRdbCategoryAndCell() {
  let categoryIndex = categoryList.selectedIndex;
  let cellIndex = cellList.selectedIndex;
  let category_id = null;
  let cell_id = null;
  if (cellIndex != -1) {
    cell_id = +cellList.options[cellIndex].value;
  }
  if (categoryIndex != -1) {
    category_id = +categoryList.options[categoryIndex].value;
  }
  socket.send(
    JSON.stringify({
      msg: "rdb-records",
      category_id: category_id,
      cell_id: cell_id,
    }),
  );
}

// Test function to send LYRDB data via WebSocket
function sendLyrdb(lyrdbData) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log("Sending LYRDB data to server...");
    socket.send(
      JSON.stringify({
        msg: "load-rdb-xml",
        xml_data: lyrdbData,
        flush_existing: true,
      }),
    );
    console.log("LYRDB data sent!");
  } else {
    console.error("WebSocket is not connected");
  }
}

async function drawInstToolTip(hoverTip) {
  context.strokeStyle = "black";
  context.lineWidth = 5;
  let rect = hoverTip.bbox;
  context.strokeRect(rect.x, rect.y, rect.width, rect.height);
  context.strokeStyle = "white";
  context.lineWidth = 3;
  context.strokeRect(rect.x, rect.y, rect.width, rect.height);

  const fontSize = 10;
  context.font = `${fontSize}px Arial`;
  context.textAlign = "center";
  context.textBaseline = "middle";

  // // Draw black border
  // context.strokeStyle = "black";
  // context.lineWidth = 4; // Border thickness
  // context.strokeText(text, centerX, centerY);

  // // Draw white text
  // context.fillStyle = "white";
  // context.fillText(js.x, centerY);

  lines = [`Instance: ${js.name}`, `Cell: ${js.cell_name}`];
  const lineHeight = fontSize * 1.2;

  // Calculate starting Y position to center text block
  const startY = js.y - ((lines.length - 1) * lineHeight) / 2;

  lines.forEach((line, index) => {
    const lineY = startY + index * lineHeight; // Y position for each line

    // Draw black border
    context.strokeStyle = "black";
    context.lineWidth = 4;
    context.strokeText(line, js.x, lineY);

    // Draw white text
    context.fillStyle = "white";
    context.fillText(line, js.x, lineY);
  });
}

let showPorts = 0; // 0: hide all 1: show cell ports 2: show all
let showText = true;
let darkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
let portToggleBtn = document.getElementById("port-toggle-btn");
let portShowAllBtn = document.getElementById("port-show-all-btn");
let txtToggleBtn = document.getElementById("text-toggle-btn");
let darkModeBtn = document.getElementById("darkmode-btn");
let darkModeIcon = document.getElementById("darkmode-icon");
async function togglePorts() {
  if (showPorts === 0) {
    socket.send(JSON.stringify({ msg: "show-ports", hierarchy: [0, 0] }));
    showPorts = 1;
    console.log("set ports to 1");
  } else {
    socket.send(JSON.stringify({ msg: "show-ports", hierarchy: [-1, -1] }));
    showPorts = 0;
    console.log("set ports to 0");
  }
  updatePortButtonAppearance();
}

async function showAllPorts() {
  socket.send(JSON.stringify({ msg: "show-ports", hierarchy: [0, -1] }));
  showPorts = 2;
  console.log("set ports to 2 (show all)");
  updatePortButtonAppearance();
}

async function showCellPorts(event) {
  let portData = document.getElementById("show-ports");
  socket.send(
    JSON.stringify({
      msg: "show-ports",
      hierarchy: [0, portData.data("ports")],
    }),
  );
}

async function toggleText() {
  showText = !showText;
  socket.send(JSON.stringify({ msg: "show-text", show: showText }));
  if (showText) {
    txtToggleBtn.classList.add("active");
    txtToggleBtn.setAttribute("title", "Hide Text Labels");
    txtToggleBtn.setAttribute("data-bs-original-title", "Hide Text Labels");
  } else {
    txtToggleBtn.classList.remove("active");
    txtToggleBtn.setAttribute("title", "Show Text Labels");
    txtToggleBtn.setAttribute("data-bs-original-title", "Show Text Labels");
  }
}

async function toggleDarkMode() {
  darkMode = !darkMode;
  if (darkMode) {
    socket.send(JSON.stringify({ msg: "dark-mode", color: "auto" }));
    darkModeBtn.setAttribute("title", "Switch to Light Mode");
    darkModeBtn.setAttribute("data-bs-original-title", "Switch to Light Mode");
    darkModeIcon.classList.replace("bi-sun-fill", "bi-moon-stars-fill");
  } else {
    socket.send(JSON.stringify({ msg: "dark-mode", color: "#FFFFFF" }));
    darkModeBtn.setAttribute("title", "Switch to Dark Mode");
    darkModeBtn.setAttribute("data-bs-original-title", "Switch to Dark Mode");
    darkModeIcon.classList.replace("bi-moon-stars-fill", "bi-sun-fill");
    console.log(darkModeBtn.children[0]);
  }
}

// Update button appearance based on port visibility state
function updatePortButtonAppearance() {
  if (portToggleBtn) {
    if (showPorts === 0) {
      portToggleBtn.classList.remove("active");
      portToggleBtn.setAttribute("title", "Show Ports");
      portToggleBtn.setAttribute("data-bs-original-title", "Show Ports");
    } else {
      portToggleBtn.classList.add("active");
      portToggleBtn.setAttribute("title", "Hide Ports");
      portToggleBtn.setAttribute("data-bs-original-title", "Hide Ports");
    }
  }

  if (portShowAllBtn) {
    if (showPorts === 2) {
      portShowAllBtn.classList.add("active");
    } else {
      portShowAllBtn.classList.remove("active");
    }
  }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
  // Initialize tooltips for all elements with data-bs-toggle="tooltip"
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]',
  );
  const tooltipList = [...tooltipTriggerList].map(
    (tooltipTriggerEl) =>
      new bootstrap.Tooltip(tooltipTriggerEl, {
        trigger: "hover", // Only show on hover, not on focus/click
        delay: { show: 100, hide: 0 }, // Quick hide, slight delay on show
        animation: false, // No animation for instant response
        placement: "bottom", // Consistent placement
      }),
  );
  console.log("Initialized", tooltipList.length, "tooltips");
}

const sideBarButton = document.getElementById("side-bar-btn");
const sideBar = document.getElementById("rightpanel");
async function toggleSideBar() {
  if (sideBar.classList.contains("show")) {
    sideBar.classList.remove("show");
    sideBarButton.textContent = "<";
  } else {
    sideBar.classList.add("show");
    sideBarButton.textContent = ">";
  }
}
sideBarButton.addEventListener("click", toggleSideBar);

// Layer visibility control functions
let globalLayers = []; // Store the layers globally for bulk operations
let selectedLayerId = null; // Store the currently selected layer for context menu

function showAllLayers() {
  setAllLayersVisibility(true);
}

function hideAllLayers() {
  setAllLayersVisibility(false);
}

function showOnlySelectedLayer() {
  if (!selectedLayerId || globalLayers.length === 0) {
    console.warn("No layer selected or no layers available");
    return;
  }

  // First hide all layers
  setLayersVisibilityRecursive(globalLayers, false);

  // Then show only the selected layer
  const selectedLayer = findLayerById(globalLayers, selectedLayerId);
  if (selectedLayer) {
    selectedLayer.v = true;
    let ev = { msg: "layer-v", id: selectedLayer.id, value: true };
    socket.send(JSON.stringify(ev));
  }
}

function findLayerById(layers, targetId) {
  for (const layer of layers) {
    if (layer.id === targetId) {
      return layer;
    }
    if ("children" in layer) {
      const found = findLayerById(layer.children, targetId);
      if (found) return found;
    }
  }
  return null;
}

function showLayerContextMenu(event, layerId) {
  event.preventDefault();
  event.stopPropagation();
  event.stopImmediatePropagation();

  selectedLayerId = layerId;

  const contextMenu = document.getElementById("layerContextMenu");
  contextMenu.style.display = "block";
  contextMenu.style.left = event.pageX + "px";
  contextMenu.style.top = event.pageY + "px";

  // Close menu when clicking elsewhere
  document.addEventListener("click", hideLayerContextMenu, { once: true });
}

function hideLayerContextMenu() {
  const contextMenu = document.getElementById("layerContextMenu");
  if (contextMenu) {
    contextMenu.style.display = "none";
  }
  selectedLayerId = null;
}

function setAllLayersVisibility(visible) {
  if (globalLayers.length === 0) {
    console.warn("No layers available for bulk visibility change");
    return;
  }

  setLayersVisibilityRecursive(globalLayers, visible);
}

function setLayersVisibilityRecursive(layers, visible) {
  layers.forEach(function (layer) {
    // Only change visibility if it's different from the target state
    if (layer.v !== visible) {
      layer.v = visible;
      // Send message to server to update layer visibility
      let ev = { msg: "layer-v", id: layer.id, value: layer.v };
      socket.send(JSON.stringify(ev));
    }

    // Recursively handle child layers
    if ("children" in layer) {
      setLayersVisibilityRecursive(layer.children, visible);
    }
  });
}

// Helper function to convert canvas coordinates to layout coordinates
async function canvasToLayout(canvasCoords) {
  return new Promise((resolve, reject) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      reject(new Error("WebSocket not connected"));
      return;
    }
    coordConversionQueue.push(resolve);
    socket.send(
      JSON.stringify({
        msg: "convert-coords",
        canvas_coords: canvasCoords,
      }),
    );
    // Add timeout to prevent hanging
    setTimeout(() => {
      const idx = coordConversionQueue.indexOf(resolve);
      if (idx !== -1) {
        coordConversionQueue.splice(idx, 1);
        reject(new Error("Coordinate conversion timeout"));
      }
    }, 1000);
  });
}

// Helper function to convert layout coordinates to canvas coordinates
async function layoutToCanvas(layoutCoords) {
  return new Promise((resolve, reject) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      reject(new Error("WebSocket not connected"));
      return;
    }
    coordConversionQueue.push(resolve);
    socket.send(
      JSON.stringify({
        msg: "convert-coords",
        layout_coords: layoutCoords,
      }),
    );
    // Add timeout to prevent hanging
    setTimeout(() => {
      const idx = coordConversionQueue.indexOf(resolve);
      if (idx !== -1) {
        coordConversionQueue.splice(idx, 1);
        reject(new Error("Coordinate conversion timeout"));
      }
    }, 1000);
  });
}

// Function to start waypoint editor with custom parameters
function startWaypointEditor(start, stop, radius, meta) {
  console.log("Starting waypoint editor with parameters:", {
    start,
    stop,
    radius,
  });
  // Set the waypoint editor parameters
  START_WAYPOINT = { x: start.x, y: start.y };
  STOP_WAYPOINT = { x: stop.x, y: stop.y };
  BEND_RADIUS = radius;

  // Reset waypoint editor state
  waypoints = [];
  waypointsMeta = meta;
  currentDirection = START_DIRECTION;
  ghostPoint = null;

  // Enable waypoint editing mode
  editing_waypoints = true;
  updateWaypointToast();

  // Update button appearance
  const waypointBtn = document.getElementById("tool-waypoint");
  if (waypointBtn) {
    waypointBtn.classList.add("active");
    waypointBtn.setAttribute("title", "Exit Waypoint Editing (L)");
    waypointBtn.setAttribute(
      "data-bs-original-title",
      "Exit Waypoint Editing (L)",
    );
  }

  // Trigger initial redraw to show start/stop markers
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ msg: "redraw" }));
    setTimeout(drawWaypoints, 50);
  }
}

// Waypoint management functions
async function addWaypoint(evt) {
  const rect = canvas.getBoundingClientRect();
  const mouseX = evt.clientX - rect.left;
  const mouseY = evt.clientY - rect.top;

  try {
    // Convert canvas coords to layout coords
    const layoutCoords = await canvasToLayout([{ x: mouseX, y: mouseY }]);
    if (!layoutCoords || !layoutCoords[0]) {
      console.error(
        "Failed to convert canvas coordinates to layout coordinates",
      );
      return;
    }
    const layoutPoint = layoutCoords[0];

    // Initialize waypoints with START_WAYPOINT if empty
    if (waypoints.length === 0) {
      waypoints.push({ ...START_WAYPOINT });
      currentDirection = START_DIRECTION;
    }

    // Get the last waypoint (in layout coordinates)
    const lastWaypoint = waypoints[waypoints.length - 1];

    // Constrain new waypoint to current direction (in layout coordinates)
    // and enforce minimum bend radius
    let newWaypoint;
    let snapped = false;
    if (currentDirection === "horizontal") {
      // Horizontal movement: keep Y same as last waypoint, use mouse X
      let newX = layoutPoint.x;

      // Enforce minimum bend radius
      const distance = Math.abs(newX - lastWaypoint.x);
      if (distance < BEND_RADIUS) {
        // Snap to minimum bend radius
        newX = lastWaypoint.x + Math.sign(newX - lastWaypoint.x) * BEND_RADIUS;
        snapped = true;
      }

      newWaypoint = { x: newX, y: lastWaypoint.y };
      currentDirection = "vertical"; // Next direction will be vertical
    } else {
      // Vertical movement: keep X same as last waypoint, use mouse Y
      let newY = layoutPoint.y;

      // Enforce minimum bend radius
      const distance = Math.abs(newY - lastWaypoint.y);
      if (distance < BEND_RADIUS) {
        // Snap to minimum bend radius
        newY = lastWaypoint.y + Math.sign(newY - lastWaypoint.y) * BEND_RADIUS;
        snapped = true;
      }

      newWaypoint = { x: lastWaypoint.x, y: newY };
      currentDirection = "horizontal"; // Next direction will be horizontal
    }

    waypoints.push(newWaypoint);
    const snapMsg = snapped
      ? ` (snapped to min bend radius ${BEND_RADIUS})`
      : "";
    console.log(
      `Added waypoint at layout coords (${newWaypoint.x.toFixed(3)}, ${newWaypoint.y.toFixed(3)})${snapMsg}. Direction: ${currentDirection}. Total waypoints: ${waypoints.length}`,
    );

    // Clear ghost point since we've placed a waypoint
    ghostPoint = null;

    // Redraw canvas to show the updated waypoints
    redrawWaypoints();
  } catch (error) {
    console.error("Error adding waypoint:", error);
  }
}

function clearWaypoints() {
  waypoints = [];
  waypointsMeta = {};
  currentDirection = START_DIRECTION;
  ghostPoint = null;
  // Request a fresh canvas redraw from server
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ msg: "redraw" }));
  }
}

async function updateGhostPoint(mouseX, mouseY) {
  if (!editing_waypoints) {
    ghostPoint = null;
    return;
  }

  try {
    // Convert canvas coords to layout coords
    const layoutCoords = await canvasToLayout([{ x: mouseX, y: mouseY }]);
    if (!layoutCoords || !layoutCoords[0]) {
      // Silently ignore conversion failures during mouse move
      return;
    }
    const layoutPoint = layoutCoords[0];

    // Initialize waypoints with START_WAYPOINT if empty
    if (waypoints.length === 0) {
      // For the first point, ghost line follows current direction from START_WAYPOINT
      if (currentDirection === "horizontal") {
        ghostPoint = { x: layoutPoint.x, y: START_WAYPOINT.y };
      } else {
        ghostPoint = { x: START_WAYPOINT.x, y: layoutPoint.y };
      }
      return;
    }

    // Get the last waypoint (in layout coordinates)
    const lastWaypoint = waypoints[waypoints.length - 1];

    // Constrain ghost point to current direction (in layout coordinates)
    // and show bend radius constraint
    if (currentDirection === "horizontal") {
      // Horizontal movement: keep Y same as last waypoint, use mouse X
      let ghostX = layoutPoint.x;

      // Apply bend radius constraint to ghost point
      const distance = Math.abs(ghostX - lastWaypoint.x);
      if (distance < BEND_RADIUS && distance > 0) {
        // Snap ghost to minimum bend radius to show where click would place waypoint
        ghostX =
          lastWaypoint.x + Math.sign(ghostX - lastWaypoint.x) * BEND_RADIUS;
      }

      ghostPoint = { x: ghostX, y: lastWaypoint.y };
    } else {
      // Vertical movement: keep X same as last waypoint, use mouse Y
      let ghostY = layoutPoint.y;

      // Apply bend radius constraint to ghost point
      const distance = Math.abs(ghostY - lastWaypoint.y);
      if (distance < BEND_RADIUS && distance > 0) {
        // Snap ghost to minimum bend radius to show where click would place waypoint
        ghostY =
          lastWaypoint.y + Math.sign(ghostY - lastWaypoint.y) * BEND_RADIUS;
      }

      ghostPoint = { x: lastWaypoint.x, y: ghostY };
    }
  } catch (error) {
    // Silently ignore errors during mouse move to avoid console spam
  }
}

function calculatePathToStop() {
  if (!editing_waypoints) return null;

  // Get the current position (either ghost point or last waypoint)
  let currentPoint;
  if (ghostPoint) {
    currentPoint = ghostPoint;
  } else if (waypoints.length > 0) {
    currentPoint = waypoints[waypoints.length - 1];
  } else {
    currentPoint = START_WAYPOINT;
  }

  // Calculate the path to STOP_WAYPOINT following straight-line rules
  const path = [];

  // If we're already at the stop waypoint, no path needed
  if (
    currentPoint.x === STOP_WAYPOINT.x &&
    currentPoint.y === STOP_WAYPOINT.y
  ) {
    return path;
  }

  // The guide line should start perpendicular to the current ghost line
  // So we use the NEXT direction (which is perpendicular to current direction)
  let nextDirection =
    currentDirection === "horizontal" ? "vertical" : "horizontal";
  let virtualWaypoint = null;

  if (nextDirection === "horizontal") {
    // Move horizontally first, then vertically
    if (currentPoint.x !== STOP_WAYPOINT.x) {
      virtualWaypoint = { x: STOP_WAYPOINT.x, y: currentPoint.y };
    }
  } else {
    // Move vertically first, then horizontally
    if (currentPoint.y !== STOP_WAYPOINT.y) {
      virtualWaypoint = { x: currentPoint.x, y: STOP_WAYPOINT.y };
    }
  }

  // Build the path
  if (
    virtualWaypoint &&
    (virtualWaypoint.x !== STOP_WAYPOINT.x ||
      virtualWaypoint.y !== STOP_WAYPOINT.y)
  ) {
    path.push(virtualWaypoint);
  }
  path.push(STOP_WAYPOINT);

  return path;
}

function finalizeWaypoints() {
  console.log("Finalizing waypoints (layout coordinates):");

  // Start with existing waypoints, or START_WAYPOINT if none
  let finalWaypoints =
    waypoints.length === 0 ? [START_WAYPOINT] : [...waypoints];

  // Add the ghost point if it exists (current mouse position waypoint)
  if (ghostPoint) {
    finalWaypoints.push(ghostPoint);
  }

  // Calculate and add path to STOP_WAYPOINT
  const pathToStop = calculatePathToStop();
  if (pathToStop && pathToStop.length > 0) {
    finalWaypoints = finalWaypoints.concat(pathToStop);
    console.log(
      "Added virtual waypoints and STOP_WAYPOINT to complete the path",
    );
  }

  // Log all final waypoints (in layout coordinates)
  finalWaypoints.forEach((waypoint, index) => {
    console.log(
      `Waypoint ${index}: (${waypoint.x.toFixed(3)}, ${waypoint.y.toFixed(3)}) µm`,
    );
  });

  console.log(`Total waypoints: ${finalWaypoints.length}`);

  // Send waypoints to parent window (for iframe embedding)
  if (window.parent && window.parent !== window) {
    let msg = {
      command: "Waypoints",
      data: {
        waypoints: finalWaypoints,
        start: START_WAYPOINT,
        stop: STOP_WAYPOINT,
        radius: BEND_RADIUS,
        meta: waypointsMeta,
      },
    };
    console.log(`Sending message: ${JSON.stringify(msg)}`);
    window.parent.postMessage(msg, "*");
    console.log("Waypoints sent to parent window");
  }

  // Update the waypoints array with the final path
  waypoints = finalWaypoints;

  // Exit waypoint editing mode and clean up
  editing_waypoints = false;
  updateWaypointToast();
  clearWaypoints();
  console.log("Waypoint editing finalized and exited");
}

function redrawWaypoints() {
  // Request a fresh canvas redraw from server first
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ msg: "redraw" }));
  }

  // Draw waypoints and lines on top after a short delay to ensure server redraw is complete
  setTimeout(drawWaypoints, 50);
}

async function drawWaypoints() {
  if (!editing_waypoints) return;

  const ctx = context;

  // If no waypoints yet, draw START_WAYPOINT
  const allPoints = waypoints.length === 0 ? [START_WAYPOINT] : waypoints;

  // Convert all layout coordinates to canvas coordinates for drawing
  const coordsToConvert = [...allPoints];
  if (ghostPoint) coordsToConvert.push(ghostPoint);
  coordsToConvert.push(STOP_WAYPOINT);

  // Add path to stop points
  const pathToStop = calculatePathToStop();
  if (pathToStop && pathToStop.length > 0) {
    coordsToConvert.push(...pathToStop);
  }

  let canvasCoords;
  try {
    canvasCoords = await layoutToCanvas(coordsToConvert);
    if (!canvasCoords || canvasCoords.length === 0) {
      console.warn(
        "Failed to convert layout coordinates to canvas coordinates",
      );
      return;
    }
  } catch (error) {
    console.warn("Error converting coordinates for drawing:", error);
    return;
  }

  // Extract converted coordinates
  const allPointsCanvas = canvasCoords.slice(0, allPoints.length);
  let ghostPointCanvas = null;
  let stopWaypointCanvas = null;
  let pathToStopCanvas = null;

  let idx = allPoints.length;
  if (ghostPoint) {
    ghostPointCanvas = canvasCoords[idx];
    idx++;
  }
  stopWaypointCanvas = canvasCoords[idx];
  idx++;

  if (pathToStop && pathToStop.length > 0) {
    pathToStopCanvas = canvasCoords.slice(idx, idx + pathToStop.length);
  }

  // Draw lines between waypoints
  if (allPointsCanvas.length > 1) {
    ctx.strokeStyle = "#FF0000"; // Red color
    ctx.lineWidth = 2;
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.moveTo(allPointsCanvas[0].x, allPointsCanvas[0].y);

    for (let i = 1; i < allPointsCanvas.length; i++) {
      ctx.lineTo(allPointsCanvas[i].x, allPointsCanvas[i].y);
    }

    ctx.stroke();
  }

  // Draw ghost line from last waypoint to ghost point
  if (ghostPointCanvas && allPointsCanvas.length > 0) {
    const lastPoint = allPointsCanvas[allPointsCanvas.length - 1];

    ctx.strokeStyle = "#FF0000"; // Red color
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]); // Dashed line for ghost

    ctx.beginPath();
    ctx.moveTo(lastPoint.x, lastPoint.y);
    ctx.lineTo(ghostPointCanvas.x, ghostPointCanvas.y);
    ctx.stroke();
  }

  // Draw guide line to STOP_WAYPOINT
  if (pathToStopCanvas && pathToStopCanvas.length > 0) {
    const startPoint =
      ghostPointCanvas ||
      (allPointsCanvas.length > 0
        ? allPointsCanvas[allPointsCanvas.length - 1]
        : allPointsCanvas[0]);

    ctx.strokeStyle = "#CCCCCC"; // Light gray color for guide
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 8]); // Very sparse dashes for guide line

    ctx.beginPath();
    ctx.moveTo(startPoint.x, startPoint.y);

    // Draw path through virtual waypoints to STOP_WAYPOINT
    for (let i = 0; i < pathToStopCanvas.length; i++) {
      ctx.lineTo(pathToStopCanvas[i].x, pathToStopCanvas[i].y);
    }

    ctx.stroke();
  }

  // Draw waypoint markers
  allPointsCanvas.forEach((point, index) => {
    ctx.fillStyle = "#FF0000"; // Red color
    ctx.strokeStyle = "#FFFFFF"; // White border
    ctx.lineWidth = 1;
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    // Draw waypoint number (start from 0 for START_WAYPOINT)
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(index.toString(), point.x, point.y);
  });

  // Draw ghost point marker if it exists
  if (ghostPointCanvas) {
    ctx.fillStyle = "#FF8888"; // Lighter red for ghost
    ctx.strokeStyle = "#FFFFFF"; // White border
    ctx.lineWidth = 1;
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(ghostPointCanvas.x, ghostPointCanvas.y, 3, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
  }

  // Draw STOP_WAYPOINT marker
  ctx.fillStyle = "#888888"; // Gray for stop waypoint
  ctx.strokeStyle = "#FFFFFF"; // White border
  ctx.lineWidth = 1;
  ctx.setLineDash([]);

  ctx.beginPath();
  ctx.arc(stopWaypointCanvas.x, stopWaypointCanvas.y, 5, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();

  // Draw "STOP" label
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "10px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("STOP", stopWaypointCanvas.x, stopWaypointCanvas.y);

  // Draw virtual waypoint markers if they exist in the path
  if (pathToStopCanvas && pathToStopCanvas.length > 1) {
    // The last point in pathToStopCanvas is STOP_WAYPOINT, so draw markers for the virtual waypoints
    for (let i = 0; i < pathToStopCanvas.length - 1; i++) {
      const virtualPoint = pathToStopCanvas[i];

      ctx.fillStyle = "#BBBBBB"; // Light gray for virtual waypoints
      ctx.strokeStyle = "#FFFFFF"; // White border
      ctx.lineWidth = 1;
      ctx.setLineDash([]);

      ctx.beginPath();
      ctx.arc(virtualPoint.x, virtualPoint.y, 3, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();

      // Draw "V" for virtual
      ctx.fillStyle = "#FFFFFF";
      ctx.font = "8px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("V", virtualPoint.x, virtualPoint.y);
    }
  }
}

//  Handle right-click: finalize waypoints if editing, otherwise prevent context menu
canvas.addEventListener("contextmenu", function (evt) {
  evt.preventDefault();

  if (editing_waypoints) {
    // Right-click while editing waypoints finalizes them
    finalizeWaypoints();
  }
});

// Hide layer context menu when clicking outside
document.addEventListener("click", function (event) {
  const contextMenu = document.getElementById("layerContextMenu");
  if (
    contextMenu &&
    contextMenu.style.display === "block" &&
    !contextMenu.contains(event.target)
  ) {
    hideLayerContextMenu();
  }
});

canvas.addEventListener(
  "mousemove",
  function (evt) {
    // Track actual dragging movement during move mode
    if (
      currentMode &&
      currentMode.toLowerCase().includes("move") &&
      isDragging
    ) {
      moveStarted = true; // Confirm that actual dragging happened
    }

    // Handle waypoint editing ghost line
    if (editing_waypoints) {
      const rect = canvas.getBoundingClientRect();
      const mouseX = evt.clientX - rect.left;
      const mouseY = evt.clientY - rect.top;
      updateGhostPoint(mouseX, mouseY);

      // Redraw immediately to show ghost line
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ msg: "redraw" }));
        // Draw waypoints and ghost line after server redraw
        setTimeout(drawWaypoints, 50);
      }
    } else {
      sendMouseEvent(canvas, "mouse_move", evt);
    }

    evt.preventDefault();
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => {
      sendHoverInfo(canvas, "inst_info", evt);
    }, 500);
    if (hoverTip) {
      socket.send(JSON.stringify({ msg: "redraw" }));
      hoverTip = false;
      // Ensure waypoints are redrawn after tooltip is cleared
      if (editing_waypoints) {
        setTimeout(drawWaypoints, 60);
      }
    }
  },
  false,
);

canvas.addEventListener(
  "click",
  function (evt) {
    if (!editing_waypoints) {
      sendMouseEvent(canvas, "mouse_click", evt);
    } else {
      addWaypoint(evt);
    }
    evt.preventDefault();
  },
  false,
);

canvas.addEventListener(
  "dblclick",
  function (evt) {
    sendMouseEvent(canvas, "mouse_dblclick", evt);
    evt.preventDefault();
  },
  false,
);

canvas.addEventListener(
  "mousedown",
  function (evt) {
    // Track move operation start
    if (currentMode && currentMode.toLowerCase().includes("move")) {
      isDragging = true;
      moveStarted = false;
      console.log("Move operation started");
    }

    sendMouseEvent(canvas, "mouse_pressed", evt);
    evt.preventDefault();
  },
  false,
);

canvas.addEventListener(
  "mouseup",
  function (evt) {
    // Detect move operation completion
    if (
      currentMode &&
      currentMode.toLowerCase().includes("move") &&
      isDragging &&
      moveStarted
    ) {
      console.log("Move operation completed");

      // Send message to VSCode about the move
      sendMessageToVSCode({
        type: "instanceMoved",
        message: "Layout instances have been moved",
        timestamp: new Date().toISOString(),
      });

      isDragging = false;
      moveStarted = false;
    }

    sendMouseEvent(canvas, "mouse_released", evt);
    evt.preventDefault();
  },
  false,
);

canvas.addEventListener(
  "mouseenter",
  function (evt) {
    sendMouseEvent(canvas, "mouse_enter", evt);
    evt.preventDefault();
  },
  false,
);

canvas.addEventListener(
  "mouseout",
  function (evt) {
    sendMouseEvent(canvas, "mouse_leave", evt);
    evt.preventDefault();
    clearTimeout(hoverTimer);
  },
  false,
);

canvas.addEventListener(
  "wheel",
  function (evt) {
    // Detect Mac platform and convert vertical scrolling to horizontal
    const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;

    if (isMac && Math.abs(evt.deltaY) > Math.abs(evt.deltaX)) {
      // On Mac, convert up/down scrolling to left/right scrolling
      const originalDeltaY = evt.deltaY;

      // Create a new wheel event with modified deltas
      if (socket.readyState == WebSocket.OPEN) {
        let ev = mouseEventToJSON(canvas, "wheel", evt);
        ev.dx = originalDeltaY; // Use original Y delta as X delta
        ev.dy = 0; // Set Y delta to 0 for pure horizontal movement
        ev.dm = evt.deltaMode;
        socket.send(JSON.stringify(ev));
      }
    } else {
      // For non-Mac or when deltaX is already larger, use normal behavior
      sendWheelEvent(canvas, "wheel", evt);
    }

    evt.preventDefault();
  },
  false,
);

window.addEventListener("keydown", function (evt) {
  if (evt.key === "Enter") {
    if (evt.shiftKey) {
      // Shift+Enter for zoom out
      socket.send(JSON.stringify({ msg: "zoom-out" }));
    } else {
      // Enter for zoom in
      socket.send(JSON.stringify({ msg: "zoom-in" }));
    }
    evt.preventDefault();
  } else if (evt.key.toLowerCase() === "f") {
    // f for zoom fit
    socket.send(JSON.stringify({ msg: "zoom-f" }));
    evt.preventDefault();
  } else {
    sendKeyEvent(canvas, "keydown", evt);
  }
});

// Icon fallback detection for VSCode webviews
function checkIconFallbacks() {
  // Check if Bootstrap Icons are loaded
  const testIcon = document.createElement("i");
  testIcon.className = "bi bi-cursor";
  testIcon.style.position = "absolute";
  testIcon.style.left = "-9999px";
  document.body.appendChild(testIcon);

  // Check if the icon has actual content (pseudo-element)
  const styles = window.getComputedStyle(testIcon, "::before");
  const hasContent =
    styles.content && styles.content !== "none" && styles.content !== '""';

  if (!hasContent) {
    // Bootstrap Icons failed to load, show fallbacks
    const iconContainers = document.querySelectorAll(".icon-fallback");
    iconContainers.forEach((container) => {
      const icon = container.querySelector(".bi");
      const fallback = container.querySelector(".fallback-text");
      if (icon && fallback) {
        icon.style.display = "none";
        fallback.style.display = "inline-block";
      }
    });
  }

  document.body.removeChild(testIcon);
}

// Run icon fallback check after page loads
document.addEventListener("DOMContentLoaded", () => {
  // Delay to allow fonts to load
  setTimeout(checkIconFallbacks, 100);

  // Initialize Bootstrap tooltips
  setTimeout(initializeTooltips, 200);
});

// VSCode messaging helper
function sendMessageToVSCode(message) {
  // Check if we're running in a VSCode webview
  if (typeof acquireVsCodeApi !== "undefined") {
    try {
      const vscode = acquireVsCodeApi();
      vscode.postMessage(message);
      console.log("Sent message to VSCode:", message);
    } catch (error) {
      console.log("Failed to send message to VSCode:", error);
    }
  } else {
    console.log("Not running in VSCode webview, message would be:", message);
  }
}

// Move operation tracking
let currentMode = "";
let isDragging = false;
let moveStarted = false;

// Top toolbar functions
function selectTool(tool) {
  console.log("Selecting tool:", tool);

  // Track current mode
  currentMode = tool;

  // Clear all active states
  const allTools = document.querySelectorAll(".tool-btn");
  allTools.forEach((btn) => btn.classList.remove("active"));

  // Set active state for selected tool based on tool name
  if (tool === "select" || tool.toLowerCase() === "select") {
    document.getElementById("tool-select").classList.add("active");
  } else if (tool.toLowerCase().includes("move")) {
    document.getElementById("tool-move").classList.add("active");
  } else if (tool.toLowerCase().includes("ruler")) {
    document.getElementById("tool-ruler").classList.add("active");
  }

  // Send mode change to server using correct message format
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        msg: "select-mode",
        value: tool,
      }),
    );
  }
}

function clearRulersFromToolbar() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        msg: "clear-annotations",
      }),
    );
  }
}

function fitAllFromToolbar() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        msg: "zoom-f",
      }),
    );
  }
}

function reloadFromToolbar() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        msg: "reload",
      }),
    );
  }
}

function toggleWaypointEditingFromToolbar() {
  // Toggle waypoint editing mode (same as pressing 'L')
  editing_waypoints = !editing_waypoints;
  updateWaypointToast();

  if (!editing_waypoints) {
    // Clear waypoints when exiting editing mode
    clearWaypoints();
  } else {
    // Reset to initial state when entering editing mode
    waypoints = [];
    currentDirection = START_DIRECTION;
    ghostPoint = null;
  }

  // Update button appearance
  const waypointBtn = document.getElementById("tool-waypoint");
  if (waypointBtn) {
    if (editing_waypoints) {
      waypointBtn.classList.add("active");
      waypointBtn.setAttribute("title", "Exit Waypoint Editing (L)");
      waypointBtn.setAttribute(
        "data-bs-original-title",
        "Exit Waypoint Editing (L)",
      );
    } else {
      waypointBtn.classList.remove("active");
      waypointBtn.setAttribute("title", "Waypoint Editing (L)");
      waypointBtn.setAttribute(
        "data-bs-original-title",
        "Waypoint Editing (L)",
      );
    }
  }

  console.log(`EditingWaypoints: ${editing_waypoints}`);
}
