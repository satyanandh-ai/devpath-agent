<div align="center">

# ⚡ DevPath
## AI Career Intelligence Platform

**Observe → Decide → Act → Evaluate → Adapt**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-devpath--agent--satya.streamlit.app-E91E63?style=for-the-badge)](https://devpath-agent-satya.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-satyanandh--ai-181717?style=for-the-badge&logo=github)](https://github.com/satyanandh-ai/devpath-agent)

*Agentic Arena 2026 · Ch. Satyanand · B.Tech AI/ML · ALIET Vijayawada*

---

> **"DevPath doesn't just analyze your resume.**
> **It analyzes you against the market — then acts on the gaps."**

</div>

---

## 🎯 The Problem DevPath Solves

Every career tool gives you generic advice.

DevPath gives you **evidence-backed intelligence**:

- ❌ Resume says Docker → ✅ GitHub has zero Docker evidence → **Credibility: Partial**
- ❌ Market needs AWS at 54% → ✅ You don't have it → **Priority Gap: High**
- ❌ Job Match says 80% → ✅ Weighted by evidence depth → **Actual Match: 63%**

---

## 🖼️ DevPath in Action

### 🏠 Career Intelligence Dashboard

![DevPath Dashboard showing Career Readiness 74, Portfolio 65, ATS 90, Credibility 67, Job Match 80 with Market Readiness 86% donut chart and skill demand comparison](https://github.com/satyanandh-ai/devpath-agent/assets/dashboard-preview.png)

> **Real scores from a real resume — no inflation:**
> - 🎯 DevPath Score: **74/100** · Industry Ready
> - 📊 Portfolio: **65** · ATS: **90** · Credibility: **67** · Job Match: **80**
> - 📈 Market Readiness: **86%** (8/10 skills matched)
> - 🔴 Priority Gaps: **AWS 54%** · **Kubernetes 42%**
> - 💚 Top Strengths: Python · Git · LangChain · LLM Integration

---

### 📄 Resume Intelligence — Real ATS Engine

![Resume Intelligence page showing ATS Score 90/100 with breakdown: Contact 20/20, Sections 20/20, Skills 20/20, Keywords 10/20, Formatting 17/20](https://github.com/satyanandh-ai/devpath-agent/assets/resume-preview.png)

> **5-category computed engine. No LLM guessing. Max score: 92.**

| Category | Score | What it checks |
|---|---|---|
| Contact Info | 20/20 ✅ | Email · Phone · LinkedIn · GitHub |
| Resume Sections | 20/20 ✅ | Summary · Education · Skills · Projects · Experience |
| Skills Coverage | 20/20 ✅ | Tiered scoring — 15+ keywords = 20pts |
| Keywords & Verbs | 10/20 ⚠️ | Action verbs · quantified achievements |
| Formatting & Length | 17/20 ✅ | Word count · bullets · dates · headers |
| **Total** | **90/100** | **Strong** |

---

### 💬 Personalized Career Chat

![Career Chat showing personalized answer to Am I ready for AI Engineer with specific scores, skill gaps Docker AWS Kubernetes and actionable recommendations](https://github.com/satyanandh-ai/devpath-agent/assets/chat-preview.png)

> **Every answer uses your actual profile — not generic ChatGPT advice.**

When asked *"Am I ready for AI Engineer?"* DevPath responds with:

```
✅ ATS Score: 90/100 — strong technical proficiency
⚠️ Portfolio: 65/100 — need more deployed projects

Skills lacking GitHub evidence:
  • Docker  • AWS  • Kubernetes

Market Readiness: 86% — close to ready
Priority action: Deploy 1 project on AWS this week
```

---

## 🏗️ Agentic Architecture

```
                      USER CAREER GOAL
                             │
                    ┌────────▼────────┐
                    │    PLANNER      │  LangGraph Supervisor
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   RESUME AGENT        GITHUB AGENT         RAG ENGINE
   ─────────────       ────────────         ──────────
   ATS Scoring         Portfolio            4 Collections:
   Skill Extract       Evidence Map         • Jobs (20)
   Structured          Deep Repo            • Interview (25)
   Analysis            Inspection           • Learning (18)
                                            • Career KB (15)
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  SKILL MATRIX   │  Central Source of Truth
                    │                 │  Confirmed/Strong/
                    │  Resume ↔ GitHub│  Partial/Weak/Not Found
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  GAP PRIORITY   │  role × market × gap × evidence
                    │    ENGINE       │
                    └────────┬────────┘
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
          JOB AGENT    ACTION PLANNER   EVALUATOR
          ──────────   ─────────────   ─────────
          Weighted     30-60-90 Day    Goal met?
          Evidence     Concrete Steps
          Scoring
               └─────────────┼─────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
         ✅ DONE                      🔄 REPLAN
         Goal achieved                Act again
```

---

## 🔬 Skill Evidence Engine

The single source of truth every DevPath module reads from:

```python
skill_matrix["docker"] = {
    "evidence_level":  "Partial",
    "evidence_reason": "Resume mention only — no GitHub Dockerfile found",
    "evidence_trace":  [
        {"source": "Resume", "detail": "Listed in skills section"},
        # No GitHub evidence
    ],
    "readiness":       45,    # computed from evidence alone
    "market_demand":   65,    # % of AI Engineer job postings
    "github_repos":    [],    # traceable — none found
}
```

### 5 Evidence Levels — Standardized Across All Modules

| Level | Meaning | Example |
|---|---|---|
| ✅ **Confirmed** | Resume + GitHub file evidence | Dockerfile found in repo |
| ✅ **Strong** | Resume + GitHub README/metadata | Mentioned in README |
| ⚠️ **Partial** | Resume only — no GitHub proof | Listed in skills, no project |
| 🟠 **Weak** | GitHub only — not on resume | Found in repo, not claimed |
| ❌ **Not Found** | No evidence anywhere | Completely missing |

---

## 🌉 Reality Check — Resume ↔ GitHub Credibility

> The feature most career tools don't have.

```
Skill          Resume    GitHub Evidence         Level
────────────────────────────────────────────────────────
Python         ✅        ✅ 5 repos              Confirmed
FastAPI        ✅        ✅ requirements.txt     Confirmed
LangChain      ✅        ✅ devpath-agent repo   Confirmed
Docker         ✅        ❌ No Dockerfile found  Partial
AWS            ✅        ❌ No boto3/S3 found    Partial
Kubernetes     ✅        ❌ No k8s config found  Partial

Credibility Score: 67%
Hidden Strengths (GitHub but not on Resume): ChromaDB · Groq
```

---

## 🔬 Evidence Simulator

> *"What happens to my Job Match if I Dockerize my project?"*
> **Deterministic projection — no AI estimation.**

```
Skill: Docker · Partial → Strong

                   BEFORE    AFTER    DELTA
Job Match:          55%  →   63%    +8%
Evidence Score:     45   →   75     +30pts
Overall Evidence:   48   →   52     +4pts

Action: Add Dockerfile to devpath-agent repo
Output: 1 GitHub file → Evidence level: Strong
```

---

## 📊 Market Intelligence

> Hybrid C+A: Computed database for scores + LLM for explanations.

| Role | Demand | India Salary | US Salary |
|---|---|---|---|
| GenAI Engineer | 🔥 Extremely High ↑120% | ₹12L–₹35L | $110K–$200K |
| MLOps Engineer | 🔥 Very High ↑58% | ₹10L–₹28L | $100K–$170K |
| AI Engineer | 🔥 Very High ↑42% | ₹8L–₹24L | $90K–$160K |
| ML Engineer | ✅ High ↑31% | ₹7L–₹20L | $85K–$150K |
| Data Scientist | ✅ High ↑18% | ₹6L–₹18L | $80K–$140K |

*Source: Prototype dataset curated from LinkedIn/Glassdoor/Naukri Q1–Q3 2026*

---

## 🤖 Agentic Mode — LangGraph Loop

```
Goal: "Get AI Engineer internship in 3 months"

[Resume Agent]   → ATS: 90 | Skills: Python, LangChain, RAG, FastAPI
[GitHub Agent]   → Portfolio: 65 | Gaps: Docker, AWS, CI/CD
[Gap Analyzer]   → Critical: AWS (54%) | Important: Kubernetes (42%)
[Job Agent]      → Match: 80% weighted | Missing: AWS, K8s
[Action Planner] → Week 1: Dockerize project → Evidence: Partial→Strong
                   Week 2: Deploy FastAPI to AWS EC2
                   Week 3: Add GitHub Actions CI/CD
[Evaluator]      → Readiness: 72% | Recommendation: REPLAN
     ↓
[REPLAN] Focus: Docker → target Strong evidence → rerun loop
```

---

## 🚀 Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Agent Loop** | LangGraph | Observe→Decide→Act→Evaluate→Adapt |
| **LLM** | Groq (`openai/gpt-oss-20b`) | Sub-second inference |
| **Orchestration** | LangChain | Tools · chains · agents |
| **RAG** | ChromaDB (in-memory) | 4-collection knowledge base |
| **ATS Engine** | Custom (5-rule) | Deterministic scoring |
| **Skill Engine** | Canonical taxonomy | Single source of truth |
| **PDF** | pypdf | Resume extraction |
| **Charts** | Plotly | Radar · bar · donut |
| **Reports** | ReportLab | PDF career reports |
| **UI** | Streamlit + CSS | Pink glass dashboard |
| **Deployment** | Streamlit Cloud | Live, zero-config |

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/satyanandh-ai/devpath-agent.git
cd devpath-agent

# Install
pip install -r requirements.txt

# Configure
echo 'GROQ_API_KEY="your_key"' > .env
echo 'GITHUB_TOKEN="your_token"' >> .env

# Run
streamlit run app.py
```

**Streamlit Cloud Secrets:**
```toml
GROQ_API_KEY = "gsk_..."
GITHUB_TOKEN = "github_pat_..."
```

---

## 🏆 Why DevPath Wins

| | Other Tools | DevPath |
|---|---|---|
| Resume Score | LLM opinion | 5-rule deterministic engine |
| Skill Proof | Resume claim | Resume + GitHub evidence |
| Gap Priority | Generic list | role × market × evidence formula |
| Job Match | Binary yes/no | Weighted evidence (0.0–1.0) |
| Market Data | Vague trends | Role-specific demand % database |
| Career Chat | Generic tips | Uses your actual scores |
| Agent Loop | Single LLM call | LangGraph observe→adapt loop |
| What-if | Not possible | Evidence Simulator (deterministic) |

---

<div align="center">

**⚡ DevPath · Agentic Arena 2026**

**Ch. Satyanand · B.Tech AI/ML · ALIET Vijayawada**

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://devpath-agent-satya.streamlit.app)

*Built with LangGraph · LangChain · Groq · ChromaDB · Streamlit*

</div>
