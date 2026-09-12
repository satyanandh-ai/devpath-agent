<div align="center">

<img src="https://img.shields.io/badge/DevPath-AI%20Career%20Intelligence-E91E63?style=for-the-badge&logo=lightning&logoColor=white" />

# ⚡ DevPath — Agentic Career Intelligence Platform

### *Observe → Decide → Act → Evaluate → Adapt*

> **DevPath doesn't just analyze your resume. It analyzes you against the market — then acts on the gaps.**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Click%20Here-E91E63?style=for-the-badge)](https://devpath-agent-satya.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-satyanandh--ai-181717?style=for-the-badge&logo=github)](https://github.com/satyanandh-ai/devpath-agent)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Loop-7C3AED?style=for-the-badge)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLM%20Inference-F54E00?style=for-the-badge)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG%20Engine-5B4FE9?style=for-the-badge)](https://trychroma.com)

<br/>

*Agentic Arena 2026 · Ch. Satyanand · B.Tech AI/ML · ALIET Vijayawada*

</div>

---

## 🎯 What is DevPath?

Most career tools answer: *"Here are some generic tips."*

**DevPath answers: "Here is your exact skill gap, why it matters, the evidence behind it, and what to do next — based on your GitHub, resume, and real 2026 hiring data."**

DevPath is a full **Agentic Career Intelligence System** powered by LangGraph that:

| Capability | What it does |
|---|---|
| 🔬 **Observes** | Analyzes resume + GitHub as evidence, not claims |
| 🧠 **Decides** | Computes gaps using Skill Evidence Matrix |
| 🎯 **Acts** | Generates market-driven roadmap and job matches |
| ⚖️ **Evaluates** | Scores readiness with weighted evidence (not binary match) |
| 🔄 **Adapts** | Reruns the loop until the goal is achievable |

---

## 🖼️ Screenshots

### 🏠 Career Intelligence Dashboard
> DevPath Score · Portfolio · ATS · Credibility · Job Match — all in one glance

