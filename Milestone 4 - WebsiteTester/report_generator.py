
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional
from urllib import response

from dotenv import load_dotenv
load_dotenv()


USE_AI_SUMMARY = True   

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    _GEMINI_AVAILABLE = True
except Exception:
    _GEMINI_AVAILABLE = False



def _ai_summary(query: str, results: list[dict]) -> str:
    """Ask Gemini for a concise summary of what the results are about."""
    if not (USE_AI_SUMMARY and _GEMINI_AVAILABLE) or not results:
        return ""

    snippets = "\n".join(
        f"{r['rank']}. {r['title']}: {r.get('snippet', '')[:200]}"
        for r in results[:6]
    )
    prompt = f"""
You are a helpful research assistant.
The user searched for: "{query}"

Here are the top search results:
{snippets}

Write a concise 2-3 sentence summary of what these results are about and
what the user is likely to find. Be factual, no fluff.
"""
    try:
        response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt)
        return response.text.strip()
        return response.text.strip()
    except Exception as e:
        return f"(AI summary unavailable: {e})"



def build_report(
    query:      str,
    url:        str,
    results:    list[dict],
    status:     str = "",
    instruction: str = "",
) -> dict:
    """
    Build and return a structured report dict.

    Fields:
        query        – original search query
        source_url   – website that was searched
        instruction  – original user instruction
        timestamp    – ISO-8601 datetime string
        status       – execution status message
        total        – number of results
        results      – list of result dicts
        ai_summary   – Gemini-generated summary (or "")
    """
    return {
        "query":       query,
        "source_url":  url,
        "instruction": instruction,
        "timestamp":   datetime.now().isoformat(timespec="seconds"),
        "status":      status,
        "total":       len(results),
        "results":     results,
        "ai_summary":  _ai_summary(query, results),
    }



def to_json(report: dict) -> str:
    """Return the report as a pretty-printed JSON string."""
    return json.dumps(report, indent=2, ensure_ascii=False)



def to_text(report: dict) -> str:
    """Return the report as a plain-text string (good for logging/printing)."""
    lines = [
        "=" * 62,
        f"  SEARCH REPORT",
        "=" * 62,
        f"  Query      : {report['query']}",
        f"  Source     : {report['source_url']}",
        f"  Timestamp  : {report['timestamp']}",
        f"  Results    : {report['total']}",
        f"  Status     : {report['status']}",
    ]
    if report.get("ai_summary"):
        lines += [
            "",
            "  AI SUMMARY",
            "  " + "-" * 58,
            *[f"  {line}" for line in report["ai_summary"].splitlines()],
        ]
    lines += ["", "  TOP RESULTS", "  " + "-" * 58]
    for r in report["results"]:
        lines += [
            f"  [{r['rank']}] {r['title']}",
            f"      {r.get('url', '')}",
            f"      {r.get('snippet', '')[:200]}",
            "",
        ]
    lines.append("=" * 62)
    return "\n".join(lines)




