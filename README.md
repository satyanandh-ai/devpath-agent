# DevPath — Agentic Career Intelligence

> **An agentic AI system that analyzes a candidate's evidence, identifies the highest-impact career gap, takes action, evaluates progress, and adapts the plan.**

<p align="center">

**Observe · Decide · Act · Evaluate · Adapt**

</p>

<p align="center">
  <a href="https://devpath-agent-satya.streamlit.app/">Live Demo</a> ·
  <a href="https://github.com/satyanandh-ai/devpath-agent">Source Code</a>
</p>

---

## Overview

Most career platforms give users information.

**DevPath helps decide what to do next.**

DevPath combines resume evidence, GitHub activity, job-market requirements, retrieval-augmented knowledge, and agentic reasoning to create a personalized career strategy.

Instead of producing a one-time recommendation, DevPath is designed around a closed-loop workflow:

```text
User Goal
   ↓
Observe
   ↓
Decide
   ↓
Act
   ↓
Evaluate
   ↓
Adapt
   ↺
```

The system continuously uses the candidate's evidence and evaluation results to determine the next highest-value action.

---

# The Problem

Students and early-career developers often have career information scattered across multiple places:

* Resume
* GitHub
* Job descriptions
* Learning resources
* Interview preparation
* Personal projects

This creates a critical gap:

> **A candidate may claim a skill on their resume without having enough evidence to demonstrate it.**

At the same time, even when a candidate knows their weaknesses, they often do not know:

* Which gap matters most?
* Which skill should be improved first?
* What action will have the highest impact?
* Does the action actually improve their readiness?
* What should they do if the first plan is insufficient?

DevPath brings these signals together and turns them into an **adaptive career decision system**.

---

# Why Agentic AI?

A conventional career assistant might work like this:

```text
Profile → LLM → Recommendation
```

That produces an answer, but the system stops there.

DevPath is designed as a goal-driven workflow:

```text
                  USER GOAL
                      │
                      ▼
                   OBSERVE
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Resume       GitHub      Market
          │           │           │
          └───────────┼───────────┘
                      ▼
                    DECIDE
                      │
                      ▼
                GAP PRIORITIZATION
                      │
                      ▼
                     ACT
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
        Skill      Project       Job
        Action      Action      Action
          │           │           │
          └───────────┼───────────┘
                      ▼
                  EVALUATE
                      │
              ┌───────┴───────┐
              │               │
             DONE            REPLAN
                              │
                              ▼
                            ADAPT
                              │
                              └──────► DECIDE
```

The important part is the **feedback loop**.

The evaluator can determine whether the current strategy is sufficient. If it is not, the system can identify the next priority and replan.

---

# Agentic Workflow

## 1. Observe

DevPath collects and analyzes available evidence:

* Resume
* GitHub profile
* Repository information
* Skill evidence
* Target role
* Market requirements
* Retrieved career knowledge

The system builds a structured view of the candidate.

---

## 2. Decide

The system identifies and prioritizes the most important skill gaps.

Rather than simply listing every missing skill, DevPath uses a **Gap Priority Engine** to determine which gaps deserve attention first.

The system can consider:

* Current evidence
* Target evidence level
* Market demand
* Job-match impact
* Potential improvement

---

## 3. Act

The Action Planner converts the selected gap into a concrete next action.

Possible actions include:

* Build a targeted project
* Strengthen a technical skill
* Improve portfolio evidence
* Prepare for an interview topic
* Improve deployment experience
* Target a relevant role

The objective is to move from **career advice** to **career action**.

---

## 4. Evaluate

After planning an action, DevPath evaluates the candidate's current state.

The evaluator considers:

* Goal achievement
* Readiness
* Remaining gaps
* Evidence
* Recommended next focus

The result determines whether the system should finish or continue.

```text
Goal Achieved?
     │
 ┌───┴───┐
YES      NO
 │        │
DONE    REPLAN
```

---

## 5. Adapt

If the goal has not been achieved, DevPath can continue the workflow with a new priority.

This is the key difference between a static roadmap and an adaptive agentic system.

```text
Evaluate
   ↓
Not sufficient
   ↓
Identify remaining bottleneck
   ↓
Replan
   ↓
New action
   ↓
Evaluate again
```

---

# Architecture

DevPath uses a **LangGraph-based agentic workflow** to coordinate specialized capabilities while maintaining structured state.

