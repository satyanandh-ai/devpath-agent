# DevPath 2.0 — Career Intelligence Platform
# Dashboard-style UI with computed (not guessed) scoring for credibility.

import streamlit as st
import requests
import json
import os
import re
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

st.set_page_config(
    page_title="DevPath — Career Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════
#  THEME — dark dashboard, inspired by analytics-SaaS reference
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(160deg, #0F1123 0%, #171933 55%, #1B1E3F 100%);
    color: #E8E8F5;
}
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #12142B !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 14.5px !important;
    color: #A8A8C0 !important;
    padding: 4px 0;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
    color: #ffffff !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(10px);
}
.metric-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 10px;
}
.metric-label { font-size: 12.5px; color: #9494B0; font-weight: 500; margin-bottom: 2px; }
.metric-value { font-size: 26px; font-weight: 800; color: #ffffff; }
.metric-empty { font-size: 12px; color: #6B6B8A; margin-top: 6px; }

/* Section card */
.panel {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 28px 30px;
    margin-bottom: 22px;
}
.panel-title { font-size: 17px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.panel-desc { font-size: 13px; color: #9494B0; margin-bottom: 18px; line-height: 1.5; }

/* Pills / tags */
.tag-good { background: rgba(52,211,153,0.15); color: #34D399; border: 1px solid rgba(52,211,153,0.3);
    border-radius: 8px; padding: 5px 12px; font-size: 12.5px; font-weight: 600; display: inline-block; margin: 3px; }
.tag-bad { background: rgba(248,113,113,0.15); color: #F87171; border: 1px solid rgba(248,113,113,0.3);
    border-radius: 8px; padding: 5px 12px; font-size: 12.5px; font-weight: 600; display: inline-block; margin: 3px; }
.tag-neutral { background: rgba(129,140,248,0.15); color: #A5B4FC; border: 1px solid rgba(129,140,248,0.3);
    border-radius: 8px; padding: 5px 12px; font-size: 12.5px; font-weight: 600; display: inline-block; margin: 3px; }

/* Inputs */
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label { color: #C4C4DC !important; font-weight: 500 !important; }

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 12px 26px !important;
    font-weight: 600 !important; font-size: 14px !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.35) !important;
}
div.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 24px rgba(99,102,241,0.5) !important; }

/* Progress bars */
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #6366F1, #34D399) !important; }

/* Alerts */
div[data-testid="stAlert"] { border-radius: 12px !important; background: rgba(255,255,255,0.04) !important; }

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  LLM SETUP
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found! Add it in Streamlit Cloud → Settings → Secrets.")
        st.stop()
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

llm = get_llm()

def ask_llm(prompt: str) -> str:
    try:
        return llm.invoke([HumanMessage(content=prompt)]).content
    except Exception as e:
        return f"ERROR: {str(e)}"

# ══════════════════════════════════════════════════════════════════════
#  CORE DATA FUNCTIONS
# ══════════════════════════════════════════════════════════════════════
def read_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text[:4000] if text.strip() else "ERROR: Could not extract text."
    except Exception as e:
        return f"ERROR: {str(e)}"

def fetch_github(username: str) -> dict:
    """Returns structured GitHub data (dict), not prose — so downstream scoring is computed, not guessed."""
    try:
        user_resp = requests.get(f"https://api.github.com/users/{username}", timeout=10)
        if user_resp.status_code == 404:
            return {"error": f"GitHub user '{username}' not found."}
        if user_resp.status_code != 200:
            return {"error": f"GitHub API error. Status: {user_resp.status_code}"}
        user_data = user_resp.json()
        repos = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100", timeout=10).json()
        if not isinstance(repos, list) or not repos:
            return {"error": f"User '{username}' has no public repositories."}

        languages = sorted({r.get("language") for r in repos if r.get("language")})
        return {
            "username": username,
            "name": user_data.get("name", "N/A"),
            "bio": user_data.get("bio", ""),
            "public_repos": len(repos),
            "followers": user_data.get("followers", 0),
            "languages": languages,
            "repos": repos,
        }
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection."}
    except requests.exceptions.Timeout:
        return {"error": "GitHub API timed out."}
    except Exception as e:
        return {"error": str(e)}

def compute_portfolio_signals(github_data: dict) -> dict:
    """Rule-based scoring from real GitHub API fields — reproducible, not LLM-guessed.
    Deliberately uses only fields already present in the repo-list response (no per-repo API calls),
    so this stays fast and doesn't risk hitting GitHub's unauthenticated rate limit during a demo.
    Each repo can earn: Deployment(3) + Documentation(2) + Originality(2) + Popularity(1) + Recency(2) = 10 max."""
    repos = github_data.get("repos", [])
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:8]

    scored = []
    cat_points = {"Deployment": 0, "Documentation": 0, "Originality": 0, "Popularity": 0, "Recency": 0}
    cat_max = {"Deployment": 3, "Documentation": 2, "Originality": 2, "Popularity": 1, "Recency": 2}
    total_signal = 0
    max_signal = 0
    now = datetime.utcnow()
    for r in top_repos:
        dep = 3 if r.get("homepage") else 0
        doc = 2 if r.get("description") else 0
        orig = 2 if not r.get("fork") else 0
        pop = 1 if r.get("stargazers_count", 0) > 0 else 0
        recent = False
        pushed_at = r.get("pushed_at")
        if pushed_at:
            try:
                pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
                recent = (now - pushed_dt).days <= 180
            except Exception:
                recent = False
        rec = 2 if recent else 0
        s = dep + doc + orig + pop + rec
        cat_points["Deployment"] += dep
        cat_points["Documentation"] += doc
        cat_points["Originality"] += orig
        cat_points["Popularity"] += pop
        cat_points["Recency"] += rec
        scored.append({"name": r["name"], "score": s, "max": 10,
                        "description": r.get("description"), "url": r.get("html_url"),
                        "deployed": bool(r.get("homepage")), "stars": r.get("stargazers_count", 0),
                        "recently_updated": recent})
        total_signal += s
        max_signal += 10

    n = len(top_repos) or 1
    breakdown = {cat: round((cat_points[cat] / (cat_max[cat] * n)) * 100) for cat in cat_points}
    portfolio_score = round((total_signal / max_signal) * 100) if max_signal else 0

    strengths = [cat for cat, pct in breakdown.items() if pct >= 60]
    weaknesses = [cat for cat, pct in breakdown.items() if pct < 40]
    if len(github_data.get("languages", [])) >= 3:
        strengths.append("Language Diversity")
    else:
        weaknesses.append("Language Diversity")

    return {
        "portfolio_score": portfolio_score,
        "breakdown": breakdown,
        "ranked_repos": sorted(scored, key=lambda x: -x["score"]),
        "strengths": strengths,
        "weaknesses": weaknesses,
    }

def build_github_skill_text(github_data: dict) -> str:
    """Languages alone miss frameworks (FastAPI, LangChain, etc). Pull repo names/descriptions/topics too
    so skill extraction actually reflects what's been built, not just the file extensions used."""
    lines = ["Languages: " + ", ".join(github_data.get("languages", []))]
    for r in github_data.get("repos", [])[:15]:
        topics = r.get("topics") or []
        lines.append(f"- {r.get('name')}: {r.get('description') or ''} (topics: {', '.join(topics)}, lang: {r.get('language') or ''})")
    return "\n".join(lines)

def compute_ats_score(resume_text: str) -> dict:
    """Rule-based ATS check — same philosophy as Portfolio Score: reproducible checks, not an LLM opinion."""
    text = resume_text.lower()
    has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text))
    has_phone = bool(re.search(r"(\+?\d[\d\-\s]{8,}\d)", resume_text))
    checks = {
        "Contact Info": has_email and has_phone,
        "Education Section": any(k in text for k in ["education", "b.tech", "bachelor", "university", "college", "degree"]),
        "Projects/Experience Section": any(k in text for k in ["experience", "projects", "internship"]),
        "Skills Section": "skill" in text,
        "Quantified Impact": bool(re.search(r"\d+%|\d+x\b|\$\d+|\b\d+\+?\s?(users|students|projects|repositories)", text)),
        "Action Verbs Used": sum(1 for v in ["built", "developed", "designed", "led", "created",
                                              "implemented", "deployed", "optimized", "managed", "automated"] if v in text) >= 3,
        "Reasonable Length (300-1200 words)": 300 <= len(resume_text.split()) <= 1200,
    }
    score = round((sum(checks.values()) / len(checks)) * 100)
    return {"score": score, "checks": checks}

