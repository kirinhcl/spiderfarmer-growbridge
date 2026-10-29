const messages = {
  en: {
    workspace: "GROW SPACE",
    overview: "Overview",
    devices: "Devices",
    history: "History",
    activity: "Activity",
    title: "A little closer to your grow.",
    subtitle: "Your environment, devices, and their story.",
    navigation: "WORKSPACE",
    local: "Connected locally",
    localNote: "A direct link to your grow space. Powered by Bluetooth.",
    disconnect: "Disconnect dashboard",
    live: "Live connection",
    delayed: "Readings delayed",
    reconnecting: "Reconnecting",
    unavailable: "Service unavailable",
    environment: "Live environment",
    updated: "Updated",
    ago: "ago",
    seconds: "s",
    noReadings: "Waiting for readings",
    temperature: "Air temperature",
    humidity: "Humidity",
    vpd: "Vapor pressure deficit",
    co2: "Carbon dioxide",
    ppfd: "Light intensity",
    soil: "Soil temperature",
    temperatureShort: "Temperature",
    humidityShort: "Humidity",
    vpdShort: "VPD",
    co2Short: "CO₂",
    ppfdShort: "PPFD",
    soilShort: "Soil temperature",
    trend: "A view over time",
    trendSubtitle: "Recorded readings from your grow space",
    export: "Export CSV",
    snapshots: "recorded snapshots",
    sampled: "Sampled across the selected period",
    complete: "All readings in this period",
    noHistory:
      "No readings in this period yet. History will appear as your system records data.",
    loading: "Loading readings…",
    controller: "Your controller",
    firmware: "Firmware",
    protocol: "Protocol",
    mode: "Access",
    enabled: "Control enabled",
    readonly: "Read only",
    retention: "History retention",
    days: "days",
    systemNote:
      "Values are reported by your controller. Check sensor placement and calibration for your setup.",
    manual: "Device controls",
    manualNote: "Changes are checked against device readback",
    light: "Grow light",
    exhaust: "Exhaust fan",
    fan: "Circulation fan",
    pump: "Water pump",
    on: "On",
    off: "Off",
    notAvailable: "Unavailable",
    readback: "Readback",
    target: "Target",
    brightness: "Brightness",
    speed: "Speed",
    gear: "Gear",
    apply: "Apply setting",
    supplyOff: "Power outlet is off",
    pumpNote: "A timed pulse. OFF is checked before completion.",
    duration: "Duration",
    runPump: "Run pump",
    pumpWaiting: "Waiting for confirmed OFF…",
    cooldown: "Next pulse in",
    max: "Max",
    power: "Power outlets",
    powerNote: "Supply power before adjusting a device",
    outlet: "Outlet",
    unassigned: "Unassigned",
    timedOnly: "Use the timed pump control",
    recent: "Recent actions",
    recentNote: "Actions from the dashboard and MCP",
    action: "Action",
    setting: "Setting",
    result: "Result",
    time: "Time",
    confirmed: "Confirmed",
    pending: "In progress",
    failed: "Failed",
    emptyActivity: "No control actions recorded yet.",
    footer: "GrowBridge · A local connection to your plants",
    timezone: "Times shown in",
    controlsDisabled:
      "This installation is in read-only mode. Enable controls in its local configuration after checking the outlet mapping.",
    staleBanner:
      "Live readings are unavailable or delayed. Controls will be available again after fresh data arrives.",
    pumpFault:
      "Pump OFF has not been confirmed. Check the pump and Bluetooth connection before further control.",
    applied: "Setting confirmed by the controller.",
    pumpDone: "Pump pulse finished. OFF confirmed.",
    powerDone: "Outlet state confirmed.",
    error: "The action could not be confirmed.",
    retry: "Retry same request",
    refreshing: "Refreshing…",
    refresh: "Refresh readings",
    connectTitle: "Your grow space, connected.",
    connectText:
      "Open the dashboard from the computer running GrowBridge. This creates a private browser connection.",
    connectHint: "Run this command on that computer:",
    connectFoot: "The GrowBridge service needs to be running.",
    reconnect: "Check connection",
    connectError:
      "The connection link has expired. Run the command again to open a fresh link.",
    lang: "Language",
    metric: "Chart measurement",
    invalidDuration: "Choose a duration within the configured pump limit.",
  },
  zh: {
    workspace: "生长空间",
    overview: "总览",
    devices: "设备",
    history: "历史数据",
    activity: "操作记录",
    title: "随时了解你的生长空间。",
    subtitle: "查看环境、控制设备，了解每一次变化。",
    navigation: "工作空间",
    local: "本地连接",
    localNote: "通过蓝牙，直接连接你的生长系统。",
    disconnect: "断开控制台",
    live: "实时连接",
    delayed: "数据延迟",
    reconnecting: "正在重连",
    unavailable: "服务不可用",
    environment: "实时环境",
    updated: "更新于",
    ago: "前",
    seconds: "秒",
    noReadings: "正在等待数据",
    temperature: "空气温度",
    humidity: "空气湿度",
    vpd: "水汽压差",
    co2: "二氧化碳",
    ppfd: "光照强度",
    soil: "土壤温度",
    temperatureShort: "空气温度",
    humidityShort: "湿度",
    vpdShort: "VPD",
    co2Short: "CO₂",
    ppfdShort: "PPFD",
    soilShort: "土壤温度",
    trend: "查看环境变化",
    trendSubtitle: "生长空间的实际记录",
    export: "导出 CSV",
    snapshots: "个记录点",
    sampled: "按时间段选取实际样本",
    complete: "此时间段内的全部记录",
    noHistory: "这个时间段还没有记录。系统开始采集后，历史数据会出现在这里。",
    loading: "正在加载数据…",
    controller: "控制器",
    firmware: "固件",
    protocol: "协议",
    mode: "操作权限",
    enabled: "允许控制",
    readonly: "只读",
    retention: "历史保留",
    days: "天",
    systemNote: "数值由控制器提供。请结合你的设备检查传感器位置和校准情况。",
    manual: "设备控制",
    manualNote: "每次操作后读取设备状态确认",
    light: "生长灯",
    exhaust: "排风扇",
    fan: "循环风扇",
    pump: "水泵",
    on: "开启",
    off: "关闭",
    notAvailable: "不可用",
    readback: "回读",
    target: "目标",
    brightness: "亮度",
    speed: "速度",
    gear: "档",
    apply: "应用设置",
    supplyOff: "供电插座未开启",
    pumpNote: "定时运行，结束前确认水泵已关闭。",
    duration: "运行时长",
    runPump: "运行水泵",
    pumpWaiting: "正在等待关闭确认…",
    cooldown: "下次可运行",
    max: "上限",
    power: "电源插座",
    powerNote: "调节设备前请先开启相应电源",
    outlet: "插座",
    unassigned: "未分配",
    timedOnly: "请使用水泵定时控制",
    recent: "最近操作",
    recentNote: "包含控制台与 MCP 发起的操作",
    action: "设备",
    setting: "设置",
    result: "结果",
    time: "时间",
    confirmed: "已确认",
    pending: "进行中",
    failed: "失败",
    emptyActivity: "还没有设备控制记录。",
    footer: "GrowBridge · 本地连接你的生长空间",
    timezone: "显示时区",
    controlsDisabled:
      "当前安装为只读模式。确认插座接线后，可在本地配置中开启控制。",
    staleBanner: "实时数据尚未到达或已延迟。收到新数据后，控制功能会恢复。",
    pumpFault: "尚未确认水泵已关闭。请检查水泵和蓝牙连接，再继续操作。",
    applied: "控制器回读确认设置已生效。",
    pumpDone: "水泵运行完成，已确认关闭。",
    powerDone: "已确认插座状态。",
    error: "未能确认操作结果。",
    retry: "重试同一个请求",
    refreshing: "正在刷新…",
    refresh: "刷新数据",
    connectTitle: "连接你的生长空间。",
    connectText: "请在运行 GrowBridge 的电脑上打开控制台，建立私有浏览器连接。",
    connectHint: "在这台电脑上运行：",
    connectFoot: "请先确保 GrowBridge 服务正在运行。",
    reconnect: "检查连接",
    connectError: "连接链接已过期，请重新运行命令以打开新链接。",
    lang: "语言",
    metric: "曲线指标",
    invalidDuration: "请选择不超过配置上限的水泵运行时长。",
  },
};

