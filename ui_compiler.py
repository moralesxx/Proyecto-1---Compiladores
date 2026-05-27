import os
import sys
from flask import Flask, request, jsonify, render_template_string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline

try:
    from ir_manual import get_available_passes, apply_manual_passes, export_manual_ir
    IR_MANUAL_OK = True
except ImportError:
    IR_MANUAL_OK = False

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
<title>Compilador v4 — Pipeline Interactivo</title>
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
    flex-shrink: 0;
  }

  .brand { display: flex; align-items: center; gap: 12px; }
  .brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .brand-title { font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em; }
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

  /* ── Layout principal ────────────────────────────── */
  .workspace {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
    gap: 0;
    flex: 1;
    overflow: hidden;
    min-height: 0;
  }

  .panel {
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
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

  .panel-header .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }

  .panel-body { flex: 1; overflow: auto; padding: 0; min-height: 0; }

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

  .phases-grid { display: flex; flex-direction: column; gap: 6px; padding: 12px; }

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
  .phase-name { flex: 1; font-weight: 700; font-family: var(--mono); font-size: 0.75rem; }
  .phase-status {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    padding: 2px 8px; border-radius: 4px;
  }
  .phase-row.ok    .phase-status { background: var(--ok);    color: #000; }
  .phase-row.error .phase-status { background: var(--error);  color: #fff; }
  .phase-row.skip  .phase-status { background: var(--skip);   color: #000; }
  .phase-row.idle  .phase-status { background: var(--border); color: var(--muted); }
  .phase-time { font-family: var(--mono); font-size: 0.7rem; color: var(--muted); min-width: 60px; text-align: right; }
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
    flex-wrap: wrap;
  }

  .tab-btn {
    padding: 8px 14px;
    font-family: var(--mono);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--muted);
    background: transparent;
    border: none;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
    text-transform: uppercase;
    white-space: nowrap;
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

  /* ── Botones ─────────────────────────────────────── */
  .editor-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    gap: 8px;
    flex-wrap: wrap;
  }

  .toolbar-left  { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .toolbar-right { display: flex; gap: 8px; align-items: center; }

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

  .btn-secondary {
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
  .btn-secondary:hover { color: var(--text); border-color: var(--muted); }
  .btn-secondary.active-toggle {
    background: var(--accent2);
    color: #fff;
    border-color: var(--accent2);
  }

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

  /* ── Panel IR Manual ────────────────────────────── */
  #ir-manual-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.75);
    z-index: 100;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  #ir-manual-overlay.open { display: flex; }

  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    width: 100%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .modal-header h2 { font-size: 1rem; font-weight: 800; color: var(--accent); }
  .modal-close {
    background: none;
    border: none;
    color: var(--muted);
    font-size: 1.4rem;
    cursor: pointer;
    line-height: 1;
    padding: 0 4px;
  }
  .modal-close:hover { color: var(--text); }

  .modal-body {
    display: grid;
    grid-template-columns: 240px 1fr;
    flex: 1;
    overflow: hidden;
    min-height: 0;
  }

  .passes-sidebar {
    border-right: 1px solid var(--border);
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-shrink: 0;
  }
  .passes-sidebar h3 {
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
  }

  .pass-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.15s;
    user-select: none;
  }
  .pass-card:hover { border-color: var(--accent2); }
  .pass-card.selected { border-color: var(--accent); background: #071a1f; }
  .pass-card-label {
    font-family: var(--mono);
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 2px;
  }
  .pass-card-name { font-size: 0.7rem; color: var(--text); margin-bottom: 4px; }
  .pass-card-desc { font-size: 0.65rem; color: var(--muted); line-height: 1.4; }
  .pass-card-cat {
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent2);
    margin-top: 4px;
  }

  .modal-main {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }

  .modal-toolbar {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    flex-shrink: 0;
    flex-wrap: wrap;
    align-items: center;
  }
  .modal-toolbar span { font-size: 0.75rem; color: var(--muted); }

  .diff-container {
    flex: 1;
    overflow: auto;
    padding: 16px;
    font-family: var(--mono);
    font-size: 0.73rem;
    line-height: 1.6;
    min-height: 0;
  }

  .diff-header { color: var(--muted); font-weight: 700; margin-bottom: 4px; }
  .diff-hunk   { color: var(--accent2); padding: 4px 0; }
  .diff-added  { background: #071a12; color: #86efac; display: block; padding: 0 4px; }
  .diff-removed{ background: #1a0707; color: #fca5a5; display: block; padding: 0 4px; text-decoration: line-through; }
  .diff-same   { color: var(--muted); display: block; padding: 0 4px; }
  .diff-unchanged { color: var(--muted); font-style: italic; padding: 8px; }

  .lli-output-box {
    border-top: 1px solid var(--border);
    padding: 12px 16px;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--ok);
    background: #050d0a;
    flex-shrink: 0;
    max-height: 120px;
    overflow-y: auto;
  }
  .lli-output-box.error-out { color: var(--error); background: #0d0505; }

  /* ── Panel Binarios ──────────────────────────────── */
  #binaries-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.75);
    z-index: 100;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  #binaries-overlay.open { display: flex; }

  .bin-modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    width: 100%;
    max-width: 700px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .bin-section {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
  }
  .bin-section h3 {
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 10px;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .bin-section label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 0.8rem;
    margin-bottom: 6px;
  }
  .bin-section input[type=checkbox] { accent-color: var(--accent); }
  .bin-output {
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--muted);
    background: var(--bg);
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    min-height: 36px;
    max-height: 120px;
    overflow-y: auto;
  }
  .bin-output.success { color: var(--ok); }
  .bin-output.failure { color: var(--error); }

  /* ── Misc ────────────────────────────────────────── */
  .empty-state { color: var(--muted); font-size: 0.8rem; padding: 20px; font-style: italic; }

  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Métricas O3 ─────────────────────────────────── */
  .metrics-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }
  .metric-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 16px;
    text-align: center;
    min-width: 100px;
  }
  .metric-card .metric-val {
    font-family: var(--mono);
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent);
  }
  .metric-card .metric-lbl { font-size: 0.65rem; color: var(--muted); margin-top: 2px; }
  .transform-list { list-style: none; padding: 0; }
  .transform-list li {
    padding: 8px 12px;
    border-left: 3px solid var(--accent2);
    margin-bottom: 6px;
    background: var(--bg);
    border-radius: 0 6px 6px 0;
    font-size: 0.75rem;
  }
  .transform-list li strong { color: var(--accent); display: block; margin-bottom: 2px; }
  .transform-list li span { color: var(--muted); font-size: 0.7rem; line-height: 1.4; }

  @media (max-width: 900px) {
    .workspace { grid-template-columns: 1fr; grid-template-rows: auto auto auto; }
    #editor-panel { grid-column: 1; grid-row: 1; }
    #phases-panel { grid-column: 1; grid-row: 2; }
    #output-panel { grid-column: 1; grid-row: 3; }
    #code-input { min-height: 300px; }
    .modal-body { grid-template-columns: 1fr; }
    .passes-sidebar { border-right: none; border-bottom: 1px solid var(--border); max-height: 200px; }
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <div class="brand-icon">⚙</div>
    <div class="brand-title">Compilador<span>UMG</span></div>
  </div>
  <span class="header-badge">PROYECTO FINAL — PIPELINE v4</span>
</header>

<div class="workspace">

  <!-- Editor -->
  <div class="panel" id="editor-panel">
    <div class="panel-header">
      <span>📝 &nbsp;CÓDIGO FUENTE</span>
      <div class="dot"></div>
    </div>
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="btn-secondary" onclick="loadExample()">Cargar ejemplo</button>
        <button class="btn-secondary" id="btn-linux-toggle"
          onclick="toggleOption('linux')" title="Compilar binario Linux en Fase 8">
          🐧 Linux
        </button>
        <button class="btn-secondary" id="btn-windows-toggle"
          onclick="toggleOption('windows')" title="Compilar .exe Windows en Fase 8">
          🪟 Windows
        </button>
        <button class="btn-secondary" onclick="openBinariesModal()">📦 Binarios</button>
        <button class="btn-secondary" onclick="openIRManual()">🔧 IR Manual</button>
      </div>
      <div class="toolbar-right">
        <button id="compile-btn" onclick="compile()">
          <span class="spinner" id="spinner"></span>
          <span id="btn-label">▶ Compilar</span>
        </button>
      </div>
    </div>
    <div class="panel-body" style="padding:0;">
      <textarea id="code-input" spellcheck="false" placeholder="// Escribe tu código aquí..."></textarea>
    </div>
  </div>

  <!-- Fases -->
  <div class="panel" id="phases-panel">
    <div class="panel-header">
      <span>⚡ &nbsp;FASES DEL PIPELINE v4</span>
    </div>
    <div class="panel-body">
      <div class="phases-grid" id="phases-grid">
        <div class="phase-row idle"><span class="phase-icon">🔤</span><span class="phase-name">Léxico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🌲</span><span class="phase-name">Sintáctico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🔍</span><span class="phase-name">Semántico</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">📄</span><span class="phase-name">TAC</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">⚙️</span><span class="phase-name">LLVM IR</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">🚀</span><span class="phase-name">Ejecución</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">✨</span><span class="phase-name">Optimización O3</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
        <div class="phase-row idle"><span class="phase-icon">💾</span><span class="phase-name">Binarios Nativos</span><span class="phase-status">—</span><span class="phase-time">—</span></div>
      </div>
    </div>
  </div>

  <!-- Salida con tabs -->
  <div class="panel" id="output-panel">
    <div class="panel-header" style="padding:0;">
      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('tac')">TAC</button>
        <button class="tab-btn" onclick="switchTab('ir')">LLVM IR</button>
        <button class="tab-btn" onclick="switchTab('ir-opt')">IR Optimizado</button>
        <button class="tab-btn" onclick="switchTab('console')">Consola</button>
        <button class="tab-btn" onclick="switchTab('lli')">Salida lli</button>
        <button class="tab-btn" onclick="switchTab('opt-metrics')">Métricas O3</button>
      </div>
    </div>
    <div class="panel-body" style="position:relative;">
      <div class="tab-content active" id="tab-tac"><span class="empty-state">— Compilar para ver el TAC —</span></div>
      <div class="tab-content" id="tab-ir"><span class="empty-state">— Compilar para ver el LLVM IR —</span></div>
      <div class="tab-content" id="tab-ir-opt"><span class="empty-state">— Compilar para ver el IR optimizado —</span></div>
      <div class="tab-content" id="tab-console"><span class="empty-state">— Aquí aparecerá la salida del intérprete —</span></div>
      <div class="tab-content" id="tab-lli"><span class="empty-state">— Aquí aparecerá la salida de lli —</span></div>
      <div class="tab-content" id="tab-opt-metrics"><span class="empty-state">— Compilar para ver métricas de optimización O3 —</span></div>
    </div>
  </div>

</div>

<!-- ══ Modal: IR Manual ══════════════════════════════════════════════════════ -->
<div id="ir-manual-overlay" onclick="closeOnOverlay(event,'ir-manual-overlay')">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <h2>🔧 Optimización Manual del IR</h2>
      <button class="modal-close" onclick="closeIRManual()">✕</button>
    </div>
    <div class="modal-body">
      <div class="passes-sidebar" id="passes-sidebar">
        <h3>Passes disponibles</h3>
        <div id="passes-list">
          <span class="empty-state" style="font-size:0.7rem">Cargando passes...</span>
        </div>
        <div style="margin-top:auto;padding-top:12px;border-top:1px solid var(--border);font-size:0.68rem;color:var(--muted)">
          Haz clic para seleccionar/deseleccionar passes. Se aplican en el orden seleccionado.
        </div>
      </div>
      <div class="modal-main">
        <div class="modal-toolbar">
          <button class="btn-secondary" onclick="applyManualPasses()" id="apply-passes-btn">▶ Aplicar passes</button>
          <button class="btn-secondary" onclick="clearPassSelection()">✕ Limpiar</button>
          <button class="btn-secondary" onclick="exportManualIR()" id="export-ir-btn">⬇ Exportar IR</button>
          <button class="btn-secondary" onclick="runManualIR()" id="run-ir-btn">🚀 Ejecutar IR resultante</button>
          <span id="passes-status"></span>
        </div>
        <div class="diff-container" id="diff-view">
          <span class="empty-state">Selecciona passes y haz clic en "Aplicar passes" para ver el diff del IR antes/después.</span>
        </div>
        <div class="lli-output-box" id="lli-manual-output" style="display:none"></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ Modal: Binarios ═══════════════════════════════════════════════════════ -->
<div id="binaries-overlay" onclick="closeOnOverlay(event,'binaries-overlay')">
  <div class="bin-modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <h2>💾 Generación de Binarios Nativos — Fase 8</h2>
      <button class="modal-close" onclick="closeBinariesModal()">✕</button>
    </div>
    <div style="overflow-y:auto;flex:1;">
      <div class="bin-section">
        <h3>🐧 Linux (binario nativo ELF)</h3>
        <label>
          <input type="checkbox" id="chk-linux" checked onchange="syncLinuxToggle()">
          Compilar para Linux (clang / llc + gcc)
        </label>
        <div class="bin-output" id="bin-linux-out">— Sin compilar aún —</div>
      </div>
      <div class="bin-section">
        <h3>🪟 Windows (.exe PE32+)</h3>
        <label>
          <input type="checkbox" id="chk-windows" checked onchange="syncWindowsToggle()">
          Compilar para Windows x64 (compilación cruzada vía MinGW)
        </label>
        <div class="bin-output" id="bin-windows-out">— Sin compilar aún —</div>
      </div>
      <div class="bin-section" style="border-bottom:none;">
        <p style="font-size:0.72rem;color:var(--muted);line-height:1.5;">
          Los binarios se compilan desde el IR optimizado (Fase 7) si está disponible,
          o desde el IR original (Fase 5). El ejecutable de Windows puede copiarse
          al sistema de archivos de Windows y ejecutarse desde cmd/PowerShell sin
          instalar herramientas adicionales.
        </p>
      </div>
    </div>
  </div>
</div>

<script>
// ─── Estado global ────────────────────────────────────────────────────────────
let lastData          = null;
let selectedPasses    = [];
let availablePasses   = [];
let compiledIRManual  = "";
let optLinux          = true;
let optWindows        = true;

const ALL_PHASE_NAMES = [
  "Léxico", "Sintáctico", "Semántico", "TAC",
  "LLVM IR", "Ejecución", "Optimización O3", "Binarios Nativos"
];

const PHASE_ICONS = {
  "Léxico":          "🔤",
  "Sintáctico":      "🌲",
  "Semántico":       "🔍",
  "TAC":             "📄",
  "LLVM IR":         "⚙️",
  "Ejecución":       "🚀",
  "Optimización O3": "✨",
  "Binarios Nativos":"💾",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────
const TAB_IDS = ['tac','ir','ir-opt','console','lli','opt-metrics'];

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    b.classList.toggle('active', TAB_IDS[i] === name);
  });
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
}

