# 🐙 DevPath Agent
### An Autonomous AI Career Agent for Developers & Students
**Submitted for Agentic Arena 2026 | TechVerse Solutions**
**Author:** Ch. Satyanand

---

## 🎯 Problem Statement
Students and early-career developers face a fragmented job search process, juggling multiple disconnected tools (resume builders, GitHub reviewers, skill-gap analyzers, etc.). This breaks focus, wastes time, and leaves candidates underprepared.

## 🚀 Proposed Solution
DevPath Agent acts as an autonomous personal career co-pilot. A user inputs a career goal, and the agent reasons, plans, and executes a multi-step career analysis using:
*   **Resume Analysis:** Parses PDFs, scores ATS compatibility, and flags weak areas.
*   **GitHub Analysis:** Fetches public repositories via the GitHub REST API to evaluate project quality.
*   **Skill Gap Detection:** Autonomously cross-references user technical stacks against target job requirements.
*   **Roadmap Generation:** Forges a personalized, 30-60-90 day execution plan.

## 🛠️ Technology Stack
*   **AI Brain:** LLaMA 3.3 (via Groq API) for ultra-low latency tool orchestration and reasoning.
*   **Framework:** LangChain + LangGraph (Agentic Loop management).
*   **Backend:** Python + FastAPI.
*   **Frontend UI:** Streamlit.