def extract_skills_llm(text: str, source_label: str) -> list:
    """LLM extracts skills into strict JSON — extraction is the LLM's job, scoring is not."""
    prompt = f"""Extract ONLY concrete technical skills (languages, frameworks, tools, platforms) mentioned in this {source_label}.
Return STRICT JSON only, no markdown fences, no explanation:
{{"skills": ["skill1", "skill2"]}}

Text:
{text[:3000]}"""
    raw = ask_llm(prompt)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json", "", 1).strip()
        skills = json.loads(cleaned).get("skills", [])
        return sorted({s.lower().strip() for s in skills if s.strip()})
    except Exception:
        return []

@tool
def full_github_report_tool(username: str) -> str:
    """Fetches a GitHub profile, computes its Portfolio Score, and extracts evidenced skills.
    Use this whenever the user wants their GitHub analyzed or wants a portfolio/credibility check."""
    data = fetch_github(username)
    if "error" in data:
        return f"ERROR: {data['error']}"
    portfolio = compute_portfolio_signals(data)
    skill_text = build_github_skill_text(data)
    skills = extract_skills_llm(skill_text, "GitHub profile")
    combined_skills = sorted(set(skills) | {l.lower() for l in data["languages"]})
    st.session_state.github_data = data
    st.session_state.portfolio = portfolio
    st.session_state.github_skills = combined_skills
    return (f"Portfolio Score: {portfolio['portfolio_score']}/100. "
            f"Strengths: {portfolio['strengths']}. Weaknesses: {portfolio['weaknesses']}. "
            f"Skills evidenced from GitHub: {combined_skills}")