// ─── Toggles de plataforma ───────────────────────────────────────────────────
function toggleOption(which) {
  if (which === 'linux') {
    optLinux = !optLinux;
    document.getElementById('btn-linux-toggle').classList.toggle('active-toggle', optLinux);
    document.getElementById('chk-linux').checked = optLinux;
  } else {
    optWindows = !optWindows;
    document.getElementById('btn-windows-toggle').classList.toggle('active-toggle', optWindows);
    document.getElementById('chk-windows').checked = optWindows;
  }
}

function syncLinuxToggle() {
  optLinux = document.getElementById('chk-linux').checked;
  document.getElementById('btn-linux-toggle').classList.toggle('active-toggle', optLinux);
}
function syncWindowsToggle() {
  optWindows = document.getElementById('chk-windows').checked;
  document.getElementById('btn-windows-toggle').classList.toggle('active-toggle', optWindows);
}

// ─── Cargar ejemplo ──────────────────────────────────────────────────────────
function loadExample() {
  document.getElementById('code-input').value = {{ example|tojson }};
}

// ─── Compilar ────────────────────────────────────────────────────────────────
async function compile() {
  const code = document.getElementById('code-input').value.trim();
  if (!code) { alert('Escribe algo de código primero.'); return; }

  const btn     = document.getElementById('compile-btn');
  const spinner = document.getElementById('spinner');
  const label   = document.getElementById('btn-label');

  btn.disabled = true;
  spinner.style.display = 'block';
  label.textContent = 'Compilando...';

  renderPhases([]);

  try {
    const resp = await fetch('/compile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, compile_linux: optLinux, compile_windows: optWindows })
    });
    const data = await resp.json();
    lastData = data;

    renderPhases(data.phases || []);

    document.getElementById('tab-tac').textContent      = data.tac_code        || '(sin TAC)';
    document.getElementById('tab-ir').textContent       = data.ir_code         || '(sin IR)';
    document.getElementById('tab-ir-opt').textContent   = data.ir_optimized    || '(sin IR optimizado)';
    document.getElementById('tab-console').textContent  = (data.console_output || []).join('\n') || '(sin salida)';
    document.getElementById('tab-lli').textContent      = data.ir_output       || '(sin salida de lli)';

    renderOptMetrics(data);
    updateBinariesModal(data);

  } catch (err) {
    document.getElementById('tab-console').textContent = 'Error de red: ' + err.message;
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    label.textContent = '▶ Compilar';
  }
}

