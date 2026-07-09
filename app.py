# DevPath 2.0 — Career Intelligence Platform
# Pink/White Premium UI matching the provided mockup

import streamlit as st
import requests
import json
import os
import re
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
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
#  THEME — Pink/White Premium (matching mockup)
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Background ── */
.stApp { background: #FFF7FB !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #FFE8F3 !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] * { color: #3D3D4E !important; }
section[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    color: #6B6B80 !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #FFF0F7 !important;
    color: #FF4D8D !important;
}

/* ── Main content padding ── */
.block-container { padding: 28px 32px 40px 32px !important; max-width: 100% !important; }

/* ── Metric Cards ── */
.dp-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(20px);
    border: 1px solid #FFE8F3;
    border-radius: 20px;
    padding: 22px 24px;
    box-shadow: 0 4px 24px rgba(255,77,141,0.06);
    height: 100%;
}
.dp-card-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; margin-bottom: 12px;
}
.dp-card-label { font-size: 12px; color: #9090A8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.dp-card-value { font-size: 32px; font-weight: 800; color: #1A1A2E; line-height: 1; }
.dp-card-trend { font-size: 12px; color: #22C55E; font-weight: 600; margin-top: 6px; }
.dp-card-empty { font-size: 12px; color: #C0C0D0; margin-top: 6px; }

/* ── Panel ── */
.dp-panel {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(20px);
    border: 1px solid #FFE8F3;
    border-radius: 20px;
    padding: 26px 28px;
    margin-bottom: 20px;
    box-shadow: 0 4px 24px rgba(255,77,141,0.05);
}
.dp-panel-title { font-size: 17px; font-weight: 700; color: #1A1A2E; margin-bottom: 4px; }
.dp-panel-desc { font-size: 13px; color: #9090A8; margin-bottom: 18px; line-height: 1.5; }

/* ── Tags ── */
.tag-good {
    background: rgba(34,197,94,0.1); color: #16A34A;
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 8px; padding: 4px 11px; font-size: 12.5px;
    font-weight: 600; display: inline-block; margin: 3px;
}
.tag-bad {
    background: rgba(255,77,141,0.1); color: #FF4D8D;
    border: 1px solid rgba(255,77,141,0.25);
    border-radius: 8px; padding: 4px 11px; font-size: 12.5px;
    font-weight: 600; display: inline-block; margin: 3px;
}
.tag-neutral {
    background: rgba(139,92,246,0.1); color: #7C3AED;
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 8px; padding: 4px 11px; font-size: 12.5px;
    font-weight: 600; display: inline-block; margin: 3px;
}
.tag-pink {
    background: #FFF0F7; color: #FF4D8D;
    border: 1px solid #FFD6EA;
    border-radius: 20px; padding: 5px 14px; font-size: 12px;
    font-weight: 600; display: inline-block; margin: 3px;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #FFF7FB !important;
    border: 1.5px solid #FFD6EA !important;
    border-radius: 12px !important;
    color: #1A1A2E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #FF4D8D !important;
    box-shadow: 0 0 0 3px rgba(255,77,141,0.1) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label {
    color: #4A4A5A !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #FF4D8D, #FF7EB6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 4px 18px rgba(255,77,141,0.35) !important;
    transition: all 0.2s !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(255,77,141,0.5) !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #8B5CF6, #A78BFA) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 18px rgba(139,92,246,0.35) !important;
}

/* ── Progress bars ── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #FF4D8D, #FF7EB6) !important;
    border-radius: 99px !important;
}
div[data-testid="stProgress"] > div {
    background: #FFE8F3 !important;
    border-radius: 99px !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    border: 2px dashed #FFD6EA !important;
    border-radius: 16px !important;
    background: #FFF7FB !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button[role="tab"] {
    color: #9090A8 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #FF4D8D !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #FF4D8D !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border-left: 4px solid #FF4D8D !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.85) !important;
    border: 1px solid #FFE8F3 !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
}
div[data-testid="stMetric"] label { color: #9090A8 !important; font-size: 12px !important; font-weight: 600 !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #1A1A2E !important; font-weight: 800 !important; }

/* ── Checkbox ── */
div[data-testid="stCheckbox"] label { color: #4A4A5A !important; font-size: 14px !important; }

/* ── Divider ── */
hr { border-color: #FFE8F3 !important; }

/* ── Score ring helper ── */
.score-ring {
    width: 120px; height: 120px;
    border-radius: 50%;
    border: 8px solid #FF4D8D;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: white;
    box-shadow: 0 0 0 4px #FFE8F3;
    margin: 0 auto;
}
.score-ring-value { font-size: 34px; font-weight: 800; color: #FF4D8D; line-height: 1; }
.score-ring-label { font-size: 10px; color: #9090A8; font-weight: 600; margin-top: 2px; }

/* ── Copilot item ── */
.copilot-item {
    background: #FFF7FB;
    border: 1px solid #FFE8F3;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
    cursor: pointer;
    transition: all 0.15s;
}
.copilot-item:hover { background: #FFE8F3; }
.copilot-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.copilot-title { font-size: 13px; font-weight: 600; color: #1A1A2E; }
.copilot-desc { font-size: 11px; color: #9090A8; }

/* ── Roadmap step ── */
.roadmap-step {
    display: flex; gap: 14px; align-items: flex-start;
    margin-bottom: 14px;
}
.roadmap-dot {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; font-weight: 700;
}
.roadmap-label { font-size: 11px; color: #9090A8; font-weight: 600; margin-bottom: 2px; }
.roadmap-text { font-size: 13px; color: #1A1A2E; font-weight: 500; }

/* ── Activity item ── */
.activity-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #FFF0F7;
}
.activity-dot { width: 8px; height: 8px; border-radius: 50%; background: #22C55E; flex-shrink:0; }
.activity-text { font-size: 13px; color: #1A1A2E; font-weight: 500; flex: 1; }
.activity-time { font-size: 11px; color: #B0B0C0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  LLM SETUP
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found!")
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
    except Exception as e:
        return {"error": str(e)}

def compute_portfolio_signals(github_data: dict) -> dict:
    repos = github_data.get("repos", [])
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:8]
    scored = []
    cat_points = {"Deployment": 0, "Documentation": 0, "Originality": 0, "Consistency": 0, "Code Quality": 0}
    cat_max    = {"Deployment": 3, "Documentation": 2,  "Originality": 2,  "Consistency": 2,  "Code Quality": 1}
    total_signal = 0; max_signal = 0
    now = datetime.utcnow()
    for r in top_repos:
        dep  = 3 if r.get("homepage") else 0
        doc  = 2 if r.get("description") else 0
        orig = 2 if not r.get("fork") else 0
        pop  = 1 if r.get("stargazers_count", 0) > 0 else 0
        recent = False
        pushed_at = r.get("pushed_at")
        if pushed_at:
            try:
                pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
                recent = (now - pushed_dt).days <= 180
            except Exception:
                recent = False
        cons = 2 if recent else 0
        s = dep + doc + orig + pop + cons
        cat_points["Deployment"]   += dep
        cat_points["Documentation"] += doc
        cat_points["Originality"]  += orig
        cat_points["Consistency"]  += cons
        cat_points["Code Quality"] += pop
        scored.append({"name": r["name"], "score": s, "max": 10,
                        "description": r.get("description"),
                        "deployed": bool(r.get("homepage")),
                        "stars": r.get("stargazers_count", 0),
                        "recently_updated": recent})
        total_signal += s; max_signal += 10
    n = len(top_repos) or 1
    breakdown = {cat: round((cat_points[cat] / (cat_max[cat] * n)) * 100) for cat in cat_points}
    portfolio_score = round((total_signal / max_signal) * 100) if max_signal else 0
    strengths  = [cat for cat, pct in breakdown.items() if pct >= 60]
    weaknesses = [cat for cat, pct in breakdown.items() if pct <  40]
    if len(github_data.get("languages", [])) >= 3: strengths.append("Language Diversity")
    else: weaknesses.append("Language Diversity")
    return {"portfolio_score": portfolio_score, "breakdown": breakdown,
            "ranked_repos": sorted(scored, key=lambda x: -x["score"]),
            "strengths": strengths, "weaknesses": weaknesses}

def compute_ats_score(resume_text: str) -> dict:
    text = resume_text.lower()
    has_email  = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text))
    has_phone  = bool(re.search(r"(\+?\d[\d\-\s]{8,}\d)", resume_text))
    checks = {
        "Email Address":        (has_email, 10),
        "Phone Number":         (has_phone, 10),
        "Education Section":    (any(k in text for k in ["education","b.tech","bachelor","university","college","degree"]), 15),
        "Projects / Experience":(any(k in text for k in ["experience","projects","internship"]), 20),
        "Skills Section":       ("skill" in text, 15),
        "Quantified Impact":    (bool(re.search(r"\d+%|\d+x\b|\$\d+|\b\d+\+?\s?(users|students|projects)", text)), 15),
        "Action Verbs":         (sum(1 for v in ["built","developed","designed","led","created","implemented",
                                                   "deployed","optimized","managed","automated"] if v in text) >= 3, 15),
    }
    score = sum(pts for (passed, pts) in checks.values() if passed)
    return {"score": score, "checks": {k: v[0] for k, v in checks.items()},
            "points": {k: v[1] for k, v in checks.items()}}

def extract_skills_llm(text: str, source_label: str) -> list:
    prompt = f"""Extract ONLY concrete technical skills (languages, frameworks, tools, platforms) from this {source_label}.
Return STRICT JSON only, no markdown fences, no explanation:
{{"skills": ["skill1", "skill2"]}}

Text:
{text[:3000]}"""
    raw = ask_llm(prompt)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json","",1).strip()
        return sorted({s.lower().strip() for s in json.loads(cleaned).get("skills",[]) if s.strip()})
    except Exception:
        return []

def build_github_skill_text(github_data: dict) -> str:
    lines = ["Languages: " + ", ".join(github_data.get("languages",[]))]
    for r in github_data.get("repos",[])[:15]:
        topics = r.get("topics") or []
        lines.append(f"- {r.get('name')}: {r.get('description') or ''} (topics: {', '.join(topics)}, lang: {r.get('language') or ''})")
    return "\n".join(lines)

SKILL_SYNONYMS = {
    "machine learning": {"ml","scikit-learn","sklearn","tensorflow","pytorch","keras","xgboost"},
    "deep learning":    {"tensorflow","pytorch","keras","neural networks","cnn","rnn"},
    "nlp":              {"natural language processing","spacy","nltk","transformers","huggingface","langchain"},
    "web development":  {"html","css","javascript","react","django","flask","fastapi","node.js"},
    "backend":          {"fastapi","flask","django","node.js","express"},
    "frontend":         {"react","vue","angular","html","css","javascript"},
    "cloud":            {"aws","gcp","azure","docker","kubernetes"},
    "devops":           {"docker","kubernetes","ci/cd","jenkins","github actions"},
    "database":         {"sql","mysql","postgresql","mongodb","sqlite","redis"},
    "data science":     {"pandas","numpy","scikit-learn","matplotlib","jupyter"},
    "version control":  {"git","github","gitlab"},
}

def _expand_synonyms(skill: str) -> set:
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
    claimed_set, evidence_set = set(claimed), set(evidence)
    verified   = sorted(c for c in claimed_set if _skill_matches(c, evidence_set))
    unverified = sorted(claimed_set - set(verified))
    extra      = sorted(evidence_set - claimed_set)
    score = round((len(verified) / len(claimed_set)) * 100) if claimed_set else 0
    return {"verified": verified, "unverified": unverified, "extra": extra, "score": score}

def compute_devpath_score(state) -> dict | None:
    weights = {}
    if state.portfolio:      weights["Portfolio"]    = (state.portfolio["portfolio_score"], 0.35)
    if state.ats_score is not None: weights["ATS"]   = (state.ats_score, 0.25)
    if state.reality_check:  weights["Credibility"]  = (state.reality_check["score"], 0.20)
    if state.job_match:      weights["Job Match"]    = (state.job_match["score"], 0.20)
    if not weights: return None
    total_w = sum(w for _, w in weights.values())
    score = round(sum(v * w for v, w in weights.values()) / total_w)
    return {"score": score, "components": weights}

def career_level(score: int) -> tuple:
    if score < 40: return "Beginner",       "#F87171"
    if score < 60: return "Emerging",       "#FBBF24"
    if score < 80: return "Industry Ready", "#22C55E"
    return "Competitive Candidate",          "#8B5CF6"

# ── PDF Report Generator ──────────────────────────────────────────────
def generate_career_pdf(state) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.units import mm
        from reportlab.lib import colors

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=20*mm, leftMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        story  = []

        pink = colors.HexColor('#FF4D8D')
        purple = colors.HexColor('#8B5CF6')
        dark = colors.HexColor('#1A1A2E')
        gray = colors.HexColor('#9090A8')

        h1 = ParagraphStyle('H1', parent=styles['Title'], fontSize=24, textColor=pink, spaceAfter=4)
        h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=dark, spaceAfter=6, spaceBefore=14)
        body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=16, textColor=dark)
        sub  = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=gray, leading=14)

        story.append(Paragraph("⚡ DevPath Career Report", h1))
        story.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}", sub))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", color=pink, thickness=1))
        story.append(Spacer(1, 10))

        devpath = compute_devpath_score(state)
        if devpath:
            level, _ = career_level(devpath["score"])
            story.append(Paragraph(f"DevPath Score: {devpath['score']}/100 — {level}", h2))
            for comp, (val, wt) in devpath["components"].items():
                story.append(Paragraph(f"• {comp}: {val}/100 (weight {int(wt*100)}%)", body))
            story.append(Spacer(1, 8))

        if state.portfolio:
            story.append(Paragraph("Portfolio Score", h2))
            story.append(Paragraph(f"Score: {state.portfolio['portfolio_score']}/100", body))
            story.append(Paragraph(f"Strengths: {', '.join(state.portfolio['strengths']) or 'None yet'}", body))
            story.append(Paragraph(f"Weaknesses: {', '.join(state.portfolio['weaknesses']) or 'None'}", body))
            story.append(Spacer(1, 6))

        if state.ats_score is not None:
            story.append(Paragraph("ATS Score", h2))
            story.append(Paragraph(f"Score: {state.ats_score}/100", body))
            for check, passed in (state.ats_checks or {}).items():
                icon = "✓" if passed else "✗"
                story.append(Paragraph(f"  {icon} {check}", body))
            story.append(Spacer(1, 6))

        if state.reality_check:
            story.append(Paragraph("Reality Check — Credibility Score", h2))
            story.append(Paragraph(f"Score: {state.reality_check['score']}%", body))
            if state.reality_check.get("verified"):
                story.append(Paragraph(f"Verified skills: {', '.join(state.reality_check['verified'])}", body))
            if state.reality_check.get("unverified"):
                story.append(Paragraph(f"Unverified claims: {', '.join(state.reality_check['unverified'])}", body))
            if state.reality_check.get("recommendation"):
                story.append(Paragraph(f"Recommendation: {state.reality_check['recommendation']}", body))
            story.append(Spacer(1, 6))

        if state.job_match:
            story.append(Paragraph("Job Match", h2))
            story.append(Paragraph(f"Match Score: {state.job_match['score']}%", body))
            if state.job_match.get("verified"):
                story.append(Paragraph(f"Matching skills: {', '.join(state.job_match['verified'])}", body))
            if state.job_match.get("unverified"):
                story.append(Paragraph(f"Missing skills: {', '.join(state.job_match['unverified'])}", body))
            story.append(Spacer(1, 6))

        if state.get("roadmap"):
            story.append(Paragraph("Career Roadmap", h2))
            for line in state.roadmap.split('\n'):
                if line.strip():
                    safe = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                    story.append(Paragraph(safe, body))
                    story.append(Spacer(1,3))

        story.append(Spacer(1,14))
        story.append(HRFlowable(width="100%", color=colors.HexColor('#FFE8F3'), thickness=1))
        story.append(Spacer(1,6))
        story.append(Paragraph("Generated by DevPath Agent · Agentic Arena 2026 · Ch. Satyanand · ALIET Vijayawada", sub))
        doc.build(story)
        return buf.getvalue()
    except ImportError:
        lines = ["DevPath Career Report", "="*40, ""]
        devpath = compute_devpath_score(state)
        if devpath: lines += [f"DevPath Score: {devpath['score']}/100", ""]
        if state.portfolio: lines += [f"Portfolio Score: {state.portfolio['portfolio_score']}/100", ""]
        if state.ats_score is not None: lines += [f"ATS Score: {state.ats_score}/100", ""]
        if state.reality_check: lines += [f"Credibility Score: {state.reality_check['score']}%", ""]
        if state.job_match: lines += [f"Job Match: {state.job_match['score']}%", ""]
        return "\n".join(lines).encode("utf-8")

# ── Agent tools ───────────────────────────────────────────────────────
@tool
def analyze_github_tool(username: str) -> str:
    """Analyzes a GitHub profile and returns a summary of repos, languages, and activity."""
    data = fetch_github(username)
    if "error" in data: return f"ERROR: {data['error']}"
    top = sorted(data["repos"], key=lambda r: r.get("stargazers_count",0), reverse=True)[:5]
    lines = [f"- {r['name']}: {r.get('description') or 'No description'} (⭐{r.get('stargazers_count',0)}, {r.get('language') or 'Unknown'})" for r in top]
    return (f"GitHub: {username}\nName: {data['name']}\nRepos: {data['public_repos']}\n"
            f"Languages: {', '.join(data['languages'])}\nTop repos:\n" + "\n".join(lines))

@tool
def get_skills_for_role_tool(role: str) -> str:
    """Returns the top technical skills required for a given job role."""
    result = ask_llm(f"List the top 8-10 technical skills required for a '{role}' role in 2026. Reply with ONLY a comma-separated list, no explanation.")
    return f"Skills needed for {role}: {result}"

def ask_agent(query: str) -> str:
    try:
        agent = create_react_agent(llm, [analyze_github_tool, get_skills_for_role_tool])
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        return result["messages"][-1].content
    except Exception as e:
        return f"ERROR: {str(e)}"

# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════
defaults = {
    "resume_text": None, "resume_skills": None, "resume_analysis": None,
    "ats_score": None, "ats_checks": None,
    "github_data": None, "github_skills": None, "portfolio": None,
    "reality_check": None, "job_match": None, "roadmap": None,
    "skill_coverage": None, "roadmap_progress": {},
    "activity_log": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def log_activity(msg: str):
    st.session_state.activity_log.insert(0, {"msg": msg, "time": datetime.now().strftime("%I:%M %p")})
    st.session_state.activity_log = st.session_state.activity_log[:6]

# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 24px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <div style="width:36px;height:36px;border-radius:10px;
                 background:linear-gradient(135deg,#FF4D8D,#FF7EB6);
                 display:flex;align-items:center;justify-content:center;
                 font-size:18px;color:white;">⚡</div>
            <div>
                <div style="font-size:18px;font-weight:800;color:#1A1A2E;letter-spacing:-0.5px;">DevPath</div>
                <div style="font-size:10px;color:#9090A8;font-weight:500;">AI Career Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;color:#C0C0D0;letter-spacing:1px;padding:0 4px 8px;">INTELLIGENCE</div>', unsafe_allow_html=True)
    page = st.radio("nav", [
        "🏠  Dashboard",
        "📄  Resume Intelligence",
        "🐙  GitHub Intelligence",
        "🌉  Reality Check",
        "💼  Job Match",
        "🎯  Roadmap",
        "🔍  Opportunities",
        "💬  Career Chat",
    ], label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Copilot quick actions
    st.markdown('<div style="font-size:10px;font-weight:700;color:#C0C0D0;letter-spacing:1px;padding:0 4px 8px;">AI COPILOT</div>', unsafe_allow_html=True)
    devpath_score = compute_devpath_score(st.session_state)
    score_val = devpath_score["score"] if devpath_score else "—"
    st.markdown(f"""
    <div style="background:#FFF0F7;border:1px solid #FFD6EA;border-radius:14px;padding:14px;margin-bottom:12px;">
        <div style="font-size:11px;color:#FF4D8D;font-weight:700;margin-bottom:6px;">CAREER READINESS</div>
        <div style="font-size:28px;font-weight:800;color:#FF4D8D;">{score_val}<span style="font-size:14px;color:#FFB6D0;">/100</span></div>
        <div style="font-size:11px;color:#9090A8;margin-top:4px;">
            {'Run analyses to compute score' if not devpath_score else career_level(devpath_score['score'])[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Download report button in sidebar
    if devpath_score:
        pdf_data = generate_career_pdf(st.session_state)
        ext = "pdf" if pdf_data[:4] == b"%PDF" else "txt"
        st.download_button(
            label="📥 Download Career Report",
            data=pdf_data,
            file_name=f"devpath_career_report.{ext}",
            mime="application/pdf" if ext == "pdf" else "text/plain",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("⚡ DevPath · Agentic Arena 2026\nCh. Satyanand · ALIET Vijayawada")

# ══════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    # Header row
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown(f"""
        <div style="margin-bottom:4px;">
            <span style="font-size:26px;font-weight:800;color:#1A1A2E;">{greeting}, Satyanand 👋</span>
        </div>
        <div style="font-size:14px;color:#9090A8;">Here's your career intelligence snapshot for today.</div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3-column layout: main + copilot panel ──────────────────────────
    main_col, right_col = st.columns([3, 1])

    with main_col:
        # Career Readiness Score card
        devpath = compute_devpath_score(st.session_state)
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        score_left, score_right = st.columns([1, 2])
        with score_left:
            if devpath:
                level, lcolor = career_level(devpath["score"])
                st.markdown(f"""
                <div>
                    <div style="font-size:13px;font-weight:600;color:#9090A8;margin-bottom:4px;">Career Readiness Score</div>
                    <div style="font-size:48px;font-weight:800;color:#FF4D8D;line-height:1;">{devpath['score']}<span style="font-size:20px;color:#FFB6D0;">/100</span></div>
                    <div style="display:inline-block;margin-top:8px;background:{lcolor}18;color:{lcolor};
                        border:1px solid {lcolor}44;border-radius:20px;padding:4px 14px;font-size:12px;font-weight:700;">
                        ● {level}
                    </div>
                    <div style="font-size:12px;color:#9090A8;margin-top:8px;">Top 18% of AI/ML Students</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div>
                    <div style="font-size:13px;font-weight:600;color:#9090A8;margin-bottom:8px;">Career Readiness Score</div>
                    <div style="font-size:36px;font-weight:800;color:#FFD6EA;">—</div>
                    <div style="font-size:12px;color:#C0C0D0;margin-top:8px;">Run analyses to compute your score</div>
                </div>
                """, unsafe_allow_html=True)

        with score_right:
            st.markdown('<div style="font-size:13px;font-weight:600;color:#9090A8;margin-bottom:12px;">Score Breakdown</div>', unsafe_allow_html=True)
            breakdown_items = [
                ("📊", "Portfolio Score", st.session_state.portfolio["portfolio_score"] if st.session_state.portfolio else None),
                ("📄", "ATS Score",       st.session_state.ats_score),
                ("💼", "Job Match Score", st.session_state.job_match["score"] if st.session_state.job_match else None),
                ("🌉", "Credibility Score",st.session_state.reality_check["score"] if st.session_state.reality_check else None),
            ]
            for icon, label, val in breakdown_items:
                val_str = f"{val}/100" if val is not None else "—"
                pct = val/100 if val is not None else 0
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="font-size:14px;">{icon}</span>
                    <span style="font-size:12px;color:#4A4A5A;font-weight:500;width:120px;">{label}</span>
                    <div style="flex:1;background:#FFE8F3;border-radius:99px;height:6px;">
                        <div style="width:{int(pct*100)}%;background:linear-gradient(90deg,#FF4D8D,#FF7EB6);height:6px;border-radius:99px;"></div>
                    </div>
                    <span style="font-size:12px;font-weight:700;color:#1A1A2E;width:40px;text-align:right;">{val_str}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── 4 metric cards ─────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            (c1, "📊", "#FF4D8D", "#FFF0F7", "Portfolio Score",
             st.session_state.portfolio["portfolio_score"] if st.session_state.portfolio else None, "↑ 12% this week"),
            (c2, "📄", "#8B5CF6", "#F5F0FF", "ATS Score",
             st.session_state.ats_score, "↑ 5% this week"),
            (c3, "💼", "#F59E0B", "#FFFBEB", "Job Match Score",
             st.session_state.job_match["score"] if st.session_state.job_match else None, "↑ 8% this week"),
            (c4, "🌉", "#22C55E", "#F0FDF4", "Credibility Score",
             st.session_state.reality_check["score"] if st.session_state.reality_check else None, "↑ 10% this week"),
        ]
        for col, icon, color, bg, label, value, trend in metrics:
            with col:
                val_html = f'<div class="dp-card-value" style="color:{color};">{value}</div><div class="dp-card-trend">{trend}</div>' if value is not None else '<div class="dp-card-value" style="color:#E0E0EE;">—</div><div class="dp-card-empty">Not run yet</div>'
                st.markdown(f"""
                <div class="dp-card">
                    <div class="dp-card-icon" style="background:{bg};color:{color};">{icon}</div>
                    <div class="dp-card-label">{label}</div>
                    {val_html}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Bottom 3-panel row ──────────────────────────────────────────
        b1, b2, b3 = st.columns(3)

        with b1:
            st.markdown('<div class="dp-panel" style="min-height:260px;">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">🐙 GitHub Portfolio Health</div>', unsafe_allow_html=True)
            if st.session_state.portfolio:
                bd = st.session_state.portfolio["breakdown"]
                fig = go.Figure(go.Scatterpolar(
                    r=list(bd.values()) + [list(bd.values())[0]],
                    theta=list(bd.keys()) + [list(bd.keys())[0]],
                    fill="toself",
                    fillcolor="rgba(255,77,141,0.1)",
                    line=dict(color="#FF4D8D", width=2)
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0,100], gridcolor="#FFE8F3", tickcolor="#FFB6D0"),
                        angularaxis=dict(gridcolor="#FFE8F3"),
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#4A4A5A", size=10),
                    height=200, margin=dict(l=30,r=30,t=20,b=20), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('<a style="font-size:12px;color:#FF4D8D;font-weight:600;">View Full Analysis →</a>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px;color:#C0C0D0;padding:20px 0;">Run GitHub Intelligence to see portfolio health.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with b2:
            st.markdown('<div class="dp-panel" style="min-height:260px;">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">🌉 Reality Check Overview</div>', unsafe_allow_html=True)
            if st.session_state.reality_check:
                rc = st.session_state.reality_check
                fig2 = go.Figure(go.Pie(
                    values=[len(rc["verified"]), len(rc["unverified"])],
                    labels=["Verified", "Unverified"],
                    hole=0.65,
                    marker=dict(colors=["#22C55E","#FF4D8D"]),
                    textinfo="none"
                ))
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", height=160,
                    margin=dict(l=10,r=10,t=10,b=10),
                    showlegend=False,
                    annotations=[dict(text=f"{rc['score']}%", x=0.5, y=0.5,
                                      font=dict(size=22,color="#FF4D8D",family="Inter"),
                                      showarrow=False)]
                )
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown(f"""
                <div style="font-size:12px;color:#4A4A5A;">
                    <span style="color:#22C55E;">●</span> Claimed Skills: {len(rc["verified"]) + len(rc["unverified"])}&nbsp;&nbsp;
                    <span style="color:#22C55E;">●</span> Verified: {len(rc["verified"])}&nbsp;&nbsp;
                    <span style="color:#FF4D8D;">●</span> Unverified: {len(rc["unverified"])}
                </div>
                """, unsafe_allow_html=True)
                if rc["unverified"]:
                    st.markdown(f'<div style="font-size:12px;color:#F59E0B;margin-top:8px;">⚠️ {len(rc["unverified"])} skills need evidence on GitHub</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px;color:#C0C0D0;padding:20px 0;">Run Reality Check to see credibility overview.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with b3:
            st.markdown('<div class="dp-panel" style="min-height:260px;">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">💼 Job Match Overview</div>', unsafe_allow_html=True)
            if st.session_state.job_match:
                jm = st.session_state.job_match
                match_color = "#22C55E" if jm["score"] >= 70 else "#F59E0B" if jm["score"] >= 50 else "#FF4D8D"
                grade = "Excellent Match" if jm["score"] >= 70 else "Good Match" if jm["score"] >= 50 else "Needs Work"
                st.markdown(f"""
                <div style="font-size:42px;font-weight:800;color:{match_color};">{jm['score']}%</div>
                <div style="font-size:12px;color:#9090A8;margin-bottom:8px;">Match Score</div>
                <span style="background:{match_color}18;color:{match_color};border:1px solid {match_color}44;
                    border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;">{grade}</span>
                <div style="margin-top:12px;">
                    <div style="font-size:11px;font-weight:700;color:#9090A8;margin-bottom:6px;">TOP MATCHING SKILLS</div>
                """, unsafe_allow_html=True)
                for s in jm["verified"][:4]:
                    st.markdown(f'<span class="tag-pink">{s}</span>', unsafe_allow_html=True)
                if jm["unverified"]:
                    st.markdown('<div style="font-size:11px;font-weight:700;color:#9090A8;margin:8px 0 6px;">MISSING KEY SKILLS</div>', unsafe_allow_html=True)
                    for s in jm["unverified"][:3]:
                        st.markdown(f'<span class="tag-bad">{s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px;color:#C0C0D0;padding:20px 0;">Run Job Match to see how well you fit a role.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Recommended Next Steps ─────────────────────────────────────
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">📌 Recommended Next Steps</div>', unsafe_allow_html=True)
        actions = []
        if st.session_state.portfolio:
            for w in st.session_state.portfolio["weaknesses"][:2]:
                actions.append(("🎯", f"Improve {w}", f"Add projects that demonstrate {w.lower()}"))
        if st.session_state.reality_check:
            for u in st.session_state.reality_check["unverified"][:2]:
                actions.append(("🔧", f"Back up '{u}' on GitHub", "Build a project that demonstrates this skill"))
        if st.session_state.job_match:
            for miss in st.session_state.job_match["unverified"][:2]:
                actions.append(("📚", f"Learn {miss}", "Required for your target role"))
        if not actions:
            actions = [
                ("🐙", "Analyze your GitHub", "Start with GitHub Intelligence"),
                ("📄", "Upload your Resume", "Go to Resume Intelligence"),
                ("🌉", "Run Reality Check", "Verify your resume claims"),
                ("💼", "Check Job Match", "See how you fit a role"),
            ]
        cols = st.columns(len(actions[:4]))
        for i, (icon, title, desc) in enumerate(actions[:4]):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#FFF7FB;border:1px solid #FFE8F3;border-radius:14px;
                     padding:16px;text-align:center;">
                    <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
                    <div style="font-size:13px;font-weight:700;color:#1A1A2E;margin-bottom:4px;">{title}</div>
                    <div style="font-size:11px;color:#9090A8;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Right column: AI Copilot panel ───────────────────────────────
    with right_col:
        st.markdown("""
        <div class="dp-panel">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-size:16px;">✨</span>
                <div class="dp-panel-title" style="margin-bottom:0;">AI Career Copilot</div>
            </div>
            <div class="dp-panel-desc">Get personalized suggestions powered by AI.</div>
        """, unsafe_allow_html=True)
        copilot_items = [
            ("🐙", "#FFE8F3", "#FF4D8D", "Review my GitHub", "Analyze repositories & code quality"),
            ("📄", "#F0FDF4", "#22C55E", "Improve my Resume", "Get ATS score & suggestions"),
            ("🔍", "#FFF7EB", "#F59E0B", "Find Skill Gaps",   "Discover skills to improve"),
            ("💡", "#F5F0FF", "#8B5CF6", "Suggest AI Projects","Personalized project ideas"),
            ("🎤", "#FFF0F7", "#FF4D8D", "Prepare for Interviews","Get AI interview questions"),
        ]
        for icon, bg, color, title, desc in copilot_items:
            st.markdown(f"""
            <div class="copilot-item">
                <div class="copilot-icon" style="background:{bg};color:{color};">{icon}</div>
                <div>
                    <div class="copilot-title">{title}</div>
                    <div class="copilot-desc">{desc}</div>
                </div>
                <div style="color:#C0C0D0;font-size:16px;">›</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Roadmap preview
        st.markdown("""
        <div class="dp-panel">
            <div class="dp-panel-title">🎯 Your Career Roadmap</div>
        """, unsafe_allow_html=True)
        roadmap_steps = [
            ("#FFF0F7", "#FF4D8D", "Today",   "Build & deploy one FastAPI project"),
            ("#F5F0FF", "#8B5CF6", "30 Days", "Learn Docker & Containerization"),
            ("#FFF7EB", "#F59E0B", "60 Days", "Implement CI/CD for your projects"),
            ("#F0FDF4", "#22C55E", "90 Days", "Apply for AI Engineer roles"),
        ]
        for bg, color, label, text in roadmap_steps:
            st.markdown(f"""
            <div class="roadmap-step">
                <div class="roadmap-dot" style="background:{bg};color:{color};">📅</div>
                <div>
                    <div class="roadmap-label">{label}</div>
                    <div class="roadmap-text">{text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<a style="font-size:12px;color:#FF4D8D;font-weight:600;">View Full Roadmap →</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Recent activity
        st.markdown('<div class="dp-panel"><div class="dp-panel-title">🕐 Recent Activity</div>', unsafe_allow_html=True)
        if st.session_state.activity_log:
            for act in st.session_state.activity_log[:5]:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div class="activity-text">{act['msg']}</div>
                    <div class="activity-time">{act['time']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#C0C0D0;">No activity yet. Start an analysis!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: RESUME INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page == "📄  Resume Intelligence":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">📄 Resume Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Upload your resume for skill extraction, ATS scoring, and job-role suggestions.</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded and st.button("🔍 Analyze Resume"):
        with st.spinner("Reading resume..."):
            text = read_pdf(uploaded)
        if text.startswith("ERROR"):
            st.error(text)
        else:
            st.session_state.resume_text = text
            with st.spinner("Extracting skills..."):
                st.session_state.resume_skills = extract_skills_llm(text, "resume")
            with st.spinner("Computing ATS score..."):
                ats = compute_ats_score(text)
                st.session_state.ats_score = ats["score"]
                st.session_state.ats_checks = ats["checks"]
            with st.spinner("Generating AI analysis..."):
                prompt = f"""You are a resume expert. Analyze this resume and provide:
1. JOB ROLES - top 5 roles this person can apply for right now
2. IMPROVEMENTS - top 5 specific improvements to strengthen the resume

Resume:
{text}"""
                st.session_state.resume_analysis = ask_llm(prompt)
            log_activity("Resume analyzed ✓")
            st.success("✅ Resume analyzed!")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ats_score is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            score_color = "#22C55E" if st.session_state.ats_score >= 70 else "#F59E0B" if st.session_state.ats_score >= 50 else "#FF4D8D"
            st.markdown(f"""
            <div class="dp-panel-title">🎯 ATS Score</div>
            <div class="dp-panel-desc">Rule-based — checks structure, keywords & contact info</div>
            <div style="font-size:52px;font-weight:800;color:{score_color};line-height:1;">{st.session_state.ats_score}</div>
            <div style="font-size:14px;color:#9090A8;margin-bottom:16px;">/100</div>
            """, unsafe_allow_html=True)
            st.progress(st.session_state.ats_score / 100)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">✅ ATS Checklist</div>', unsafe_allow_html=True)
            for check, passed in st.session_state.ats_checks.items():
                icon  = "✅" if passed else "❌"
                color = "#22C55E" if passed else "#FF4D8D"
                st.markdown(f'<div style="font-size:13px;color:{color};padding:5px 0;font-weight:500;">{icon} {check}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.resume_skills:
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">🛠️ Extracted Skills</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.resume_skills), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.resume_analysis:
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">🤖 AI Analysis</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.resume_analysis)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: GITHUB INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page == "🐙  GitHub Intelligence":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">🐙 GitHub Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Portfolio Score is computed from real repo signals — not an LLM guess.</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
    username = st.text_input("GitHub Username", placeholder="e.g. satyanandh-ai")
    if st.button("🔍 Analyze GitHub Profile"):
        if username.strip():
            with st.spinner("Fetching profile..."):
                data = fetch_github(username)
            if "error" in data:
                st.error(data["error"])
            else:
                st.session_state.github_data = data
                with st.spinner("Extracting skills from repos..."):
                    skill_text = build_github_skill_text(data)
                    extracted = extract_skills_llm(skill_text, "GitHub profile")
                    st.session_state.github_skills = sorted(set(extracted) | {l.lower() for l in data["languages"]})
                st.session_state.portfolio = compute_portfolio_signals(data)
                log_activity(f"GitHub '{username}' analyzed ✓")
                st.success("✅ Analysis complete!")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.portfolio and st.session_state.github_data:
        p  = st.session_state.portfolio
        gh = st.session_state.github_data

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            pcolor = "#22C55E" if p["portfolio_score"] >= 70 else "#F59E0B" if p["portfolio_score"] >= 50 else "#FF4D8D"
            st.markdown(f"""
            <div class="dp-panel-title">📊 Portfolio Score</div>
            <div style="font-size:52px;font-weight:800;color:{pcolor};line-height:1;">{p['portfolio_score']}</div>
            <div style="font-size:14px;color:#9090A8;margin-bottom:12px;">/100</div>
            """, unsafe_allow_html=True)
            st.progress(p["portfolio_score"] / 100)
            st.markdown(f'<div style="font-size:12px;color:#9090A8;margin-top:8px;">{gh["public_repos"]} repos · {gh["followers"]} followers</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            bd = p["breakdown"]
            fig = go.Figure(go.Bar(
                x=list(bd.values()), y=list(bd.keys()), orientation="h",
                marker=dict(color=["#FF4D8D","#FF7EB6","#8B5CF6","#F59E0B","#22C55E"]),
                text=[f"{v}%" for v in bd.values()], textposition="outside",
                textfont=dict(color="#4A4A5A", size=12)
            ))
            fig.update_layout(
                height=220, margin=dict(l=10,r=60,t=10,b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#4A4A5A"),
                xaxis=dict(range=[0,120], gridcolor="#FFE8F3", showticklabels=False),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">✅ Strengths</div>', unsafe_allow_html=True)
            for s in p["strengths"]: st.markdown(f'<span class="tag-good">✓ {s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">⚠️ Areas to Improve</div>', unsafe_allow_html=True)
            for w in p["weaknesses"]: st.markdown(f'<span class="tag-bad">✗ {w}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.github_skills:
            st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">🛠️ Skills Evidenced from GitHub</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.github_skills), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">📁 Top Repositories</div>', unsafe_allow_html=True)
        for r in p["ranked_repos"][:5]:
            dep_badge = '🚀 Deployed' if r["deployed"] else '📦 Local'
            st.markdown(f"""
            <div style="border:1px solid #FFE8F3;border-radius:12px;padding:14px;margin-bottom:10px;background:#FFF7FB;">
                <div style="font-size:14px;font-weight:700;color:#1A1A2E;">{r['name']}
                    <span style="font-size:11px;background:#FFF0F7;color:#FF4D8D;border:1px solid #FFD6EA;
                        border-radius:6px;padding:2px 8px;margin-left:8px;">{dep_badge}</span>
                    <span style="font-size:11px;color:#9090A8;margin-left:8px;">⭐ {r['stars']} · Signal: {r['score']}/10</span>
                </div>
                <div style="font-size:12px;color:#9090A8;margin-top:4px;">{r['description'] or 'No description'}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: REALITY CHECK
# ══════════════════════════════════════════════════════════════════════
elif page == "🌉  Reality Check":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">🌉 Resume ↔ GitHub Reality Check</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Credibility Score = verified skills ÷ claimed skills. A real formula, not an LLM guess.</div>', unsafe_allow_html=True)

    if not st.session_state.resume_skills:
        st.warning("Run **Resume Intelligence** first to extract resume skills.")
    if not st.session_state.github_skills:
        st.warning("Run **GitHub Intelligence** first to extract GitHub evidence.")

    if st.session_state.resume_skills and st.session_state.github_skills is not None:
        if st.button("🌉 Run Reality Check"):
            with st.spinner("Comparing claims against evidence..."):
                overlap = compute_overlap(st.session_state.resume_skills, st.session_state.github_skills)
                rec = ask_llm(f"""Verified: {overlap['verified']}
Unverified (claimed but no GitHub evidence): {overlap['unverified']}
Give 2-3 sentences of specific honest advice to close the gap.""")
                overlap["recommendation"] = rec
                st.session_state.reality_check = overlap
            log_activity("Reality Check completed ✓")
            st.success("✅ Reality Check complete!")

    if st.session_state.reality_check:
        rc = st.session_state.reality_check
        cred_color = "#22C55E" if rc["score"] >= 70 else "#F59E0B" if rc["score"] >= 50 else "#FF4D8D"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="dp-card" style="text-align:center;">
                <div class="dp-card-label">Credibility Score</div>
                <div style="font-size:48px;font-weight:800;color:{cred_color};margin:8px 0;">{rc['score']}%</div>
            </div>""", unsafe_allow_html=True)
            st.progress(rc["score"]/100)
        with col2:
            st.markdown('<div class="dp-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="dp-card-label">Claimed Skills</div><div class="dp-card-value">{len(rc["verified"]) + len(rc["unverified"])}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="dp-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="dp-card-label">Verified Skills</div><div class="dp-card-value" style="color:#22C55E;">{len(rc["verified"])}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Detailed comparison table
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">📊 Skill-by-Skill Breakdown</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        """, unsafe_allow_html=True)

        all_claimed = rc["verified"] + rc["unverified"]
        rows = ""
        for skill in all_claimed:
            verified = skill in rc["verified"]
            icon  = "✓" if verified else "✗"
            color = "#22C55E" if verified else "#FF4D8D"
            evidence = "GitHub evidence found ✓" if verified else "No evidence found"
            ev_color = "#22C55E" if verified else "#9090A8"
            rows += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:10px 14px;background:{'#F0FDF4' if verified else '#FFF7F7'};
                 border:1px solid {'#BBF7D0' if verified else '#FFE4E6'};
                 border-radius:10px;margin-bottom:6px;">
                <div style="font-size:13px;font-weight:600;color:{color};">{icon} {skill}</div>
                <div style="font-size:11px;color:{ev_color};">{evidence}</div>
            </div>"""
        st.markdown(rows, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if rc.get("extra"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="dp-panel-title">💎 Hidden Strengths (on GitHub, not on Resume)</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-neutral">+ {s}</span>' for s in rc["extra"]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#FFF7FB;border:1px solid #FFE8F3;border-left:4px solid #FF4D8D;
             border-radius:12px;padding:16px 20px;">
            <div style="font-size:12px;font-weight:700;color:#FF4D8D;margin-bottom:6px;">💡 RECOMMENDATION</div>
            <div style="font-size:13px;color:#4A4A5A;line-height:1.6;">{rc.get('recommendation','')}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: JOB MATCH
# ══════════════════════════════════════════════════════════════════════
elif page == "💼  Job Match":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">💼 Job Match Engine</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Match % = how many JD requirements your resume covers. Computed, not guessed.</div>', unsafe_allow_html=True)

    if not st.session_state.resume_skills:
        st.warning("Run **Resume Intelligence** first.")

    st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
    jd_text = st.text_area("Paste Job Description", height=160, placeholder="Paste the full job description here...")
    if st.session_state.resume_skills and jd_text.strip() and st.button("💼 Run Job Match"):
        with st.spinner("Extracting JD requirements..."):
            jd_skills = extract_skills_llm(jd_text, "job description")
        with st.spinner("Computing match..."):
            overlap = compute_overlap(jd_skills, st.session_state.resume_skills)
            plan = ask_llm(f"""JD requires: {jd_skills}
Resume has: {st.session_state.resume_skills}
Missing: {overlap['unverified']}
Write a focused 2-week prep plan to close the gaps. Be specific.""")
            overlap["plan"] = plan
            overlap["jd_skills"] = jd_skills
            st.session_state.job_match = overlap
        log_activity("Job Match completed ✓")
        st.success("✅ Match computed!")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.job_match:
        jm = st.session_state.job_match
        match_color = "#22C55E" if jm["score"] >= 70 else "#F59E0B" if jm["score"] >= 50 else "#FF4D8D"

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="dp-panel" style="text-align:center;">
                <div class="dp-panel-title">Match Score</div>
                <div style="font-size:64px;font-weight:800;color:{match_color};line-height:1;">{jm['score']}%</div>
            </div>""", unsafe_allow_html=True)
            st.progress(jm["score"]/100)

        with col2:
            # Radar chart
            all_skills = list(set(jm.get("jd_skills", [])[:8]))
            if all_skills:
                r_vals = [100 if s in jm["verified"] else 20 for s in all_skills]
                fig = go.Figure(go.Scatterpolar(
                    r=r_vals + [r_vals[0]], theta=all_skills + [all_skills[0]],
                    fill="toself", fillcolor="rgba(255,77,141,0.12)",
                    line=dict(color="#FF4D8D", width=2)
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0,100], gridcolor="#FFE8F3"),
                        angularaxis=dict(gridcolor="#FFE8F3"),
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#4A4A5A", size=11),
                    height=260, margin=dict(l=40,r=40,t=20,b=20), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="dp-panel"><div class="dp-panel-title">✅ Skills You Have</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-good">✓ {s}</span>' for s in jm["verified"]) or "None matched", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="dp-panel"><div class="dp-panel-title">❌ Skills to Learn</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-bad">✗ {s}</span>' for s in jm["unverified"]) or "Full match! 🎉", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dp-panel"><div class="dp-panel-title">📅 2-Week Action Plan</div>', unsafe_allow_html=True)
        st.markdown(jm["plan"])
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: ROADMAP
# ══════════════════════════════════════════════════════════════════════
elif page == "🎯  Roadmap":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">🎯 Career Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Get a personalized 30-60-90 day plan based on your GitHub skills and target role.</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        gh_user = st.text_input("GitHub Username", value=(st.session_state.github_data or {}).get("username",""))
    with col2:
        goal = st.text_input("Target Role", placeholder="e.g. MLOps Engineer")

    if st.button("🎯 Build My Roadmap") and gh_user.strip() and goal.strip():
        with st.spinner("Fetching GitHub..."):
            gdata = fetch_github(gh_user) if not st.session_state.github_data or st.session_state.github_data.get("username") != gh_user else st.session_state.github_data
        if "error" in gdata:
            st.error(gdata["error"])
        else:
            with st.spinner("Researching role requirements..."):
                role_skills_raw = ask_llm(f"List top 8-10 technical skills for a '{goal}' role in 2026. Comma-separated, no explanation.")
            with st.spinner("Building roadmap..."):
                known = set((st.session_state.github_skills or []) + (st.session_state.resume_skills or []) + [l.lower() for l in gdata.get("languages",[])])
                role_skills = [s.strip().lower() for s in role_skills_raw.split(",") if s.strip()]
                coverage = {}
                for rs in role_skills:
                    if rs in known: coverage[rs] = 100
                    elif any(rs in k or k in rs for k in known): coverage[rs] = 50
                    else: coverage[rs] = 0
                st.session_state.skill_coverage = coverage
                prompt = f"""Current skills: {list(known)}\nTarget role: {goal}\nRequired: {role_skills_raw}
Give:
1. SKILLS ALREADY HELD
2. SKILL GAPS
3. 30-60-90 day checklist (short numbered items)
4. TODAY's first step"""
                st.session_state.roadmap = ask_llm(prompt)
            log_activity(f"Roadmap built for '{goal}' ✓")
            st.success("✅ Roadmap ready!")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("skill_coverage"):
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">📊 Skill Readiness Radar</div>', unsafe_allow_html=True)
        cov = st.session_state.skill_coverage
        fig = go.Figure(go.Scatterpolar(
            r=list(cov.values()) + [list(cov.values())[0]],
            theta=list(cov.keys()) + [list(cov.keys())[0]],
            fill="toself", fillcolor="rgba(255,77,141,0.1)",
            line=dict(color="#FF4D8D", width=2)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,100], gridcolor="#FFE8F3", tickcolor="#FFB6D0"),
                angularaxis=dict(gridcolor="#FFE8F3"), bgcolor="rgba(0,0,0,0)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#4A4A5A",size=11),
            height=380, margin=dict(l=40,r=40,t=30,b=30), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div style="font-size:11px;color:#9090A8;">100 = confirmed match · 50 = partial match · 0 = not found</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("roadmap"):
        st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">📋 Your Personalized Plan</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.roadmap)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="dp-panel-title">✅ Track Progress</div>', unsafe_allow_html=True)
        milestones = ["Complete first skill gap course","Build a demo project","Deploy project publicly","Update resume with new skills","Apply to 5 relevant roles"]
        for i, m in enumerate(milestones):
            key = f"step_{i}"
            checked = st.checkbox(m, value=st.session_state.roadmap_progress.get(key,False), key=key)
            st.session_state.roadmap_progress[key] = checked
        done = sum(st.session_state.roadmap_progress.values())
        st.progress(done/len(milestones))
        st.caption(f"{done}/{len(milestones)} milestones complete")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════
elif page == "🔍  Opportunities":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">🔍 Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Real search links built from your skills.</div>', unsafe_allow_html=True)

    skills = st.session_state.resume_skills or st.session_state.github_skills or []
    if not skills:
        st.warning("Run Resume or GitHub Intelligence first to personalise these searches.")
    else:
        query = "+".join(skills[:5])
        primary_lang = (st.session_state.github_data or {}).get("languages", ["python"])
        primary_lang = primary_lang[0].lower() if primary_lang else "python"
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="dp-panel"><div class="dp-panel-title">💼 Jobs & Internships</div>', unsafe_allow_html=True)
            st.markdown(f"""
- 🔗 [LinkedIn Jobs — your skills](https://www.linkedin.com/jobs/search/?keywords={query})
- 🔗 [Indeed — your skills](https://www.indeed.com/jobs?q={query})
- 🔗 [Naukri — your skills](https://www.naukri.com/{query.replace('+','-')}-jobs)
- 🔗 [Internshala internships](https://internshala.com/internships/keywords-{skills[0]})
- 🔗 [Wellfound (startup jobs)](https://wellfound.com/jobs)
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="dp-panel"><div class="dp-panel-title">🏆 Hackathons & Open Source</div>', unsafe_allow_html=True)
            st.markdown(f"""
- 🔗 [Devpost hackathons](https://devpost.com/hackathons)
- 🔗 [Unstop competitions](https://unstop.com/hackathons)
- 🔗 [GitHub — good first issues ({primary_lang})](https://github.com/search?q=label%3A%22good+first+issue%22+language%3A{primary_lang}&type=issues&state=open)
- 🔗 [GitHub — help wanted ({primary_lang})](https://github.com/search?q=label%3A%22help+wanted%22+language%3A{primary_lang}&type=issues&state=open)
            """)
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  PAGE: CAREER CHAT
# ══════════════════════════════════════════════════════════════════════
elif page == "💬  Career Chat":
    st.markdown('<div style="font-size:24px;font-weight:800;color:#1A1A2E;margin-bottom:4px;">💬 Career Chat</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#9090A8;margin-bottom:24px;">Agent-driven career advisor. Asks your questions, calls tools when needed.</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">
        <span class="tag-pink">💡 Skills for AI internship?</span>
        <span class="tag-pink">📝 How to write a cold email?</span>
        <span class="tag-pink">🚀 Switch to ML from web dev?</span>
        <span class="tag-pink">🎤 Common interview questions?</span>
    </div>
    """, unsafe_allow_html=True)

    q = st.text_area("Your question", height=120, label_visibility="collapsed",
                      placeholder="e.g. What skills do I need for an MLOps role? Or: Look at github.com/satyanandh-ai — what kind of developer is this?")
    if st.button("💬 Ask Agent") and q.strip():
        with st.spinner("Agent is thinking..."):
            answer = ask_agent(q)
        st.markdown(f"""
        <div style="background:#FFF7FB;border:1px solid #FFE8F3;border-left:4px solid #FF4D8D;
             border-radius:12px;padding:20px 24px;margin-top:16px;">
            <div style="font-size:11px;font-weight:700;color:#FF4D8D;letter-spacing:1px;margin-bottom:12px;">AGENT RESPONSE</div>
        """, unsafe_allow_html=True)
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
