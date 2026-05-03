from flask import Flask, render_template_string, request
from agent import get_steps
from generated import generate_code
from report_generator import generate_report

import traceback
import json

app = Flask(__name__)


def execute_and_scrape(code):
    namespace = {}
    try:
        exec(compile(code, "<generated>", "exec"), namespace)
        run_fn = namespace.get("run_search")
        if run_fn is None:
            return [], "❌ run_search() not found in generated code."
        results = run_fn()
        return results, f"✅ Execution successful – {len(results)} result(s) found."
    except Exception:
        tb = traceback.format_exc()
        return [], f"❌ Execution failed:\n{tb}"


def _extract_query_and_url(steps):
    query = ""
    url = "https://www.google.com"
    for s in steps:
        if s.get("action") == "open_url":
            url = s.get("url", url)
        if s.get("action") == "search":
            query = s.get("text", "")
    return query, url


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Browser Automation Agent</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:      #0d0f14;
    --surface: #13161e;
    --border:  #1e2330;
    --accent:  #00e5ff;
    --text:    #d4daf0;
    --muted:   #5a6080;
    --success: #00e5a0;
    --error:   #ff4f7b;
    --radius:  10px;
    --mono:    'Space Mono', monospace;
    --sans:    'DM Sans', sans-serif;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    padding: 2rem 1rem 4rem;
  }
  .container { max-width: 980px; margin: 0 auto; }
  header { text-align: center; margin-bottom: 2.5rem; }
  header h1 {
    font-family: var(--mono);
    font-size: clamp(1.4rem, 4vw, 2.2rem);
    letter-spacing: .06em;
    color: var(--accent);
    text-shadow: 0 0 28px rgba(0,229,255,.35);
  }
  header p { color: var(--muted); font-size: .9rem; margin-top: .4rem; }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  .card-title {
    font-family: var(--mono);
    font-size: .7rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: .5rem;
  }
  .card-title::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--accent);
  }
  .input-row { display: flex; gap: .75rem; flex-wrap: wrap; }
  .input-row input[type="text"] {
    flex: 1; min-width: 200px;
    background: #0a0c12;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: var(--sans); font-size: 1rem;
    padding: .75rem 1rem; outline: none;
    transition: border-color .2s, box-shadow .2s;
  }
  .input-row input[type="text"]:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0,229,255,.12);
  }
  .input-row input::placeholder { color: var(--muted); }
  button[type="submit"] {
    background: var(--accent); color: #000;
    border: none; border-radius: var(--radius);
    padding: .75rem 1.6rem;
    font-family: var(--mono); font-size: .85rem; font-weight: 700;
    letter-spacing: .05em; cursor: pointer;
    transition: opacity .2s, box-shadow .2s; white-space: nowrap;
  }
  button[type="submit"]:hover { opacity:.88; box-shadow: 0 0 18px rgba(0,229,255,.4); }
  .status {
    font-family: var(--mono); font-size: .82rem;
    padding: .75rem 1rem; border-radius: var(--radius);
    white-space: pre-wrap; word-break: break-word;
  }
  .status.ok  { background: rgba(0,229,160,.08); border:1px solid rgba(0,229,160,.3); color:var(--success); }
  .status.err { background: rgba(255,79,123,.08); border:1px solid rgba(255,79,123,.3); color:var(--error); }
  pre {
    background: #080a10; border:1px solid var(--border);
    border-radius: var(--radius); padding: 1.1rem;
    overflow-x: auto; font-family: var(--mono);
    font-size: .76rem; line-height: 1.65;
    color: #a8b4d8; max-height: 340px;
  }
  details > summary {
    cursor: pointer; font-family: var(--mono); font-size:.75rem;
    color: var(--muted); list-style: none;
    padding: .4rem 0; user-select: none;
  }
  details > summary:hover, details[open] > summary { color: var(--accent); }
  .steps-grid { display: flex; flex-wrap: wrap; gap: .75rem; }
  .step-badge {
    background: #0a0c12; border:1px solid var(--border);
    border-radius: 8px; padding: .6rem 1rem;
    font-family: var(--mono); font-size: .75rem; line-height: 1.6;
  }
  .step-badge .ak { color: var(--accent); font-weight: 700; }
  .step-badge .av { color: #f1fa8c; }
  .pipeline {
    display: flex; align-items: center; gap: .4rem;
    flex-wrap: wrap; font-family: var(--mono); font-size: .7rem;
  }
  .p-step {
    background: rgba(0,229,255,.08);
    border: 1px solid rgba(0,229,255,.2);
    border-radius: 20px; padding: .3rem .8rem; color: var(--accent);
  }
  .p-arrow { color: var(--muted); }
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>⚡ Browser Automation Agent</h1>
    <p>Natural language → JSON steps → Playwright code → Live browser → Results report</p>
  </header>

  <div class="card">
    <div class="card-title">Instruction</div>
    <form method="POST">
      <div class="input-row">
        <input type="text" name="user_input"
          placeholder='e.g. "open google.com and search nptel courses"'
          value="{{ user_input or '' }}" autocomplete="off" autofocus>
        <button type="submit">▶ RUN</button>
      </div>
    </form>
  </div>

  {% if steps is not none %}

  <div class="card">
    <div class="card-title">Pipeline</div>
    <div class="pipeline">
      <div class="p-step">① agent.py → JSON steps</div>
      <div class="p-arrow">→</div>
      <div class="p-step">② generated.py → Playwright code</div>
      <div class="p-arrow">→</div>
      <div class="p-step">③ exec() → browser runs</div>
      <div class="p-arrow">→</div>
      <div class="p-step">④ report_generator.py → report</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">① Parsed Steps — agent.py output (JSON)</div>
    <div class="steps-grid">
      {% for s in steps %}
      <div class="step-badge">
        {% for k, v in s.items() %}
        <div><span class="ak">{{ k }}:</span> <span class="av">{{ v }}</span></div>
        {% endfor %}
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="card">
    <div class="card-title">② Generated Playwright Code — generated.py output</div>
    <details>
      <summary>Click to expand / collapse</summary>
      <pre>{{ generated_code }}</pre>
    </details>
  </div>

  <div class="card">
    <div class="card-title">③ Execution Status</div>
    <div class="status {{ 'ok' if status and status.startswith('✅') else 'err' }}">{{ status }}</div>
  </div>

  <div class="card">
    <div class="card-title">④ Report — report_generator.py output</div>
    {% if report_html %}
      {{ report_html | safe }}
    {% else %}
      <div style="color:var(--muted);text-align:center;padding:1.5rem;">
        No report generated — check execution status above.
      </div>
    {% endif %}
  </div>

  {% if report_json %}
  <div class="card">
    <div class="card-title">Report JSON (raw)</div>
    <details>
      <summary>Click to expand / collapse</summary>
      <pre>{{ report_json }}</pre>
    </details>
  </div>
  {% endif %}

  {% endif %}

</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    user_input     = None
    steps          = None
    generated_code = None
    status         = None
    report_html    = None
    report_json    = None

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()

        if user_input:
            steps          = get_steps(user_input)
            generated_code = generate_code(steps)
            results, status = execute_and_scrape(generated_code)
            query, url     = _extract_query_and_url(steps)
            report         = generate_report(
                query=query,
                url=url,
                results=results,
                status=status,
                instruction=user_input,
            )
            report_html = report["html"]
            report_json = report["json"]

    return render_template_string(
        TEMPLATE,
        user_input=user_input,
        steps=steps,
        generated_code=generated_code,
        status=status,
        report_html=report_html,
        report_json=report_json,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)