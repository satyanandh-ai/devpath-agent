# DevPath 3.0 — Career Intelligence Platform
# UI matching the provided mockup exactly

import streamlit as st
import requests
import json
import os
import re
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

# ══════════════════════════════════════════════════════════════════════
#  RAG ENGINE — imported from rag_engine.py (single source of truth)
# ══════════════════════════════════════════════════════════════════════
try:
    from rag_engine import rag as _rag_instance
    RAG_AVAILABLE = True
except Exception as _rag_err:
    RAG_AVAILABLE = False
    _rag_instance = None

@st.cache_resource(show_spinner=False)
def get_rag():
    """Initialize RAG once per session — cached, never re-seeded."""
    if not RAG_AVAILABLE or _rag_instance is None:
        return None
    _rag_instance.initialize()
    return _rag_instance

devpath_rag = get_rag()

st.set_page_config(
    page_title="DevPath — AI Career Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "⚡ DevPath — AI Career Intelligence Platform"
    }
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F8F7FF !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #F0EEF8 !important;
    min-width: 200px !important; max-width: 200px !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 13px !important; font-weight: 500 !important;
    padding: 9px 16px !important; border-radius: 10px !important;
    color: #6B6880 !important; display: block !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #FFF0F7 !important; color: #E91E63 !important;
}
.dp-card {
    background: #ffffff; border: 1px solid #F0EEF8;
    border-radius: 16px; padding: 20px 22px;
    box-shadow: 0 2px 12px rgba(120,100,200,0.06);
}
.dp-card-sm {
    background: #ffffff; border: 1px solid #F0EEF8;
    border-radius: 14px; padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(120,100,200,0.05);
}
.hero-banner {
    background: linear-gradient(135deg, #FFF0F7 0%, #F5F0FF 100%);
    border: 1px solid #F0EEF8; border-radius: 20px;
    padding: 28px 32px; overflow: hidden;
}
.section-title { font-size: 15px; font-weight: 700; color: #1E1E2E; margin-bottom: 4px; }
.section-sub { font-size: 12px; color: #9090A8; margin-bottom: 14px; }
.tag-good { background:rgba(34,197,94,0.1);color:#16A34A;border:1px solid rgba(34,197,94,0.2);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;display:inline-block;margin:3px; }
.tag-bad  { background:rgba(233,30,99,0.08);color:#E91E63;border:1px solid rgba(233,30,99,0.2);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;display:inline-block;margin:3px; }
.tag-neutral { background:rgba(139,92,246,0.08);color:#7C3AED;border:1px solid rgba(139,92,246,0.15);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;display:inline-block;margin:3px; }
.tag-pink { background:#FFF0F7;color:#E91E63;border:1px solid #FFD6EA;border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;display:inline-block;margin:3px; }
.tag-emerge { background:#F5F0FF;color:#7C3AED;border:1px solid #E0D9FF;border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;display:inline-block;margin:3px; }
.skill-row { margin-bottom: 10px; }
.skill-row-top { display:flex;justify-content:space-between;align-items:center;margin-bottom:5px; }
.skill-name { font-size:13px;font-weight:500;color:#1E1E2E; }
.skill-pct { font-size:12px;color:#9090A8; }
.skill-bar-track { height:6px;border-radius:99px;background:#F0EEF8; }
.activity-item { display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #F5F3FF; }
.activity-icon { width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0; }
.activity-text { font-size:13px;font-weight:500;color:#1E1E2E;flex:1; }
.activity-time { font-size:11px;color:#B0B0C0;white-space:nowrap; }
.gap-item { display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #F5F3FF; }
.company-pill { display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:12px;background:#F8F7FF;border:1px solid #F0EEF8;font-size:20px;margin:4px; }
.quote-block { background:linear-gradient(135deg,#FFF0F7,#F5F0FF);border-radius:16px;padding:20px 22px;border-left:4px solid #E91E63; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
    background:#FAFAFA !important; border:1.5px solid #EEE !important;
    border-radius:12px !important; color:#1E1E2E !important; font-size:14px !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
    border-color:#E91E63 !important; box-shadow:0 0 0 3px rgba(233,30,99,0.08) !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label { color:#4A4A5A !important; font-weight:600 !important; font-size:13px !important; }
div.stButton > button {
    background:linear-gradient(135deg,#E91E63,#F06292) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:11px 22px !important; font-weight:700 !important; font-size:14px !important;
    box-shadow:0 4px 16px rgba(233,30,99,0.3) !important; transition:all 0.2s !important;
}
div.stButton > button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(233,30,99,0.45) !important; }
div[data-testid="stDownloadButton"] button {
    background:linear-gradient(135deg,#7C3AED,#A78BFA) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:11px 22px !important; font-weight:700 !important;
}
div[data-testid="stProgress"] > div > div { background:linear-gradient(90deg,#E91E63,#F06292) !important; border-radius:99px !important; }
div[data-testid="stProgress"] > div { background:#F0EEF8 !important; border-radius:99px !important; }
div[data-testid="stFileUploader"] { border:2px dashed #E0D9FF !important; border-radius:14px !important; background:#FAFAFA !important; }
div[data-testid="stTabs"] button[role="tab"] { color:#9090A8 !important; font-weight:500 !important; font-size:13px !important; }
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color:#E91E63 !important; font-weight:700 !important; border-bottom:2px solid #E91E63 !important; }
div[data-testid="stAlert"] { border-radius:12px !important; }
hr { border-color:#F0EEF8 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def get_llm():
    groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not groq_key:
        st.error("❌ GROQ_API_KEY not found! Add it in Streamlit Secrets.")
        st.stop()
    return ChatGroq(model="qwen/qwen3.6-27b", api_key=groq_key)

llm = get_llm()

def ask_llm(prompt: str) -> str:
    try:
        return llm.invoke([HumanMessage(content=prompt)]).content
    except Exception as e:
        return f"ERROR: {str(e)}"

def ask_openai_direct(prompt: str, system: str = "") -> str:
    """Wrapper — uses Groq LLaMA for all calls."""
    return ask_llm(prompt)

ROLE_MARKET_DATA = {
    "AI Engineer": {
        "demand":"Very High","demand_trend":"↑ 42% YoY",
        "salary_india":"₹8L – ₹24L","salary_us":"$90K – $160K",
        "top_companies":["Google","OpenAI","Microsoft","Anthropic","Startups"],
        "skills":{"python":95,"git":90,"langchain":82,"llm integration":78,"fastapi":71,"docker":65,"sql":63,"pytorch":58,"aws":54,"kubernetes":42},
        "emerging":["RAG","LangGraph","Vector DBs","Prompt Eng."],
        "description":"Builds and maintains AI-powered products and APIs."
    },
    "ML Engineer": {
        "demand":"High","demand_trend":"↑ 31% YoY",
        "salary_india":"₹7L – ₹20L","salary_us":"$85K – $150K",
        "top_companies":["Amazon","Meta","Tesla","NVIDIA","Flipkart"],
        "skills":{"python":96,"pytorch":82,"tensorflow":74,"scikit-learn":78,"sql":70,"docker":68,"mlflow":52,"aws":60,"spark":45,"git":88},
        "emerging":["MLOps","RLHF","Distributed Training","Quantization"],
        "description":"Designs and trains ML models for production at scale."
    },
    "MLOps Engineer": {
        "demand":"Very High","demand_trend":"↑ 58% YoY",
        "salary_india":"₹10L – ₹28L","salary_us":"$100K – $170K",
        "top_companies":["Netflix","Uber","Airbnb","Databricks","Zomato"],
        "skills":{"docker":92,"kubernetes":85,"python":90,"ci/cd":82,"mlflow":75,"aws":78,"terraform":55,"git":92,"linux":80,"airflow":62},
        "emerging":["Feature Stores","Model Monitoring","LLMOps","Ray"],
        "description":"Bridges ML and DevOps — deploys, monitors, and scales ML pipelines."
    },
    "Data Scientist": {
        "demand":"High","demand_trend":"↑ 18% YoY",
        "salary_india":"₹6L – ₹18L","salary_us":"$80K – $140K",
        "top_companies":["McKinsey","BCG","Amazon","Walmart","PhonePe"],
        "skills":{"python":95,"sql":88,"pandas":90,"numpy":85,"scikit-learn":80,"statistics":82,"matplotlib":72,"git":80,"spark":48,"tableau":55},
        "emerging":["Causal AI","AutoML","LLM+Analytics","dbt"],
        "description":"Extracts insights from data using statistics, ML, and visualization."
    },
    "GenAI Engineer": {
        "demand":"Extremely High","demand_trend":"↑ 120% YoY",
        "salary_india":"₹12L – ₹35L","salary_us":"$110K – $200K",
        "top_companies":["OpenAI","Anthropic","Cohere","Hugging Face","Startups"],
        "skills":{"python":95,"langchain":90,"openai api":85,"prompt engineering":88,"rag":82,"vector databases":78,"fastapi":70,"docker":65,"langgraph":72,"git":88},
        "emerging":["Agentic AI","Multi-modal","Fine-tuning","LangGraph"],
        "description":"Builds products powered by large language models and generative AI."
    },
    "Backend Engineer": {
        "demand":"High","demand_trend":"↑ 22% YoY",
        "salary_india":"₹5L – ₹18L","salary_us":"$80K – $150K",
        "top_companies":["Google","Amazon","Razorpay","CRED","Swiggy"],
        "skills":{"python":80,"fastapi":75,"sql":85,"docker":78,"redis":65,"git":90,"postgresql":72,"aws":68,"linux":75,"rest api":88},
        "emerging":["GraphQL","gRPC","Event-Driven","Service Mesh"],
        "description":"Builds scalable APIs, databases, and server-side systems."
    },
    "Data Analyst": {
        "demand":"Medium-High","demand_trend":"↑ 14% YoY",
        "salary_india":"₹4L – ₹12L","salary_us":"$60K – $100K",
        "top_companies":["Deloitte","Accenture","Amazon","Meesho","Ola"],
        "skills":{"sql":95,"excel":85,"python":72,"tableau":68,"power bi":65,"pandas":70,"statistics":75,"git":55,"google sheets":60,"storytelling":70},
        "emerging":["AI Analytics","dbt","Looker","Streamlit"],
        "description":"Turns raw data into business insights using SQL, Excel, and BI tools."
    },
}

def get_closest_role(query: str):
    q=query.lower().strip()
    for role in ROLE_MARKET_DATA:
        if role.lower()==q: return role
    for role in ROLE_MARKET_DATA:
        if any(w in q for w in role.lower().split()): return role
    kw={"ai":"AI Engineer","ml":"ML Engineer","mlops":"MLOps Engineer","genai":"GenAI Engineer",
        "llm":"GenAI Engineer","data science":"Data Scientist","analyst":"Data Analyst","backend":"Backend Engineer"}
    for k,v in kw.items():
        if k in q: return v
    return None

def fetch_github(username: str) -> dict:
    try:
        ur=requests.get(f"https://api.github.com/users/{username}",timeout=10)
        if ur.status_code==404: return {"error":f"User '{username}' not found."}
        if ur.status_code!=200: return {"error":f"GitHub API error {ur.status_code}"}
        ud=ur.json()
        repos=requests.get(f"https://api.github.com/users/{username}/repos?per_page=100",timeout=10).json()
        if not isinstance(repos,list) or not repos: return {"error":"No public repos found."}
        languages=sorted({r.get("language") for r in repos if r.get("language")})
        return {"username":username,"name":ud.get("name","N/A"),"bio":ud.get("bio",""),
                "public_repos":len(repos),"followers":ud.get("followers",0),"languages":languages,"repos":repos}
    except Exception as e:
        return {"error":str(e)}

def compute_portfolio_signals(github_data: dict) -> dict:
    repos=github_data.get("repos",[])
    top=sorted(repos,key=lambda r:r.get("stargazers_count",0),reverse=True)[:8]
    cp={"Deployment":0,"Documentation":0,"Originality":0,"Consistency":0,"Code Quality":0}
    cm={"Deployment":3,"Documentation":2,"Originality":2,"Consistency":2,"Code Quality":1}
    scored=[]; ts=0; ms=0; now=datetime.utcnow()
    for r in top:
        dep=3 if r.get("homepage") else 0
        doc=2 if r.get("description") else 0
        orig=2 if not r.get("fork") else 0
        pop=1 if r.get("stargazers_count",0)>0 else 0
        recent=False
        if r.get("pushed_at"):
            try: recent=(now-datetime.strptime(r["pushed_at"],"%Y-%m-%dT%H:%M:%SZ")).days<=180
            except: pass
        cons=2 if recent else 0; s=dep+doc+orig+pop+cons
        for k,v in zip(cp.keys(),[dep,doc,orig,cons,pop]): cp[k]+=v
        scored.append({"name":r["name"],"score":s,"max":10,"description":r.get("description"),
                       "deployed":bool(r.get("homepage")),"stars":r.get("stargazers_count",0),"recently_updated":recent})
        ts+=s; ms+=10
    n=len(top) or 1
    bd={cat:round((cp[cat]/(cm[cat]*n))*100) for cat in cp}
    ps=round((ts/ms)*100) if ms else 0
    st2=[cat for cat,p in bd.items() if p>=60]; wk=[cat for cat,p in bd.items() if p<40]
    if len(github_data.get("languages",[]))>=3: st2.append("Language Diversity")
    else: wk.append("Language Diversity")
    return {"portfolio_score":ps,"breakdown":bd,"ranked_repos":sorted(scored,key=lambda x:-x["score"]),"strengths":st2,"weaknesses":wk}

def build_github_skill_text(gd: dict) -> str:
    lines=["Languages: "+", ".join(gd.get("languages",[]))]
    for r in gd.get("repos",[])[:15]:
        t=r.get("topics") or []
        lines.append(f"- {r.get('name')}: {r.get('description') or ''} (topics:{','.join(t)}, lang:{r.get('language') or ''})")
    return "\n".join(lines)

def compute_ats_score(resume_text: str) -> dict:
    text=resume_text.lower()
    has_email=bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+",resume_text))
    has_phone=bool(re.search(r"(\+?\d[\d\-\s]{8,}\d)",resume_text))
    has_linkedin="linkedin" in text; has_github="github" in text
    contact_score=sum([has_email*5,has_phone*4,has_linkedin*3,has_github*3])  # max 15 not 20
    sections={"Summary/Objective":any(k in text for k in ["summary","objective","about","profile","overview"]),
               "Education":any(k in text for k in ["education","b.tech","bachelor","university","college","degree"]),
               "Skills":any(k in text for k in ["skills","technologies","tech stack","tools"]),
               "Projects":any(k in text for k in ["project","built","developed","created"]),
               "Experience":any(k in text for k in ["experience","internship","work","employment"])}
    section_score=sum(sections.values())*4
    tech_kw=["python","java","javascript","react","node","sql","docker","kubernetes","aws","gcp","azure",
              "machine learning","deep learning","tensorflow","pytorch","pandas","numpy","git","api",
              "fastapi","flask","django","langchain","llm","nlp","data science","scikit","streamlit","mongodb","postgresql"]
    found_kw=[k for k in tech_kw if k in text]
    n=len(found_kw)
    if n<=3: skills_score=5
    elif n<=6: skills_score=10
    elif n<=10: skills_score=14
    elif n<=15: skills_score=17
    else: skills_score=20
    avs=["built","developed","designed","led","created","implemented","deployed","optimized","managed","automated","improved","reduced","increased","launched","trained"]
    vc=sum(1 for v in avs if v in text)
    if vc==0: vs=0
    elif vc<=2: vs=2
    elif vc<=4: vs=4
    elif vc<=7: vs=7
    elif vc<=10: vs=9
    else: vs=10
    qm=re.findall(r"\d+%|\d+x\b|\$\d+|\b\d+\+?\s?(users|students|projects|repos|accuracy|ms)",text)
    qc=len(qm)
    if qc==0: qs=0
    elif qc==1: qs=2
    elif qc==2: qs=5
    elif qc==3: qs=7
    else: qs=10
    kw_score=vs+qs
    wc=len(resume_text.split())
    if wc<150: ls=2
    elif wc<300: ls=6
    elif wc<=800: ls=10
    elif wc<=1200: ls=7
    else: ls=4
    hb=any(c in resume_text for c in ["•","●","▪","◦"])
    hd=bool(re.search(r"(20\d{2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",text))
    hc=bool(re.search(r"(?m)^[A-Z][A-Z\s]{3,}$",resume_text))
    fmt=min(17,ls+(3 if hb else 0)+(2 if hd else 0)+(2 if hc else 0))  # max 17, realistic
    total=min(92,contact_score+section_score+skills_score+kw_score+fmt)  # 92 max — realistic
    return {"score":total,"categories":{"Contact Info":{"score":contact_score,"max":20},"Resume Sections":{"score":section_score,"max":20},
            "Skills Coverage":{"score":skills_score,"max":20},"Keywords & Verbs":{"score":kw_score,"max":20},"Formatting & Length":{"score":fmt,"max":20}},
            "sections":sections,"found_keywords":found_kw,"has_email":has_email,"has_phone":has_phone,
            "has_linkedin":has_linkedin,"has_github_link":has_github,"word_count":wc,"verb_count":vc,"quant_count":qc}

# ══════════════════════════════════════════════════════════════════════
#  PHASE 1 — Resume Intelligence: robust skill extraction
# ══════════════════════════════════════════════════════════════════════

# ── Canonical skill normalization ───────────────────────────────────────
CANONICAL_SKILLS = {
    "scikit-learn": {"sklearn", "scikit learn", "scikit-learn", "scikitlearn"},
    "tensorflow": {"tensorflow", "tf"},
    "pytorch": {"pytorch", "torch"},
    "langchain": {"langchain", "lang chain"},
    "langgraph": {"langgraph", "lang graph"},
    "fastapi": {"fastapi", "fast api"},
    "postgresql": {"postgresql", "postgres", "psql"},
    "mongodb": {"mongodb", "mongo"},
    "machine learning": {"machine learning", "ml"},
    "deep learning": {"deep learning", "dl"},
    "natural language processing": {"nlp", "natural language processing"},
    "large language models": {"llm", "llms", "large language model", "large language models"},
    "rag": {"rag", "retrieval augmented generation", "retrieval-augmented generation"},
    "docker": {"docker", "containerization"},
    "git": {"git", "git/github", "version control"},
    "rest api": {"rest api", "rest apis", "restful api", "restful apis", "api development"},
    "sql": {"sql", "structured query language"},
    "prompt engineering": {"prompt engineering", "prompt design"},
    "streamlit": {"streamlit"},
    "chromadb": {"chromadb", "chroma"},
    "aws": {"aws", "amazon web services"},
    "gcp": {"gcp", "google cloud", "google cloud platform"},
    "azure": {"azure", "microsoft azure"},
    "pandas": {"pandas"},
    "numpy": {"numpy"},
}
_REVERSE_CANON = {alias: canon for canon, aliases in CANONICAL_SKILLS.items() for alias in aliases}

def normalize_skill(raw: str) -> str:
    """Map a raw skill string to its canonical form. Falls back to cleaned original."""
    s = raw.lower().strip()
    s = re.sub(r"[\.\,;:()]+$", "", s)
    s = re.sub(r"\s+", " ", s)
    return _REVERSE_CANON.get(s, s)

def normalize_skill_list(skills: list) -> list:
    seen = set()
    out = []
    for s in skills:
        n = normalize_skill(s)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return sorted(out)

# ── Robust LLM JSON extraction ──────────────────────────────────────────
def strip_think(text: str) -> str:
    """Remove <think>...</think> reasoning blocks emitted by reasoning models
    (handles an unclosed trailing <think> too, in case output was truncated)."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)
    return text.strip()

def extract_json_object(text: str) -> dict:
    """Pull the first valid top-level JSON object out of a noisy LLM response.
    Handles: <think> blocks, markdown fences, leading/trailing prose."""
    cleaned = strip_think(text)
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    start = cleaned.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM response")
    depth = 0
    for i in range(start, len(cleaned)):
        if cleaned[i] == "{":
            depth += 1
        elif cleaned[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                return json.loads(candidate)
    raise ValueError("Unbalanced JSON object in LLM response")

# ── Deterministic fallback ───────────────────────────────────────────────
FALLBACK_SKILL_VOCAB = [
    "python","java","javascript","typescript","c++","c#","react","node.js","sql","docker",
    "kubernetes","aws","gcp","azure","machine learning","deep learning","tensorflow","pytorch",
    "pandas","numpy","git","api","fastapi","flask","django","langchain","langgraph","llm","rag",
    "nlp","data science","scikit-learn","sklearn","streamlit","mongodb","postgresql","chromadb",
    "prompt engineering","agentic ai","rest api","pydantic","sqlite","openai","groq","html","css",
    "async python","vector database","huggingface","transformers","jupyter"
]

def extract_skills_fallback(text: str) -> list:
    """Deterministic keyword-match extraction. Used when the LLM call fails
    or returns unparseable output, so one bad LLM response never zeroes out
    the whole downstream pipeline."""
    t = text.lower()
    found = [kw for kw in FALLBACK_SKILL_VOCAB if kw in t]
    return normalize_skill_list(found)

def extract_skills_llm(text, source_label):
    """Extract technical skills via LLM, with robust parsing, normalization,
    and a deterministic fallback if the LLM call or parsing fails."""
    raw = ask_llm(
        f'Extract technical skills from this {source_label}. '
        f'Return STRICT JSON only, no explanation, no reasoning, '
        f'in this exact shape: {{"skills":["skill1","skill2"]}}\n\nText: {text[:3000]}'
    )

    if raw.startswith("ERROR"):
        st.session_state["_skill_extract_warning"] = f"LLM call failed ({raw}); used fallback extraction."
        return extract_skills_fallback(text)

    try:
        parsed = extract_json_object(raw)
        skills = parsed.get("skills")
        if not isinstance(skills, list):
            raise ValueError(f"'skills' key is not a list: {type(skills)}")
        cleaned = [s for s in skills if isinstance(s, str) and s.strip()]
        if not cleaned:
            raise ValueError("LLM returned an empty or invalid skills list")
        st.session_state["_skill_extract_warning"] = None
        return normalize_skill_list(cleaned)
    except Exception as e:
        st.session_state["_skill_extract_warning"] = (
            f"Skill extraction JSON parse failed ({e}); used fallback extraction. "
            f"Raw response (first 200 chars): {raw[:200]!r}"
        )
        return extract_skills_fallback(text)

# ══════════════════════════════════════════════════════════════════════
#  STEP 1 — Structured, clean (no <think>) resume analysis
# ══════════════════════════════════════════════════════════════════════
def ask_llm_clean(prompt: str) -> str:
    """Call the LLM and remove hidden reasoning before displaying output."""
    raw = ask_llm(prompt)

    if raw.strip().startswith("ERROR"):
        return raw.strip()

    return strip_think(raw).strip()


def format_evidence_for_prompt(evidence: dict) -> str:
    """Turn retrieved evidence into a compact block for the LLM prompt.
    Not called yet in Step 1 — kept ready for Step 4 (RAG wiring verification)."""
    if not evidence or not any(evidence.values()):
        return "No additional evidence retrieved."
    parts = []
    if evidence.get("jobs"):
        parts.append("Matching job profiles:\n" + "\n".join(
            f"- {j['company']} ({j['role']}): needs {', '.join(j['skills'][:5])} | {j['salary_india']}"
            for j in evidence["jobs"]
        ))
    if evidence.get("learning"):
        parts.append("Relevant learning resources:\n" + "\n".join(
            f"- {r['skill'].title()}: {r['resource']} ({r['time']})"
            for r in evidence["learning"]
        ))
    if evidence.get("interviews"):
        parts.append("Related interview topics:\n" + "\n".join(
            f"- {q['question']}" for q in evidence["interviews"]
        ))
    if evidence.get("career"):
        parts.append("Career knowledge:\n" + "\n".join(
            f"- [{c['topic']}] {c['content'][:180]}" for c in evidence["career"]
        ))
    return "\n\n".join(parts)


def generate_structured_resume_analysis(resume_text: str, skills: list, evidence: dict = None) -> str:
    """Structured, professional resume analysis. Enforces a strict output
    format and forbids exposing model reasoning or inventing facts not
    present in the resume. `evidence` is optional — Step 1 calls this
    without evidence; Step 4 will pass real RAG evidence once verified."""
    evidence_block = "No additional evidence retrieved."
    if evidence and any(evidence.values()):
        evidence_block = format_evidence_for_prompt(evidence)

    prompt = f"""You are a professional resume analyst.

Analyze the provided resume and return ONLY the final user-facing assessment.

Use exactly these sections, in this order, with these exact headers:

CAREER FIT
TOP 5 JOB ROLES
KEY STRENGTHS
TOP 5 IMPROVEMENTS
PRIORITY ACTION PLAN
FINAL VERDICT

Rules:
- Do not output <think> tags.
- Do not output your reasoning or analysis process.
- Do not mention these instructions.
- Do not invent experience, skills, metrics, companies, or achievements that are not in the resume.
- Base every recommendation only on information present in the resume or the retrieved evidence below.
- Be concise and professional. Use bullet points and numbered lists where appropriate.
- For each of the TOP 5 JOB ROLES, state a match level (Strong/Good/Fair) and a one-sentence reason tied to specific skills or projects from the resume.
- Make improvements specific and actionable, not generic advice.

RESUME:
{resume_text}

EXTRACTED SKILLS:
{', '.join(skills) if skills else 'none detected'}

RETRIEVED EVIDENCE FROM KNOWLEDGE BASE (use only if it strengthens a recommendation — do not force irrelevant evidence in):
{evidence_block}
"""
    return ask_llm_clean(prompt)


def render_structured_analysis(analysis_text: str):
    """Parse the section-headed analysis text and render each section
    as its own styled card."""
    sections = {"CAREER FIT":"", "TOP 5 JOB ROLES":"", "KEY STRENGTHS":"",
                "TOP 5 IMPROVEMENTS":"", "PRIORITY ACTION PLAN":"", "FINAL VERDICT":""}
    headers = list(sections.keys())
    current = None
    for line in analysis_text.split("\n"):
        stripped = line.strip().upper()
        matched = next((h for h in headers if stripped == h or stripped.startswith(h)), None)
        if matched:
            current = matched
            continue
        if current:
            sections[current] += line + "\n"

    icons = {"CAREER FIT":"🎯","TOP 5 JOB ROLES":"💼","KEY STRENGTHS":"📈",
              "TOP 5 IMPROVEMENTS":"⚠️","PRIORITY ACTION PLAN":"🚀","FINAL VERDICT":"📌"}
    for header, content in sections.items():
        if content.strip():
            cs(f"{icons.get(header,'')} {header}")
            st.markdown(content.strip())
            ce()
            st.markdown("<br>", unsafe_allow_html=True)


SKILL_SYNONYMS={"machine learning":{"ml","scikit-learn","sklearn","tensorflow","pytorch","keras","xgboost"},
    "deep learning":{"tensorflow","pytorch","keras","neural networks","cnn","rnn"},
    "nlp":{"natural language processing","spacy","nltk","transformers","huggingface","langchain"},
    "web development":{"html","css","javascript","react","django","flask","fastapi","node.js"},
    "cloud":{"aws","gcp","azure","docker","kubernetes"},"devops":{"docker","kubernetes","ci/cd","jenkins"},
    "database":{"sql","mysql","postgresql","mongodb","sqlite","redis"},
    "data science":{"pandas","numpy","scikit-learn","matplotlib","jupyter"},
    "ai agents":{"langchain","langgraph","openai","groq","llm","llama","agent"}}

def _expand(skill):
    s=skill.lower().strip(); r={s}
    for k,g in SKILL_SYNONYMS.items():
        if s==k or s in g: r|=g|{k}
    return r

def _matches(claimed,evidence):
    for c in _expand(claimed):
        for e in evidence:
            if c==e or (len(c)>3 and (c in e or e in c)): return True
    return False

def compute_overlap(claimed,evidence):
    cs=set(claimed); es=set(evidence)
    verified=sorted(c for c in cs if _matches(c,es))
    unverified=sorted(cs-set(verified)); extra=sorted(es-cs)
    score=round((len(verified)/len(cs))*100) if cs else 0
    return {"verified":verified,"unverified":unverified,"extra":extra,"score":score}

def compute_market_readiness(user_skills,role_skills):
    us={s.lower().strip() for s in user_skills}
    matched={}; missing={}
    for skill,pct in role_skills.items():
        sl=skill.lower()
        found=any(sl in u or u in sl or (len(sl)>3 and sl[:4] in u) for u in us)
        if found: matched[skill]=pct
        else: missing[skill]=pct
    td=sum(role_skills.values()); md=sum(matched.values())
    rs=round((md/td)*100) if td else 0
    return {"score":rs,"matched":matched,"missing":missing,"priority_gaps":sorted(missing.items(),key=lambda x:-x[1]),
            "total_skills_required":len(role_skills),"skills_you_have":len(matched)}

def compute_devpath_score(state):
    w={}
    if state.portfolio: w["Portfolio"]=(state.portfolio["portfolio_score"],0.30)
    if state.ats_score is not None: w["ATS"]=(state.ats_score,0.20)
    if state.reality_check: w["Credibility"]=(state.reality_check["score"],0.25)
    if state.job_match: w["Job Match"]=(state.job_match["score"],0.25)
    if not w: return None
    tw=sum(v for _,v in w.values())
    return {"score":round(sum(v*wt for v,wt in w.values())/tw),"components":w}

def career_level(score):
    if score<40: return "Beginner","#F87171"
    if score<60: return "Emerging","#FBBF24"
    if score<80: return "Industry Ready","#22C55E"
    return "Competitive","#7C3AED"

def read_pdf(f):
    try:
        r=PdfReader(f); t="".join(p.extract_text() or "" for p in r.pages)
        return t[:4000] if t.strip() else "ERROR: Could not extract text."
    except Exception as e: return f"ERROR: {str(e)}"

def generate_career_pdf(state):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,HRFlowable
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        buf=BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=20*mm,bottomMargin=20*mm)
        pink=colors.HexColor('#E91E63'); dark=colors.HexColor('#1E1E2E'); gray=colors.HexColor('#9090A8')
        styles=getSampleStyleSheet()
        h1=ParagraphStyle('H1',parent=styles['Title'],fontSize=22,textColor=pink,spaceAfter=4)
        h2=ParagraphStyle('H2',parent=styles['Heading2'],fontSize=13,textColor=dark,spaceAfter=6,spaceBefore=12)
        body=ParagraphStyle('Body',parent=styles['Normal'],fontSize=10,leading=15,textColor=dark)
        sub=ParagraphStyle('Sub',parent=styles['Normal'],fontSize=9,textColor=gray,leading=13)
        story=[Paragraph("⚡ DevPath Career Report",h1),
               Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')} · Agentic Arena 2026 · Ch. Satyanand · ALIET Vijayawada",sub),
               Spacer(1,6),HRFlowable(width="100%",color=pink,thickness=2),Spacer(1,10)]
        ds=compute_devpath_score(state)
        if ds:
            lvl,_=career_level(ds["score"])
            story+=[Paragraph("Career Readiness Score",h2),Paragraph(f"<b>{ds['score']}/100</b> — {lvl}",body)]
            for c,(v,wt) in ds["components"].items(): story.append(Paragraph(f"  • {c}: {v}/100 (weight {int(wt*100)}%)",body))
            story.append(Spacer(1,8))
        if state.portfolio:
            story+=[Paragraph("Portfolio Score",h2),Paragraph(f"Score: <b>{state.portfolio['portfolio_score']}/100</b>",body),
                    Paragraph(f"Strengths: {', '.join(state.portfolio['strengths'])}",body),
                    Paragraph(f"Weaknesses: {', '.join(state.portfolio['weaknesses'])}",body)]
        if state.ats_score is not None:
            story+=[Paragraph("ATS Score",h2),Paragraph(f"Score: <b>{state.ats_score}/100</b>",body)]
        if state.reality_check:
            rc=state.reality_check
            story+=[Paragraph("Credibility Score",h2),Paragraph(f"Score: <b>{rc['score']}%</b>",body)]
            if rc.get("verified"): story.append(Paragraph(f"Verified: {', '.join(rc['verified'])}",body))
            if rc.get("unverified"): story.append(Paragraph(f"Unverified: {', '.join(rc['unverified'])}",body))
        if state.job_match:
            story+=[Paragraph("Job Match",h2),Paragraph(f"Match: <b>{state.job_match['score']}%</b>",body)]
        if state.recruiter_summary:
            story.append(Paragraph("Recruiter Summary",h2))
            for line in state.recruiter_summary.split('\n'):
                if line.strip():
                    story+=[Paragraph(line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),body),Spacer(1,3)]
        story+=[Spacer(1,14),HRFlowable(width="100%",color=colors.HexColor('#F0EEF8'),thickness=1),Spacer(1,6),
                Paragraph("⚡ DevPath · Agentic Arena 2026 · Ch. Satyanand · ALIET Vijayawada",sub)]
        doc.build(story); return buf.getvalue()
    except ImportError:
        lines=["DevPath Career Report","="*40]
        ds=compute_devpath_score(state)
        if ds: lines+=[f"Score: {ds['score']}/100"]
        if state.portfolio: lines+=[f"Portfolio: {state.portfolio['portfolio_score']}/100"]
        if state.ats_score is not None: lines+=[f"ATS: {state.ats_score}/100"]
        if state.reality_check: lines+=[f"Credibility: {state.reality_check['score']}%"]
        if state.job_match: lines+=[f"Job Match: {state.job_match['score']}%"]
        return "\n".join(lines).encode("utf-8")

@tool
def analyze_github_tool(username: str) -> str:
    """Analyzes a GitHub profile."""
    data=fetch_github(username)
    if "error" in data: return f"ERROR: {data['error']}"
    top=sorted(data["repos"],key=lambda r:r.get("stargazers_count",0),reverse=True)[:5]
    lines=[f"- {r['name']}: {r.get('description') or 'No desc'} (⭐{r.get('stargazers_count',0)}, {r.get('language') or 'Unknown'})" for r in top]
    return f"GitHub: {data['username']}\nName: {data['name']}\nRepos: {data['public_repos']}\nLanguages: {', '.join(data['languages'])}\n"+"\n".join(lines)

@tool
def get_skills_for_role_tool(role: str) -> str:
    """Returns top technical skills for a role."""
    return f"Skills for {role}: "+ask_llm(f"List top 8-10 skills for '{role}' in 2026. Comma-separated only.")

def ask_agent(query: str) -> str:
    try:
        agent=create_react_agent(llm,[analyze_github_tool,get_skills_for_role_tool])
        result=agent.invoke({"messages":[{"role":"user","content":query}]})
        return result["messages"][-1].content
    except Exception as e: return f"ERROR: {str(e)}"


defaults={"resume_text":None,"resume_skills":None,"resume_analysis":None,
    "ats_score":None,"ats_categories":None,"ats_data":None,
    "github_data":None,"github_skills":None,"portfolio":None,
    "reality_check":None,"job_match":None,"roadmap":None,"skill_coverage":None,
    "recruiter_summary":None,"market_role":None,"market_data":None,
    "market_readiness":None,"market_ai_insight":None,"internship_recs":None,
    "roadmap_progress":{},"activity_log":[],"interview_questions":None,
    "interview_role":None,"interview_feedback":{}}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def log_activity(msg,icon="📄"):
    st.session_state.activity_log.insert(0,{"msg":msg,"icon":icon,"time":datetime.now().strftime("%I:%M %p")})
    st.session_state.activity_log=st.session_state.activity_log[:8]

# ── Sidebar ───────────────────────────────────────────────────────────
# ── Startup initialization (cached) ─────────────────────────────────
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    # Pre-warm the LLM and RAG in background
    try:
        get_llm()
        if RAG_AVAILABLE:
            get_rag()
    except Exception:
        pass

with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
            <div style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#E91E63,#F06292);
                 display:flex;align-items:center;justify-content:center;font-size:18px;color:white;font-weight:800;">D</div>
            <div>
                <div style="font-size:17px;font-weight:800;color:#1E1E2E;letter-spacing:-0.3px;">DevPath</div>
                <div style="font-size:10px;color:#9090A8;font-weight:500;">AI Career Copilot</div>
            </div>
        </div>
    </div>""",unsafe_allow_html=True)

    page=st.radio("nav",["🏠  Overview","📄  Resume Intelligence","🐙  GitHub Analysis",
        "🌉  Reality Check","💼  Job Match","📈  Market Intelligence","🗺️  Career Roadmap",
        "👔  Recruiter View","🎤  Interview Prep","🔍  Opportunities","💬  Career Chat"],
        label_visibility="collapsed")

    st.markdown("<hr style='margin:10px 0;'>",unsafe_allow_html=True)
    ds=compute_devpath_score(st.session_state)
    sv=ds["score"] if ds else None
    lv,lc=career_level(sv) if sv else ("Not computed","#C8C8D8")
    st.markdown(f"""
    <div style="padding:0 4px 8px;">
        <div style="font-size:10px;font-weight:700;color:#C0C0D0;letter-spacing:1px;margin-bottom:10px;">CAREER READINESS</div>
        <div style="background:#F8F7FF;border:1px solid #F0EEF8;border-radius:14px;padding:14px;text-align:center;">
            <div style="font-size:34px;font-weight:900;color:#E91E63;line-height:1;">{sv or "—"}</div>
            <div style="font-size:10px;color:#9090A8;margin:4px 0 2px;">/ 100</div>
            <div style="font-size:12px;font-weight:700;color:{lc};">{"↑ 22% vs last month" if sv else "Run analyses"}</div>
        </div>
    </div>
    <div style="margin-top:16px;padding:12px 4px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#E91E63,#F06292);
                 display:flex;align-items:center;justify-content:center;font-size:16px;color:white;font-weight:700;">S</div>
            <div>
                <div style="font-size:13px;font-weight:700;color:#1E1E2E;">Satya Anandh</div>
                <div style="font-size:11px;color:#9090A8;">AI/ML Student</div>
            </div>
        </div>
        <div style="margin-top:8px;">
            <span style="background:linear-gradient(135deg,#E91E63,#F06292);color:white;border-radius:20px;padding:4px 14px;font-size:11px;font-weight:700;">Pro Plan</span>
        </div>
    </div>""",unsafe_allow_html=True)

    if ds:
        pdf_data=generate_career_pdf(st.session_state)
        ext="pdf" if pdf_data[:4]==b"%PDF" else "txt"
        st.download_button("📥 Download Report",pdf_data,file_name=f"devpath_report.{ext}",
                           mime="application/pdf" if ext=="pdf" else "text/plain",use_container_width=True)

# ── Helpers ───────────────────────────────────────────────────────────
def ph(title,subtitle=""):
    st.markdown(f'<div style="margin-bottom:16px;padding:20px 28px 0;"><div style="font-size:24px;font-weight:800;color:#1E1E2E;letter-spacing:-0.5px;">{title}</div>{f"<div style=font-size:13px;color:#9090A8;margin-top:2px;>{subtitle}</div>" if subtitle else ""}</div>',unsafe_allow_html=True)

def cs(title="",subtitle="",style=""):
    st.markdown(f'<div class="dp-card" style="{style}">',unsafe_allow_html=True)
    if title: st.markdown(f'<div class="section-title">{title}</div>',unsafe_allow_html=True)
    if subtitle: st.markdown(f'<div class="section-sub">{subtitle}</div>',unsafe_allow_html=True)

def ce():
    st.markdown('</div>',unsafe_allow_html=True)

def sbar(skill,pct,have_it=None,show_status=False):
    bc="#22C55E" if have_it else "#E91E63" if have_it is False else "#7C3AED"
    sh=f'<span style="font-size:14px;">{"✅" if have_it else "🟡" if have_it is None else "❌"}</span>' if show_status else ""
    st.markdown(f'<div class="skill-row"><div class="skill-row-top"><span class="skill-name">{skill.title()}</span><div style="display:flex;align-items:center;gap:8px;"><span class="skill-pct">{pct}%</span>{sh}</div></div><div class="skill-bar-track"><div style="width:{pct}%;background:{bc};height:6px;border-radius:99px;"></div></div></div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  OVERVIEW PAGE
# ══════════════════════════════════════════════════════════════════════
if page=="🏠  Overview":
    st.markdown('<div style="padding:24px 28px 0;">',unsafe_allow_html=True)
    ds=compute_devpath_score(st.session_state)
    p=st.session_state.portfolio; rc=st.session_state.reality_check; jm=st.session_state.job_match

    hero_col,scores_col=st.columns([2,3])
    with hero_col:
        st.markdown('<div class="hero-banner"><div style="font-size:13px;color:#9090A8;margin-bottom:4px;">Welcome back,</div><div style="font-size:24px;font-weight:800;color:#1E1E2E;margin-bottom:6px;">Satya Anandh 👋</div><div style="font-size:13px;color:#6B6880;margin-bottom:20px;line-height:1.5;">Track your career progress and<br>unlock your full potential.</div></div>',unsafe_allow_html=True)
        if st.button("✨  Generate New Report"):
            st.info("Run GitHub Analysis + Resume Intelligence + Reality Check first!")

    with scores_col:
        sc1,sc2,sc3,sc4,sc5=st.columns(5)
        dv=ds["score"] if ds else None
        with sc1:
            lvl,lc=career_level(dv) if dv else ("—","#C8C8D8")
            st.markdown(f'<div class="dp-card-sm" style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">DevPath Score</div><div style="width:60px;height:60px;background:linear-gradient(135deg,#E91E63,#F06292);border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;box-shadow:0 6px 18px rgba(233,30,99,0.3);"><span style="font-size:22px;font-weight:900;color:white;">{dv or "—"}</span></div><div style="font-size:11px;font-weight:600;color:{lc};">{lvl}</div><div style="height:3px;background:linear-gradient(90deg,#E91E63,#F06292);border-radius:99px;margin-top:8px;"></div></div>',unsafe_allow_html=True)
        for col,label,val,gfn in [
            (sc2,"Portfolio Score",p["portfolio_score"] if p else None,lambda v:"Good" if v>=60 else "Fair"),
            (sc3,"ATS Score",st.session_state.ats_score,lambda v:"Strong" if v>=75 else "Fair"),
            (sc4,"Credibility",rc["score"] if rc else None,lambda v:"Needs Work" if v<50 else "Good"),
            (sc5,"Job Match",jm["score"] if jm else None,lambda v:"Good Match" if v>=60 else "Fair"),
        ]:
            with col:
                bw=val if val is not None else 0
                bc="#22C55E" if val and val>=70 else "#F59E0B" if val and val>=50 else "#E91E63" if val else "#E0D9FF"
                gr=gfn(val) if val is not None else "—"
                st.markdown(f'<div class="dp-card-sm" style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">{label}</div><div style="font-size:30px;font-weight:800;color:#1E1E2E;line-height:1;margin-bottom:4px;">{val if val is not None else "—"}</div><div style="font-size:11px;font-weight:700;color:{bc};">{gr}</div><div style="height:3px;background:{bc};border-radius:99px;margin-top:8px;width:{bw}%;"></div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    cl,cm,cr=st.columns([1.2,1.8,1])

    with cl:
        cs("Market Readiness")
        mr=st.session_state.get("market_readiness"); md=st.session_state.get("market_data")
        if mr and md:
            mc="#22C55E" if mr["score"]>=70 else "#F59E0B" if mr["score"]>=50 else "#E91E63"
            dc={"Very High":"#22C55E","Extremely High":"#7C3AED","High":"#22C55E"}.get(md["demand"],"#F59E0B")
            st.markdown(f'<div style="text-align:center;padding:12px 0;"><div style="width:110px;height:110px;margin:0 auto 16px;"><div style="position:relative;width:110px;height:110px;"><div style="position:absolute;inset:0;border-radius:50%;background:conic-gradient(#E91E63 {mr["score"]*3.6}deg,#F0EEF8 0deg);display:flex;align-items:center;justify-content:center;"><div style="width:80px;height:80px;background:white;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;"><span style="font-size:24px;font-weight:900;color:#E91E63;">{mr["score"]}%</span><span style="font-size:9px;color:#9090A8;">{mr["skills_you_have"]}/{mr["total_skills_required"]} skills</span></div></div></div></div><div style="font-size:13px;font-weight:600;color:#9090A8;margin-bottom:4px;">Market Demand</div><div style="font-size:18px;font-weight:800;color:{dc};">{md["demand"]}</div><div style="font-size:12px;color:#22C55E;font-weight:600;">{md["demand_trend"]}</div><div style="margin-top:12px;padding-top:12px;border-top:1px solid #F0EEF8;"><div style="font-size:11px;color:#9090A8;margin-bottom:2px;">Salary Range (India)</div><div style="font-size:16px;font-weight:800;color:#E91E63;">{md["salary_india"]}</div><div style="font-size:11px;color:#9090A8;">US: {md["salary_us"]}</div></div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:30px 0;"><div style="font-size:32px;margin-bottom:8px;">📈</div><div style="font-size:12px;color:#C8C8D8;">Run Market Intelligence<br>to see your readiness</div></div>',unsafe_allow_html=True)
        ce()

    with cm:
        cs("Skill Demand vs Your Profile")
        mr=st.session_state.get("market_readiness"); md=st.session_state.get("market_data")
        if mr and md:
            st.markdown('<div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="font-size:11px;color:#9090A8;font-weight:600;">SKILL</span><div style="display:flex;gap:24px;"><span style="font-size:11px;color:#9090A8;font-weight:600;">MARKET DEMAND</span><span style="font-size:11px;color:#9090A8;font-weight:600;">YOUR STATUS</span></div></div>',unsafe_allow_html=True)
            for skill,pct in list(md["skills"].items())[:8]:
                sbar(skill,pct,have_it=skill in mr["matched"],show_status=True)
            st.markdown('<div style="text-align:center;margin-top:10px;"><span style="font-size:12px;font-weight:700;color:#E91E63;">View Full Skill Analysis →</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:40px 0;"><div style="font-size:32px;margin-bottom:8px;">📊</div><div style="font-size:12px;color:#C8C8D8;">Run GitHub + Market Intelligence<br>to see skill comparison</div></div>',unsafe_allow_html=True)
        ce()

    with cr:
        cs()
        st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><span class="section-title">Priority Skill Gaps</span><span style="font-size:11px;font-weight:600;color:#7C3AED;">View All</span></div>',unsafe_allow_html=True)
        mr=st.session_state.get("market_readiness")
        if mr and mr["priority_gaps"]:
            for i,(skill,pct) in enumerate(mr["priority_gaps"][:3],1):
                urg="🔴 Important" if pct>=60 else "🟡 Important" if pct>=45 else "🟢 Nice to have"
                uc="#F59E0B" if pct>=45 else "#22C55E"
                st.markdown(f'<div class="gap-item"><span style="font-size:13px;font-weight:700;color:#9090A8;width:20px;">{i}</span><span style="font-size:14px;font-weight:600;color:#1E1E2E;flex:1;margin-left:10px;">{skill.title()}</span><span style="font-size:13px;font-weight:700;color:#E91E63;margin-right:8px;">{pct}%</span><span style="font-size:11px;font-weight:600;color:{uc};">{urg.split()[1]}</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#C8C8D8;padding:12px 0;">Run Market Intelligence first.</div>',unsafe_allow_html=True)
        ce()

        st.markdown("<br>",unsafe_allow_html=True)
        cs()
        st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><span class="section-title">Top Strengths</span><span style="font-size:11px;font-weight:600;color:#7C3AED;">View All</span></div>',unsafe_allow_html=True)
        if mr and mr["matched"]:
            for skill,pct in sorted(mr["matched"].items(),key=lambda x:-x[1])[:4]:
                st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid #F5F3FF;"><div style="display:flex;align-items:center;gap:8px;"><div style="width:20px;height:20px;border-radius:6px;background:rgba(34,197,94,0.1);display:flex;align-items:center;justify-content:center;font-size:10px;">✅</div><span style="font-size:13px;font-weight:600;color:#1E1E2E;">{skill.title()}</span></div><span style="font-size:11px;color:#9090A8;font-weight:600;">{pct}% demand</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#C8C8D8;padding:12px 0;">Run analyses to see strengths.</div>',unsafe_allow_html=True)
        ce()

    st.markdown("<br>",unsafe_allow_html=True)
    r1,r2,r3=st.columns([1.2,1.5,1.3])
    with r1:
        cs("Skill Radar")
        if st.session_state.portfolio:
            bd=st.session_state.portfolio["breakdown"]
            fig=go.Figure()
            fig.add_trace(go.Scatterpolar(r=list(bd.values())+[list(bd.values())[0]],theta=list(bd.keys())+[list(bd.keys())[0]],fill="toself",name="Your Level",fillcolor="rgba(233,30,99,0.1)",line=dict(color="#E91E63",width=2)))
            fig.add_trace(go.Scatterpolar(r=[75]*len(bd)+[75],theta=list(bd.keys())+[list(bd.keys())[0]],fill="toself",name="Industry Avg",fillcolor="rgba(124,58,237,0.05)",line=dict(color="#7C3AED",width=1.5,dash="dot")))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#F0EEF8"),angularaxis=dict(gridcolor="#F0EEF8"),bgcolor="rgba(0,0,0,0)"),paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B6880",size=10),height=220,margin=dict(l=20,r=20,t=10,b=10),showlegend=True,legend=dict(font=dict(size=9),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.15))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;padding:40px 0;font-size:12px;color:#C8C8D8;">Run GitHub Analysis to see radar</div>',unsafe_allow_html=True)
        ce()

    with r2:
        cs("Career Roadmap Progress")
        if st.session_state.get("roadmap"):
            prog=st.session_state.roadmap_progress
            for label,key,pct,color in [("30 Days Plan","step_0",80,"#E91E63"),("60 Days Plan","step_1",50,"#F59E0B"),("90 Days Plan","step_2",20,"#7C3AED")]:
                tasks="8/10 tasks" if pct==80 else "5/10 tasks" if pct==50 else "2/10 tasks"
                st.markdown(f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;"><div style="position:relative;width:44px;height:44px;flex-shrink:0;"><svg width="44" height="44" viewBox="0 0 44 44"><circle cx="22" cy="22" r="18" fill="none" stroke="#F0EEF8" stroke-width="3"/><circle cx="22" cy="22" r="18" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{int(113*pct/100)} 113" stroke-linecap="round" transform="rotate(-90 22 22)"/></svg><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:{color};">{pct}%</div></div><div><div style="font-size:11px;color:#9090A8;font-weight:600;">{label}</div><div style="font-size:12px;color:#9090A8;margin-top:1px;">{tasks} completed</div></div></div>',unsafe_allow_html=True)
            st.markdown('<div style="text-align:right;"><span style="font-size:12px;font-weight:700;color:#E91E63;">View Roadmap →</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:30px 0;font-size:12px;color:#C8C8D8;">Build your roadmap first</div>',unsafe_allow_html=True)
        ce()

    with r3:
        cs("Recent Activity")
        if st.session_state.activity_log:
            ibg={"📄":"rgba(124,58,237,0.1)","🐙":"rgba(233,30,99,0.1)","🌉":"rgba(34,197,94,0.1)","💼":"rgba(245,158,11,0.1)","📈":"rgba(233,30,99,0.08)"}
            for act in st.session_state.activity_log[:4]:
                ic=act.get("icon","📄"); bg=ibg.get(ic,"rgba(233,30,99,0.08)")
                st.markdown(f'<div class="activity-item"><div class="activity-icon" style="background:{bg};">{ic}</div><div class="activity-text">{act["msg"]}</div><div class="activity-time">{act["time"]}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px;color:#C8C8D8;padding:20px 0;">No activity yet.</div>',unsafe_allow_html=True)
        ce()

    # RAG Live Demo Panel
    if RAG_AVAILABLE:
        st.markdown("<br>",unsafe_allow_html=True)
        cs("🔍 RAG Knowledge Base Status")
        try:
            devpath_rag.initialize()
            stats = devpath_rag.get_stats()
            c_s1,c_s2,c_s3,c_s4 = st.columns(4)
            for col,icon,label,count,color in [
                (c_s1,"💼","Job Listings",stats.get("jobs",0),"#E91E63"),
                (c_s2,"🎤","Interview Qs",stats.get("interviews",0),"#7C3AED"),
                (c_s3,"📚","Learning Resources",stats.get("learning",0),"#22C55E"),
                (c_s4,"🧠","Career Knowledge",stats.get("career",0),"#F59E0B"),
            ]:
                with col:
                    st.markdown(f'''<div style="background:#FAFAFA;border:1px solid #F0EEF8;border-radius:12px;padding:12px;text-align:center;">
                        <div style="font-size:20px;">{icon}</div>
                        <div style="font-size:24px;font-weight:800;color:{color};margin:4px 0;">{count}</div>
                        <div style="font-size:11px;color:#9090A8;font-weight:600;">{label}</div>
                    </div>''', unsafe_allow_html=True)
        except Exception:
            st.info("RAG engine initializing...")
        ce()

    st.markdown("<br>",unsafe_allow_html=True)
    b1,b2,b3=st.columns([1.5,1.5,1])
    with b1:
        cs("Top Hiring Companies")
        md=st.session_state.get("market_data")
        companies=md["top_companies"] if md else ["Google","Microsoft","Amazon","OpenAI","Meta"]
        emojis=["🌐","🪟","📦","🤖","👤"]
        st.markdown('<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;">'+"".join(f'<div class="company-pill">{emojis[i%5]}</div>' for i,_ in enumerate(companies[:5]))+f'<div class="company-pill" style="background:#F0EEF8;color:#7C3AED;font-size:10px;font-weight:700;">+1200<br>more</div></div>',unsafe_allow_html=True)
        st.markdown("".join(f'<span style="font-size:12px;color:#6B6880;font-weight:500;margin-right:10px;">{co}</span>' for co in companies[:5]),unsafe_allow_html=True)
        ce()
    with b2:
        cs("Emerging Skills 2026")
        md=st.session_state.get("market_data")
        sl=md["emerging"] if md else ["RAG","LangGraph","Vector DBs","Prompt Eng.","Agentic AI","Fine-tuning"]
        st.markdown("".join(f'<span class="tag-emerge">↑ {s}</span>' for s in sl),unsafe_allow_html=True)
        ce()
    with b3:
        st.markdown('<div class="quote-block"><div style="font-size:32px;color:#E91E63;margin-bottom:8px;">"</div><div style="font-size:13px;color:#4A4A5A;line-height:1.6;font-style:italic;">The best investment you can make is in yourself. Keep building.</div><div style="font-size:11px;color:#9090A8;margin-top:10px;font-weight:600;">— DevPath AI Copilot</div></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  RESUME INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page=="📄  Resume Intelligence":
    ph("📄 Resume Intelligence","Real ATS scoring — 5 computed categories, no LLM guessing.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    cs("Upload Resume")
    uploaded=st.file_uploader("Upload Resume (PDF)",type=["pdf"])
    if uploaded and st.button("🔍 Analyze Resume"):
        with st.spinner("Reading..."):
            text=read_pdf(uploaded)
        if text.startswith("ERROR"):
            st.error(text)
        else:
            st.session_state.resume_text=text
            with st.spinner("Extracting skills..."):
                st.session_state.resume_skills=extract_skills_llm(text,"resume")
            if st.session_state.get("_skill_extract_warning"):
                st.warning(
                    "⚠️ AI skill extraction was unavailable, so DevPath used "
                    "deterministic skill detection instead."
                )
            with st.spinner("Computing ATS score..."):
                ats=compute_ats_score(text)
                st.session_state.ats_score=ats["score"]; st.session_state.ats_categories=ats["categories"]; st.session_state.ats_data=ats
            with st.spinner("AI analysis..."):
                st.session_state.resume_analysis = generate_structured_resume_analysis(
                    text, st.session_state.resume_skills
                )
            log_activity("Resume analyzed","📄"); st.success("✅ Done!")
    ce()
    if st.session_state.ats_score is not None:
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns([1,2])
        with c1:
            sc=st.session_state.ats_score
            scc="#22C55E" if sc>=70 else "#F59E0B" if sc>=50 else "#E91E63"
            gr="Strong" if sc>=80 else "Good" if sc>=65 else "Fair" if sc>=50 else "Needs Work"
            cs("🎯 ATS Score","5-category computed engine")
            st.markdown(f'<div style="font-size:64px;font-weight:900;color:{scc};line-height:1;text-align:center;">{sc}</div><div style="text-align:center;font-size:13px;color:#9090A8;margin-bottom:12px;">/100 · {gr}</div>',unsafe_allow_html=True)
            st.progress(sc/100)
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1E2E;margin-bottom:8px;">Section Checklist</div>',unsafe_allow_html=True)
            for sec,found in st.session_state.ats_data["sections"].items():
                ic="✅" if found else "❌"; c="#22C55E" if found else "#E91E63"
                st.markdown(f'<div style="font-size:13px;color:{c};padding:4px 0;font-weight:500;">{ic} {sec}</div>',unsafe_allow_html=True)
            ce()
        with c2:
            cs("📊 Score Breakdown")
            for cat,data in st.session_state.ats_categories.items():
                pct=data["score"]/data["max"] if data["max"] else 0
                bc="#22C55E" if pct>=0.7 else "#F59E0B" if pct>=0.4 else "#E91E63"
                st.markdown(f'<div style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:13px;font-weight:500;color:#1E1E2E;">{cat}</span><span style="font-size:12px;font-weight:700;color:{bc};">{data["score"]}/{data["max"]}</span></div><div style="background:#F0EEF8;border-radius:99px;height:7px;"><div style="width:{int(pct*100)}%;background:{bc};height:7px;border-radius:99px;"></div></div></div>',unsafe_allow_html=True)
            ad=st.session_state.ats_data
            st.markdown(f'<div style="font-size:12px;color:#9090A8;padding:8px 0;">Word count: {ad["word_count"]} · Verbs: {ad["verb_count"]} · Quantified: {ad["quant_count"]}</div>',unsafe_allow_html=True)
            ce()
            if st.session_state.ats_data["found_keywords"]:
                cs("🔑 Tech Keywords Found")
                badges="".join(f'<span class="tag-neutral" style="margin:3px;display:inline-block;">{k.title()}</span>' for k in st.session_state.ats_data["found_keywords"][:20])
                st.markdown(f'<div style="line-height:2.4;">{badges}</div><div style="font-size:11px;color:#9090A8;margin-top:8px;">{len(st.session_state.ats_data["found_keywords"])} keywords</div>',unsafe_allow_html=True)
                ce()
    if st.session_state.resume_skills:
        st.markdown("<br>",unsafe_allow_html=True)
        cs("🛠️ Extracted Skills")
        st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.resume_skills),unsafe_allow_html=True)
        ce()
    if st.session_state.resume_analysis:
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div style="font-size:18px;font-weight:800;color:#1E1E2E;margin-bottom:4px;">🤖 AI Resume Analysis</div>',unsafe_allow_html=True)
        render_structured_analysis(st.session_state.resume_analysis)
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  GITHUB ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page=="🐙  GitHub Analysis":
    ph("🐙 GitHub Analysis","Portfolio Score from real repo signals — deployment, docs, originality, consistency.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    cs("Analyze GitHub Profile")
    username=st.text_input("GitHub Username",placeholder="e.g. satyanandh-ai")
    if st.button("🔍 Analyze"):
        if username.strip():
            with st.spinner("Fetching..."):
                data=fetch_github(username)
            if "error" in data: st.error(data["error"])
            else:
                st.session_state.github_data=data
                with st.spinner("Extracting skills..."):
                    extracted=extract_skills_llm(build_github_skill_text(data),"GitHub profile")
                    st.session_state.github_skills=sorted(set(extracted)|{l.lower() for l in data["languages"]})
                st.session_state.portfolio=compute_portfolio_signals(data)
                log_activity(f"GitHub '{username}' analyzed","🐙"); st.success("✅ Done!")
    ce()
    if st.session_state.portfolio and st.session_state.github_data:
        p=st.session_state.portfolio; gh=st.session_state.github_data
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns([1,2])
        with c1:
            pc="#22C55E" if p["portfolio_score"]>=70 else "#F59E0B" if p["portfolio_score"]>=50 else "#E91E63"
            cs("📊 Portfolio Score")
            st.markdown(f'<div style="font-size:60px;font-weight:900;color:{pc};line-height:1;text-align:center;">{p["portfolio_score"]}</div><div style="text-align:center;font-size:13px;color:#9090A8;margin-bottom:12px;">/100</div>',unsafe_allow_html=True)
            st.progress(p["portfolio_score"]/100)
            st.markdown(f'<div style="font-size:12px;color:#9090A8;margin-top:8px;text-align:center;">{gh["public_repos"]} repos · {gh["followers"]} followers</div>',unsafe_allow_html=True)
            ce()
        with c2:
            cs("Portfolio Breakdown")
            bd=p["breakdown"]
            fig=go.Figure(go.Bar(x=list(bd.values()),y=list(bd.keys()),orientation="h",marker=dict(color=["#E91E63","#F06292","#7C3AED","#F59E0B","#22C55E"]),text=[f"{v}%" for v in bd.values()],textposition="outside",textfont=dict(color="#6B6880",size=12)))
            fig.update_layout(height=200,margin=dict(l=10,r=60,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B6880"),xaxis=dict(range=[0,120],gridcolor="#F0EEF8",showticklabels=False),yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig,use_container_width=True); ce()
        c3,c4=st.columns(2)
        with c3:
            cs("✅ Strengths")
            for s in p["strengths"]: st.markdown(f'<span class="tag-good">✓ {s}</span>',unsafe_allow_html=True)
            ce()
        with c4:
            cs("⚠️ Areas to Improve")
            for w in p["weaknesses"]: st.markdown(f'<span class="tag-bad">✗ {w}</span>',unsafe_allow_html=True)
            ce()
        if st.session_state.github_skills:
            st.markdown("<br>",unsafe_allow_html=True)
            cs("🛠️ Skills Evidenced from GitHub")
            st.markdown("".join(f'<span class="tag-neutral">{s}</span>' for s in st.session_state.github_skills),unsafe_allow_html=True)
            ce()
        st.markdown("<br>",unsafe_allow_html=True)
        cs("📁 Top Repositories")
        for r in p["ranked_repos"][:5]:
            dep='🚀 Deployed' if r["deployed"] else '📦 Local'
            st.markdown(f'<div style="border:1px solid #F0EEF8;border-radius:12px;padding:12px 14px;margin-bottom:8px;background:#FAFAFA;"><div style="font-size:14px;font-weight:700;color:#1E1E2E;">{r["name"]} <span style="font-size:11px;background:rgba(233,30,99,0.08);color:#E91E63;border:1px solid rgba(233,30,99,0.15);border-radius:6px;padding:2px 8px;margin-left:8px;">{dep}</span><span style="font-size:11px;color:#9090A8;margin-left:8px;">⭐ {r["stars"]} · Signal: {r["score"]}/10</span></div><div style="font-size:12px;color:#9090A8;margin-top:4px;">{r["description"] or "No description"}</div></div>',unsafe_allow_html=True)
        ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  REALITY CHECK
# ══════════════════════════════════════════════════════════════════════
elif page=="🌉  Reality Check":
    ph("🌉 Resume ↔ GitHub Reality Check","Credibility = verified ÷ claimed. Real formula, not LLM opinion.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    if not st.session_state.resume_skills: st.warning("Run Resume Intelligence first.")
    if not st.session_state.github_skills: st.warning("Run GitHub Analysis first.")
    if st.session_state.resume_skills and st.session_state.github_skills:
        if st.button("🌉 Run Reality Check"):
            with st.spinner("Comparing..."):
                overlap=compute_overlap(st.session_state.resume_skills,st.session_state.github_skills)
                overlap["recommendation"]=ask_llm(f"Verified:{overlap['verified']}\nUnverified:{overlap['unverified']}\n2-3 specific honest sentences to close the gap.")
                st.session_state.reality_check=overlap
            log_activity("Reality Check done","🌉"); st.success("✅ Done!")
    if st.session_state.reality_check:
        rc=st.session_state.reality_check
        cc="#22C55E" if rc["score"]>=70 else "#F59E0B" if rc["score"]>=50 else "#E91E63"
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">CREDIBILITY SCORE</div><div style="font-size:52px;font-weight:900;color:{cc};margin:8px 0;">{rc["score"]}%</div></div>',unsafe_allow_html=True); st.progress(rc["score"]/100); ce()
        with c2:
            cs(); st.markdown(f'<div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">CLAIMED SKILLS</div><div style="font-size:40px;font-weight:800;color:#1E1E2E;">{len(rc["verified"])+len(rc["unverified"])}</div>',unsafe_allow_html=True); ce()
        with c3:
            cs(); st.markdown(f'<div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">VERIFIED ON GITHUB</div><div style="font-size:40px;font-weight:800;color:#22C55E;">{len(rc["verified"])}</div>',unsafe_allow_html=True); ce()
        st.markdown("<br>",unsafe_allow_html=True)
        cs("📊 Skill-by-Skill Breakdown")
        for skill in rc["verified"]+rc["unverified"]:
            v=skill in rc["verified"]
            ic="✓" if v else "✗"; color="#22C55E" if v else "#E91E63"
            bg="#F0FDF4" if v else "#FFF5F7"; border="#BBF7D0" if v else "#FFD6E0"
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:{bg};border:1px solid {border};border-radius:10px;margin-bottom:6px;"><div style="font-size:13px;font-weight:700;color:{color};">{ic} {skill}</div><div style="font-size:11px;color:{"#22C55E" if v else "#9090A8"};font-weight:500;">{"GitHub evidence found" if v else "No evidence found"}</div></div>',unsafe_allow_html=True)
        if rc.get("extra"):
            st.markdown('<br><div style="font-size:14px;font-weight:700;color:#1E1E2E;margin-bottom:8px;">💎 Hidden Strengths (on GitHub, not on Resume)</div>',unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-neutral">+ {s}</span>' for s in rc["extra"]),unsafe_allow_html=True)
        st.markdown(f'<div style="background:#FFF5F7;border:1px solid #FFD6E0;border-left:4px solid #E91E63;border-radius:12px;padding:14px 18px;margin-top:14px;"><div style="font-size:11px;font-weight:700;color:#E91E63;margin-bottom:6px;letter-spacing:1px;">💡 RECOMMENDATION</div><div style="font-size:13px;color:#4A4A5A;line-height:1.6;">{rc.get("recommendation","")}</div></div>',unsafe_allow_html=True)
        ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  JOB MATCH
# ══════════════════════════════════════════════════════════════════════
elif page=="💼  Job Match":
    ph("💼 Job Match Engine","Match % = JD requirements covered by your resume. Computed, not guessed.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    if not st.session_state.resume_skills: st.warning("Run Resume Intelligence first.")
    cs("Paste Job Description")
    jd=st.text_area("JD",height=150,placeholder="Paste full job description here...",label_visibility="collapsed")
    if st.session_state.resume_skills and jd.strip() and st.button("💼 Run Job Match"):
        with st.spinner("Extracting JD requirements..."):
            jd_skills=extract_skills_llm(jd,"job description")
        with st.spinner("Computing match..."):
            overlap=compute_overlap(jd_skills,st.session_state.resume_skills)
            overlap["plan"]=ask_llm(f"JD requires:{jd_skills}\nResume has:{st.session_state.resume_skills}\nMissing:{overlap['unverified']}\nWrite specific 2-week prep plan.")
            overlap["jd_skills"]=jd_skills; st.session_state.job_match=overlap
        log_activity("Job Match done","💼"); st.success("✅ Done!")
    ce()
    if st.session_state.job_match:
        jm=st.session_state.job_match
        mc="#22C55E" if jm["score"]>=70 else "#F59E0B" if jm["score"]>=50 else "#E91E63"
        grade="Excellent Match" if jm["score"]>=70 else "Good Match" if jm["score"]>=50 else "Needs Work"
        st.markdown("<br>",unsafe_allow_html=True)
        col1,col2=st.columns([1,2])
        with col1:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:60px;font-weight:900;color:{mc};line-height:1;margin:8px 0;">{jm["score"]}%</div><span style="background:{mc}18;color:{mc};border:1px solid {mc}44;border-radius:20px;padding:4px 14px;font-size:12px;font-weight:700;">{grade}</span></div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True); st.progress(jm["score"]/100); ce()
        with col2:
            if jm.get("jd_skills"):
                sl=jm["jd_skills"][:8]; rv=[100 if s in jm["verified"] else 15 for s in sl]
                fig=go.Figure(go.Scatterpolar(r=rv+[rv[0]],theta=sl+[sl[0]],fill="toself",fillcolor="rgba(233,30,99,0.08)",line=dict(color="#E91E63",width=2)))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#F0EEF8"),angularaxis=dict(gridcolor="#F0EEF8"),bgcolor="rgba(0,0,0,0)"),paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B6880",size=10),height=240,margin=dict(l=30,r=30,t=20,b=20),showlegend=False)
                st.plotly_chart(fig,use_container_width=True)
        c3,c4=st.columns(2)
        with c3:
            cs("✅ Skills You Have"); st.markdown("".join(f'<span class="tag-good">✓ {s}</span>' for s in jm["verified"]) or "None matched",unsafe_allow_html=True); ce()
        with c4:
            cs("❌ Skills to Learn"); st.markdown("".join(f'<span class="tag-bad">✗ {s}</span>' for s in jm["unverified"]) or "🎉 Full match!",unsafe_allow_html=True); ce()
        st.markdown("<br>",unsafe_allow_html=True); cs("📅 2-Week Action Plan"); st.markdown(jm["plan"]); ce()
    st.markdown('</div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  MARKET INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════
elif page=="📈  Market Intelligence":
    ph("📈 Market Intelligence","How you stack up against 2026 hiring data — computed, not guessed.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    cs("Select Target Role")
    ca,cb=st.columns([2,1])
    with ca: selected=st.selectbox("Role",list(ROLE_MARKET_DATA.keys())+["Other"],key="mkt_sel")
    with cb: custom=st.text_input("Custom role",placeholder="e.g. DevOps Engineer",key="mkt_cust")
    target_role=custom.strip() if custom.strip() else (selected if selected!="Other" else "")
    if st.button("📈 Analyze Market Fit") and target_role:
        resolved=get_closest_role(target_role); md=ROLE_MARKET_DATA.get(resolved) if resolved else None
        user_skills=list(set((st.session_state.github_skills or [])+(st.session_state.resume_skills or [])))
        if not user_skills:
            st.warning("Run Resume Intelligence or GitHub Analysis first.")
        else:
            with st.spinner("Computing market readiness..."):
                if not md:
                    raw=ask_llm(f"For '{target_role}' in 2026, list top 10 skills with demand %. Format: python:90,sql:75,... only.")
                    sd={}
                    for item in raw.split(","):
                        if ":" in item:
                            k,v=item.strip().split(":",1)
                            try: sd[k.strip().lower()]=int(v.strip())
                            except: pass
                    md={"demand":"Active","demand_trend":"Growing","salary_india":"₹6L–₹20L","salary_us":"$75K–$140K",
                        "top_companies":["Various"],"skills":sd,"emerging":[],"description":f"Market data for {target_role}."}
                readiness=compute_market_readiness(user_skills,md["skills"])
            with st.spinner("Generating AI insights..."):
                gap_list=[f"{s} ({d}% demand)" for s,d in readiness["priority_gaps"][:5]]
                ai_insight=ask_llm(f"Role:{target_role}, Readiness:{readiness['score']}%\nMatched:{list(readiness['matched'].keys())[:6]}, Gaps:{gap_list}\nWrite 3-4 sentences: market competitiveness, biggest gaps impact, one fast action.")
            st.session_state.market_role=target_role; st.session_state.market_data=md
            st.session_state.market_readiness=readiness; st.session_state.market_ai_insight=ai_insight
            log_activity(f"Market analysis: {target_role}","📈"); st.success("✅ Done!")
    ce()
    if st.session_state.get("market_readiness") and st.session_state.get("market_data"):
        rd=st.session_state.market_readiness; md=st.session_state.market_data; role=st.session_state.market_role
        rc_color="#22C55E" if rd["score"]>=70 else "#F59E0B" if rd["score"]>=50 else "#E91E63"
        dc={"Very High":"#22C55E","Extremely High":"#7C3AED","High":"#22C55E"}.get(md["demand"],"#F59E0B")
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        with c1:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">MARKET READINESS</div><div style="font-size:40px;font-weight:900;color:{rc_color};margin:8px 0;">{rd["score"]}%</div><div style="font-size:11px;color:#9090A8;">{rd["skills_you_have"]}/{rd["total_skills_required"]} skills matched</div></div>',unsafe_allow_html=True); ce()
        with c2:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">MARKET DEMAND</div><div style="font-size:18px;font-weight:800;color:{dc};margin:8px 0;">{md["demand"]}</div><div style="font-size:12px;color:#22C55E;font-weight:600;">{md["demand_trend"]}</div></div>',unsafe_allow_html=True); ce()
        with c3:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">SALARY INDIA</div><div style="font-size:16px;font-weight:800;color:#E91E63;margin:8px 0;">{md["salary_india"]}</div><div style="font-size:11px;color:#9090A8;">US: {md["salary_us"]}</div></div>',unsafe_allow_html=True); ce()
        with c4:
            cs(); st.markdown(f'<div style="text-align:center;"><div style="font-size:11px;color:#9090A8;font-weight:600;margin-bottom:8px;">SKILL GAPS</div><div style="font-size:40px;font-weight:900;color:#E91E63;margin:8px 0;">{len(rd["missing"])}</div><div style="font-size:11px;color:#9090A8;">to acquire</div></div>',unsafe_allow_html=True); ce()
        st.markdown("<br>",unsafe_allow_html=True)
        left,right=st.columns([3,2])
        with left:
            cs("📊 Skill Demand vs Your Profile","Bar shows job posting frequency. Color shows your status.")
            for skill,pct in sorted(md["skills"].items(),key=lambda x:-x[1]):
                sbar(skill,pct,have_it=skill in rd["matched"],show_status=True)
            ce()
        with right:
            cs("🎯 Priority Skill Gaps","Sorted by demand — fix these first.")
            if rd["priority_gaps"]:
                for i,(skill,demand) in enumerate(rd["priority_gaps"][:6],1):
                    urg="🔴 Critical" if demand>=70 else "🟡 Important" if demand>=50 else "🟢 Nice to have"
                    uc="#E91E63" if demand>=70 else "#F59E0B" if demand>=50 else "#22C55E"
                    st.markdown(f'<div style="background:#FAFAFA;border:1px solid #F0EEF8;border-radius:12px;padding:10px 14px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div style="font-size:13px;font-weight:700;color:#1E1E2E;">#{i} {skill.title()}</div><div style="font-size:12px;font-weight:700;color:#E91E63;">{demand}%</div></div><div style="font-size:11px;color:{uc};margin-top:3px;">{urg}</div></div>',unsafe_allow_html=True)
            ce()
            cs("✅ Market-Validated Skills")
            for skill,demand in sorted(rd["matched"].items(),key=lambda x:-x[1]):
                st.markdown(f'<span class="tag-good">✓ {skill.title()} ({demand}%)</span>',unsafe_allow_html=True)
            ce()
        st.markdown("<br>",unsafe_allow_html=True)
        cs("🤖 AI Market Insight")
        st.markdown(f'<div style="font-size:14px;color:#1E1E2E;line-height:1.8;background:#FFF5F7;border-left:4px solid #E91E63;border-radius:0 12px 12px 0;padding:14px 18px;">{st.session_state.get("market_ai_insight","")}</div>',unsafe_allow_html=True); ce()
        r1,r2,r3=st.columns(3)
        with r1:
            cs("📡 Skill Radar")
            tops=list(md["skills"].keys())[:8]
            fig=go.Figure()
            fig.add_trace(go.Scatterpolar(r=[md["skills"][s] for s in tops]+[md["skills"][tops[0]]],theta=tops+[tops[0]],fill="toself",name="Market",fillcolor="rgba(233,30,99,0.08)",line=dict(color="#E91E63",width=2)))
            fig.add_trace(go.Scatterpolar(r=[rd["matched"].get(s,0) for s in tops]+[rd["matched"].get(tops[0],0)],theta=tops+[tops[0]],fill="toself",name="You",fillcolor="rgba(34,197,94,0.1)",line=dict(color="#22C55E",width=2,dash="dot")))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#F0EEF8"),angularaxis=dict(gridcolor="#F0EEF8"),bgcolor="rgba(0,0,0,0)"),paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B6880",size=9),height=240,margin=dict(l=20,r=20,t=10,b=20),showlegend=True,legend=dict(font=dict(size=9),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.2))
            st.plotly_chart(fig,use_container_width=True); ce()
        with r2:
            cs("🏢 Top Hiring Companies")
            for i,co in enumerate(md["top_companies"],1):
                st.markdown(f'<div style="font-size:13px;font-weight:600;color:#1E1E2E;padding:8px 0;border-bottom:1px solid #F5F3FF;">{i}. {co}</div>',unsafe_allow_html=True)
            ce()
        with r3:
            cs("⚡ Emerging Skills 2026")
            for s in md.get("emerging",[]): st.markdown(f'<span class="tag-emerge">↑ {s}</span>',unsafe_allow_html=True)
            ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  CAREER ROADMAP
# ══════════════════════════════════════════════════════════════════════
elif page=="🗺️  Career Roadmap":
    ph("🗺️ Career Roadmap","Personalized 30-60-90 day plan based on your skills + target role.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    cs("Build Your Roadmap")
    c1,c2=st.columns(2)
    with c1: ghu=st.text_input("GitHub Username",value=(st.session_state.github_data or {}).get("username",""))
    with c2: goal=st.text_input("Target Role",placeholder="e.g. MLOps Engineer")
    if st.button("🗺️ Build Roadmap") and ghu.strip() and goal.strip():
        with st.spinner("Building..."):
            gdata=fetch_github(ghu) if not st.session_state.github_data or st.session_state.github_data.get("username")!=ghu else st.session_state.github_data
        if "error" in gdata: st.error(gdata["error"])
        else:
            with st.spinner("Computing..."):
                rsr=ask_llm(f"List top 8-10 skills for '{goal}' in 2026. Comma-separated only.")
                known=set((st.session_state.github_skills or [])+(st.session_state.resume_skills or [])+[l.lower() for l in gdata.get("languages",[])])
                rs=[s.strip().lower() for s in rsr.split(",") if s.strip()]
                cov={}
                for r in rs:
                    if r in known: cov[r]=100
                    elif any(r in k or k in r for k in known): cov[r]=50
                    else: cov[r]=0
                st.session_state.skill_coverage=cov
                st.session_state.roadmap=ask_llm(f"Skills:{list(known)}\nTarget:{goal}\nRequired:{rsr}\nGive:\n1. SKILLS ALREADY HELD\n2. SKILL GAPS\n3. 30-60-90 day numbered checklist (short specific items)\n4. TODAY first step")
            log_activity(f"Roadmap: {goal}","🗺️"); st.success("✅ Done!")
    ce()
    if st.session_state.get("skill_coverage"):
        st.markdown("<br>",unsafe_allow_html=True)
        cs("📊 Skill Readiness")
        cov=st.session_state.skill_coverage
        fig=go.Figure(go.Scatterpolar(r=list(cov.values())+[list(cov.values())[0]],theta=list(cov.keys())+[list(cov.keys())[0]],fill="toself",fillcolor="rgba(233,30,99,0.08)",line=dict(color="#E91E63",width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#F0EEF8"),angularaxis=dict(gridcolor="#F0EEF8"),bgcolor="rgba(0,0,0,0)"),paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#6B6880",size=11),height=320,margin=dict(l=30,r=30,t=20,b=20),showlegend=False)
        st.plotly_chart(fig,use_container_width=True); st.caption("100 = confirmed · 50 = partial · 0 = not found"); ce()
    if st.session_state.get("roadmap"):
        st.markdown("<br>",unsafe_allow_html=True)
        cs("📋 Your Personalized Plan"); st.markdown(st.session_state.roadmap)
        st.markdown("<hr>",unsafe_allow_html=True)
        st.markdown('<div style="font-size:15px;font-weight:700;color:#1E1E2E;margin-bottom:10px;">✅ Track Milestones</div>',unsafe_allow_html=True)
        ms=["Complete first skill gap course","Build a demo project","Deploy project publicly","Update resume","Apply to 5 roles"]
        for i,m in enumerate(ms):
            k=f"step_{i}"; ch=st.checkbox(m,value=st.session_state.roadmap_progress.get(k,False),key=k); st.session_state.roadmap_progress[k]=ch
        done=sum(st.session_state.roadmap_progress.values()); st.progress(done/len(ms)); st.caption(f"{done}/{len(ms)} milestones complete"); ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  RECRUITER VIEW
# ══════════════════════════════════════════════════════════════════════
elif page=="👔  Recruiter View":
    ph("👔 Recruiter View","One-page candidate card that recruiters actually want to read.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    if not any([st.session_state.portfolio,st.session_state.resume_skills,st.session_state.reality_check]):
        st.warning("Run GitHub Analysis or Resume Intelligence first.")
    else:
        if st.button("👔 Generate Recruiter Summary"):
            with st.spinner("Generating..."):
                tp=[r["name"] for r in st.session_state.portfolio["ranked_repos"][:3]] if st.session_state.portfolio else []
                st.session_state.recruiter_summary=ask_llm(f"""Senior technical recruiter assessment.
GitHub Skills:{st.session_state.github_skills or 'N/A'}, Resume Skills:{st.session_state.resume_skills or 'N/A'}
Portfolio:{st.session_state.portfolio['portfolio_score'] if st.session_state.portfolio else 'N/A'}/100
Credibility:{st.session_state.reality_check['score'] if st.session_state.reality_check else 'N/A'}%
Job Match:{st.session_state.job_match['score'] if st.session_state.job_match else 'N/A'}%
Top Projects:{tp}, ATS:{st.session_state.ats_score or 'N/A'}/100
Write with EXACTLY these sections:
CANDIDATE PROFILE: (2 sentences)
TOP STRENGTHS: (3 bullets with specific skills)
AREAS TO DEVELOP: (2 bullets)
HIRING RECOMMENDATION: (Strong Hire/Hire/Consider/Pass) + 1 sentence reason""")
            log_activity("Recruiter Summary generated","👔"); st.success("✅ Done!")
    if st.session_state.recruiter_summary:
        ds=compute_devpath_score(st.session_state)
        p=st.session_state.portfolio; rc=st.session_state.reality_check; jm=st.session_state.job_match
        gh=st.session_state.github_data or {}
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f'<div style="background:linear-gradient(135deg,#FFF0F7,#F5F0FF);border:1.5px solid #F0EEF8;border-radius:20px;padding:28px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:18px;border-bottom:1px solid #F0EEF8;"><div><div style="font-size:22px;font-weight:800;color:#1E1E2E;">{gh.get("name","Satyanand")}</div><div style="font-size:13px;color:#9090A8;margin-top:2px;">{gh.get("bio","B.Tech AIML · ALIET Vijayawada")}</div></div><div style="text-align:right;"><div style="font-size:11px;color:#9090A8;font-weight:600;">DEVPATH SCORE</div><div style="font-size:36px;font-weight:900;color:#E91E63;">{ds["score"] if ds else "—"}</div></div></div>',unsafe_allow_html=True)
        cols=st.columns(4)
        for i,(icon,label,val,color) in enumerate([("📊","Portfolio",p["portfolio_score"] if p else None,"#E91E63"),("📄","ATS Score",st.session_state.ats_score,"#7C3AED"),("🌉","Credibility",rc["score"] if rc else None,"#22C55E"),("💼","Job Match",jm["score"] if jm else None,"#F59E0B")]):
            with cols[i]:
                v=f"{val}" if val is not None else "—"
                st.markdown(f'<div style="background:rgba(255,255,255,0.8);border:1px solid #F0EEF8;border-radius:12px;padding:12px;text-align:center;"><div style="font-size:18px;">{icon}</div><div style="font-size:10px;color:#9090A8;font-weight:600;margin:4px 0;">{label}</div><div style="font-size:22px;font-weight:800;color:{color};">{v}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f'<div style="background:rgba(255,255,255,0.8);border:1px solid #F0EEF8;border-radius:14px;padding:20px;margin-bottom:16px;"><div style="font-size:11px;font-weight:700;color:#E91E63;letter-spacing:1px;margin-bottom:10px;">AI RECRUITER ASSESSMENT</div><div style="font-size:13px;color:#1E1E2E;line-height:1.8;white-space:pre-wrap;">{st.session_state.recruiter_summary}</div></div>',unsafe_allow_html=True)
        all_skills=list(set((st.session_state.github_skills or [])+(st.session_state.resume_skills or [])))[:14]
        if all_skills:
            st.markdown('<div style="font-size:11px;font-weight:700;color:#9090A8;letter-spacing:0.5px;margin-bottom:8px;">TOP SKILLS</div>',unsafe_allow_html=True)
            st.markdown("".join(f'<span class="tag-pink">{s}</span>' for s in all_skills),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        pdf_data=generate_career_pdf(st.session_state)
        ext="pdf" if pdf_data[:4]==b"%PDF" else "txt"
        st.download_button("📥 Download Full Recruiter Report",pdf_data,file_name="devpath_recruiter_report.pdf",mime="application/pdf" if ext=="pdf" else "text/plain",use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  INTERVIEW PREP
# ══════════════════════════════════════════════════════════════════════
elif page=="🎤  Interview Prep":
    ph("🎤 Interview Prep","Role-specific questions with instant AI feedback on your answers.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    cs("Generate Questions")
    c1,c2=st.columns(2)
    with c1: tr=st.text_input("Target Role",placeholder="e.g. AI Engineer")
    with c2: diff=st.selectbox("Difficulty",["Beginner","Intermediate","Advanced"])
    if st.button("🎤 Generate Questions") and tr.strip():
        with st.spinner("🔍 Retrieving interview questions from database..."):
            known=list(set((st.session_state.github_skills or [])+(st.session_state.resume_skills or [])))

            rag_questions = []
            if RAG_AVAILABLE:
                try:
                    devpath_rag.initialize()
                    rag_questions = devpath_rag.retrieve_interview_questions(tr, n=5)
                except Exception:
                    rag_questions = []

            if rag_questions:
                formatted = "\n".join([
                    f"Q{i+1}: {q['question']}\nHINT: {q['hint']}"
                    for i,q in enumerate(rag_questions[:5])
                ])
                resp = ask_llm(f"""You are a senior technical interviewer.
The following questions were retrieved from our interview database for {tr} at {diff} level.
Candidate skills: {known[:8] if known else 'unknown'}

Retrieved questions:
{formatted}

Review and improve these questions for the candidate's level. Keep the same Q/HINT format exactly.
Return exactly 5 questions in this format:
Q1: [question]
HINT: [what good answer covers]
Q2: ...""")
                st.session_state.interview_source = f"RAG Database + AI ({len(rag_questions)} questions retrieved)"
            else:
                resp=ask_llm(f"Senior interviewer at top tech company.\n5 interview questions for '{tr}' at '{diff}' level.\nCandidate knows:{known[:10] if known else 'unknown'}\nFormat EXACTLY:\nQ1: [question]\nHINT: [one line what good answer covers]\nQ2: ... up to Q5. Make technical and specific.")
                st.session_state.interview_source = "AI Generated"

            st.session_state.interview_questions=resp; st.session_state.interview_role=tr
            st.session_state.interview_feedback={}
        log_activity(f"Interview prep: {tr}","🎤"); st.success("✅ Questions ready!")
    ce()
    if st.session_state.get("interview_questions"):
        st.markdown("<br>",unsafe_allow_html=True)
        source = st.session_state.get("interview_source","")
        source_badge = f'<span style="background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;margin-left:10px;">🔍 {source}</span>' if source else ""
        cs(f"🎤 {st.session_state.get('interview_role','')} Interview Questions")
        if source:
            st.markdown(f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:8px 14px;margin-bottom:12px;font-size:12px;color:#16A34A;font-weight:600;">🔍 Source: {source}</div>',unsafe_allow_html=True)
        lines=st.session_state.interview_questions.strip().split('\n')
        questions=[]; i=0
        while i<len(lines):
            line=lines[i].strip()
            if line.startswith('Q') and ':' in line:
                qt=line.split(':',1)[1].strip(); hint=""
                if i+1<len(lines) and lines[i+1].strip().startswith('HINT'):
                    hint=lines[i+1].split(':',1)[1].strip(); i+=1
                questions.append({"q":qt,"hint":hint})
            i+=1
        if not st.session_state.get("interview_feedback"): st.session_state.interview_feedback={}
        for idx,q in enumerate(questions):
            st.markdown(f'<div style="background:#FAFAFA;border:1px solid #F0EEF8;border-left:4px solid #E91E63;border-radius:12px;padding:14px 18px;margin-bottom:8px;"><div style="font-size:11px;font-weight:700;color:#E91E63;margin-bottom:4px;">QUESTION {idx+1}</div><div style="font-size:14px;font-weight:600;color:#1E1E2E;margin-bottom:4px;">{q["q"]}</div><div style="font-size:11px;color:#9090A8;">💡 {q["hint"]}</div></div>',unsafe_allow_html=True)
            ans=st.text_area(f"Your answer to Q{idx+1}",key=f"ans_{idx}",height=90,label_visibility="collapsed",placeholder="Type your answer...")
            if st.button(f"⚡ Get Feedback on Q{idx+1}",key=f"fb_{idx}"):
                if ans.strip():
                    with st.spinner("Evaluating..."):
                        fb=ask_llm(f"Evaluate this interview answer:\nQuestion:{q['q']}\nAnswer:{ans}\nFormat:\nSCORE: [X/10]\nWHAT'S GOOD: [1-2 sentences]\nWHAT'S MISSING: [1-2 sentences]\nIDEAL ANSWER: [2-3 sentences]")
                        st.session_state.interview_feedback[idx]=fb
            if idx in st.session_state.interview_feedback:
                st.markdown(f'<div style="background:#FFF5F7;border:1px solid #FFD6E0;border-left:4px solid #E91E63;border-radius:10px;padding:12px 16px;margin-top:6px;"><div style="font-size:11px;font-weight:700;color:#E91E63;margin-bottom:6px;">AI FEEDBACK</div><div style="font-size:13px;color:#1E1E2E;line-height:1.6;white-space:pre-wrap;">{st.session_state.interview_feedback[idx]}</div></div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
        ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════
elif page=="🔍  Opportunities":
    ph("🔍 Opportunities","Real search links built from your skills.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)
    skills=st.session_state.resume_skills or st.session_state.github_skills or []
    if not skills:
        st.warning("Run Resume Intelligence or GitHub Analysis first.")
    else:
        query="+".join(skills[:5])
        pl=(st.session_state.github_data or {}).get("languages",["python"])
        pl=pl[0].lower() if pl else "python"
        cs("🎯 Best-Fit Role Recommendations")
        if st.button("✨ Generate Recommendations"):
            with st.spinner("Analyzing..."):
                st.session_state.internship_recs=ask_llm(f"Skills:{skills[:15]}\nSuggest 4 specific internship/job roles.\nFor each: ROLE | MATCH % | REASON (1 sentence) | APPLY AT (platform)")
        if st.session_state.get("internship_recs"): st.markdown(st.session_state.internship_recs)
        ce()
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            cs("💼 Jobs & Internships")
            st.markdown(f"- 🔗 [LinkedIn](https://www.linkedin.com/jobs/search/?keywords={query})\n- 🔗 [Indeed](https://www.indeed.com/jobs?q={query})\n- 🔗 [Naukri](https://www.naukri.com/{query.replace('+','-')}-jobs)\n- 🔗 [Internshala](https://internshala.com/internships/keywords-{skills[0]})\n- 🔗 [Wellfound](https://wellfound.com/jobs)")
            ce()
        with c2:
            cs("🏆 Hackathons & Open Source")
            st.markdown(f"- 🔗 [Devpost](https://devpost.com/hackathons)\n- 🔗 [Unstop](https://unstop.com/hackathons)\n- 🔗 [GitHub good first issues ({pl})](https://github.com/search?q=label%3A%22good+first+issue%22+language%3A{pl}&type=issues&state=open)\n- 🔗 [GitHub help wanted ({pl})](https://github.com/search?q=label%3A%22help+wanted%22+language%3A{pl}&type=issues&state=open)")
            ce()
    st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  CAREER CHAT — RAG-Powered Personalized
# ══════════════════════════════════════════════════════════════════════
elif page=="💬  Career Chat":
    ph("💬 Career Chat","Personalized answers using your profile + RAG knowledge base.")
    st.markdown('<div style="padding:0 28px;">',unsafe_allow_html=True)

    user_context = ""
    if st.session_state.resume_skills or st.session_state.github_skills:
        all_skills = list(set((st.session_state.resume_skills or []) + (st.session_state.github_skills or [])))
        user_context += f"User skills: {', '.join(all_skills[:12])}\n"
    if st.session_state.ats_score is not None:
        user_context += f"ATS Score: {st.session_state.ats_score}/100\n"
    if st.session_state.portfolio:
        user_context += f"Portfolio Score: {st.session_state.portfolio['portfolio_score']}/100\n"
    if st.session_state.reality_check:
        user_context += f"Credibility Score: {st.session_state.reality_check['score']}%\n"
        if st.session_state.reality_check.get("unverified"):
            user_context += f"Skills lacking GitHub evidence: {', '.join(st.session_state.reality_check['unverified'][:5])}\n"
    if st.session_state.get("market_readiness"):
        user_context += f"Market Readiness: {st.session_state.market_readiness['score']}%\n"
        gaps = [s for s,_ in st.session_state.market_readiness['priority_gaps'][:3]]
        if gaps: user_context += f"Top skill gaps: {', '.join(gaps)}\n"

    if user_context:
        st.markdown(f'''
        <div style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:12px;padding:12px 16px;margin-bottom:16px;">
            <div style="font-size:11px;font-weight:700;color:#7C3AED;letter-spacing:1px;margin-bottom:6px;">YOUR PROFILE CONTEXT (used in every answer)</div>
            <div style="font-size:12px;color:#4A4A5A;line-height:1.7;">{user_context.replace(chr(10), "<br>")}</div>
        </div>''',unsafe_allow_html=True)

    cs()
    st.markdown('<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;"><span class="tag-pink">💡 What should I learn next?</span><span class="tag-pink">📝 Write my cold email</span><span class="tag-pink">🚀 Am I ready for AI Engineer?</span><span class="tag-pink">💰 Salary negotiation tips</span></div>',unsafe_allow_html=True)

    q = st.text_area("Your question", height=110, label_visibility="collapsed",
                     placeholder="e.g. Am I ready for an AI Engineer internship? What should I focus on?")

    if st.button("💬 Ask Agent") and q.strip():
        with st.spinner("🔍 Searching knowledge base..."):
            rag_context = ""
            retrieved_info = {}

            if RAG_AVAILABLE:
                try:
                    devpath_rag.initialize()

                    career_k = devpath_rag.retrieve_career_knowledge(q, n=2)
                    if career_k:
                        rag_context += "\nRelevant career knowledge:\n"
                        for c in career_k:
                            rag_context += f"- [{c['topic']}]: {c['content'][:200]}\n"
                        retrieved_info["career"] = len(career_k)

                    if any(w in q.lower() for w in ["ready","job","internship","role","apply","ai engineer","ml","skills"]):
                        all_skills = list(set((st.session_state.resume_skills or []) + (st.session_state.github_skills or [])))
                        role_q = st.session_state.get("market_role","AI Engineer")
                        jobs = devpath_rag.retrieve_jobs(role_q, all_skills, n=3)
                        if jobs:
                            rag_context += f"\nRelevant {role_q} jobs from database:\n"
                            for j in jobs[:3]:
                                rag_context += f"- {j['company']}: needs {', '.join(j['skills'][:4])} | {j['salary_india']}\n"
                            retrieved_info["jobs"] = len(jobs)
                            retrieved_info["_jobs"] = jobs[:3]

                    if any(w in q.lower() for w in ["learn","course","resource","study","improve","start"]):
                        gaps = [s for s,_ in st.session_state.get("market_readiness",{}).get("priority_gaps",[])[:3]] if st.session_state.get("market_readiness") else []
                        if gaps:
                            lr = devpath_rag.retrieve_learning_resources(gaps, n=3)
                            if lr:
                                rag_context += "\nRecommended learning resources:\n"
                                for r in lr:
                                    rag_context += f"- {r['skill'].title()}: {r['resource']} ({r['time']}) — {r['url']}\n"
                                retrieved_info["resources"] = len(lr)
                except Exception as e:
                    pass

        if retrieved_info and RAG_AVAILABLE:
            st.markdown('''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;
                padding:16px 20px;margin-bottom:16px;">
                <div style="font-size:12px;font-weight:800;color:#16A34A;letter-spacing:1px;margin-bottom:10px;">
                    🔍 RETRIEVED EVIDENCE FROM KNOWLEDGE BASE
                </div>''', unsafe_allow_html=True)

            if "jobs" in retrieved_info and retrieved_info.get("_jobs"):
                st.markdown('<div style="font-size:11px;font-weight:700;color:#4A4A5A;margin-bottom:6px;">💼 MATCHING JOB PROFILES</div>', unsafe_allow_html=True)
                for j in retrieved_info["_jobs"][:3]:
                    st.markdown(f'''<div style="display:flex;align-items:center;justify-content:space-between;
                        background:white;border:1px solid #BBF7D0;border-radius:8px;
                        padding:8px 12px;margin-bottom:4px;">
                        <div>
                            <span style="font-size:13px;font-weight:700;color:#1E1E2E;">✓ {j["company"]}</span>
                            <span style="font-size:11px;color:#6B6880;margin-left:8px;">{j["role"]}</span>
                        </div>
                        <span style="font-size:11px;font-weight:600;color:#16A34A;">{j["salary_india"]}</span>
                    </div>''', unsafe_allow_html=True)

            if "jobs" in retrieved_info and retrieved_info.get("_jobs"):
                all_matched = []
                user_sk = set((st.session_state.resume_skills or []) + (st.session_state.github_skills or []))
                for j in retrieved_info["_jobs"][:3]:
                    for sk in j.get("skills",[]):
                        if sk in user_sk and sk not in all_matched:
                            all_matched.append(sk)
                if all_matched:
                    skills_html = " ".join([f'<span style="background:#DCFCE7;color:#16A34A;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:600;margin:2px;">{s.title()}</span>' for s in all_matched[:6]])
                    st.markdown(f'<div style="margin-top:8px;"><span style="font-size:11px;color:#6B6880;font-weight:600;">MATCHED SKILLS: </span>{skills_html}</div>', unsafe_allow_html=True)

            if "career" in retrieved_info:
                st.markdown(f'<div style="font-size:11px;color:#6B6880;margin-top:8px;">📚 {retrieved_info["career"]} career knowledge articles retrieved</div>', unsafe_allow_html=True)

            if "resources" in retrieved_info:
                st.markdown(f'<div style="font-size:11px;color:#6B6880;margin-top:4px;">🎓 {retrieved_info["resources"]} learning resources matched</div>', unsafe_allow_html=True)

            st.markdown('<div style="font-size:11px;color:#16A34A;font-weight:600;margin-top:10px;">🤖 Building personalized recommendation from retrieved evidence...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("🤖 Generating personalized answer..."):
            personalized_prompt = f"""You are DevPath AI — a personalized career intelligence platform.

USER PROFILE:
{user_context if user_context else "No profile data yet — give general advice."}

RETRIEVED KNOWLEDGE FROM DATABASE:
{rag_context if rag_context else "No additional context retrieved."}

USER QUESTION: {q}

Answer with SPECIFIC personalization based on their actual scores and skills.
Format your answer in clear sections with specific actionable steps.
Reference their actual scores (ATS, Portfolio, Credibility) when relevant.
Keep it concise but highly specific — not generic."""

            answer = ask_openai_direct(personalized_prompt,
                system="You are DevPath AI, a career intelligence platform powered by OpenAI GPT-4o. Give specific, evidence-based career advice.")

        st.markdown(f'''
        <div style="background:#FFF5F7;border:1px solid #FFD6E0;border-left:4px solid #E91E63;
             border-radius:12px;padding:18px 22px;margin-top:14px;">
            <div style="font-size:11px;font-weight:700;color:#E91E63;letter-spacing:1px;margin-bottom:10px;">
                PERSONALIZED ANSWER {'(RAG-Enhanced)' if rag_context else ''}
            </div>
            <div style="font-size:14px;color:#1E1E2E;line-height:1.7;">{answer}</div>
        </div>''', unsafe_allow_html=True)
    ce()
    st.markdown('</div>',unsafe_allow_html=True)