const paths = {
  leaf: '<path d="M20 4C9 3 3 8 5 15c2 6 14 5 15-11Z"/><path d="M4 21c1-6 5-10 11-13"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  devices:
    '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M9 9h6v6H9zM9 1v3m6-3v3m-6 16v3m6-3v3M1 9h3m-3 6h3m16-6h3m-3 6h3"/>',
  chart: '<path d="M4 4v16h17M7 14l4-5 4 3 5-7"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
  refresh: '<path d="M20 8a8 8 0 1 0 0 8M20 3v5h-5"/>',
  temp: '<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0Z"/><path d="M12 7v10"/>',
  drop: '<path d="M12 3C10 7 5 11 5 15a7 7 0 0 0 14 0c0-4-5-8-7-12Z"/><path d="M9 15c0 2 1 3 3 3"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
  wind: '<path d="M3 8h12a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h7a3 3 0 1 1-3 3"/>',
  fan: '<circle cx="12" cy="12" r="2"/><path d="M10 10C5 6 10-1 14 4c2 3-1 5-2 6m2 2c6-2 10 5 4 7-4 1-5-3-5-5m-3-1c-1 6-9 6-8 0 1-4 5-3 7-2"/>',
  air: '<circle cx="6" cy="9" r="2"/><circle cx="17" cy="7" r="3"/><circle cx="11" cy="17" r="4"/>',
  power: '<path d="M12 2v9M6 5a9 9 0 1 0 12 0"/>',
  download: '<path d="M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V6a4 4 0 0 1 8 0v4m-4 5v2"/>',
};
const icon = (name) =>
  `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.leaf}</svg>`;