@tool
def reality_check_tool(_: str = "") -> str:
    """Compares the user's resume skills (must already be uploaded/analyzed this session) against their
    GitHub evidence (must already be fetched this session), producing a Credibility Score. Call this only
    after both resume skills and GitHub skills are available."""
    if not st.session_state.resume_skills:
        return "ERROR: No resume skills found in session — ask the user to upload a resume in Resume Intelligence first."
    if not st.session_state.github_skills:
        return "ERROR: No GitHub skills found in session — run full_github_report_tool first."
    overlap = compute_overlap(st.session_state.resume_skills, st.session_state.github_skills)
    st.session_state.reality_check = overlap
    return f"Credibility Score: {overlap['score']}%. Verified: {overlap['verified']}. Unverified (claimed but no GitHub evidence): {overlap['unverified']}."

@tool
def roadmap_preview_tool(target_role: str) -> str:
    """Compares known skills (resume + GitHub, whatever is available this session) against the skills
    required for a target role, returning the gap. Use this when the user states a career goal."""
    known = sorted(set((st.session_state.github_skills or []) + (st.session_state.resume_skills or [])))
    role_skills_raw = ask_llm(f"List top 8-10 technical skills for a '{target_role}' role in 2026. Comma-separated, no explanation.")
    return f"Known skills: {known}. Required for {target_role}: {role_skills_raw}. Build the full 30-60-90 roadmap on the Roadmap page using these."

@tool
def analyze_github_tool(username: str) -> str:
    """Analyzes a GitHub profile and returns a readable summary of repos, languages, and activity."""
    data = fetch_github(username)
    if "error" in data:
        return f"ERROR: {data['error']}"
    top = sorted(data["repos"], key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]
    lines = [f"- {r['name']}: {r.get('description') or 'No description'} (⭐ {r.get('stargazers_count', 0)}, {r.get('language') or 'Unknown'})" for r in top]
    return (f"GitHub: {username}\nName: {data['name']}\nPublic repos: {data['public_repos']}\n"
            f"Languages: {', '.join(data['languages'])}\nTop repos:\n" + "\n".join(lines))

@tool
def get_skills_for_role_tool(role: str) -> str:
    """Returns the top technical skills required for a given job role."""
    result = ask_llm(f"List the top 8-10 technical skills required for a '{role}' role in 2026. Reply with ONLY a comma-separated list, no explanation.")
    return f"Skills needed for {role}: {result}"

def ask_agent(query: str, tools=None, return_trace=False):
    """Lets the LLM decide whether/which tool to call, rather than a hardcoded call path — genuinely agentic."""
    tools = tools or [analyze_github_tool, get_skills_for_role_tool]
    try:
        agent = create_react_agent(llm, tools)
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        if return_trace:
            trace = []
            for m in result["messages"]:
                calls = getattr(m, "tool_calls", None)
                if calls:
                    for c in calls:
                        trace.append(f"🔧 Called `{c['name']}` with {c['args']}")
            return result["messages"][-1].content, trace
        return result["messages"][-1].content
    except Exception as e:
        return (f"ERROR: {str(e)}", []) if return_trace else f"ERROR: {str(e)}"

SKILL_SYNONYMS = {
    "machine learning": {"ml", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "xgboost"},
    "deep learning": {"tensorflow", "pytorch", "keras", "neural networks", "cnn", "rnn"},
    "nlp": {"natural language processing", "spacy", "nltk", "transformers", "huggingface", "langchain"},
    "web development": {"html", "css", "javascript", "react", "django", "flask", "fastapi", "node.js"},
    "backend": {"fastapi", "flask", "django", "node.js", "express", "spring boot"},
    "frontend": {"react", "vue", "angular", "html", "css", "javascript"},
    "cloud": {"aws", "gcp", "azure", "docker", "kubernetes"},
    "devops": {"docker", "kubernetes", "ci/cd", "jenkins", "github actions"},
    "database": {"sql", "mysql", "postgresql", "mongodb", "sqlite", "redis"},
    "data science": {"pandas", "numpy", "scikit-learn", "matplotlib", "jupyter"},
    "version control": {"git", "github", "gitlab"},
}