// ─── Render fases ────────────────────────────────────────────────────────────
function renderPhases(phases) {
  const grid    = document.getElementById('phases-grid');
  const phaseMap = {};
  (phases || []).forEach(p => phaseMap[p.name] = p);

  grid.innerHTML = ALL_PHASE_NAMES.map(name => {
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
    const errHtml = (p.errors||[]).length
      ? `<div class="phase-errors" style="display:block">` +
        p.errors.map(e => `⚠ Línea ${e.line}, Col ${e.column}: ${e.message}`).join('\n') +
        `</div>`
      : '';
    return `<div class="phase-row ${cls}">
      <span class="phase-icon">${PHASE_ICONS[name]||'•'}</span>
      <span class="phase-name">${name}</span>
      <span class="phase-status">${p.status}</span>
      <span class="phase-time">${p.time_ms} ms</span>
    </div>${errHtml}`;
  }).join('');
}

// ─── Métricas O3 ─────────────────────────────────────────────────────────────
function renderOptMetrics(data) {
  const el = document.getElementById('tab-opt-metrics');
  const mb = data.opt_metrics_before || {};
  const ma = data.opt_metrics_after  || {};
  const ts = data.opt_transformations || [];
  const pct = data.opt_reduction_pct || 0;

  if (!mb.instructions && mb.instructions !== 0) {
    el.innerHTML = '<span class="empty-state">— Compilar para ver métricas O3 —</span>';
    return;
  }

  const metricCards = [
    { lbl: 'Instrucciones antes', val: mb.instructions || 0 },
    { lbl: 'Instrucciones después', val: ma.instructions || 0 },
    { lbl: 'Reducción', val: pct + '%' },
    { lbl: 'Funciones', val: mb.functions || 0 },
    { lbl: 'Bloques básicos', val: mb.basic_blocks || 0 },
  ].map(m => `<div class="metric-card">
    <div class="metric-val">${m.val}</div>
    <div class="metric-lbl">${m.lbl}</div>
  </div>`).join('');

  const transformHtml = ts.length
    ? `<ul class="transform-list">${ts.map(t =>
        `<li><strong>${t.name}</strong><span>${t.description}</span></li>`
      ).join('')}</ul>`
    : '<span class="empty-state">Sin transformaciones detectadas.</span>';

  el.innerHTML = `
    <div style="padding:16px;">
      <div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:12px;">
        Métricas de Optimización O3
      </div>
      <div class="metrics-row">${metricCards}</div>
      <div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin:12px 0 8px;">
        Transformaciones Aplicadas
      </div>
      ${transformHtml}
    </div>`;
}

