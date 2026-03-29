# 🤖 AI Test Automation Agent

An intelligent, fully-autonomous browser testing tool powered by **LangGraph**, **Google Gemini**, and **Playwright**, wrapped in a modern **Flask/Vanilla CSS** web application.

## 🚀 Features

- **Natural Language Parsing**: Just type what you want the browser to do (e.g., "Go to YouTube and search for lofi music") and the AI will convert it into actionable JSON.
- **Adaptive DOM Mapping**: The Playwright executor engine dynamically falls back to role-based or text-based element selections if the primary CSS selectors aren't found or change suddenly.
- **Rich Reporting Module**: Returns highly-structured JSON reports that measure execution time step-by-step and safely capture element failure logs.
- **Premium Frontend UI**: A dark-mode, glassmorphic UI displaying live summary stats, an animated timeline of test executions, and raw generated outputs.
- **LangGraph Workflow**: A strict, reliable loop: `Input` → `Parser` → `Generator` → `Executor` → `Reporter`.

---

## 🛠️ Architecture Overview

The system runs entirely via `Flask` (`app.py`), delegating automated logic to a dedicated LangGraph workflow state machine.

- **`parser/instruction_parser.py`**: Extracts the structured actions from raw English via Gemini (with spaCy fallback).
- **`generator/code_generator.py`**: Converts structured JSON actions into verifiable Playwright scripts (mainly used for developer debugging).
- **`executor/playwright_runner.py`**: A robust runtime for the `.click()`, `.fill()`, and `.goto()` sequences. Contains the adaptive fallback logics (`get_by_role`, `get_by_text`).
- **`reporting/report_builder.py`**: Evaluates individual step times and exceptions into a final JSON payload containing pass/fail metrics.
- **`workflow/langgraph_flow.py`**: Connects the parser -> generator -> executor -> reporter pipeline.

---

## ⚙️ Setup Instructions

### Prerequisites
Make sure you have **Python 3.10+**.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Environment Setup
Create a `.env` file in the root directory and add your Google Gemini API key:
```ini
GEMINI_API_KEY=AIzaSy...
```

### 4. Run the Application
```bash
python app.py
```
*The app will start on HTTP Port 5000: `http://localhost:5000`*

---

## ✔️ Example Queries

You can execute queries against the built-in demo login page, or external sites.

**Local Form Testing (Uses `localhost:5000/sample`)**:
> `"Open localhost:5000/sample, type admin into username, type password123 into password, click login"`

**External Deep-Navigation**:
> `"Go to youtube.com, search for relaxing music, press enter, and click the first thumbnail"`

*(Note: The automation engine intelligently auto-switches to "Headed mode" for media URLs like YouTube to avoid automatic bot blocks, and remains completely Headless for other automation loops).*