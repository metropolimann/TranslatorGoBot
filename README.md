# PDF → Translate → Archive Bot

> Split large PDFs into page packs, translate any pack into another language via
> Google Translate (driven by a real Brave browser), archive the translated PDF,
> and keep a full audit trail in **SQLite** (local) and **PostgreSQL** (remote).

<p align="center">
  <em>Desktop application · Python 3.11+ · PySide6 · PyMuPDF · Playwright · SQLAlchemy</em>
</p>

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [CLI](#cli)
  - [GUI](#gui)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Task History Schema](#task-history-schema)
- [Development](#development)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Features

- **PDF splitting** — split any page range `[n1, n2]` of a PDF into fixed-size
  packs of `m` pages, named `<identifier>_<basename>_p<start>-<end>.pdf`.
- **Browser-driven translation** — drives `translate.google.com` inside Brave
  (or Chromium / Chrome) with a persistent profile so the session looks human.
- **Pluggable translator backends** — fall back to `deep-translator` (no browser)
  or the official Google Cloud Translation API without touching the pipeline.
- **Translation as PDF** — the translated text is rendered to a real `.pdf`
  (Unicode-safe fonts bundled) under `RawTranslatedMaterial/`.
- **Dual database history** — every task is written to **SQLite** locally and
  mirrored to **PostgreSQL** when the network is available (offline queue +
  background sync, no duplicates).
- **Native desktop GUI** — Qt6 interface with a responsive progress bar; long
  jobs run in worker threads, never blocking the UI.
- **CLI-first** — every workflow is available from the terminal before the GUI
  ever loads, which makes automation and testing trivial.

---

## Screenshots

> _Screenshots will live in `docs/screenshots/` once Phase 6 lands._

| Tab        | Preview                                          |
| ---------- | ------------------------------------------------ |
| Split      | `docs/screenshots/split-tab.png` (coming soon)   |
| Translate  | `docs/screenshots/translate-tab.png` (coming soon) |
| History    | `docs/screenshots/history-tab.png` (coming soon) |
| Settings   | `docs/screenshots/settings-tab.png` (coming soon) |

---

## Requirements

| Component     | Version      | Notes                                             |
| ------------- | ------------ | ------------------------------------------------- |
| Python        | 3.11+        | 3.12 also supported                               |
| Brave Browser | latest       | Required for the browser translator backend       |
| SQLite        | 3.35+        | Bundled with Python                               |
| PostgreSQL    | 14+          | Optional — only needed for the remote mirror      |
| OS            | Win / macOS / Linux | GUI tested on all three                    |

Python dependencies are pinned in `pyproject.toml`. The three heavy ones are
`PyMuPDF`, `playwright`, and `PySide6`.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/pdf-translate-bot.git
cd pdf-translate-bot