// ─── Modal Binarios ──────────────────────────────────────────────────────────
function openBinariesModal()  { document.getElementById('binaries-overlay').classList.add('open'); }
function closeBinariesModal() { document.getElementById('binaries-overlay').classList.remove('open'); }

function updateBinariesModal(data) {
  const lOut = document.getElementById('bin-linux-out');
  const wOut = document.getElementById('bin-windows-out');

  if (data.binary_linux) {
    lOut.textContent = data.binary_linux_output || data.binary_linux;
    lOut.className   = 'bin-output success';
  } else {
    lOut.textContent = data.binary_linux_output || '— No compilado para Linux —';
    lOut.className   = 'bin-output' + (data.binary_linux_output ? ' failure' : '');
  }

  if (data.binary_windows) {
    wOut.textContent = data.binary_windows_output || data.binary_windows;
    wOut.className   = 'bin-output success';
  } else {
    wOut.textContent = data.binary_windows_output || '— No compilado para Windows —';
    wOut.className   = 'bin-output' + (data.binary_windows_output ? ' failure' : '');
  }
}

// ─── Modal IR Manual ──────────────────────────────────────────────────────────
async function openIRManual() {
  document.getElementById('ir-manual-overlay').classList.add('open');
  if (availablePasses.length === 0) {
    await loadPasses();
  }
}
function closeIRManual() { document.getElementById('ir-manual-overlay').classList.remove('open'); }
function closeOnOverlay(evt, id) {
  if (evt.target === document.getElementById(id)) {
    document.getElementById(id).classList.remove('open');
  }
}