```text
                         ┌─────────────────┐
                         │    USER GOAL    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    SUPERVISOR   │
                         │    LangGraph    │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │ Resume      │     │ GitHub      │     │ Job /       │
       │ Intelligence│     │ Intelligence│     │ Market      │
       └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         ┌─────────────────┐
                         │  Skill Matrix   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Gap Priority    │
                         │ Engine          │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Action Planner  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Evaluator    │
                         └────────┬────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                       DONE              REPLAN
                                           │
                                           └──────► Supervisor
```

---

# Agent State

The agentic workflow maintains structured state across the execution cycle:

```text
goal
resume_analysis
github_analysis
skill_gaps
job_matches
action_plan
evaluation
iteration
status
next_agent
```

This allows information produced during one stage to influence subsequent decisions instead of treating every model call as an isolated request.

---

# Core Intelligence Engines

## Resume Intelligence

Analyzes the candidate's resume for:

* Skills
* Keywords
* Resume quality
* Role alignment
* Improvement opportunities
* ATS-oriented signals

---

## GitHub Evidence Engine

Analyzes real development evidence from GitHub.

It can inspect signals such as:

* Repositories
* Programming languages
* README quality
* Project structure
* Dependencies
* Docker/deployment evidence
* Repository activity

The goal is to understand what the candidate has **actually demonstrated**, not only what they claim.

---

## Resume ↔ GitHub Reality Check

One of DevPath's core ideas is comparing:

```text
Resume Claims
      ↕
GitHub Evidence
```

Example:

```text
Python       → Strong evidence
FastAPI      → Strong evidence
LangChain    → Demonstrated
Docker       → Limited evidence
AWS          → No evidence
```

This helps identify the difference between:

**"I listed the skill."**

and

**"I have evidence that demonstrates the skill."**

---

# Skill Evidence Engine

DevPath uses a structured skill taxonomy and evidence model to represent candidate capability.

Evidence can be evaluated across multiple levels, allowing the system to distinguish between a skill that is merely mentioned and one that is supported by stronger portfolio evidence.

This evidence model feeds the:

* Skill Matrix
* Gap Priority Engine
* Evidence Simulator
* Career evaluation

---

# Gap Priority Engine

Not every skill gap has the same value.

DevPath prioritizes gaps using available evidence and market information rather than simply asking an LLM to rank skills.

The system can estimate the potential value of improving a skill by simulating an evidence upgrade and comparing the resulting change in:

* Job-match potential
* Evidence strength
* Overall readiness

This helps answer:

> **"Which improvement is worth doing first?"**

---

# Market Intelligence

DevPath connects candidate capability with role requirements.

It can surface:

* Target-role requirements
* Skill demand
* Job-match signals
* Market priorities
* Emerging skills
* Career opportunities

The purpose is to prevent users from following a roadmap that is disconnected from the roles they actually want.

---

# Retrieval-Augmented Generation

DevPath includes a RAG layer for retrieving relevant career knowledge.

```text
Career Knowledge
      │
      ▼
Document Ingestion
      │
      ▼
Chunking
      │
      ▼
Embeddings
      │
      ▼
Vector Retrieval
      │
      ▼
Relevant Context
      │
      ▼
Agent Reasoning
```

The retrieval layer can provide context for:

* Career guidance
* Skills
* Roles
* Interview preparation
* Learning resources

The retrieved context is used alongside the candidate's profile rather than relying only on the model's internal knowledge.

---

# Evidence Simulation

DevPath includes a deterministic **what-if analysis** capability.

Instead of asking:

> "Would learning Docker help?"

the system can simulate an evidence upgrade and estimate how that change could affect candidate signals.

Conceptually:

```text
Current Evidence
      ↓
Simulate Skill Upgrade
      ↓
Compare Before / After
      ↓
Estimate Impact
```

This allows the action planner to prefer potentially higher-value interventions.

---

# Interview Coach

DevPath also supports personalized interview preparation.

It can provide:

* Role-specific questions
* Candidate-focused practice
* Answer evaluation
* Feedback
* Improvement guidance

Interview preparation is informed by the broader career profile rather than being completely independent of it.

---

# Application Experience

DevPath is organized as a multi-page Streamlit application with dedicated career intelligence workflows.

The current application includes capabilities for:

* Career dashboard
* Resume analysis
* GitHub analysis
* Skill evidence
* Market intelligence
* Career intelligence
* RAG knowledge
* Agentic Mode
* Interview preparation
* Reports and visualizations

The **Agentic Mode** exposes the execution process so users can see the workflow rather than receiving only a final recommendation.

---

# Technology Stack