def _expand_synonyms(skill: str) -> set:
    """Curated alias dictionary, not an LLM guess — same computed-not-guessed standard as everything else."""
    skill = skill.lower().strip()
    related = {skill}
    for key, group in SKILL_SYNONYMS.items():
        if skill == key or skill in group:
            related |= group | {key}
    return related

def _skill_matches(claimed_skill: str, evidence_set: set) -> bool:
    for candidate in _expand_synonyms(claimed_skill):
        for e in evidence_set:
            if candidate == e or (len(candidate) > 3 and (candidate in e or e in candidate)):
                return True
    return False

def compute_overlap(claimed: list, evidence: list) -> dict:
    """Set overlap with synonym/substring fuzzy matching — 'machine learning' now correctly matches
    'scikit-learn' on GitHub instead of being wrongly flagged as unverified."""
    claimed_set, evidence_set = set(claimed), set(evidence)
    verified = sorted(c for c in claimed_set if _skill_matches(c, evidence_set))
    unverified = sorted(claimed_set - set(verified))
    extra = sorted(evidence_set - claimed_set)
    score = round((len(verified) / len(claimed_set)) * 100) if claimed_set else 0
    return {"verified": verified, "unverified": unverified, "extra": extra, "score": score}

def compute_devpath_score(state):
    """Weighted average of whatever metrics have actually been computed so far.
    Weights: Portfolio 35%, ATS 25%, Credibility 20%, Job Match 20% — renormalized
    over only the components available, so an incomplete run doesn't unfairly tank the score."""
    weights = {}
    if state.portfolio: weights["Portfolio"] = (state.portfolio["portfolio_score"], 0.35)
    if state.ats_score is not None: weights["ATS"] = (state.ats_score, 0.25)
    if state.reality_check: weights["Credibility"] = (state.reality_check["score"], 0.20)
    if state.job_match: weights["Job Match"] = (state.job_match["score"], 0.20)
    if not weights:
        return None
    total_w = sum(w for _, w in weights.values())
    score = round(sum(v * w for v, w in weights.values()) / total_w)
    return {"score": score, "components": weights}

def career_level(score: int) -> str:
    if score < 40: return "Beginner"
    if score < 60: return "Emerging"
    if score < 80: return "Industry Ready"
    return "Competitive Candidate"

# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════
for key in ["resume_text", "resume_skills", "resume_analysis", "ats_score", "ats_checks", "github_data",
            "github_skills", "portfolio", "reality_check", "job_match", "roadmap_progress", "skill_coverage"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.roadmap_progress is None:
    st.session_state.roadmap_progress = {}

# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR NAV
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding: 8px 0 24px;">
        <div style="width:38px; height:38px; border-radius:11px;
             background:linear-gradient(135deg,#6366F1,#8B5CF6);
             display:flex; align-items:center; justify-content:center; font-size:18px;">⚡</div>
        <div style="font-size:19px; font-weight:800; color:white; letter-spacing:-0.5px;">DevPath</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠  Dashboard",
        "🤖  Auto-Pilot",
        "📄  Resume Intelligence",
        "🐙  GitHub Intelligence",
        "🌉  Reality Check",
        "💼  Job Match",
        "🎯  Roadmap",
        "🔍  Opportunities",
        "💬  Career Chat",
    ], label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("⚡ DevPath · Agentic Arena 2026\nCh. Satyanand · ALIET Vijayawada")

# ══════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    st.markdown(f"### Good {'morning' if datetime.now().hour < 12 else 'afternoon'} 👋")
    st.caption("Here's your career intelligence snapshot.")

    devpath = compute_devpath_score(st.session_state)
    if devpath:
        level = career_level(devpath["score"])
        level_color = {"Beginner": "#F87171", "Emerging": "#FBBF24",
                       "Industry Ready": "#34D399", "Competitive Candidate": "#818CF8"}[level]
        col_score, col_chart = st.columns([1, 2])
        with col_score:
            st.markdown(f"""
            <div class="panel" style="text-align:center;">
                <div class="panel-desc">DEVPATH SCORE</div>
                <div style="font-size:52px; font-weight:800; color:white;">{devpath['score']}</div>
                <div style="display:inline-block; margin-top:6px; background:{level_color}22; color:{level_color};
                    border:1px solid {level_color}55; border-radius:20px; padding:5px 16px; font-size:13px; font-weight:700;">
                    {level}
                </div>
                <div class="metric-empty" style="margin-top:14px;">Weighted average of the metrics you've run — see breakdown →</div>
            </div>
            """, unsafe_allow_html=True)
        with col_chart:
            comps = devpath["components"]
            fig = go.Figure(go.Bar(
                x=[v[0] for v in comps.values()], y=list(comps.keys()), orientation="h",
                marker=dict(color=["#6366F1", "#34D399", "#F472B6", "#FBBF24"][:len(comps)]),
                text=[f"{v[0]}%  (weight {int(v[1]*100)}%)" for v in comps.values()], textposition="outside"
            ))
            fig.update_layout(
                height=220, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E8E8F5"), xaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run any analysis below (GitHub, Resume, Reality Check, or Job Match) to see your DevPath Score.")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "📊", "Portfolio Score", st.session_state.portfolio["portfolio_score"] if st.session_state.portfolio else None, "Run GitHub Intelligence", "#6366F1"),
        (c2, "🌉", "Credibility Score", st.session_state.reality_check["score"] if st.session_state.reality_check else None, "Run Reality Check", "#34D399"),
        (c3, "💼", "Job Match", st.session_state.job_match["score"] if st.session_state.job_match else None, "Run Job Match", "#F472B6"),
        (c4, "🐙", "Public Repos", st.session_state.github_data.get("public_repos") if st.session_state.github_data and "error" not in st.session_state.github_data else None, "Run GitHub Intelligence", "#FBBF24"),
    ]
    for col, icon, label, value, empty_hint, color in metrics:
        with col:
            val_html = f'<div class="metric-value">{value}{"%" if label != "Public Repos" else ""}</div>' if value is not None else f'<div class="metric-empty">Not run yet — {empty_hint}</div>'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon" style="background:{color}22; color:{color};">{icon}</div>
                <div class="metric-label">{label}</div>
                {val_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    colA, colB = st.columns([3, 2])
    with colA:
        st.markdown('<div class="panel"><div class="panel-title">📌 Recommended Actions</div><div class="panel-desc">Computed from whichever analyses you\'ve run so far.</div>', unsafe_allow_html=True)
        actions = []
        if st.session_state.portfolio:
            for w in st.session_state.portfolio["weaknesses"]:
                actions.append(f"Improve: {w}")
        if st.session_state.reality_check:
            for u in st.session_state.reality_check["unverified"][:3]:
                actions.append(f"Back up claimed skill with a project: {u}")
        if not actions:
            actions = ["Run GitHub Intelligence and Reality Check to get personalized actions here."]
        for a in actions[:6]:
            st.markdown(f"☐ {a}")
        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="panel"><div class="panel-title">🧭 Where to go next</div>', unsafe_allow_html=True)
        st.markdown("""
        1. **GitHub Intelligence** → get your Portfolio Score
        2. **Resume Intelligence** → upload resume, extract skills
        3. **Reality Check** → verify resume claims against GitHub
        4. **Job Match** → paste a JD, get a real match %
        5. **Roadmap** → build your 30-60-90 plan
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: AUTO-PILOT  (true agentic orchestration, not a fixed pipeline)
# ══════════════════════════════════════════════════════════════════════
elif page == "🤖  Auto-Pilot":
    st.markdown('<div class="panel"><div class="panel-title">🤖 Auto-Pilot</div><div class="panel-desc">Give it one goal. The agent decides which tools to call and in what order — this is where DevPath is genuinely agentic, not a fixed pipeline. If you\'ve already uploaded a resume this session, it can be pulled into Reality Check automatically.</div>', unsafe_allow_html=True)

    st.caption("Try: \"Analyze github.com/torvalds and tell me if they're ready for a Kernel Engineer role\" or \"Check my GitHub against my resume and suggest a roadmap to become an MLOps Engineer\" (mention your GitHub username in the goal).")
    goal = st.text_area("Your goal", height=100, label_visibility="collapsed",
                         placeholder="e.g. Analyze GitHub user satyanandh-ai, run a reality check against my resume, and tell me if I'm ready for an AI Engineer role.")

    if st.button("Run Auto-Pilot") and goal.strip():
        tools = [full_github_report_tool, reality_check_tool, roadmap_preview_tool, get_skills_for_role_tool]
        with st.spinner("Agent is planning and executing..."):
            answer, trace = ask_agent(goal, tools=tools, return_trace=True)
        if trace:
            st.markdown("**Agent execution trace**")
            for t in trace:
                st.caption(t)
        else:
            st.caption("Agent answered directly — decided no tool call was needed for this goal.")
        st.markdown("---")
        st.write(answer)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: RESUME INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page == "📄  Resume Intelligence":
    st.markdown('<div class="panel"><div class="panel-title">📄 Resume Intelligence</div><div class="panel-desc">Upload your resume for skill extraction, job-role suggestions, and ATS feedback.</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded and st.button("Analyze Resume"):
        with st.spinner("Extracting text..."):
            text = read_pdf(uploaded)
        if text.startswith("ERROR"):
            st.error(text)
        else:
            st.session_state.resume_text = text
            with st.spinner("Extracting skills..."):
                st.session_state.resume_skills = extract_skills_llm(text, "resume")
            with st.spinner("Scoring ATS compatibility..."):
                ats = compute_ats_score(text)
                st.session_state.ats_score = ats["score"]
                st.session_state.ats_checks = ats["checks"]
            with st.spinner("Generating analysis..."):
                prompt = f"""You are a resume expert. Analyze this resume and give:
1. JOB ROLES - top 5 roles this person can apply for now
2. IMPROVEMENTS - top 5 specific fixes

Resume:
{text}"""
                st.session_state.resume_analysis = ask_llm(prompt)
            st.success("Done.")

    if st.session_state.ats_score is not None:
        st.metric("ATS Score", f"{st.session_state.ats_score}/100")
        st.caption("Rule-based: checks for contact info, key sections, quantified impact, action verbs, and length — not an LLM opinion.")
        st.progress(st.session_state.ats_score / 100)
        st.markdown("".join(
            f'<span class="{"tag-good" if v else "tag-bad"}">{"✓" if v else "✗"} {k}</span>'
            for k, v in st.session_state.ats_checks.items()
        ), unsafe_allow_html=True)
    if st.session_state.resume_skills:
        st.markdown("**Extracted Skills**")
        st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.resume_skills), unsafe_allow_html=True)
    if st.session_state.resume_analysis:
        st.markdown("---")
        st.markdown(st.session_state.resume_analysis)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: GITHUB INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page == "🐙  GitHub Intelligence":
    st.markdown('<div class="panel"><div class="panel-title">🐙 GitHub Intelligence</div><div class="panel-desc">Portfolio Score is computed from real repo signals (deployment, docs, originality) — not an LLM guess.</div>', unsafe_allow_html=True)
    username = st.text_input("GitHub Username", placeholder="e.g. satyanandh-ai")
    if st.button("Analyze GitHub"):
        with st.spinner("Fetching profile..."):
            data = fetch_github(username)
        if "error" in data:
            st.error(data["error"])
        else:
            st.session_state.github_data = data
            with st.spinner("Extracting skill evidence from repos..."):
                skill_text = build_github_skill_text(data)
                extracted = extract_skills_llm(skill_text, "GitHub profile (repo names, descriptions, topics, languages)")
                # union with raw languages as a floor, in case extraction misses something obvious
                st.session_state.github_skills = sorted(set(extracted) | {l.lower() for l in data["languages"]})
            st.session_state.portfolio = compute_portfolio_signals(data)
            st.success("Done.")

    if st.session_state.portfolio and st.session_state.github_data and "error" not in st.session_state.github_data:
        p = st.session_state.portfolio
        gh = st.session_state.github_data
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Portfolio Score", f"{p['portfolio_score']}/100")
            st.progress(p['portfolio_score'] / 100)
            st.caption(f"{gh['public_repos']} public repos · {gh['followers']} followers")
        with col2:
            st.markdown("**Strengths**")
            st.markdown("".join(f'<span class="tag-good">✓ {s}</span>' for s in p["strengths"]) or "—", unsafe_allow_html=True)
            st.markdown("**Weaknesses**")
            st.markdown("".join(f'<span class="tag-bad">✗ {s}</span>' for s in p["weaknesses"]) or "—", unsafe_allow_html=True)

        st.markdown("**Portfolio Breakdown**")
        bd = p["breakdown"]
        fig = go.Figure(go.Bar(
            x=list(bd.values()), y=list(bd.keys()), orientation="h",
            marker=dict(color="#8B5CF6"), text=[f"{v}%" for v in bd.values()], textposition="outside"
        ))
        fig.update_layout(
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8E8F5"), xaxis=dict(range=[0, 115], gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig, use_container_width=True)

        if st.session_state.github_skills:
            st.markdown("**Skills Evidenced (from repo names, descriptions, topics & languages)**")
            st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.github_skills), unsafe_allow_html=True)

        st.markdown("**Top Repositories (ranked by computed signal score)**")
        for r in p["ranked_repos"][:5]:
            st.markdown(f"- **{r['name']}** — {r['score']}/{r['max']} · {'🚀 deployed' if r['deployed'] else 'not deployed'} · ⭐ {r['stars']}  \n  _{r['description'] or 'No description'}_")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: REALITY CHECK  (killer feature)
# ══════════════════════════════════════════════════════════════════════
elif page == "🌉  Reality Check":
    st.markdown('<div class="panel"><div class="panel-title">🌉 Resume ↔ GitHub Reality Check</div><div class="panel-desc">Credibility Score = verified skills ÷ claimed skills. A real formula, not an LLM opinion.</div>', unsafe_allow_html=True)

    if not st.session_state.resume_skills:
        st.warning("Run **Resume Intelligence** first to extract resume skills.")
    if not st.session_state.github_skills:
        st.warning("Run **GitHub Intelligence** first to extract GitHub evidence.")

    if st.session_state.resume_skills and st.session_state.github_skills is not None:
        if st.button("Run Reality Check"):
            with st.spinner("Comparing claims against evidence..."):
                overlap = compute_overlap(st.session_state.resume_skills, st.session_state.github_skills)
                rec_prompt = f"""Verified skills: {overlap['verified']}
Unverified (claimed but no GitHub evidence): {overlap['unverified']}
Give 2-3 sentences of specific, honest advice on closing the gap. Be direct."""
                overlap["recommendation"] = ask_llm(rec_prompt)
                st.session_state.reality_check = overlap
            st.success("Done.")

    if st.session_state.reality_check:
        rc = st.session_state.reality_check
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Credibility Score", f"{rc['score']}%")
            st.progress(rc['score'] / 100)
        with col2:
            st.markdown("**Verified (resume + GitHub agree)**")
            st.markdown("".join(f'<span class="tag-good">✓ {s}</span>' for s in rc["verified"]) or "None found", unsafe_allow_html=True)
            st.markdown("**Unverified (claimed, no GitHub evidence)**")
            st.markdown("".join(f'<span class="tag-bad">✗ {s}</span>' for s in rc["unverified"]) or "None", unsafe_allow_html=True)
            if rc["extra"]:
                st.markdown("**Bonus: on GitHub but not on resume**")
                st.markdown("".join(f'<span class="tag-neutral">+ {s}</span>' for s in rc["extra"]), unsafe_allow_html=True)
        st.markdown("**Recommendation**")
        st.write(rc["recommendation"])
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: JOB MATCH
# ══════════════════════════════════════════════════════════════════════
elif page == "💼  Job Match":
    st.markdown('<div class="panel"><div class="panel-title">💼 Job Description Match Engine</div><div class="panel-desc">Match % = resume skills that appear in the JD ÷ total JD skills required. Computed, not guessed.</div>', unsafe_allow_html=True)

    if not st.session_state.resume_skills:
        st.warning("Run **Resume Intelligence** first.")
    jd_text = st.text_area("Paste Job Description", height=180, placeholder="Paste the full job description here...")

    if st.session_state.resume_skills and jd_text.strip() and st.button("Run Match"):
        with st.spinner("Extracting JD requirements..."):
            jd_skills = extract_skills_llm(jd_text, "job description")
        with st.spinner("Computing match..."):
            overlap = compute_overlap(jd_skills, st.session_state.resume_skills)
            # here "claimed"=jd requirements, "evidence"=resume skills -> score = % of JD requirements the resume covers
            plan_prompt = f"""JD requires: {jd_skills}
Resume has: {st.session_state.resume_skills}
Missing: {overlap['unverified']}
Write a focused 2-week preparation plan to close the gaps. Be specific and actionable."""
            overlap["plan"] = ask_llm(plan_prompt)
            overlap["jd_skills"] = jd_skills
            st.session_state.job_match = overlap
        st.success("Done.")

    if st.session_state.job_match:
        jm = st.session_state.job_match
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Match Score", f"{jm['score']}%")
            st.progress(jm['score'] / 100)
        with col2:
            st.markdown("**Have**")
            st.markdown("".join(f'<span class="tag-good">✓ {s}</span>' for s in jm["verified"]) or "None", unsafe_allow_html=True)
            st.markdown("**Missing**")
            st.markdown("".join(f'<span class="tag-bad">✗ {s}</span>' for s in jm["unverified"]) or "None — full match!", unsafe_allow_html=True)
        st.markdown("**2-Week Action Plan**")
        st.write(jm["plan"])
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: ROADMAP
# ══════════════════════════════════════════════════════════════════════
elif page == "🎯  Roadmap":
    st.markdown('<div class="panel"><div class="panel-title">🎯 Career Roadmap</div><div class="panel-desc">Cross-references your GitHub skills against a target role for a 30-60-90 day plan, with progress tracking.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        gh_user = st.text_input("GitHub Username", value=(st.session_state.github_data or {}).get("username", ""))
    with col2:
        goal = st.text_input("Target Role", placeholder="e.g. MLOps Engineer")

    if st.button("Build Roadmap") and gh_user.strip() and goal.strip():
        with st.spinner("Fetching GitHub data..."):
            gdata = fetch_github(gh_user) if not st.session_state.github_data or st.session_state.github_data.get("username") != gh_user else st.session_state.github_data
        if "error" in gdata:
            st.error(gdata["error"])
        else:
            with st.spinner("Researching role requirements..."):
                role_skills_raw = ask_llm(f"List top 8-10 technical skills for a '{goal}' role in 2026. Comma-separated, no explanation.")
            with st.spinner("Building roadmap..."):
                known_skills = set((st.session_state.github_skills or []) + (st.session_state.resume_skills or []) + [l.lower() for l in gdata.get("languages", [])])
                role_skills = [s.strip().lower() for s in role_skills_raw.split(",") if s.strip()]
                coverage = {}
                for rs in role_skills:
                    if rs in known_skills:
                        coverage[rs] = 100
                    elif any(rs in k or k in rs for k in known_skills):
                        coverage[rs] = 50
                    else:
                        coverage[rs] = 0
                st.session_state.skill_coverage = coverage

                prompt = f"""Current GitHub languages/skills: {gdata['languages']}
Target role: {goal}
Required skills: {role_skills_raw}

Give:
1. SKILLS ALREADY HELD
2. SKILL GAPS
3. A 30-60-90 day plan as a numbered checklist (make each item short, one line)
4. FIRST STEP for today"""
                roadmap_text = ask_llm(prompt)
                st.session_state.roadmap = roadmap_text
        st.success("Roadmap ready.")

    if st.session_state.get("skill_coverage"):
        st.markdown("**Skill Readiness for this Role**")
        st.caption("100 = confirmed match, 50 = partial/related match found, 0 = not found in your resume or GitHub")
        cov = st.session_state.skill_coverage
        fig = go.Figure(go.Scatterpolar(
            r=list(cov.values()) + [list(cov.values())[0]],
            theta=list(cov.keys()) + [list(cov.keys())[0]],
            fill="toself", line=dict(color="#8B5CF6")
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
                       angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E8E8F5"), height=380,
            margin=dict(l=40, r=40, t=30, b=30), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    if st.session_state.get("roadmap"):
        st.write(st.session_state.roadmap)
        st.markdown("---")
        st.markdown("**Track your progress**")
        for i in range(1, 6):
            key = f"step_{i}"
            checked = st.checkbox(f"Milestone {i} completed", value=st.session_state.roadmap_progress.get(key, False), key=key)
            st.session_state.roadmap_progress[key] = checked
        done = sum(st.session_state.roadmap_progress.values())
        st.progress(done / 5)
        st.caption(f"{done}/5 milestones marked complete")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: OPPORTUNITIES  (real links, not fabricated matches)
# ══════════════════════════════════════════════════════════════════════
elif page == "🔍  Opportunities":
    st.markdown('<div class="panel"><div class="panel-title">🔍 Opportunities</div><div class="panel-desc">Real search links built from your skills — not fabricated listings or match percentages, since we can\'t verify live postings against your profile.</div>', unsafe_allow_html=True)

    skills = st.session_state.resume_skills or st.session_state.github_skills or []
    if not skills:
        st.warning("Run Resume or GitHub Intelligence first to personalize these searches.")
    else:
        query = "+".join(skills[:5])
        primary_lang = (st.session_state.github_data or {}).get("languages", ["python"])
        primary_lang = primary_lang[0].lower() if primary_lang else "python"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**💼 Jobs & Internships**")
            st.markdown(f"""
- 🔗 [LinkedIn Jobs — your top skills]({f"https://www.linkedin.com/jobs/search/?keywords={query}"})
- 🔗 [Indeed — your top skills]({f"https://www.indeed.com/jobs?q={query}"})
- 🔗 [Naukri — your top skills]({f"https://www.naukri.com/{query.replace('+', '-')}-jobs"})
- 🔗 [Internshala internships]({f"https://internshala.com/internships/keywords-{skills[0]}"})
- 🔗 [Wellfound (startup jobs)](https://wellfound.com/jobs)
            """)
        with col2:
            st.markdown("**🏆 Hackathons & Open Source**")
            st.markdown(f"""
- 🔗 [Devpost hackathons](https://devpost.com/hackathons)
- 🔗 [Unstop hackathons & competitions](https://unstop.com/hackathons)
- 🔗 [GitHub — good first issues in {primary_lang}]({f"https://github.com/search?q=label%3A%22good+first+issue%22+language%3A{primary_lang}&type=issues&state=open"})
- 🔗 [GitHub — help wanted in {primary_lang}]({f"https://github.com/search?q=label%3A%22help+wanted%22+language%3A{primary_lang}&type=issues&state=open"})
            """)
        st.caption("These are search queries pre-filled with your skills, not curated recommendations — click through to see what's actually live right now.")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: CAREER CHAT
# ══════════════════════════════════════════════════════════════════════
elif page == "💬  Career Chat":
    st.markdown('<div class="panel"><div class="panel-title">💬 Career Chat</div><div class="panel-desc">Agent-driven: it decides on its own whether to look up a GitHub profile or research role skills based on your question.</div>', unsafe_allow_html=True)
    q = st.text_area("Your question", height=120, label_visibility="collapsed",
                      placeholder="e.g. Look at github.com/torvalds and tell me what kind of developer he is\ne.g. What skills do I need for an MLOps role?")
    if st.button("Ask Agent") and q.strip():
        with st.spinner("Agent is reasoning..."):
            st.write(ask_agent(q))
    st.markdown("</div>", unsafe_allow_html=True)