async function loadPasses() {
  try {
    const resp = await fetch('/ir_passes');
    const data = await resp.json();
    availablePasses = data.passes || [];
    renderPassesList();
  } catch(e) {
    document.getElementById('passes-list').innerHTML =
      '<span class="empty-state" style="font-size:0.7rem;color:var(--error)">Error cargando passes.</span>';
  }
}

function renderPassesList() {
  const container = document.getElementById('passes-list');
  if (!availablePasses.length) {
    container.innerHTML = '<span class="empty-state" style="font-size:0.7rem">Sin passes disponibles.</span>';
    return;
  }
  container.innerHTML = availablePasses.map(p => `
    <div class="pass-card ${selectedPasses.includes(p.id) ? 'selected' : ''}"
         id="pass-card-${p.id}"
         onclick="togglePass('${p.id}')">
      <div class="pass-card-label">${p.label}</div>
      <div class="pass-card-name">${p.name}</div>
      <div class="pass-card-desc">${p.description}</div>
      <div class="pass-card-cat">${p.category}</div>
    </div>
  `).join('');
}

function togglePass(id) {
  if (selectedPasses.includes(id)) {
    selectedPasses = selectedPasses.filter(p => p !== id);
  } else {
    selectedPasses.push(id);
  }
  document.querySelectorAll('.pass-card').forEach(el => el.classList.remove('selected'));
  selectedPasses.forEach(id => {
    const el = document.getElementById('pass-card-' + id);
    if (el) el.classList.add('selected');
  });
  document.getElementById('passes-status').textContent =
    selectedPasses.length ? `${selectedPasses.length} pass(es) seleccionado(s): ${selectedPasses.join(', ')}` : '';
}