def to_html(report: dict) -> str:
    """Return a self-contained HTML report card string."""

    def esc(s: str) -> str:
        return (s.replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))

    
    summary_html = ""
    if report.get("ai_summary"):
        summary_html = f"""
        <div class="report-summary">
          <div class="report-label">🤖 AI Summary</div>
          <p>{esc(report['ai_summary'])}</p>
        </div>"""

    
    rows = ""
    for r in report["results"]:
        title   = esc(r.get("title",   ""))
        url     = esc(r.get("url",     ""))
        snippet = esc(r.get("snippet", ""))
        rank    = r.get("rank", "")
        rows += f"""
        <tr>
          <td class="rpt-rank">{rank}</td>
          <td class="rpt-title">
            {'<a href="' + url + '" target="_blank" rel="noopener">' + title + '</a>' if url else title}
            {'<div class="rpt-url">' + url[:90] + ('…' if len(url) > 90 else '') + '</div>' if url else ''}
          </td>
          <td class="rpt-snippet">{snippet[:280] + ('…' if len(snippet) > 280 else '')}</td>
        </tr>"""

    
    return f"""
<div class="report-card">
  <style>
    .report-card {{
      background: #13161e;
      border: 1px solid #1e2330;
      border-radius: 10px;
      padding: 1.5rem;
      font-family: 'DM Sans', sans-serif;
      color: #d4daf0;
    }}
    .report-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: .5rem 1.5rem;
      margin-bottom: 1.2rem;
    }}
    .report-meta-item {{
      font-size: .78rem;
      color: #5a6080;
    }}
    .report-meta-item span {{
      color: #00e5ff;
      font-weight: 600;
    }}
    .report-label {{
      font-size: .7rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: #00e5ff;
      margin-bottom: .5rem;
      font-family: 'Space Mono', monospace;
    }}
    .report-summary {{
      background: rgba(0,229,255,.05);
      border: 1px solid rgba(0,229,255,.15);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1.2rem;
      font-size: .88rem;
      line-height: 1.65;
      color: #a8b4d8;
    }}
    .report-summary p {{ margin: 0; }}
    .rpt-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .84rem;
    }}
    .rpt-table th {{
      font-family: 'Space Mono', monospace;
      font-size: .65rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: #5a6080;
      padding: .5rem .8rem;
      border-bottom: 1px solid #1e2330;
      text-align: left;
    }}
    .rpt-table td {{
      padding: .7rem .8rem;
      border-bottom: 1px solid #1e2330;
      vertical-align: top;
    }}
    .rpt-table tr:last-child td {{ border-bottom: none; }}
    .rpt-table tr:hover td {{ background: rgba(255,255,255,.02); }}
    .rpt-rank  {{ color: #5a6080; font-family: monospace; width: 2rem; text-align: center; }}
    .rpt-title a {{ color: #00e5ff; text-decoration: none; font-weight: 600; display: block; }}
    .rpt-title a:hover {{ text-decoration: underline; }}
    .rpt-url   {{ color: #00e5a0; font-size: .7rem; margin-top: .2rem; word-break: break-all; }}
    .rpt-snippet {{ color: #8892b0; font-size: .8rem; line-height: 1.55; }}
  </style>

  <div class="report-meta">
    <div class="report-meta-item">Query: <span>{esc(report['query'])}</span></div>
    <div class="report-meta-item">Source: <span>{esc(report['source_url'])}</span></div>
    <div class="report-meta-item">Results: <span>{report['total']}</span></div>
    <div class="report-meta-item">Time: <span>{esc(report['timestamp'])}</span></div>
  </div>

  {summary_html}

  <table class="rpt-table">
    <thead>
      <tr><th>#</th><th>Title &amp; URL</th><th>Snippet</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""




def generate_report(
    query:       str,
    url:         str,
    results:     list[dict],
    status:      str = "",
    instruction: str = "",
) -> dict:
    """
    Build the report and return a dict with keys:
        data  – structured dict
        json  – JSON string
        text  – plain-text string
        html  – HTML card string
    """
    report = build_report(
        query=query,
        url=url,
        results=results,
        status=status,
        instruction=instruction,
    )
    return {
        "data": report,
        "json": to_json(report),
        "text": to_text(report),
        "html": to_html(report),
    }




if __name__ == "__main__":
   
    dummy_results = [
        {
            "rank": 1,
            "title": "NPTEL Online Courses | IIT Courses",
            "url": "https://nptel.ac.in/courses",
            "snippet": "NPTEL provides online courses from IITs and IISc, covering engineering, science and humanities.",
        },
        {
            "rank": 2,
            "title": "NPTEL Swayam Portal",
            "url": "https://swayam.gov.in/explorer?searchText=nptel",
            "snippet": "Explore thousands of NPTEL courses on the Swayam platform with certificates.",
        },
        {
            "rank": 3,
            "title": "NPTEL YouTube Channel",
            "url": "https://www.youtube.com/@iit",
            "snippet": "Free video lectures from IIT professors covering all engineering branches.",
        },
    ]

    report = generate_report(
        query="nptel courses",
        url="https://www.google.com",
        results=dummy_results,
        status="✅ Test run – 3 dummy results",
        instruction="open google.com and search nptel courses",
    )

    print(report["text"])
    print("\n── JSON preview (first 400 chars) ──")
    print(report["json"][:400])