| Layer                  | Technology                |
| ---------------------- | ------------------------- |
| Language               | Python                    |
| Frontend               | Streamlit                 |
| Agent Orchestration    | LangGraph                 |
| LLM Framework          | LangChain                 |
| LLM Provider           | Groq                      |
| Retrieval              | ChromaDB                  |
| GitHub Analysis        | GitHub API                |
| Embeddings / Retrieval | FastEmbed / Vector Search |
| Visualization          | Plotly                    |
| Reports                | ReportLab                 |
| Deployment             | Streamlit Cloud           |

---

# Project Structure

```text
devpath-agent/
│
├── app.py
│   ├── Skill Evidence Engine
│   ├── GitHub Evidence Engine
│   ├── ATS Engine
│   ├── Skill Matrix
│   ├── Gap Priority Engine
│   ├── Evidence Simulator
│   ├── RAG Engine
│   ├── LangGraph Agent Loop
│   └── Streamlit UI
│
├── agent.py
│   └── Agent / tool components
│
├── rag_engine.py
│   └── Standalone RAG engine
│
├── requirements.txt
├── .env.example
├── .gitignore
├── tests/
└── README.md
```

---

# Example Agent Run

### Goal

```text
Become job-ready for an AI Engineer internship.
```

### Observe

```text
Resume
 ├── Python
 ├── FastAPI
 └── LangChain

GitHub
 ├── AI projects
 ├── Python repositories
 └── Limited deployment evidence

Market
 ├── Docker
 ├── Cloud
 └── MLOps
```

### Decide

```text
Highest-priority gap:
Deployment evidence
```

### Act

```text
Build and deploy an AI application
with production-style deployment.
```

### Evaluate

```text
Goal achieved?
NO

Remaining bottleneck:
Cloud deployment evidence
```

### Adapt

```text
Replan:
Prioritize cloud deployment next.
```

### Result

```text
The roadmap changes based on evaluation.
```

That is the core behavior DevPath is designed to demonstrate:

> **The system does not stop at analysis. It uses evaluation to determine what should happen next.**

---

# Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/satyanandh-ai/devpath-agent.git
cd devpath-agent
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file using `.env.example`.

Example:

```env
GROQ_API_KEY=your_api_key_here
GITHUB_TOKEN=your_token_here
```

Only configure the credentials required by your selected workflows.

## 5. Run the application

```bash
streamlit run app.py
```

---

# Security

**Never commit secrets to GitHub.**

Do not commit:

```text
.env
API keys
Access tokens
Passwords
Private credentials
```

Use `.env` locally and keep secrets outside source control.

---

# Live Demo

🚀 **Web Application**

https://devpath-agent-satya.streamlit.app/

💻 **Source Code**

https://github.com/satyanandh-ai/devpath-agent

---

# Design Principles

### Evidence over claims

Skills should be supported by meaningful evidence whenever possible.

### Goal over generic advice

Recommendations should be connected to a defined career objective.

### Action over information

The system should identify what the candidate can actually do next.

### Evaluation over one-shot generation

The system should evaluate progress instead of assuming the first plan is correct.

### Adaptation over static roadmaps

When priorities change, the plan should be able to change with them.

---

# Why DevPath?

Traditional tools often solve one part of the career problem:

| Capability           | Traditional Approach    | DevPath                       |
| -------------------- | ----------------------- | ----------------------------- |
| Resume               | Resume scoring          | Resume Intelligence           |
| Portfolio            | Manual GitHub review    | GitHub Evidence Engine        |
| Skill validation     | Resume claims           | Resume ↔ GitHub Reality Check |
| Skill prioritization | Generic recommendations | Gap Priority Engine           |
| Market fit           | Job-board browsing      | Market Intelligence           |
| Career roadmap       | Static advice           | Adaptive action planning      |
| Evaluation           | Usually absent          | Agent evaluator               |
| Adaptation           | Usually absent          | Replanning loop               |

The central idea is simple:

> **Don't just tell candidates what they are missing. Determine what matters most, take action, evaluate the result, and adapt.**

---

# Hackathon Focus

DevPath is designed to demonstrate the core properties of an agentic AI system:

```text
Observe
   ↓
Decide
   ↓
Act
   ↓
Evaluate
   ↓
Adapt
   ↺
```

The system combines:

**LangGraph + specialized tools + structured state + evidence analysis + RAG + evaluation + adaptive planning.**

---

# 👨‍💻 Built By

## Ch. Satyanand

**B.Tech — Artificial Intelligence & Machine Learning**

Andhra Loyola Institute of Engineering & Technology
Vijayawada, Andhra Pradesh, India

**GitHub:** https://github.com/satyanandh-ai

---

# License

This project is released under the **MIT License**.

---

<p align="center">

### DevPath

**Observe. Decide. Act. Evaluate. Adapt.**

</p>
