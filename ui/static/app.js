const runBtn = document.getElementById("runBtn");
const overall = document.getElementById("overall");
const rows = document.getElementById("rows");
const errorBox = document.getElementById("errorBox");
const truncBox = document.getElementById("truncBox");
const configBox = document.getElementById("configBox");
const canvas = document.getElementById("scope");
const ctx = canvas.getContext("2d");
const filters = document.getElementById("filters");

let events = [];
let filter = "ALL";
let sweep = 0;

function setOverall(value) {
  overall.textContent = value;
  overall.className = "overall " + (value === "PASS" || value === "FAIL" ? value : "");
}

function setCounters(counters, count) {
  document.getElementById("cParsed").textContent = counters.packets_parsed;
  document.getElementById("cPassed").textContent = counters.packets_passed;
  document.getElementById("cFailed").textContent = counters.packets_failed;
  document.getElementById("cViolations").textContent = counters.violation_count;
  document.getElementById("cParse").textContent = counters.parse_error_count;
  document.getElementById("cEvents").textContent = count;
}

function renderConfig(config) {
  configBox.innerHTML =
    "<div><b>MODE</b> " +
    config.system_mode +
    "</div><div><b>MAX TARGETS</b> " +
    config.max_allowed_targets +
    "</div><div><b>MAX LATENCY</b> " +
    config.max_latency_ms +
    " ms</div><div><b>STATES</b> " +
    config.allowed_states.join(" · ") +
    "</div>";
}

function renderTable() {
  const visible = events.filter((event) => filter === "ALL" || event.status === filter);
  rows.innerHTML = visible
    .map((event) => {
      const why = event.reasons.length ? event.reasons.join(" | ") : "—";
      const id = event.packet_id == null ? "—" : event.packet_id;
      return (
        "<tr class='" +
        event.status +
        "'><td>" +
        event.status +
        "</td><td>" +
        event.line_number +
        "</td><td>" +
        id +
        "</td><td>" +
        (event.timestamp || "—") +
        "</td><td>" +
        (event.state || "PARSE") +
        "</td><td>" +
        (event.targets == null ? "—" : event.targets) +
        "</td><td>" +
        (event.distance == null ? "—" : event.distance) +
        "</td><td>" +
        (event.velocity == null ? "—" : event.velocity) +
        "</td><td class='why'>" +
        why +
        "</td></tr>"
      );
    })
    .join("");
}

function drawScope() {
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const radius = w * 0.42;
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "rgba(26,255,194,0.18)";
  ctx.lineWidth = 1;
  for (let i = 1; i <= 4; i += 1) {
    ctx.beginPath();
    ctx.arc(cx, cy, (radius * i) / 4, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.beginPath();
  ctx.moveTo(cx - radius, cy);
  ctx.lineTo(cx + radius, cy);
  ctx.moveTo(cx, cy - radius);
  ctx.lineTo(cx, cy + radius);
  ctx.stroke();

  const gradient = ctx.createLinearGradient(
    cx,
    cy,
    cx + Math.cos(sweep) * radius,
    cy + Math.sin(sweep) * radius
  );
  gradient.addColorStop(0, "rgba(26,255,194,0)");
  gradient.addColorStop(1, "rgba(26,255,194,0.45)");
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.arc(cx, cy, radius, sweep - 0.45, sweep);
  ctx.closePath();
  ctx.fill();

  const n = Math.max(events.length, 1);
  events.forEach((event, index) => {
    const angle = (index / n) * Math.PI * 2 - Math.PI / 2;
    const ring = event.kind === "parse" ? 0.92 : 0.35 + (index % 5) * 0.1;
    const x = cx + Math.cos(angle) * radius * ring;
    const y = cy + Math.sin(angle) * radius * ring;
    ctx.beginPath();
    ctx.fillStyle = event.status === "PASS" ? "#1affc2" : "#ff4d4d";
    ctx.shadowColor = ctx.fillStyle;
    ctx.shadowBlur = 12;
    ctx.arc(x, y, event.status === "FAIL" ? 6 : 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  });
}

function tick() {
  sweep += 0.025;
  drawScope();
  requestAnimationFrame(tick);
}

async function runScan() {
  errorBox.hidden = true;
  truncBox.hidden = true;
  setOverall("SCANNING");
  runBtn.disabled = true;
  const configText = document.getElementById("configText").value.trim();
  const streamText = document.getElementById("streamText").value.trim();
  const body =
    configText || streamText
      ? { config_text: configText, stream_text: streamText }
      : {
          config_path: document.getElementById("configPath").value.trim(),
          stream_path: document.getElementById("streamPath").value.trim(),
        };
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Scan failed");
    }
    events = data.events;
    setOverall(data.counters.overall);
    setCounters(data.counters, events.length);
    renderConfig(data.config);
    renderTable();
    truncBox.hidden = !data.truncated;
  } catch (error) {
    setOverall("ERROR");
    errorBox.hidden = false;
    errorBox.textContent = error.message;
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener("click", runScan);
filters.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-filter]");
  if (!button) {
    return;
  }
  filter = button.dataset.filter;
  for (const child of filters.querySelectorAll("button")) {
    child.classList.toggle("active", child === button);
  }
  renderTable();
});

tick();
runScan();