function clearPassSelection() {
  selectedPasses = [];
  renderPassesList();
  document.getElementById('passes-status').textContent = '';
  document.getElementById('diff-view').innerHTML =
    '<span class="empty-state">Selecciona passes y haz clic en "Aplicar passes".</span>';
  const lliBox = document.getElementById('lli-manual-output');
  lliBox.style.display = 'none';
  lliBox.textContent = '';
}

async function applyManualPasses() {
  if (!selectedPasses.length) { alert('Selecciona al menos un pass.'); return; }

  const irSrc = (lastData && lastData.ir_code) ? lastData.ir_code : '';
  if (!irSrc) { alert('Compila primero para generar el IR.'); return; }

  const btn = document.getElementById('apply-passes-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Aplicando...';
  document.getElementById('diff-view').innerHTML =
    '<span class="empty-state">Aplicando optimizaciones...</span>';

  try {
    const resp = await fetch('/ir_manual_apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ir_code: irSrc, passes: selectedPasses })
    });
    const data = await resp.json();
    compiledIRManual = data.ir_after || '';
    renderDiff(data);
  } catch(e) {
    document.getElementById('diff-view').innerHTML =
      `<span style="color:var(--error)">Error: ${e.message}</span>`;
  } finally {
    btn.disabled = false;
    btn.textContent = '▶ Aplicar passes';
  }
}