![Dashboard](https://devpath-agent-satya.streamlit.app/~/+/media/dashboard.png)

**What you see:**
- 🎯 **DevPath Score: 74/100** — weighted composite of all engines
- 📊 **Market Readiness: 86%** — 8/10 role skills matched
- 📈 **Skill Demand vs Profile** — hiring demand % per skill, green = you have it
- 🔴 **Priority Gaps** — AWS 54% · Kubernetes 42% (computed, not guessed)
- 💪 **Top Strengths** — Python 95% · Git 90% · LangChain 82%

---

### 📄 Resume Intelligence — Real ATS Engine
> 5-category computed scoring. No LLM guessing. Max 92.

**Score Breakdown:**
| Category | Score | What it checks |
|---|---|---|
| Contact Info | 20/20 | Email · Phone · LinkedIn · GitHub |
| Resume Sections | 20/20 | Summary · Education · Skills · Projects · Experience |
| Skills Coverage | 20/20 | Tiered: 0–3 skills=5pts · 16+=20pts |
| Keywords & Verbs | 10/20 | Action verbs + quantified achievements |
| Formatting & Length | 17/20 | Word count curve · bullets · dates |

✅ ATS Score: **90/100** with transparent breakdown per category

---

### 💬 Career Chat — Personalized Intelligence
> Every answer uses your actual scores, not generic advice.

**Example response to "Am I ready for AI Engineer?":**
```
Career Readiness Assessment
ATS Score: 90/100 — strong technical proficiency
Portfolio Score: 65/100 — needs more deployed projects

Skill Gaps with GitHub evidence missing:
• Docker · AWS · Kubernetes

Market Readiness: 86% — close to AI Engineer ready
Priority actions: Deploy 1 project on AWS this week
```

---

## 🏗️ Agentic Architecture

```
                    USER CAREER GOAL
                           ↓
                    ┌─────────────┐
                    │   PLANNER   │  ← LangGraph Supervisor
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
    RESUME AGENT    GITHUB AGENT      RAG ENGINE
    (ATS + Skills)  (Portfolio +   (4 Collections:
                    Evidence Map)   Jobs · Interview
                                   Learning · Career)
           └───────────────┼───────────────┘
                           ↓
                    SKILL EVIDENCE MATRIX
                    (Confirmed/Strong/Partial/Weak/Not Found)
                           ↓
                    GAP PRIORITY ENGINE
                    (role_weight × market × gap × evidence)
                           ↓
                    JOB MATCH AGENT
                    (weighted evidence scores, not binary)
                           ↓
                    ACTION PLANNER
                           ↓
                    EVALUATOR
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
        Goal achieved?             Not enough
              ↓                         ↓
            DONE                   REPLAN → ACT AGAIN
```

---

## ✨ Feature Overview

### 🔬 Skill Evidence Engine
The central intelligence layer every module reads from:

```python
# Per-skill evidence — 5 levels, fully traceable
skill_matrix["docker"] = {
    "evidence_level":  "Partial",        # Confirmed/Strong/Partial/Weak/Not Found
    "evidence_reason": "Resume mention only — no GitHub file evidence found",
    "evidence_trace":  [{"source":"Resume","detail":"Mentioned in skills section"}],
    "readiness":       45,               # Computed from evidence (separate from market)
    "market_demand":   65,               # % of job postings requiring this skill
    "github_repos":    [],               # Traceable to actual repos
}
```

**5 Evidence Levels (standardized across all modules):**
| Level | Meaning |
|---|---|
| ✅ Confirmed | Resume mention + GitHub file evidence (Dockerfile, requirements.txt) |
| ✅ Strong | Resume mention + GitHub metadata/README |
| ⚠️ Partial | Resume mention only — no GitHub evidence |
| 🟠 Weak | GitHub evidence only — not on resume |
| ❌ Not Found | No evidence detected anywhere |

---

### 📊 Job Market Intelligence — Hybrid C+A
> Computed database + LLM explanations. Not fabricated scores.

| Role | Demand | Salary India | Salary US |
|---|---|---|---|
| GenAI Engineer | Extremely High ↑ 120% | ₹12L – ₹35L | $110K – $200K |
| MLOps Engineer | Very High ↑ 58% | ₹10L – ₹28L | $100K – $170K |
| AI Engineer | Very High ↑ 42% | ₹8L – ₹24L | $90K – $160K |
| ML Engineer | High ↑ 31% | ₹7L – ₹20L | $85K – $150K |
| Data Scientist | High ↑ 18% | ₹6L – ₹18L | $80K – $140K |

---

### 🔬 Evidence Simulator
> "What happens to my Job Match if I strengthen Docker?"

```
SIMULATION: Docker · Partial → Strong

Job Match:       55% → 63%   (+8%)
Evidence Score:  45  → 75    (+30pts)
Overall Evidence: 48 → 52    (+4pts)

* All numbers deterministic. No AI estimation.
```

---

### 🌉 Reality Check — Resume ↔ GitHub Credibility
> The feature most career tools don't have.

```
Skill          Resume    GitHub           Evidence Level
──────────────────────────────────────────────────────
Python         ✅        ✅ 5 repos        Confirmed
FastAPI        ✅        ✅ requirements   Confirmed
LangChain      ✅        ✅ devpath-agent  Confirmed
Docker         ✅        ❌ Not found      Partial
AWS            ✅        ❌ Not found      Partial

Credibility Score: 67%
Hidden Strengths: ChromaDB · Groq (on GitHub, not on resume)
```

---

### 🤖 Agentic Mode — LangGraph Loop
```
Goal: "Get AI Engineer internship in 3 months"
    ↓
[Resume Agent]    → ATS: 90, Skills: Python, LangChain, RAG...
[GitHub Agent]    → Portfolio: 65, Deployed: 1, Evidence gaps: Docker
[Gap Analyzer]    → Critical: AWS, Docker | High: Kubernetes
[Job Agent]       → Match: 80% | Missing: AWS, Kubernetes
[Action Planner]  → Week 1: Dockerize devpath-agent
                    Week 2: Deploy FastAPI to AWS EC2
                    Week 3: Add GitHub Actions CI/CD
[Evaluator]       → Readiness: 72% | Recommendation: replan
    ↓
[REPLAN] → Focus: Docker → evidence target: Strong
```

---

### 📚 RAG Knowledge Base
> 4 ChromaDB collections. Retrieved evidence shown before every answer.

| Collection | Records | Used By |
|---|---|---|
| 💼 Job Intelligence | 20 job profiles | Career Chat · Market Intel |
| 🎤 Interview Questions | 25 role-specific Qs | Interview Prep |
| 📚 Learning Resources | 18 curated resources | Roadmap · Career Chat |
| 🧠 Career Knowledge | 15 KB articles | Recruiter View · Chat |

**Live retrieval panel shown to user:**
```
🔍 RAG Retrieved: ✓ 3 jobs · ✓ 2 career articles · ✓ 3 resources
   Matching: OpenAI AI Engineer · Anthropic AI Engineer · Amazon ML Engineer
   🤖 Building personalized recommendation from retrieved evidence...
```

---

## 🚀 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Groq (openai/gpt-oss-20b) | Sub-second inference |
| **Agent Orchestration** | LangGraph + LangChain | Observe→Decide→Act→Evaluate→Adapt |
| **RAG** | ChromaDB (in-memory) | 4-collection knowledge retrieval |
| **Embeddings** | Custom hash embedding | Zero-dependency, offline-capable |
| **ATS Engine** | 5-rule computed scoring | No LLM — deterministic |
| **Skill Engine** | Canonical taxonomy | Single source of truth |
| **PDF Processing** | pypdf | Resume extraction |
| **Charts** | Plotly | Radar · bar · donut charts |
| **PDF Reports** | ReportLab | Career report export |
| **Frontend** | Streamlit + Custom CSS | Pink glass UI |
| **Deployment** | Streamlit Cloud | Live, zero-config |

---

## 📦 Installation

```bash
# 1. Clone
git clone https://github.com/satyanandh-ai/devpath-agent.git
cd devpath-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
echo "GROQ_API_KEY=your_key_here" > .env
echo "GITHUB_TOKEN=your_token_here" >> .env

# 4. Run
streamlit run app.py
```

### Requirements
```
streamlit · langchain · langchain-core · langchain-groq
langgraph · pypdf · requests · python-dotenv
plotly · reportlab · chromadb · numpy · fastembed
```

### Streamlit Cloud Secrets
```toml
GROQ_API_KEY = "gsk_your_key_here"
GITHUB_TOKEN = "github_pat_your_token_here"
```

---

## 🎬 Demo Flow (3 Minutes)

| Step | Action | What judges see |
|---|---|---|
| 1 | Upload resume | ATS Score: 90/100 with 5-category breakdown |
| 2 | GitHub Analysis | Portfolio: 65/100 · Evidence map per skill |
| 3 | Reality Check | Credibility: 67% · Confirmed vs Partial skills |
| 4 | Market Intelligence | 86% market ready · AWS + K8s gaps |
| 5 | Career Chat → "Am I ready?" | RAG retrieved evidence panel + personalized answer |
| 6 | Agentic Mode | Full loop: Goal → Analyze → Gap → Plan → Evaluate → Adapt |
| 7 | Job Match + Evidence Simulator | "If I learn Docker: Job Match 55% → 63%" |

---

## 🏆 What Makes DevPath Different

| Feature | Other Tools | DevPath |
|---|---|---|
| Resume scoring | LLM guess ("7/10") | 5-category deterministic engine |
| Skill verification | None | Resume ↔ GitHub Evidence Matrix |
| Gap priority | Generic advice | Computed: role × market × evidence |
| Market data | Generic tips | 8-role database with demand % |
| Job match | Binary present/absent | Weighted evidence scores (0.0–1.0) |
| Career chat | Generic ChatGPT | Uses your actual scores + RAG evidence |
| Agent loop | Single LLM call | LangGraph observe→decide→act→evaluate→adapt |
| Evidence simulator | None | "What if I learn X?" — deterministic projection |

---

## 📁 Project Structure

```
devpath-agent/
├── app.py              # Main application — all engines + 12 pages (3258 lines)
│   ├── Skill Evidence Engine    # Canonical taxonomy, 5 evidence levels
│   ├── GitHub Evidence Engine   # Deep repo inspection (README, requirements, Dockerfile)
│   ├── ATS Engine               # 5-category rule-based, max 92
│   ├── Skill Matrix             # Central source of truth
│   ├── Gap Priority Engine      # Weighted formula
│   ├── Evidence Simulator       # Deterministic "what if" projections
│   ├── RAG Engine               # ChromaDB 4 collections (embedded)
│   ├── LangGraph Agent Loop     # Agentic Mode
│   └── 12 Pages                 # Full UI
├── rag_engine.py       # Standalone RAG engine with fastembed
├── requirements.txt    # 13 dependencies
└── README.md
```

---

## 👨‍💻 Built By

**Ch. Satyanand**
B.Tech Artificial Intelligence & Machine Learning
ALIET — Vijayawada, Andhra Pradesh

🔗 [GitHub](https://github.com/satyanandh-ai) · 🚀 [Live Demo](https://devpath-agent-satya.streamlit.app)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**⚡ DevPath · Agentic Arena 2026**

*Built with LangChain · LangGraph · Groq · ChromaDB · Streamlit*

[![Deploy on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://devpath-agent-satya.streamlit.app)

</div>