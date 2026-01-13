# DeepStrike AI

<p align="center">
  <img src="assets/logo.png" width="160" />
</p>

<p align="center">
  <strong>Autonomous AI‑Assisted Pentest & Dark‑Web Intelligence Framework</strong><br/>
  Multi‑AI • TOR‑First • Optional Heavy Modules • Pro‑Ready CLI
</p>

<p align="center">
  <a href="https://pypi.org/project/deepstrike-ai/"><img alt="PyPI" src="https://img.shields.io/pypi/v/deepstrike-ai"></a>
  <a href="https://pypi.org/project/deepstrike-ai/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/deepstrike-ai"></a>
  <img alt="License" src="https://img.shields.io/github/license/deepstrike-ai/deepstrike">
  <img alt="Status" src="https://img.shields.io/badge/status-production--ready-brightgreen">
</p>

---

## 🚀 Overview

**DeepStrike AI** is a modular, TOR‑first, AI‑assisted security framework designed for **professional pentesters, red‑team operators, and security researchers**.

It combines:

* Multi‑AI attack planning
* Autonomous reconnaissance workflows
* Dark‑web intelligence modules
* Optional crypto & scraper tooling

> ⚠️ **Ethical & Legal Notice**
> DeepStrike AI is intended **only** for authorized security testing, education, and research. You must have **explicit permission** before scanning or targeting any system.

---

## ✨ Key Features

### 🧠 Multi‑AI Attack Planning

* Pluggable AI providers (Gemini, OpenAI, extensible)
* AI‑generated pentest phases & tooling recommendations
* Provider auto‑selection with graceful fallback

### 🕸️ TOR‑First Architecture

* Automatic TOR bootstrap
* IP rotation & circuit renewal
* Dark‑web compatible networking

### 🔍 Dark‑Web Intelligence (Optional)

* Onion scraping (text, images, files)
* Credit‑card & data leak pattern detection
* TOR‑safe async scraping

### 🪙 Crypto Recovery Research Module (Optional)

* BIP‑39 / WIF / key pattern detection
* Filesystem & AI‑assisted discovery
* Balance checking via TOR

### 🖥️ Rich CLI Interface

* Full interactive menu
* Async‑first design
* Clean Rich‑powered UI

---

## 📦 Installation

### Basic (Core Framework Only)

```bash
pip install deepstrike-ai
```

This installs:

* CLI
* TOR control
* AI planner core

### With Dark‑Web Scraper

```bash
pip install deepstrike-ai[scraper]
```

### With Crypto Research Module

```bash
pip install deepstrike-ai[crypto]
```

### Full Installation (All Modules)

```bash
pip install deepstrike-ai[all]
```

> 💡 Optional dependencies are **lazy‑loaded** — missing packages will never crash the CLI unless you enter the module.

---

## 🧪 Supported Python Versions

* Python **3.8+**
* Tested on Linux (Kali, Parrot, Ubuntu)
* Termux supported (with reduced feature set)

---

## 🖥️ Usage

Launch the CLI:

```bash
deepstrike
```

### Main Menu

* Autonomous Pentest
* Dark‑Web Crypto Hunt
* Dark‑Web Scraper
* AI Attack Planner
* TOR Status

Everything runs **async**, TOR‑safe, and sandboxed.

---

## 🧩 Architecture

```
deepstrike/
├── ai/            # Multi‑AI providers & agents
├── ui/            # Rich CLI menus
├── tor/           # TOR bootstrap & control
├── modules/       # Optional heavy modules
├── config.py
├── cli.py
└── __main__.py
```

Design goals:

* No hard dependency failures
* Optional heavy modules
* Clean import boundaries

---

## 🛡️ Security Philosophy

* No background scanning
* No auto‑exploitation
* No data exfiltration
* User‑controlled execution

DeepStrike **plans**, **assists**, and **orchestrates** — *you* remain in control.

---

## 🧰 Development

Clone and install editable:

```bash
git clone https://github.com/deepstrike-ai/deepstrike.git
cd deepstrike
pip install -e .
```

Run formatter:

```bash
black .
```

---

## 📞 Support

* 📧 Email: **[support@deepstrike.ai](mailto:hackura@keemail.me)**
* 🐞 Issues: GitHub Issues
* 📖 Docs: Coming soon

Commercial support & enterprise licensing available.

---

## 🗺️ Roadmap

* [x] Modular AI providers
* [x] TOR‑first networking
* [x] Optional heavy dependencies
* [ ] Plugin system
* [ ] Web dashboard
* [ ] Report export (PDF/JSON)
* [ ] Blue‑team defensive mode

---

## 📜 License

MIT License © DeepStrike Team

---

> Built by security professionals, for security professionals.