function renderDiff(data) {
  const container = document.getElementById('diff-view');
  const diff = data.diff || [];

  if (!diff.length) {
    if (data.unchanged) {
      container.innerHTML = '<div class="diff-unchanged">✓ El IR no cambió con los passes seleccionados. El código ya es óptimo o los passes no aplican a este programa.</div>';
    } else {
      container.innerHTML = '<span class="empty-state">Sin cambios para mostrar.</span>';
    }
    return;
  }

  const html = diff.map(line => {
    const esc = line.line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    if (line.type === 'header')  return `<div class="diff-header">${esc}</div>`;
    if (line.type === 'hunk')    return `<div class="diff-hunk">${esc}</div>`;
    if (line.type === 'added')   return `<span class="diff-added">+ ${esc}</span>`;
    if (line.type === 'removed') return `<span class="diff-removed">- ${esc}</span>`;
    return `<span class="diff-same">  ${esc}</span>`;
  }).join('');

  const passInfo = (data.passes_applied || []).map(p =>
    `<li><strong>${p.name}</strong>: ${p.description}</li>`
  ).join('');

  container.innerHTML = `
    <div style="margin-bottom:12px;">
      <div style="font-size:0.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;">Passes aplicados</div>
      <ul class="transform-list">${passInfo}</ul>
    </div>
    <div style="font-size:0.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;">Diff IR antes → después</div>
    <div style="font-family:var(--mono);font-size:0.72rem;">${html}</div>`;

  // Mostrar salida lli si está disponible
  const lli = data.lli_result || {};
  const lliBox = document.getElementById('lli-manual-output');
  if (lli.output || lli.error) {
    lliBox.style.display = 'block';
    lliBox.textContent = '[lli] ' + (lli.output || lli.error || '');
    lliBox.className = 'lli-output-box' + (lli.success ? '' : ' error-out');
  }
}

async function runManualIR() {
  if (!compiledIRManual) { alert('Aplica passes primero.'); return; }
  const btn = document.getElementById('run-ir-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Ejecutando...';
  try {
    const resp = await fetch('/ir_manual_run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ir_code: compiledIRManual })
    });
    const data = await resp.json();
    const lliBox = document.getElementById('lli-manual-output');
    lliBox.style.display = 'block';
    lliBox.textContent = '[lli] ' + (data.output || data.error || '(sin salida)');
    lliBox.className = 'lli-output-box' + (data.success ? '' : ' error-out');
  } catch(e) {
    alert('Error ejecutando IR: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '🚀 Ejecutar IR resultante';
  }
}

async function exportManualIR() {
  if (!compiledIRManual) { alert('Aplica passes primero para obtener un IR resultante.'); return; }
  try {
    const resp = await fetch('/ir_manual_export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ir_code: compiledIRManual })
    });
    const data = await resp.json();
    if (data.success) {
      alert('IR exportado exitosamente: ' + data.path);
    } else {
      alert('Error exportando IR: ' + data.error);
    }
  } catch(e) {
    alert('Error: ' + e.message);
  }
}