const escape = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
const $ = (id) => document.getElementById(id);
const state = {
  lang: localStorage.getItem("growbridge-language") === "zh" ? "zh" : "en",
  authorized: false,
  network: true,
  status: null,
  settings: null,
  series: null,
  operations: [],
  metric: "temp",
  hours: 1,
  busy: false,
  pumpBusy: false,
  drafts: {},
  dirty: new Set(),
  pumpSeconds: null,
  retry: null,
  refreshing: false,
  lastHistory: 0,
};
const metrics = [
  {
    key: "temp",
    name: "temperature",
    short: "temperatureShort",
    unit: "°C",
    precision: 1,
    icon: "temp",
  },
  {
    key: "humi",
    name: "humidity",
    short: "humidityShort",
    unit: "% RH",
    precision: 1,
    icon: "drop",
  },
  {
    key: "vpd",
    name: "vpd",
    short: "vpdShort",
    unit: "kPa",
    precision: 2,
    icon: "wind",
  },
  {
    key: "co2",
    name: "co2",
    short: "co2Short",
    unit: "ppm",
    precision: 0,
    icon: "air",
  },
  {
    key: "ppfd",
    name: "ppfd",
    short: "ppfdShort",
    unit: "µmol/m²/s",
    precision: 0,
    icon: "sun",
  },
  {
    key: "tempSoil",
    name: "soil",
    short: "soilShort",
    unit: "°C",
    precision: 1,
    icon: "leaf",
  },
];
const deviceInfo = [
  { key: "light", module: "light", max: 100, icon: "sun", label: "brightness" },
  { key: "exhaust", module: "blower", max: 100, icon: "wind", label: "speed" },
  { key: "fan", module: "fan", max: 10, icon: "fan", label: "gear" },
];
const t = (key) => messages[state.lang][key] || key;
const numeric = (value) => typeof value === "number" && Number.isFinite(value);
const format = (value, precision = 0) =>
  numeric(value)
    ? value.toLocaleString(state.lang === "zh" ? "zh-CN" : "en-GB", {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : "—";
const when = (stamp, date = false) =>
  new Date(stamp * 1000).toLocaleString(
    state.lang === "zh" ? "zh-CN" : "en-GB",
    date
      ? { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }
      : { hour: "2-digit", minute: "2-digit", second: "2-digit" },
  );
const brand = () =>
  `<a class="brand" href="#overview"><span class="brand-mark">${icon("leaf")}</span><span>GrowBridge<small>GROW WELL. STAY CLOSE.</small></span></a>`;
let resizeObserver;
let toastTimer;
let hoverIndex = null;

function mount() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  document.title = `GrowBridge · ${t("workspace")}`;
  resizeObserver?.disconnect();
  $("app").innerHTML = `<div class="app-shell">
    <aside class="sidebar">${brand()}<div class="nav-label">${t("navigation")}</div>
      <nav class="nav" aria-label="${t("navigation")}">${[
        ["overview", "grid"],
        ["devices", "devices"],
        ["history", "chart"],
        ["activity", "clock"],
      ]
        .map(
          ([name, symbol], i) =>
            `<a href="#${name}" class="${i === 0 ? "active" : ""}" aria-label="${t(name)}">${icon(symbol)}<span>${t(name)}</span></a>`,
        )
        .join("")}</nav>
      <div class="sidebar-bottom"><div class="local-badge">${icon("lock")}${t("local")}</div><p class="sidebar-note">${t("localNote")}</p><button id="logout" class="text-button">${t("disconnect")}</button></div>
    </aside>
    <main class="main" id="overview"><header class="page-header"><div><div class="eyebrow">${t("workspace")} / AC5</div><h1>${t("title")}</h1><p class="subtitle">${t("subtitle")}</p></div>
      <div class="header-actions"><span id="connection" class="pill warn">${t("reconnecting")}</span><select id="language" class="language" aria-label="${t("lang")}"><option value="en">English</option><option value="zh">简体中文</option></select><button id="refresh" class="icon-button" aria-label="${t("refresh")}">${icon("refresh")}</button></div></header>
      <div id="banner" class="banner" hidden></div>
      <section aria-labelledby="environment-heading"><div class="section-heading"><h2 id="environment-heading">${t("environment")}</h2><span id="last-updated" class="section-meta">${t("noReadings")}</span></div>
        <div class="metrics">${metrics.map((m) => `<article class="metric-card"><div class="metric-top"><span>${t(m.name)}</span><div class="metric-icon">${icon(m.icon)}</div></div><div class="metric-number" id="metric-${m.key}">—</div><div class="metric-unit">${m.unit}</div></article>`).join("")}</div>
      </section>
      <div class="history-grid"><section id="history" class="panel" aria-labelledby="history-heading"><div class="panel-heading"><div><h2 id="history-heading">${t("trend")}</h2><p>${t("trendSubtitle")}</p></div><button id="export" class="small-button">${icon("download")}${t("export")}</button></div>
        <div class="chart-toolbar"><select id="chart-metric" class="metric-select" aria-label="${t("metric")}">${metrics.map((m) => `<option value="${m.key}">${t(m.short)} · ${m.unit}</option>`).join("")}</select><div class="range-tabs" role="group" aria-label="${t("history")}">${[1, 6, 24, 168].map((h) => `<button data-hours="${h}" class="${state.hours === h ? "selected" : ""}" aria-pressed="${state.hours === h}">${h === 168 ? "7d" : h + "h"}</button>`).join("")}</div></div>
        <div class="chart-wrap"><canvas id="chart" role="img" aria-label="${t("trend")}"></canvas><div id="chart-empty" class="chart-empty">${t("loading")}</div><div id="chart-tooltip" class="chart-tooltip" hidden></div></div><div class="chart-caption"><span id="chart-count">—</span><span id="chart-sampling"></span></div></section>
        <aside class="panel system-panel"><h2>${t("controller")}</h2><div class="system-art"><div class="controller-icon">${icon("devices")}</div><div><strong>Spider Farmer AC5</strong><span>GGS · Bluetooth</span></div></div>${[
          ["firmware", "firmware"],
          ["protocol", "protocol"],
          ["mode", "access"],
          ["retention", "retention"],
        ]
          .map(
            ([label, id]) =>
              `<div class="system-row"><span>${t(label)}</span><strong id="system-${id}">—</strong></div>`,
          )
          .join("")}<p class="system-foot">${t("systemNote")}</p></aside></div>
      <section id="devices" aria-labelledby="devices-heading"><div class="section-heading"><h2 id="devices-heading">${t("manual")}</h2><span class="section-meta">${t("manualNote")}</span></div><div class="controls-grid">
        ${deviceInfo.map((d) => `<article class="control-card"><div class="control-title"><span class="device-symbol">${icon(d.icon)}</span><span class="device-state" id="device-state-${d.key}">—</span></div><h3>${t(d.key)}</h3><p class="device-readback" id="readback-${d.key}">—</p><label class="target-row" for="slider-${d.key}"><span>${t(d.label)}</span><output id="target-${d.key}" for="slider-${d.key}">—</output></label><input id="slider-${d.key}" class="device-range" type="range" min="0" max="${d.max}" step="1" value="0" disabled><button class="primary-button" id="apply-${d.key}" disabled>${t("apply")}</button></article>`).join("")}
        <article class="control-card pump-card"><div class="control-title"><span class="device-symbol">${icon("drop")}</span><span id="pump-state" class="device-state">—</span></div><h3>${t("pump")}</h3><p class="pump-note" id="pump-note">${t("pumpNote")}</p><label class="target-row" for="pump-seconds"><span>${t("duration")}</span><output id="pump-limit">—</output></label><div class="pump-input"><input id="pump-seconds" type="number" min="0.1" step="0.1" value="5" disabled><span>${t("seconds")}</span></div><button id="run-pump" class="primary-button" disabled>${icon("drop")}<span>${t("runPump")}</span></button></article>
      </div><div class="panel outlets-panel"><div class="outlets-header"><h3>${t("power")}</h3><span>${t("powerNote")}</span></div><div class="outlet-grid">${[1, 2, 3, 4, 5].map((n) => `<div class="outlet" id="outlet-card-${n}">${icon("power")}<div class="outlet-info"><strong>${t("outlet")} ${n}</strong><span id="outlet-label-${n}">—</span></div><button id="outlet-${n}" class="switch" role="switch" aria-checked="false" aria-label="${t("outlet")} ${n}" disabled></button></div>`).join("")}</div></div></section>
      <section id="activity" class="panel activity-panel" aria-labelledby="activity-heading"><div class="panel-heading"><div><h2 id="activity-heading">${t("recent")}</h2><p>${t("recentNote")}</p></div>${icon("clock")}</div><div class="activity-scroll"><table class="activity-table"><thead><tr><th>${t("action")}</th><th>${t("setting")}</th><th>${t("result")}</th><th>${t("time")}</th></tr></thead><tbody id="activity-body"></tbody></table></div></section>
      <footer class="page-footer"><span>${t("footer")}</span><span>${t("timezone")} ${escape(Intl.DateTimeFormat().resolvedOptions().timeZone)}</span></footer>
    </main><div id="toast" class="toast" role="status" aria-live="polite" hidden></div>
    <div id="connect-overlay" class="connect-overlay"><div class="connect-card">${brand()}<h2>${t("connectTitle")}</h2><p>${t("connectText")}</p><p>${t("connectHint")}</p><code>growbridge dashboard</code><p>${t("connectFoot")}</p><p id="connect-error" class="connect-error" hidden></p><button id="reconnect" class="small-button">${icon("refresh")}${t("reconnect")}</button></div></div>
  </div>`;
  $("language").value = state.lang;
  $("chart-metric").value = state.metric;
  $("language").addEventListener("change", (event) => {
    state.lang = event.target.value;
    localStorage.setItem("growbridge-language", state.lang);
    mount();
  });
  $("refresh").addEventListener("click", () => load(true));
  $("reconnect").addEventListener("click", async () => {
    try {
      await api("/health");
      state.authorized = true;
      await load(true);
    } catch {
      showConnect(t("connectError"));
    }
  });
  $("logout").addEventListener("click", async () => {
    try {
      await api("/ui/logout", { method: "POST" });
    } finally {
      state.authorized = false;
      showConnect();
    }
  });
  $("chart-metric").addEventListener("change", (event) => {
    state.metric = event.target.value;
    hoverIndex = null;
    drawChart();
  });
  document.querySelectorAll("[data-hours]").forEach((button) =>
    button.addEventListener("click", async () => {
      state.hours = Number(button.dataset.hours);
      state.series = null;
      hoverIndex = null;
      document.querySelectorAll("[data-hours]").forEach((b) => {
        b.classList.toggle("selected", b === button);
        b.setAttribute("aria-pressed", b === button);
      });
      drawChart();
      await loadHistory();
    }),
  );
  document.querySelectorAll(".nav a").forEach((link) =>
    link.addEventListener("click", () => {
      document
        .querySelectorAll(".nav a")
        .forEach((a) => a.classList.toggle("active", a === link));
    }),
  );
  deviceInfo.forEach((d) => {
    $("slider-" + d.key).addEventListener("input", (event) => {
      state.drafts[d.key] = Number(event.target.value);
      state.dirty.add(d.key);
      updateTarget(d);
    });
    $("apply-" + d.key).addEventListener("click", () =>
      mutate(
        "/control/" + d.key,
        { level: state.drafts[d.key] },
        "applied",
        d.key,
      ),
    );
  });
  $("pump-seconds").addEventListener("input", (event) => {
    state.pumpSeconds = Number(event.target.value);
    updateControls();
  });
  $("run-pump").addEventListener("click", () => {
    if (
      !numeric(state.pumpSeconds) ||
      state.pumpSeconds <= 0 ||
      state.pumpSeconds > state.settings.max_pump_seconds
    ) {
      toast(t("invalidDuration"), true);
      return;
    }
    mutate("/pump", { seconds: state.pumpSeconds }, "pumpDone", "pump");
  });
  [1, 2, 3, 4, 5].forEach((n) =>
    $("outlet-" + n).addEventListener("click", () =>
      mutate(
        "/outlet",
        { number: n, on: state.status.data.outlet?.["O" + n]?.on !== 1 },
        "powerDone",
      ),
    ),
  );
  $("export").addEventListener("click", () => {
    if (state.authorized)
      window.location.assign("/history/export.csv?hours=" + state.hours);
  });
  const canvas = $("chart");
  resizeObserver = new ResizeObserver(() => drawChart());
  resizeObserver.observe(canvas.parentElement);
  canvas.addEventListener("pointermove", (event) => {
    const rect = canvas.getBoundingClientRect();
    const samples = chartSamples();
    if (!samples.length || !state.series) return;
    const fraction = Math.max(
      0,
      Math.min(1, (event.clientX - rect.left - 45) / (rect.width - 63)),
    );
    const at =
      state.series.window.start +
      fraction * (state.series.window.end - state.series.window.start);
    hoverIndex = samples.reduce(
      (best, s, index) =>
        Math.abs(s.timestamp - at) < Math.abs(samples[best].timestamp - at)
          ? index
          : best,
      0,
    );
    drawChart();
  });
  canvas.addEventListener("pointerleave", () => {
    hoverIndex = null;
    drawChart();
  });
  render();
  requestAnimationFrame(drawChart);
}

class AuthError extends Error {}
async function api(path, options = {}) {
  const headers = {};
  if (options.method && options.method !== "GET")
    headers["X-GrowBridge-UI"] = "1";
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch(path, {
    method: options.method || "GET",
    headers,
    credentials: "same-origin",
    cache: "no-store",
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  const body = await response.json();
  if (response.status === 401) throw new AuthError(t("connectError"));
  if (!response.ok)
    throw new Error(typeof body.detail === "string" ? body.detail : t("error"));
  return body;
}

function showConnect(error = "") {
  $("connect-overlay").hidden = false;
  $("connect-error").textContent = error;
  $("connect-error").hidden = !error;
  updateControls();
}
async function load(force = false) {
  if (!state.authorized || state.refreshing) return;
  state.refreshing = true;
  $("refresh").classList.add("spin");
  try {
    const [status, settings] = await Promise.all([
      api("/status"),
      api("/ui/settings"),
    ]);
    state.status = status;
    state.settings = settings;
    state.network = true;
    if (state.pumpSeconds === null)
      state.pumpSeconds = Math.min(5, settings.max_pump_seconds);
    render();
    if (force || Date.now() - state.lastHistory > 30000) {
      await Promise.all([loadHistory(), loadActivity()]);
    }
  } catch (error) {
    if (error instanceof AuthError) {
      state.authorized = false;
      showConnect(error.message);
    } else {
      state.network = false;
      updateControls();
    }
  } finally {
    state.refreshing = false;
    $("refresh").classList.remove("spin");
  }
}
async function loadHistory() {
  if (!state.authorized) return;
  const hours = state.hours;
  try {
    const data = await api("/history/series?hours=" + hours + "&points=600");
    if (hours === state.hours) {
      state.series = data;
      state.lastHistory = Date.now();
      hoverIndex = null;
      drawChart();
    }
  } catch (error) {
    if (error instanceof AuthError) {
      state.authorized = false;
      showConnect(error.message);
    } else toast(error.message, true);
  }
}
async function loadActivity() {
  const data = await api("/activity?limit=12");
  state.operations = data.operations;
  renderActivity();
}

function liveReady() {
  const health = state.status?.health;
  const age = health?.last_sample_at
    ? Math.max(0, Date.now() / 1000 - health.last_sample_at)
    : Infinity;
  return (
    state.authorized &&
    state.network &&
    health?.connected &&
    !health.stale &&
    age <= (state.settings?.stale_seconds || 20)
  );
}
function canControl() {
  return (
    liveReady() &&
    state.status.health.controls_enabled &&
    !state.status.health.pump_off_unconfirmed &&
    !state.busy
  );
}
function updateTarget(device) {
  $("target-" + device.key).textContent =
    format(state.drafts[device.key]) +
    (device.key === "fan" ? " " + t("gear") : "%");
}
function render() {
  $("connect-overlay").hidden = state.authorized;
  if (state.status) {
    const data = state.status.data;
    metrics.forEach((metric) => {
      $("metric-" + metric.key).textContent = format(
        data.sensor?.[metric.key],
        metric.precision,
      );
    });
    deviceInfo.forEach((device) => {
      const actual = data[device.module];
      const present = actual && numeric(actual.level);
      const on =
        present &&
        (actual.on === 1 || (actual.on === undefined && actual.level > 0));
      const badge = $("device-state-" + device.key);
      badge.textContent = present ? t(on ? "on" : "off") : t("notAvailable");
      badge.classList.toggle("on", Boolean(on));
      const power =
        data.outlet?.["O" + state.status.health.outlet_mapping[device.key]]
          ?.on === 1;
      $("readback-" + device.key).textContent = present
        ? t("readback") +
          ": " +
          format(actual.level) +
          (device.key === "fan" ? " " + t("gear") : "%") +
          (power ? "" : " · " + t("supplyOff"))
        : t("notAvailable");
      if (!state.dirty.has(device.key))
        state.drafts[device.key] = present ? actual.level : 0;
      $("slider-" + device.key).value = state.drafts[device.key];
      updateTarget(device);
    });
    const system = state.status.system;
    $("system-firmware").textContent = system.ver || "—";
    $("system-protocol").textContent = state.status.health.protocol_version
      ? "BLE v" + state.status.health.protocol_version
      : "—";
    $("system-access").textContent = t(
      state.status.health.controls_enabled ? "enabled" : "readonly",
    );
    const mapping = state.status.health.outlet_mapping;
    [1, 2, 3, 4, 5].forEach((number) => {
      const name = Object.keys(mapping).find((key) => mapping[key] === number);
      $("outlet-label-" + number).textContent = name
        ? t(name)
        : t("unassigned");
      const on = data.outlet?.["O" + number]?.on === 1;
      $("outlet-" + number).classList.toggle("on", on);
      $("outlet-" + number).setAttribute("aria-checked", String(on));
      $("outlet-" + number).setAttribute(
        "aria-label",
        t("outlet") +
          " " +
          number +
          " · " +
          (name ? t(name) : t("unassigned")) +
          " · " +
          t(on ? "on" : "off"),
      );
      $("outlet-card-" + number).classList.toggle("on", on);
    });
    const pumpOn = data.outlet?.["O" + mapping.pump]?.on === 1;
    $("pump-state").textContent = t(pumpOn ? "on" : "off");
    $("pump-state").classList.toggle("on", pumpOn);
  }
  if (state.settings) {
    $("system-retention").textContent =
      state.settings.retention_days + " " + t("days");
    $("pump-limit").textContent =
      t("max") + " " + state.settings.max_pump_seconds + t("seconds");
    $("pump-seconds").max = state.settings.max_pump_seconds;
    if (document.activeElement !== $("pump-seconds"))
      $("pump-seconds").value = state.pumpSeconds;
  }
  renderActivity();
  updateControls();
  drawChart();
}
function updateControls() {
  const health = state.status?.health;
  const ready = liveReady();
  const connection = $("connection");
  connection.textContent = !state.network
    ? t("unavailable")
    : !health?.connected
      ? t("reconnecting")
      : ready
        ? t("live")
        : t("delayed");
  connection.className =
    "pill" + (ready ? "" : state.network ? " warn" : " bad");
  if (health?.last_sample_at) {
    const age = Math.max(
      0,
      Math.floor(Date.now() / 1000 - health.last_sample_at),
    );
    $("last-updated").textContent =
      t("updated") +
      " " +
      (age < 60
        ? age + t("seconds") + " " + t("ago")
        : when(health.last_sample_at));
  }
  const banner = $("banner");
  const fault = health?.pump_off_unconfirmed;
  banner.hidden =
    !state.authorized || (ready && health?.controls_enabled && !fault);
  banner.textContent = fault
    ? t("pumpFault")
    : !ready
      ? t("staleBanner")
      : t("controlsDisabled");
  banner.classList.toggle("error", Boolean(fault));
  const allowed = canControl();
  deviceInfo.forEach((device) => {
    const exists = numeric(state.status?.data[device.module]?.level);
    $("slider-" + device.key).disabled = !allowed || !exists;
    $("apply-" + device.key).disabled = !allowed || !exists;
  });
  const remaining = state.settings
    ? Math.max(0, Math.ceil(state.settings.pump_ready_at - Date.now() / 1000))
    : 0;
  $("pump-seconds").disabled = !allowed;
  $("run-pump").disabled =
    !allowed ||
    remaining > 0 ||
    !state.status?.data.outlet?.["O" + health?.outlet_mapping.pump];
  $("run-pump").querySelector("span").textContent = state.pumpBusy
    ? t("pumpWaiting")
    : t("runPump") +
      " · " +
      format(state.pumpSeconds, Number.isInteger(state.pumpSeconds) ? 0 : 1) +
      t("seconds");
  $("pump-note").textContent =
    remaining > 0 && !state.pumpBusy
      ? t("cooldown") + " " + remaining + t("seconds")
      : t("pumpNote");
  [1, 2, 3, 4, 5].forEach((number) => {
    const pump = number === health?.outlet_mapping.pump;
    const assigned = Object.values(health?.outlet_mapping || {}).includes(
      number,
    );
    const on = state.status?.data.outlet?.["O" + number]?.on === 1;
    $("outlet-" + number).disabled =
      !allowed ||
      !assigned ||
      !state.status?.data.outlet?.["O" + number] ||
      (pump && !on);
    $("outlet-" + number).title = pump && !on ? t("timedOnly") : "";
  });
  $("export").disabled = !state.authorized || !state.network;
}

async function mutate(path, params, success, dirtyKey, retryBody = null) {
  if (state.busy || (!retryBody && !canControl())) return;
  const body = retryBody || {
    ...params,
    request_id: "ui-" + crypto.randomUUID(),
  };
  state.busy = true;
  state.pumpBusy = path === "/pump";
  updateControls();
  try {
    await api(path, { method: "POST", body });
    if (dirtyKey) state.dirty.delete(dirtyKey);
    state.retry = null;
    toast(t(success));
  } catch (error) {
    if (error instanceof AuthError) {
      state.authorized = false;
      showConnect(error.message);
    } else {
      state.retry = { path, params, success, dirtyKey, body };
      toast(t("error") + " " + error.message, true, true);
    }
  } finally {
    state.busy = false;
    state.pumpBusy = false;
    if (state.authorized) {
      try {
        const [status, settings] = await Promise.all([
          api("/status"),
          api("/ui/settings"),
        ]);
        state.status = status;
        state.settings = settings;
        await loadActivity();
        render();
      } catch {
        await load(true);
      }
    }
    updateControls();
  }
}
function toast(message, error = false, retry = false) {
  clearTimeout(toastTimer);
  const box = $("toast");
  box.className = "toast" + (error ? " error" : "");
  box.textContent = message;
  box.hidden = false;
  if (retry) {
    const button = document.createElement("button");
    button.className = "small-button";
    button.textContent = t("retry");
    button.addEventListener("click", () => {
      const r = state.retry;
      if (r) mutate(r.path, r.params, r.success, r.dirtyKey, r.body);
    });
    box.append(" ", button);
  }
  toastTimer = setTimeout(
    () => {
      box.hidden = true;
    },
    error ? 25000 : 5000,
  );
}
function renderActivity() {
  $("activity-body").innerHTML = state.operations.length
    ? state.operations
        .map((operation) => {
          const key = ["light", "exhaust", "fan", "pump", "outlet"].includes(
            operation.action,
          )
            ? operation.action
            : "action";
          let setting = "—";
          if (key === "pump")
            setting = format(operation.params.seconds, 1) + t("seconds");
          else if (key === "outlet")
            setting =
              t("outlet") +
              " " +
              operation.params.number +
              " · " +
              t(operation.params.on ? "on" : "off");
          else if (numeric(operation.params.level))
            setting =
              format(operation.params.level) +
              (key === "fan" ? " " + t("gear") : "%");
          const result =
            operation.state === "complete"
              ? "confirmed"
              : operation.state === "pending"
                ? "pending"
                : "failed";
          return `<tr><td>${escape(t(key))}</td><td>${escape(setting)}</td><td><span class="status-tag ${result === "confirmed" ? "" : result}">${t(result)}</span></td><td title="${escape(operation.request_id)}">${escape(when(operation.requested_at, true))}</td></tr>`;
        })
        .join("")
    : `<tr><td colspan="4" class="empty-row">${t("emptyActivity")}</td></tr>`;
}

function chartSamples() {
  return (state.series?.samples || []).filter((sample) =>
    numeric(sample.data.sensor?.[state.metric]),
  );
}
function drawChart() {
  const canvas = $("chart");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  const ratio = window.devicePixelRatio || 1;
  canvas.width = rect.width * ratio;
  canvas.height = rect.height * ratio;
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  const w = rect.width,
    h = rect.height,
    pad = { left: 45, right: 18, top: 17, bottom: 32 };
  const pw = w - pad.left - pad.right,
    ph = h - pad.top - pad.bottom;
  const metric = metrics.find((m) => m.key === state.metric),
    samples = chartSamples();
  $("chart-empty").hidden = samples.length > 0;
  $("chart-empty").textContent = state.series ? t("noHistory") : t("loading");
  $("chart-count").textContent = state.series
    ? format(samples.length) +
      " " +
      t("snapshots") +
      " / " +
      format(state.series.total_samples)
    : "—";
  $("chart-sampling").textContent = state.series
    ? t(state.series.downsampled ? "sampled" : "complete")
    : "";
  $("chart-tooltip").hidden = true;
  if (!samples.length) return;
  canvas.setAttribute(
    "aria-label",
    t(metric.short) +
      ": " +
      samples.length +
      " " +
      t("snapshots") +
      ", " +
      state.hours +
      "h",
  );
  const values = samples.map((s) => s.data.sensor[state.metric]);
  let min = Math.min(...values),
    max = Math.max(...values);
  const spread = Math.max(
    max - min,
    metric.precision === 0 ? 4 : metric.precision === 2 ? 0.08 : 0.8,
  );
  min -= spread * 0.25;
  max += spread * 0.25;
  const x = (stamp) =>
    pad.left +
    ((stamp - state.series.window.start) /
      (state.series.window.end - state.series.window.start)) *
      pw;
  const y = (value) => pad.top + ph - ((value - min) / (max - min)) * ph;
  ctx.font = "9px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.fillStyle = "#859087";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 3; i++) {
    const position = pad.top + (ph * i) / 3;
    ctx.strokeStyle = "#edf0e8";
    ctx.beginPath();
    ctx.moveTo(pad.left, position);
    ctx.lineTo(w - pad.right, position);
    ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(
      format(max - ((max - min) * i) / 3, metric.precision),
      pad.left - 9,
      position + 3,
    );
  }
  for (let i = 0; i <= 4; i++) {
    const stamp =
      state.series.window.start +
      ((state.series.window.end - state.series.window.start) * i) / 4;
    ctx.textAlign = i === 0 ? "left" : i === 4 ? "right" : "center";
    const label = new Date(stamp * 1000).toLocaleString(
      state.lang === "zh" ? "zh-CN" : "en-GB",
      state.hours > 24
        ? { month: "short", day: "numeric" }
        : { hour: "2-digit", minute: "2-digit" },
    );
    ctx.fillText(label, pad.left + (pw * i) / 4, h - 10);
  }
  const gap = Math.max(30, state.series.window.bucket_seconds * 2.5);
  ctx.strokeStyle = "#327858";
  ctx.lineWidth = 2;
  ctx.lineJoin = "round";
  ctx.beginPath();
  samples.forEach((sample, i) => {
    const px = x(sample.timestamp),
      py = y(values[i]);
    if (!i || sample.timestamp - samples[i - 1].timestamp > gap)
      ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  });
  ctx.stroke();
  if (samples.length === 1) {
    ctx.fillStyle = "#327858";
    ctx.beginPath();
    ctx.arc(x(samples[0].timestamp), y(values[0]), 3, 0, Math.PI * 2);
    ctx.fill();
  }
  if (hoverIndex !== null && samples[hoverIndex]) {
    const sample = samples[hoverIndex],
      px = x(sample.timestamp),
      py = y(values[hoverIndex]);
    ctx.strokeStyle = "#adc6af";
    ctx.setLineDash([3, 3]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(px, pad.top);
    ctx.lineTo(px, pad.top + ph);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#23684d";
    ctx.beginPath();
    ctx.arc(px, py, 3.5, 0, Math.PI * 2);
    ctx.fill();
    const tip = $("chart-tooltip");
    tip.textContent =
      when(sample.timestamp, true) +
      " · " +
      format(values[hoverIndex], metric.precision) +
      " " +
      metric.unit;
    tip.hidden = false;
    tip.style.left = Math.min(Math.max(0, px - 90), w - 185) + "px";
    tip.style.top = Math.max(0, py - 48) + "px";
  }
}

async function connectFromLocation() {
  const fragment = new URLSearchParams(location.hash.slice(1));
  const code = fragment.get("session");
  if (code) history.replaceState(null, "", location.pathname + location.search);
  try {
    if (code)
      await api("/ui/session/redeem", { method: "POST", body: { code } });
    else await api("/health");
    state.authorized = true;
    await load(true);
  } catch (error) {
    showConnect(code ? t("connectError") : "");
  }
}

async function start() {
  mount();
  await connectFromLocation();
  window.addEventListener("hashchange", () => {
    if (new URLSearchParams(location.hash.slice(1)).has("session"))
      connectFromLocation();
  });
  setInterval(() => {
    if (state.authorized && document.visibilityState === "visible") load();
  }, 5000);
  setInterval(() => {
    if (document.visibilityState === "visible") updateControls();
  }, 1000);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && state.authorized) load(true);
  });
}
start();
