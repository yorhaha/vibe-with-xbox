from __future__ import annotations

import json
import queue
import subprocess
import threading
import webbrowser
from dataclasses import asdict
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import __version__
from .bridge import BridgeEvent, ControllerBridge
from .config import APP_NAME, CONFIG_PATH, guide_rows, load_config, write_default_config
from .doctor import CheckResult, run_checks
from .macos import open_accessibility_settings


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vibe with Xbox</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #1e242b;
      --muted: #68717c;
      --line: #d7d2c7;
      --paper: #f7f3ea;
      --panel: #fffdf7;
      --panel-2: #eef5f1;
      --accent: #f0b33f;
      --green: #4f9d64;
      --red: #c9564c;
      --blue: #3e83be;
      --yellow: #d5bf35;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      padding: 20px 28px;
      background: #20262e;
      color: #f8fafc;
    }
    h1 {
      margin: 0;
      font-size: 26px;
      letter-spacing: 0;
    }
    header p {
      margin: 4px 0 0;
      color: #d8dde4;
      font-size: 14px;
    }
    .version {
      color: #d8dde4;
      font-size: 13px;
      white-space: nowrap;
    }
    main {
      display: grid;
      grid-template-columns: minmax(420px, 1.25fr) minmax(340px, 0.75fr);
      gap: 18px;
      padding: 18px;
      max-width: 1240px;
      margin: 0 auto;
    }
    .toolbar,
    .status-bar,
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .toolbar {
      grid-column: 1 / -1;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      padding: 12px;
    }
    button {
      appearance: none;
      border: 1px solid #b8b1a4;
      background: #fffaf0;
      color: var(--ink);
      border-radius: 7px;
      padding: 9px 13px;
      font-weight: 700;
      cursor: pointer;
    }
    button.primary {
      background: #20262e;
      color: #fff;
      border-color: #20262e;
    }
    button:hover { border-color: #81796c; }
    .status-bar {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1px;
      overflow: hidden;
    }
    .status-item {
      padding: 11px 13px;
      background: #fffaf0;
      min-width: 0;
    }
    .status-item strong {
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 4px;
    }
    .status-item span {
      display: block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .panel {
      padding: 16px;
      min-width: 0;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 17px;
    }
    .controller-wrap {
      min-height: 500px;
      display: grid;
      place-items: center;
      background: linear-gradient(180deg, #fffdf7, #f0f6f5);
      border-radius: 8px;
      border: 1px solid #e4ded2;
    }
    svg {
      width: min(100%, 720px);
      height: auto;
      overflow: visible;
    }
    .controller-body {
      fill: #242b34;
      stroke: #12161c;
      stroke-width: 4;
    }
    .control {
      transition: fill 120ms ease, stroke 120ms ease, transform 120ms ease;
      transform-box: fill-box;
      transform-origin: center;
    }
    .button-base { fill: #333c48; stroke: #11161c; stroke-width: 2; }
    .control.active .button-base,
    .control.active.button-base {
      fill: var(--accent);
      stroke: #8d6420;
    }
    .control.active { transform: scale(1.04); }
    .button-text {
      fill: #fff;
      font-weight: 800;
      font-size: 16px;
      text-anchor: middle;
      dominant-baseline: middle;
      pointer-events: none;
    }
    .callout {
      stroke: #7d766b;
      stroke-width: 1.4;
      fill: none;
    }
    .callout-label {
      fill: #272a2e;
      font-size: 13px;
      font-weight: 750;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      text-align: left;
      border-bottom: 1px solid #e6e0d6;
      padding: 9px 8px;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }
    tr.active {
      background: #fff2cf;
    }
    .checks {
      margin-top: 16px;
    }
    .check {
      display: grid;
      grid-template-columns: 130px 110px 1fr;
      gap: 10px;
      padding: 9px 0;
      border-bottom: 1px solid #e6e0d6;
      font-size: 14px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 82px;
      border-radius: 999px;
      padding: 4px 8px;
      font-weight: 800;
      font-size: 12px;
    }
    .ok { background: #dff2e4; color: #216633; }
    .warn { background: #fff0c7; color: #75520d; }
    .fail { background: #ffe0dc; color: #8d2c24; }
    .note {
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; }
      .status-bar { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Vibe with Xbox</h1>
      <p>用 Xbox 手柄操作 Claude Code 和 tmux</p>
    </div>
    <div class="version">v__VERSION__</div>
  </header>
  <main>
    <section class="toolbar" aria-label="控制操作">
      <button class="primary" id="start">启动手柄映射</button>
      <button id="stop">停止</button>
      <button id="checks">运行环境检查</button>
      <button id="config">打开配置</button>
      <button id="accessibility">辅助功能权限</button>
      <button id="quit">退出应用</button>
    </section>
    <section class="status-bar">
      <div class="status-item"><strong>手柄</strong><span id="connection">尚未启动</span></div>
      <div class="status-item"><strong>最近操作</strong><span id="last-action">暂无手柄操作</span></div>
    </section>
    <section class="panel">
      <h2>手柄按键说明</h2>
      <div class="controller-wrap">
        __CONTROLLER_SVG__
      </div>
    </section>
    <aside class="panel">
      <h2>当前映射</h2>
      <table>
        <thead><tr><th>控制项</th><th>操作</th></tr></thead>
        <tbody id="mapping-table"></tbody>
      </table>
      <div class="checks">
        <h2>环境检查</h2>
        <div id="check-list"></div>
      </div>
      <p class="note">
        tmux 操作仅作用于本机 tmux；请先在本机终端进入 tmux 会话。
      </p>
    </aside>
  </main>
  <script>
    const mappingRows = __MAPPING__;
    const controls = new Map(mappingRows.map(row => [row.control, row]));
    const table = document.getElementById("mapping-table");
    const activeTimers = new Map();

    function renderMapping() {
      table.innerHTML = "";
      mappingRows.forEach(row => {
        const tr = document.createElement("tr");
        const control = document.createElement("td");
        const action = document.createElement("td");
        tr.dataset.control = row.control;
        control.textContent = row.name;
        action.textContent = row.label;
        tr.appendChild(control);
        tr.appendChild(action);
        table.appendChild(tr);
      });
    }

    async function post(path) {
      const res = await fetch(path, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }

    function setText(id, text) {
      document.getElementById(id).textContent = text || "";
    }

    function setActive(control, active) {
      if (!control) return;
      const svgNodes = document.querySelectorAll(`[data-control="${control}"]`);
      svgNodes.forEach(node => node.classList.toggle("active", active));
      const row = table.querySelector(`[data-control="${control}"]`);
      if (row) row.classList.toggle("active", active);
    }

    function pulse(control) {
      setActive(control, true);
      if (activeTimers.has(control)) clearTimeout(activeTimers.get(control));
      activeTimers.set(control, setTimeout(() => setActive(control, false), 180));
    }

    function renderChecks(checks) {
      const list = document.getElementById("check-list");
      list.innerHTML = "";
      checks.forEach(check => {
        const div = document.createElement("div");
        const name = document.createElement("strong");
        const status = document.createElement("span");
        const message = document.createElement("span");
        div.className = "check";
        const label = check.status === "ok" ? "正常" : check.status === "fail" ? "不可用" : "需要设置";
        name.textContent = check.name;
        status.className = `pill ${check.status}`;
        status.textContent = label;
        message.textContent = check.message;
        div.appendChild(name);
        div.appendChild(status);
        div.appendChild(message);
        list.appendChild(div);
      });
    }

    function handleEvent(event) {
      if (event.kind === "connected") setText("connection", event.message);
      if (event.kind === "stopped") setText("connection", "已停止");
      if (event.kind === "error") setText("connection", event.message);
      if (event.kind === "action") {
        const row = controls.get(event.control);
        setText("last-action", `${row ? row.name : event.control}：${event.action_label}`);
        pulse(event.control);
      }
      if (event.kind === "down" || event.kind === "pulse") setActive(event.control, true);
      if (event.kind === "up") setActive(event.control, false);
      if (event.kind === "debug") setText("last-action", event.message);
    }

    document.getElementById("start").addEventListener("click", async () => {
      const result = await post("/api/start");
      setText("connection", result.message);
    });
    document.getElementById("stop").addEventListener("click", async () => {
      const result = await post("/api/stop");
      setText("connection", result.message);
    });
    document.getElementById("checks").addEventListener("click", async () => {
      renderChecks((await post("/api/checks")).checks);
    });
    document.getElementById("config").addEventListener("click", async () => {
      const result = await post("/api/config");
      setText("last-action", result.message);
    });
    document.getElementById("accessibility").addEventListener("click", async () => {
      const result = await post("/api/accessibility");
      setText("last-action", result.message);
    });
    document.getElementById("quit").addEventListener("click", async () => {
      const result = await post("/api/quit");
      setText("connection", result.message);
    });

    renderMapping();
    post("/api/checks").then(result => renderChecks(result.checks));

    const events = new EventSource("/events");
    events.onmessage = message => handleEvent(JSON.parse(message.data));
  </script>
</body>
</html>
"""


def controller_svg(config: dict[str, Any]) -> str:
    labels = {row["control"]: row["label"] for row in guide_rows(config)}

    def label(control: str) -> str:
        return escape(labels.get(control, control))

    return f"""
<svg viewBox="0 0 760 520" role="img" aria-label="Xbox 手柄按键映射">
  <path class="controller-body" d="M130 170 C190 90 280 130 320 140 L440 140 C480 130 570 90 630 170 C680 245 710 390 640 430 C590 460 530 400 475 370 L285 370 C230 400 170 460 120 430 C50 390 80 245 130 170 Z"/>

  <g class="control" data-control="LB"><rect class="button-base" x="190" y="98" width="140" height="38" rx="12"/><text class="button-text" x="260" y="118">LB</text></g>
  <g class="control" data-control="RB"><rect class="button-base" x="430" y="98" width="140" height="38" rx="12"/><text class="button-text" x="500" y="118">RB</text></g>
  <g class="control" data-control="RT"><rect class="button-base" x="510" y="48" width="150" height="34" rx="12"/><text class="button-text" x="585" y="66">长按 RT</text></g>

  <g class="control" data-control="LEFT_STICK_UP">
    <circle class="button-base" cx="245" cy="238" r="46"/>
    <text class="button-text" x="245" y="238">L</text>
  </g>
  <g class="control" data-control="LEFT_STICK_DOWN">
    <circle class="button-base" cx="245" cy="238" r="27"/>
  </g>
  <circle class="button-base" cx="455" cy="340" r="45"/>
  <g class="control" data-control="RIGHT_STICK_UP"><path class="button-base" d="M455 300 L472 326 L438 326 Z"/></g>
  <g class="control" data-control="RIGHT_STICK_DOWN"><path class="button-base" d="M455 380 L472 354 L438 354 Z"/></g>
  <g class="control" data-control="RIGHT_STICK_LEFT"><path class="button-base" d="M415 340 L441 323 L441 357 Z"/></g>
  <g class="control" data-control="RIGHT_STICK_RIGHT"><path class="button-base" d="M495 340 L469 323 L469 357 Z"/></g>

  <g class="control" data-control="DPAD_UP"><rect class="button-base" x="180" y="305" width="36" height="45" rx="8"/></g>
  <g class="control" data-control="DPAD_DOWN"><rect class="button-base" x="180" y="390" width="36" height="45" rx="8"/></g>
  <g class="control" data-control="DPAD_LEFT"><rect class="button-base" x="132" y="353" width="45" height="36" rx="8"/></g>
  <g class="control" data-control="DPAD_RIGHT"><rect class="button-base" x="219" y="353" width="45" height="36" rx="8"/></g>
  <rect class="button-base" x="180" y="353" width="36" height="36" rx="8"/>

  <g class="control" data-control="START"><rect class="button-base" x="350" y="232" width="68" height="34" rx="14"/><text class="button-text" x="384" y="250">Start</text></g>

  <g class="control" data-control="Y"><circle class="button-base" cx="548" cy="202" r="26" fill="var(--yellow)"/><text class="button-text" x="548" y="202">Y</text></g>
  <g class="control" data-control="X"><circle class="button-base" cx="504" cy="246" r="26" fill="var(--blue)"/><text class="button-text" x="504" y="246">X</text></g>
  <g class="control" data-control="B"><circle class="button-base" cx="592" cy="246" r="26" fill="var(--red)"/><text class="button-text" x="592" y="246">B</text></g>
  <g class="control" data-control="A"><circle class="button-base" cx="548" cy="290" r="26" fill="var(--green)"/><text class="button-text" x="548" y="290">A</text></g>

  <path class="callout" d="M548 170 L548 118"/><text class="callout-label" x="548" y="104" text-anchor="middle">{label("Y")}</text>
  <path class="callout" d="M620 246 L692 240"/><text class="callout-label" x="700" y="244">{label("B")}</text>
  <path class="callout" d="M548 322 L612 394"/><text class="callout-label" x="620" y="404">{label("A")}</text>
  <path class="callout" d="M478 246 L415 205"/><text class="callout-label" x="407" y="202" text-anchor="end">{label("X")}</text>

  <path class="callout" d="M245 190 L210 112"/><text class="callout-label" x="205" y="98" text-anchor="end">{label("LEFT_STICK_UP")}</text>
  <path class="callout" d="M245 285 L318 436"/><text class="callout-label" x="326" y="446">{label("LEFT_STICK_DOWN")}</text>
  <path class="callout" d="M455 295 L420 276"/><text class="callout-label" x="412" y="276" text-anchor="end">{label("RIGHT_STICK_UP")}</text>
  <path class="callout" d="M455 385 L420 420"/><text class="callout-label" x="412" y="430" text-anchor="end">{label("RIGHT_STICK_DOWN")}</text>
  <path class="callout" d="M410 340 L350 326"/><text class="callout-label" x="342" y="326" text-anchor="end">{label("RIGHT_STICK_LEFT")}</text>
  <path class="callout" d="M500 340 L550 326"/><text class="callout-label" x="558" y="326">{label("RIGHT_STICK_RIGHT")}</text>
  <path class="callout" d="M198 305 L126 270"/><text class="callout-label" x="116" y="270" text-anchor="end">{label("DPAD_UP")}</text>
  <path class="callout" d="M198 435 L126 462"/><text class="callout-label" x="116" y="466" text-anchor="end">{label("DPAD_DOWN")}</text>
  <path class="callout" d="M132 371 L74 371"/><text class="callout-label" x="64" y="375" text-anchor="end">{label("DPAD_LEFT")}</text>
  <path class="callout" d="M264 371 L322 371"/><text class="callout-label" x="332" y="375">{label("DPAD_RIGHT")}</text>
  <path class="callout" d="M260 98 L260 58"/><text class="callout-label" x="260" y="44" text-anchor="middle">{label("LB")}</text>
  <path class="callout" d="M500 98 L500 58"/><text class="callout-label" x="500" y="44" text-anchor="middle">{label("RB")}</text>
  <path class="callout" d="M585 48 L648 20"/><text class="callout-label" x="656" y="24">{label("RT")}</text>
  <path class="callout" d="M384 232 L384 190"/><text class="callout-label" x="384" y="176" text-anchor="middle">{label("START")}</text>
</svg>
"""


def render_index(config: dict[str, Any]) -> str:
    return (
        HTML_TEMPLATE.replace("__VERSION__", __version__)
        .replace("__MAPPING__", json.dumps(guide_rows(config)))
        .replace("__CONTROLLER_SVG__", controller_svg(config))
    )


class LocalGuideApp:
    def __init__(self, config_path: Path | None = None, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.config_path = config_path
        self.config = load_config(config_path)
        self.host = host
        self.port = port
        self.bridge: ControllerBridge | None = None
        self.server_thread: threading.Thread | None = None
        self.subscribers: list[queue.Queue[dict[str, Any]]] = []
        self.lock = threading.Lock()
        self.state_lock = threading.Lock()
        self.main_wakeup = threading.Event()
        self.bridge_requested = False
        self.bridge_running = False
        self.quit_requested = False
        self.check_results: list[CheckResult] = []
        self.check_requested = False
        self.check_complete = threading.Event()
        self.check_request_lock = threading.Lock()
        self.server = self._make_server()

    @property
    def url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}/"

    def run(self, open_browser: bool = True) -> int:
        # SDL controller events are only reliable on macOS when pygame is
        # initialized and pumped from the process main thread.  HTTP requests
        # therefore run in the background while this thread owns the bridge.
        self.check_results = run_checks()
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
            name="vibe-with-xbox-http",
        )
        self.server_thread.start()
        if open_browser:
            webbrowser.open(self.url)
        print(f"{APP_NAME} is running at {self.url}")

        if self.config.get("general", {}).get("auto_start_bridge", False):
            self.start_bridge()

        try:
            while True:
                self.main_wakeup.wait()
                self.main_wakeup.clear()
                with self.state_lock:
                    if self.quit_requested:
                        break
                    should_check = self.check_requested
                    self.check_requested = False
                    should_start = self.bridge_requested
                if should_check:
                    self.check_results = run_checks()
                    self.check_complete.set()
                if not should_start:
                    continue
                self._run_bridge_on_main_thread()
        except KeyboardInterrupt:
            print()
        finally:
            self.stop_bridge()
            self.server.shutdown()
            self.server.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=1.0)
        return 0

    def _run_bridge_on_main_thread(self) -> None:
        bridge = ControllerBridge(self.config, callback=self.on_bridge_event)
        with self.state_lock:
            if not self.bridge_requested or self.quit_requested:
                return
            self.bridge = bridge
            self.bridge_running = True

        try:
            bridge.run()
        except Exception as exc:
            self.on_bridge_event(BridgeEvent("error", message=f"手柄映射异常退出：{exc}"))
        finally:
            bridge.stop()
            with self.state_lock:
                if self.bridge is bridge:
                    self.bridge = None
                self.bridge_running = False
                self.bridge_requested = False

    def _make_server(self) -> ThreadingHTTPServer:
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                path = urlparse(self.path).path
                if path == "/":
                    self._send_html(render_index(app.config))
                elif path == "/events":
                    self._send_events()
                else:
                    # The reason phrase must be latin-1; the Chinese hint goes
                    # in the body instead.
                    self.send_error(HTTPStatus.NOT_FOUND, "Not Found", "未找到页面")

            def do_POST(self) -> None:
                path = urlparse(self.path).path
                if path == "/api/start":
                    self._send_json(app.start_bridge())
                elif path == "/api/stop":
                    self._send_json(app.stop_bridge())
                elif path == "/api/checks":
                    self._send_json({"checks": [asdict(check) for check in app.refresh_checks()]})
                elif path == "/api/config":
                    self._send_json(app.open_config())
                elif path == "/api/accessibility":
                    open_accessibility_settings()
                    self._send_json({"ok": True, "message": "已打开辅助功能设置。"})
                elif path == "/api/quit":
                    self._send_json(app.quit())
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, "Not Found", "未找到页面")

            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def _send_html(self, body: str) -> None:
                data = body.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _send_json(self, payload: dict[str, Any]) -> None:
                data = json.dumps(payload).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _send_events(self) -> None:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()

                client_queue: queue.Queue[dict[str, Any]] = queue.Queue()
                app.add_subscriber(client_queue)
                try:
                    self.wfile.write(b": connected\n\n")
                    self.wfile.flush()
                    while True:
                        payload = client_queue.get()
                        data = f"data: {json.dumps(payload)}\n\n".encode("utf-8")
                        self.wfile.write(data)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
                finally:
                    app.remove_subscriber(client_queue)

        for port in [self.port, *range(self.port + 1, self.port + 10), 0]:
            try:
                server = ThreadingHTTPServer((self.host, port), Handler)
                server.daemon_threads = True
                return server
            except OSError:
                continue
        raise RuntimeError("无法启动本地说明页面服务。")

    def refresh_checks(self) -> list[CheckResult]:
        # Do not reinitialize pygame while the live bridge owns it.  When the
        # bridge is idle, schedule the check on the same main thread SDL uses.
        with self.check_request_lock:
            with self.state_lock:
                if self.bridge_running or self.bridge_requested or self.quit_requested:
                    return list(self.check_results)
                self.check_requested = True
                self.check_complete.clear()
            self.main_wakeup.set()
            self.check_complete.wait(timeout=5.0)
            return list(self.check_results)

    def add_subscriber(self, client_queue: queue.Queue[dict[str, Any]]) -> None:
        with self.lock:
            self.subscribers.append(client_queue)

    def remove_subscriber(self, client_queue: queue.Queue[dict[str, Any]]) -> None:
        with self.lock:
            if client_queue in self.subscribers:
                self.subscribers.remove(client_queue)

    def broadcast(self, payload: dict[str, Any]) -> None:
        with self.lock:
            subscribers = list(self.subscribers)
        for subscriber in subscribers:
            subscriber.put(payload)

    def on_bridge_event(self, event: BridgeEvent) -> None:
        self.broadcast(
            {
                "kind": event.kind,
                "control": event.control,
                "value": event.value,
                "message": event.message,
                "action_label": event.action_label,
            }
        )

    def start_bridge(self) -> dict[str, Any]:
        with self.state_lock:
            if self.bridge_running or self.bridge_requested:
                return {"ok": True, "message": "手柄映射已在运行。"}
            self.bridge_requested = True
        self.main_wakeup.set()
        return {"ok": True, "message": "正在启动手柄映射……"}

    def stop_bridge(self) -> dict[str, Any]:
        with self.state_lock:
            self.bridge_requested = False
            bridge = self.bridge
        if bridge:
            bridge.stop()
        self.main_wakeup.set()
        return {"ok": True, "message": "已停止。"}

    def open_config(self) -> dict[str, Any]:
        path = write_default_config(self.config_path or CONFIG_PATH)
        subprocess.run(["open", str(path)], check=False)
        return {"ok": True, "message": f"已打开配置文件：{path}"}

    def quit(self) -> dict[str, Any]:
        with self.state_lock:
            self.quit_requested = True
            self.bridge_requested = False
            bridge = self.bridge
        if bridge:
            bridge.stop()
        self.main_wakeup.set()
        threading.Thread(target=self.server.shutdown, daemon=True).start()
        return {"ok": True, "message": "Vibe with Xbox 正在退出。"}


def run_gui(config_path: Path | None = None) -> int:
    app = LocalGuideApp(config_path=config_path)
    return app.run()