// ─── Init ────────────────────────────────────────────────────────────────────
document.getElementById('btn-linux-toggle').classList.add('active-toggle');
document.getElementById('btn-windows-toggle').classList.add('active-toggle');

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') compile();
  if (e.key === 'Escape') {
    document.getElementById('ir-manual-overlay').classList.remove('open');
    document.getElementById('binaries-overlay').classList.remove('open');
  }
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
    data           = request.get_json()
    source         = data.get("code", "")
    comp_linux     = data.get("compile_linux", True)
    comp_windows   = data.get("compile_windows", True)

    result = run_pipeline(
        source,
        tac_file        = "output.tac",
        ll_file         = "output.ll",
        opt_ll_file     = "output.opt.ll",
        linux_bin       = "output_linux",
        windows_exe     = "output_windows.exe",
        compile_linux   = comp_linux,
        compile_windows = comp_windows,
    )
    return jsonify(result.to_dict())


@app.route("/ir_passes", methods=["GET"])
def get_ir_passes():
    if not IR_MANUAL_OK:
        return jsonify({"passes": []})
    return jsonify({"passes": get_available_passes()})


@app.route("/ir_manual_apply", methods=["POST"])
def ir_manual_apply():
    if not IR_MANUAL_OK:
        return jsonify({"success": False, "error": "ir_manual.py no disponible",
                        "diff": [], "ir_after": "", "passes_applied": []})
    data     = request.get_json()
    ir_code  = data.get("ir_code", "")
    passes   = data.get("passes", [])

    result = apply_manual_passes(ir_code, passes,
                                 run_with_lli=True,
                                 output_file="output.manual.ll")
    return jsonify(result.to_dict())


@app.route("/ir_manual_run", methods=["POST"])
def ir_manual_run():
    """Re-ejecuta un IR con lli para verificar el comportamiento tras optimización manual."""
    import subprocess, tempfile, os
    data    = request.get_json()
    ir_code = data.get("ir_code", "")
    if not ir_code:
        return jsonify({"success": False, "output": "", "error": "IR vacío"})

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ll",
                                     delete=False, encoding="utf-8") as f:
        f.write(ir_code)
        tmp = f.name
    try:
        proc = subprocess.run(["lli", tmp],
                              capture_output=True, text=True, timeout=10)
        return jsonify({
            "success": proc.returncode == 0,
            "output":  proc.stdout,
            "error":   proc.stderr,
        })
    except FileNotFoundError:
        return jsonify({"success": False, "output": "",
                        "error": "[lli no encontrado]"})
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "output": "",
                        "error": "[Timeout ejecutando IR]"})
    except Exception as e:
        return jsonify({"success": False, "output": "", "error": str(e)})
    finally:
        try: os.unlink(tmp)
        except Exception: pass


@app.route("/ir_manual_export", methods=["POST"])
def ir_manual_export():
    if not IR_MANUAL_OK:
        return jsonify({"success": False, "error": "ir_manual.py no disponible"})
    data    = request.get_json()
    ir_code = data.get("ir_code", "")
    path    = "output.manual.ll"
    ok      = export_manual_ir(ir_code, path)
    return jsonify({
        "success": ok,
        "path":    os.path.abspath(path) if ok else "",
        "error":   "" if ok else "Error al escribir el archivo",
    })


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║   Compilador UMG — Interfaz Web v4  (Pipeline v4)   ║")
    print("║   http://localhost:5000                              ║")
    print("║   Ctrl+C para detener  |  Ctrl+Enter para compilar  ║")
    print("╚══════════════════════════════════════════════════════╝")
    app.run(debug=True, port=5000, use_reloader=False)