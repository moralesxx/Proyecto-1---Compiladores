

import os
import sys
from flask import Flask, request, jsonify, render_template_string

# Asegurarse de que el directorio actual esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline

app = Flask(__name__)

# ─── Código de ejemplo ────────────────────────────────────────────────────────

EJEMPLO = """\
program {
    // Variables y arreglos
    int[] nums = [3, 1, 4, 1, 5];
    int total = 0;
    int i = 0;

    // Ciclo con break y modulo
    while (i < 5) {
        int r = nums[i] % 2;
        if (r == 0) {
            total = total + nums[i];
        }
        i = i + 1;
        if (total > 10) { break; }
    }

    // Funcion recursiva
    int fibonacci(int n) {
        if (n <= 1) { return n; }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    string msg = "Fibonacci(7) = ";
    print(msg);
    print(fibonacci(7));
    print("Total pares: ");
    print(total);
}
"""

# ─── HTML de la interfaz ─────────────────────────────────────────────────────

HTML_UI = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Compilador v3 — Interfaz Interactiva</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

  :root {
    --bg:       #0d0f14;
    --surface:  #13161e;
    --border:   #1e2333;
    --accent:   #00e5ff;
    --accent2:  #7c3aed;
    --ok:       #22c55e;
    --error:    #ef4444;
    --skip:     #f59e0b;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --mono:     'JetBrains Mono', monospace;
    --sans:     'Syne', sans-serif;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ── Header ─────────────────────────────────────── */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }

  .brand-title {
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
  }

  .brand-title span { color: var(--accent); }

  .header-badge {
    background: var(--accent2);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    letter-spacing: 0.08em;
  }

  /* ── Layout ──────────────────────────────────────── */
  .workspace {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
    gap: 0;
    flex: 1;
    overflow: hidden;
  }

  .panel {
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    flex-shrink: 0;
  }

  .panel-header .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
  }

  .panel-body {
    flex: 1;
    overflow: auto;
    padding: 0;
  }

  /* ── Editor ──────────────────────────────────────── */
  #editor-panel { grid-column: 1; grid-row: 1 / 3; }

  #code-input {
    width: 100%;
    height: 100%;
    min-height: 500px;
    background: #0a0c10;
    color: #c9d1d9;
    font-family: var(--mono);
    font-size: 0.82rem;
    line-height: 1.7;
    border: none;
    outline: none;
    resize: none;
    padding: 20px;
    tab-size: 4;
  }

  /* ── Fases ───────────────────────────────────────── */
  #phases-panel { grid-column: 2; grid-row: 1; }

  .phases-grid {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 12px;
    gap: 6px;
  }

  .phase-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--bg);
    border: 1px solid var(--border);
    font-size: 0.8rem;
    transition: all 0.2s;
  }

  .phase-row.ok    { border-color: var(--ok);    background: #052012; }
  .phase-row.error { border-color: var(--error);  background: #1a0505; }
  .phase-row.skip  { border-color: var(--skip);   background: #1a1005; }
  .phase-row.idle  { opacity: 0.5; }

  .phase-icon { font-size: 1rem; width: 20px; text-align: center; }

  .phase-name {
    flex: 1;
    font-weight: 700;
    font-family: var(--mono);
    font-size: 0.75rem;
  }

  .phase-status {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .phase-row.ok    .phase-status { background: var(--ok);    color: #000; }
  .phase-row.error .phase-status { background: var(--error);  color: #fff; }
  .phase-row.skip  .phase-status { background: var(--skip);   color: #000; }
  .phase-row.idle  .phase-status { background: var(--border); color: var(--muted); }

  .phase-time {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--muted);
    min-width: 60px;
    text-align: right;
  }

  .phase-errors {
    padding: 8px 14px 10px 44px;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: #fca5a5;
    line-height: 1.5;
    display: none;
  }

  /* ── Tabs de salida ──────────────────────────────── */
  #output-panel { grid-column: 2; grid-row: 2; }

  .tabs {
    display: flex;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }

  .tab-btn {
    padding: 8px 16px;
    font-family: var(--mono);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--muted);
    background: transparent;
    border: none;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
    text-transform: uppercase;
  }

  .tab-btn:hover { color: var(--text); }
  .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

  .tab-content {
    display: none;
    font-family: var(--mono);
    font-size: 0.75rem;
    line-height: 1.7;
    padding: 16px;
    white-space: pre-wrap;
    word-break: break-all;
    color: #a0aec0;
    height: 100%;
    overflow: auto;
  }

  .tab-content.active { display: block; }

  /* ── Compile button ──────────────────────────────── */
  .editor-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    gap: 8px;
  }

  #compile-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, var(--accent), #00b4cc);
    color: #000;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    font-family: var(--sans);
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    cursor: pointer;
    transition: all 0.15s;
  }

  #compile-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(0,229,255,0.3); }
  #compile-btn:active { transform: translateY(0); }
  #compile-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  #load-example-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 7px 14px;
    border-radius: 6px;
    font-family: var(--sans);
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.15s;
  }

  #load-example-btn:hover { color: var(--text); border-color: var(--muted); }

  /* ── Spinner ─────────────────────────────────────── */
  .spinner {
    width: 14px; height: 14px;
    border: 2px solid rgba(0,0,0,0.3);
    border-top-color: #000;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    display: none;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Misc ────────────────────────────────────────── */
  .empty-state {
    color: var(--muted);
    font-size: 0.8rem;
    padding: 20px;
    font-style: italic;
  }

  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  @media (max-width: 900px) {
    .workspace { grid-template-columns: 1fr; grid-template-rows: auto auto auto; }
    #editor-panel { grid-column: 1; grid-row: 1; }
    #phases-panel { grid-column: 1; grid-row: 2; }
    #output-panel { grid-column: 1; grid-row: 3; }
    #code-input { min-height: 300px; }
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <div class="brand-icon">⚙</div>
    <div class="brand-title">Compilador<span>UMG</span></div>
  </div>
  <span class="header-badge">PROYECTO 3 — PIPELINE v3</span>
</header>

<div class="workspace">

  <!-- Editor -->
  <div class="panel" id="editor-panel">
    <div class="panel-header">
      <span>📝 &nbsp;CÓDIGO FUENTE</span>
      <div class="dot"></div>
    </div>
    <div class="editor-toolbar">
      <button id="load-example-btn" onclick="loadExample()">Cargar ejemplo</button>
      <button id="compile-btn" onclick="compile()">
        <span class="spinner" id="spinner"></span>
        <span id="btn-label">▶ Compilar</span>
      </button>
    </div>
    <div class="panel-body" style="padding:0;">
      <textarea id="code-input" spellcheck="false" placeholder="// Escribe tu código aquí..."></textarea>
    </div>
  </div>

  <!-- Fases -->
  <div class="panel" id="phases-panel">
    <div class="panel-header">
      <span>⚡ &nbsp;FASES DEL PIPELINE</span>
    </div>
    <div class="panel-body">
      <div class="phases-grid" id="phases-grid">
        <!-- Placeholders -->
        <div class="phase-row idle"><span class="phase-icon">🔤</span><span class="phase-name">Léxico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🌲</span><span class="phase-name">Sintáctico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🔍</span><span class="phase-name">Semántico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">📄</span><span class="phase-name">TAC</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">⚙️</span><span class="phase-name">LLVM IR</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🚀</span><span class="phase-name">Ejecución</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
      </div>
    </div>
  </div>

  <!-- Salida con tabs -->
  <div class="panel" id="output-panel">
    <div class="panel-header" style="padding:0;">
      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('tac')">TAC</button>
        <button class="tab-btn" onclick="switchTab('ir')">LLVM IR</button>
        <button class="tab-btn" onclick="switchTab('console')">Consola</button>
        <button class="tab-btn" onclick="switchTab('lli')">Salida lli</button>
      </div>
    </div>
    <div class="panel-body" style="position:relative;">
      <div class="tab-content active" id="tab-tac"><span class="empty-state">— Compilar para ver el TAC generado —</span></div>
      <div class="tab-content" id="tab-ir"><span class="empty-state">— Compilar para ver el LLVM IR generado —</span></div>
      <div class="tab-content" id="tab-console"><span class="empty-state">— Aquí aparecerá la salida del intérprete —</span></div>
      <div class="tab-content" id="tab-lli"><span class="empty-state">— Aquí aparecerá la salida de lli —</span></div>
    </div>
  </div>

</div>

<script>
const PHASE_ICONS = {
  "Léxico":     "🔤",
  "Sintáctico": "🌲",
  "Semántico":  "🔍",
  "TAC":        "📄",
  "LLVM IR":    "⚙️",
  "Ejecución":  "🚀",
};

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach((b,i) => {
    const tabs = ['tac','ir','console','lli'];
    b.classList.toggle('active', tabs[i] === name);
  });
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
}

function loadExample() {
  document.getElementById('code-input').value = {{ example|tojson }};
}

async function compile() {
  const code = document.getElementById('code-input').value.trim();
  if (!code) { alert('Escribe algo de código primero.'); return; }

  const btn = document.getElementById('compile-btn');
  const spinner = document.getElementById('spinner');
  const label = document.getElementById('btn-label');

  btn.disabled = true;
  spinner.style.display = 'block';
  label.textContent = 'Compilando...';

  // Reset fases
  renderPhases([]);

  try {
    const resp = await fetch('/compile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });
    const data = await resp.json();

    renderPhases(data.phases || []);

    document.getElementById('tab-tac').textContent     = data.tac_code    || '(sin TAC)';
    document.getElementById('tab-ir').textContent      = data.ir_code     || '(sin IR)';
    document.getElementById('tab-console').textContent = (data.console_output || []).join('\n') || '(sin salida)';
    document.getElementById('tab-lli').textContent     = data.ir_output   || '(sin salida de lli)';

  } catch (err) {
    document.getElementById('tab-console').textContent = 'Error de red: ' + err.message;
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    label.textContent = '▶ Compilar';
  }
}

function renderPhases(phases) {
  const grid = document.getElementById('phases-grid');
  const phaseNames = ['Léxico','Sintáctico','Semántico','TAC','LLVM IR','Ejecución'];

  const phaseMap = {};
  (phases || []).forEach(p => phaseMap[p.name] = p);

  grid.innerHTML = phaseNames.map(name => {
    const p = phaseMap[name];
    if (!p) {
      return `<div class="phase-row idle">
        <span class="phase-icon">${PHASE_ICONS[name]||'•'}</span>
        <span class="phase-name">${name}</span>
        <span class="phase-status">—</span>
        <span class="phase-time">—</span>
      </div>`;
    }

    const cls = p.status === 'OK' ? 'ok' : p.status === 'ERROR' ? 'error' : 'skip';
    const errHtml = (p.errors||[]).length ? `<div class="phase-errors" style="display:block">` +
      p.errors.map(e => `⚠ Línea ${e.line}, Col ${e.column}: ${e.message}`).join('\n') +
      `</div>` : '';

    return `<div class="phase-row ${cls}">
      <span class="phase-icon">${PHASE_ICONS[name]||'•'}</span>
      <span class="phase-name">${name}</span>
      <span class="phase-status">${p.status}</span>
      <span class="phase-time">${p.time_ms} ms</span>
    </div>${errHtml}`;
  }).join('');
}

// Ctrl+Enter para compilar
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') compile();
});
</script>
</body>
</html>"""


# ─── Rutas Flask ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML_UI, example=EJEMPLO)


@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    source = data.get("code", "")

    result = run_pipeline(source, tac_file="output.tac", ll_file="output.ll")
    return jsonify(result.to_dict())


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   Compilador UMG — Interfaz Web v3       ║")
    print("║   http://localhost:5000                  ║")
    print("║   Ctrl+C para detener                    ║")
    print("╚══════════════════════════════════════════╝")
    app.run(debug=True, port=5000, use_reloader=False)
