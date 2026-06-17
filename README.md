# 🚀 DevPath Agent

An Autonomous AI Career Agent for Developers & Students

Submitted for Agentic Arena 2026 · TechVerse Solutions
Author: Ch. Satyanand

---

## 🎯 Problem Statement

Students and early-career developers face a fragmented job search process — juggling resume builders, GitHub reviewers, skill-gap analyzers, and interview prep tools separately. This breaks focus, wastes time, and leaves candidates underprepared for real opportunities.

## 💡 Proposed Solution

DevPath Agent is an autonomous personal career co-pilot. Instead of answering one question at a time like a typical chatbot, it reasons, plans, and executes a multi-step career analysis the moment a user states their goal.

For example: a user says "I want to become a Machine Learning Engineer" and the agent autonomously analyzes their GitHub, cross-references it against the target role's requirements, and delivers a personalized roadmap — no further prompting required.

## ✨ Features

- 🐙 **GitHub Analyzer** — Fetches public repositories via the GitHub REST API and evaluates tech stack, project quality, and developer profile.
- 📄 **Resume Analyzer** — Parses uploaded PDF resumes, extracts skills, and generates an ATS compatibility score out of 10.
- 🌉 **Bridge Plan (core feature)** — Cross-references GitHub skills against the target role's requirements and produces a personalized 30-60-90 day roadmap.
- 💬 **Career Chat** — Open-ended conversational agent for any career, skill, or job-search question.

## 🧠 Why This Is Truly Agentic

Unlike a simple chatbot, DevPath Agent demonstrates all four pillars of agentic AI:

- 🔍 **Reasoning** — Understands the user's career goal and breaks it into logical sub-tasks.
- 🗺️ **Planning** — Decides which tools to call and in what order, without user guidance.
- 🛠️ **Tool Use** — Autonomously calls the GitHub API, PDF parser, and skills database.
- ⚙️ **Autonomy** — Completes the full analysis end-to-end from a single input.

## 🏗️ Architecture

```
User Input/Goal
      |
LangGraph Agent (LLaMA 3.3 / Groq)
      |
      |-- GitHub Tool (REST API)
      |-- Resume Parser (PyPDF2)
      |-- Skills Database (Role Mapping)
      |
Cross-Reference & Roadmap Generation
      |
Streamlit UI Output
```

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🧠 AI Brain | LLaMA 3.3 (via Groq API) | Ultra-low latency reasoning and tool orchestration |
| 🔗 Agent Framework | LangChain + LangGraph | Agentic loop management and tool calling |
| ⚙️ Backend | Python | Core application logic |
| 📄 Resume Parsing | PyPDF2 | PDF text extraction |
| 🐙 External Data | GitHub REST API | Real-time repository and profile analysis |
| 🎨 Frontend | Streamlit | Interactive multi-tab web interface |

## 🎬 Demo Walkthrough

The app runs as a 4-tab interactive dashboard:

1. 🐙 **GitHub Analyzer** — paste any username, get an instant developer profile breakdown.
2. 📄 **Resume Analyzer** — upload a PDF, get skills, job matches, and an ATS score.
3. 🌉 **Bridge Plan** — combine a GitHub handle with a career goal for a personalized roadmap.
4. 💬 **Career Chat** — ask any open-ended career question.

## ⚙️ Getting Started

### ✅ Prerequisites
- Python 3.10+
- A free Groq API key (https://console.groq.com/keys)

### 📦 Installation

```bash
git clone https://github.com/satyanandh-ai/devpath-agent.git
cd devpath-agent

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install langchain langchain-groq langgraph streamlit pypdf2 requests python-dotenv
```

### 🔑 Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### ▶️ Run the App

```bash
streamlit run app.py
```

The app will open automatically at http://localhost:8501

## 📂 Project Structure

```
devpath-agent/
├── app.py              # Streamlit web application (main UI)
├── agent.py            # CLI version of the agent
├── .env                # API keys (not committed)
├── .gitignore
└── README.md
```

## 🌍 Expected Impact

| Who Benefits | Impact |
|---|---|
| 🎓 Students & Freshers | Get a clear, personalized action plan instead of generic advice |
| 💼 Working Professionals | Identify upskilling needs to switch roles or get promoted |
| 👨‍💻 Developers | Understand how their GitHub profile looks to recruiters in seconds |

## 👤 Author

**Ch. Satyanand**
B.Tech AIML, Andhra Loyola Institute of Engineering & Technology (ALIET), Vijayawada
GitHub: https://github.com/satyanandh-ai

---

Built for Agentic Arena 2026 · TechVerse Solutions 🚀