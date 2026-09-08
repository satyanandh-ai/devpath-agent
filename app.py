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
#  SKILL EVIDENCE ENGINE (embedded)
# ══════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
#  SKILL EVIDENCE ENGINE — Central source of truth for DevPath
#  ONE canonical taxonomy. Every module reads from this.
#  Fix 1: No duplicates. Fix 2: git ≠ github. Fix 4: 5 evidence levels.
#  Fix 5: Traceable evidence. Fix 6: Single canonical taxonomy.
# ══════════════════════════════════════════════════════════════════════

import requests
import re
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════
#  THE ONE CANONICAL SKILL TAXONOMY — DevPath single source of truth
#
#  Rules enforced:
#  1. git ≠ github (separate skills, separate evidence)
#  2. javascript ≠ typescript (related but NOT the same)
#  3. java ≠ spring (framework ≠ language)
#  4. Each skill maps only to its direct aliases — no overreach
#  5. This is the ONLY definition — no other taxonomy exists in this file
# ══════════════════════════════════════════════════════════════════════
SKILL_SYNONYMS = {
    # ── Programming Languages ─────────────────────────────────────────
    "python":               {"python3", "python2"},
    "javascript":           {"javascript", "js", "node.js", "nodejs"},
    "typescript":           {"typescript", "ts"},           # separate from javascript
    "java":                 {"java"},                        # separate from spring
    "spring":               {"spring", "springboot", "spring boot"},
    "sql":                  {"sql", "structured query language"},
    "mysql":                {"mysql"},
    "postgresql":           {"postgresql", "postgres", "psql"},
    "sqlite":               {"sqlite"},

    # ── AI / ML ───────────────────────────────────────────────────────
    "machine learning":     {"machine learning", "ml"},
    "deep learning":        {"deep learning", "dl", "neural network"},
    "pytorch":              {"pytorch", "torch"},
    "tensorflow":           {"tensorflow", "keras", "tf"},
    "scikit-learn":         {"scikit-learn", "sklearn", "scikit learn"},
    "nlp":                  {"natural language processing", "nlp", "spacy", "nltk"},
    "computer vision":      {"computer vision", "opencv", "cv2", "image recognition"},

    # ── LLM / GenAI ───────────────────────────────────────────────────
    "llm":                  {"large language model", "llm", "llms"},
    "langchain":            {"langchain"},
    "langgraph":            {"langgraph"},
    "rag":                  {"rag", "retrieval augmented generation", "retrieval-augmented generation"},
    "prompt engineering":   {"prompt engineering", "prompt design", "chain of thought"},
    "openai api":           {"openai api", "chatgpt api", "gpt-4", "gpt-3"},
    "groq":                 {"groq", "groq api"},
    "huggingface":          {"huggingface", "hugging face", "transformers"},

    # ── DevOps / Infra ────────────────────────────────────────────────
    "docker":               {"docker", "dockerfile", "docker-compose", "docker compose", "containerization"},
    "kubernetes":           {"kubernetes", "k8s", "kubectl", "helm"},
    "aws":                  {"aws", "amazon web services", "boto3", "s3", "ec2", "aws lambda", "sagemaker"},
    "gcp":                  {"gcp", "google cloud", "bigquery", "cloud run"},
    "azure":                {"azure", "microsoft azure"},
    "ci/cd":                {"ci/cd", "github actions", "jenkins", "gitlab ci", "cicd", "continuous integration"},
    "linux":                {"linux", "ubuntu", "bash", "shell script", "unix"},
    "terraform":            {"terraform", "infrastructure as code"},

    # ── Version Control — git ≠ github (enforced) ─────────────────────
    "git":                  {"git", "version control", "git commit", "git push", "git clone"},
    "github":               {"github", "github.com", "github repo"},
    "github-api":           {"github api", "pygithub", "octokit"},

    # ── Web Frameworks ────────────────────────────────────────────────
    "fastapi":              {"fastapi", "fast api"},
    "flask":                {"flask"},
    "django":               {"django", "django rest framework"},
    "rest api":             {"rest api", "restful api", "api development", "http api"},

    # ── Data Engineering ──────────────────────────────────────────────
    "pandas":               {"pandas"},
    "numpy":                {"numpy"},
    "spark":                {"spark", "pyspark", "apache spark"},
    "airflow":              {"airflow", "apache airflow"},
    "mlflow":               {"mlflow"},
    "dbt":                  {"dbt", "data build tool"},

    # ── Databases ─────────────────────────────────────────────────────
    "mongodb":              {"mongodb", "mongo", "pymongo"},
    "redis":                {"redis"},
    "vector database":      {"chromadb", "pinecone", "weaviate", "qdrant", "faiss", "milvus", "vector database"},

    # ── Viz / UI ──────────────────────────────────────────────────────
    "streamlit":            {"streamlit"},
    "plotly":               {"plotly"},
    "tableau":              {"tableau"},
    "power bi":             {"power bi", "powerbi"},

    # ── Other Tools ───────────────────────────────────────────────────
    "jupyter":              {"jupyter", "jupyter notebook", "ipynb"},
    "reportlab":            {"reportlab"},
    "opencv":               {"opencv", "cv2"},
}

# ══════════════════════════════════════════════════════════════════════
#  5 EVIDENCE LEVELS — Standard language across ALL DevPath modules
# ══════════════════════════════════════════════════════════════════════
EVIDENCE_LEVELS = {
    "Confirmed": "Strong direct evidence from multiple reliable sources",
    "Strong":    "Multiple reliable signals — resume + GitHub file inspection",
    "Partial":   "Some evidence but incomplete — resume mention or metadata only",
    "Weak":      "Weak or indirect signal — description mention or topic tag",
    "Not Found": "No evidence detected in resume or GitHub",
}

def normalize_skill(skill: str) -> str:
    """
    Normalize a raw skill string to its canonical form.

    Bug fix: substring matching removed — only exact canonical or alias match.
    Phrase normalization (whitespace/punctuation) is applied before matching.
    No arbitrary substring logic that can produce false positives.
    """
    # Clean: lowercase, strip, normalize whitespace and punctuation
    s = skill.lower().strip()
    s = re.sub(r"[\.\,;:()/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # 1. Direct canonical match
    if s in SKILL_SYNONYMS:
        return s

    # 2. Exact alias match
    for canonical, synonyms in SKILL_SYNONYMS.items():
        if s in synonyms:
            return canonical

    # 3. Controlled phrase normalization only:
    #    Allow matching if cleaned version matches exactly
    #    (e.g. "scikit learn" → "scikit-learn", "node js" → "javascript")
    s_nopunct = re.sub(r"[-_\s]+", " ", s).strip()
    if s_nopunct in SKILL_SYNONYMS:
        return s_nopunct
    for canonical, synonyms in SKILL_SYNONYMS.items():
        canon_nopunct = re.sub(r"[-_\s]+", " ", canonical).strip()
        if s_nopunct == canon_nopunct:
            return canonical
        for syn in synonyms:
            syn_nopunct = re.sub(r"[-_\s]+", " ", syn).strip()
            if s_nopunct == syn_nopunct:
                return canonical

    # 4. No match — return cleaned string as-is (never do substring guessing)
    return s

def normalize_skill_list(skills: list) -> list:
    """Deduplicate and normalize a list of skills to canonical forms."""
    seen = set()
    result = []
    for skill in skills:
        if not skill or not skill.strip():
            continue
        normalized = normalize_skill(skill)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return sorted(result)

MARKET_DEMAND = {
    "python": 95, "fastapi": 71, "langchain": 82, "langgraph": 72,
    "rag": 82, "docker": 65, "kubernetes": 42, "aws": 54,
    "gcp": 38, "azure": 45, "pytorch": 58, "tensorflow": 52,
    "scikit-learn": 48, "pandas": 70, "numpy": 65, "sql": 63,
    "mongodb": 40, "redis": 38, "git": 90, "ci/cd": 55,
    "mlflow": 35, "airflow": 30, "spark": 28, "nlp": 55,
    "machine learning": 72, "deep learning": 58, "llm": 80,
    "vector database": 75, "streamlit": 45, "flask": 48,
    "django": 42, "rest api": 78, "linux": 60,
    "prompt engineering": 80,
}

def _text_has_skill(text: str, skill: str) -> bool:
    """
    Check if text contains a skill using word-boundary matching.
    Prevents false positives like 'git' matching inside other words.
    """
    text_lower = text.lower()
    terms = SKILL_SYNONYMS.get(skill, set()) | {skill}
    for term in terms:
        if not term:
            continue
        # Use word-boundary regex for short terms (avoids substring false positives)
        if len(term) <= 4:
            pattern = r'' + re.escape(term) + r''
        else:
            # Longer terms — substring is acceptable (e.g. "langchain" in "uses langchain")
            pattern = re.escape(term)
        if re.search(pattern, text_lower):
            return True
    return False

# ══════════════════════════════════════════════════════════════════════
#  GITHUB EVIDENCE ENGINE
# ══════════════════════════════════════════════════════════════════════
def fetch_github_evidence(username: str, github_token: str = "") -> dict:
    """
    Deep GitHub analysis — inspects repo contents, not just metadata.
    Returns per-skill evidence with repo names, files, and strength.
    """
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    # 1. Fetch user repos
    try:
        resp = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100",
            headers=headers, timeout=10
        )
        if resp.status_code != 200:
            return {"error": f"GitHub API error: {resp.status_code}"}
        repos = resp.json()
        if not isinstance(repos, list):
            return {"error": "Invalid GitHub response"}
    except Exception as e:
        return {"error": str(e)}

    # 2. Build evidence map: skill → list of evidence items
    evidence_map = {skill: [] for skill in SKILL_SYNONYMS}

    for repo in repos[:15]:  # inspect top 15 repos
        repo_name = repo.get("name", "")
        repo_desc = repo.get("description") or ""
        repo_lang = repo.get("language") or ""
        repo_topics = repo.get("topics") or []
        repo_url = repo.get("html_url", "")

        # Check language
        for skill in SKILL_SYNONYMS:
            if _text_has_skill(repo_lang, skill):
                evidence_map[skill].append({
                    "repo": repo_name,
                    "type": "language",
                    "detail": f"Primary language: {repo_lang}",
                    "url": repo_url
                })

        # Check description
        for skill in SKILL_SYNONYMS:
            if _text_has_skill(repo_desc, skill):
                evidence_map[skill].append({
                    "repo": repo_name,
                    "type": "description",
                    "detail": f"Mentioned in repo description",
                    "url": repo_url
                })

        # Check topics
        topics_text = " ".join(repo_topics)
        for skill in SKILL_SYNONYMS:
            if _text_has_skill(topics_text, skill):
                evidence_map[skill].append({
                    "repo": repo_name,
                    "type": "topic",
                    "detail": f"Tagged as topic: {', '.join(t for t in repo_topics if _text_has_skill(t, skill))}",
                    "url": repo_url
                })

        # Inspect README and requirements.txt for key repos
        if not repo.get("fork") and repo.get("stargazers_count", 0) >= 0:
            for fname in ["requirements.txt", "README.md", "Dockerfile", "docker-compose.yml"]:
                try:
                    file_resp = requests.get(
                        f"https://api.github.com/repos/{username}/{repo_name}/contents/{fname}",
                        headers=headers, timeout=5
                    )
                    if file_resp.status_code == 200:
                        import base64
                        file_data = file_resp.json()
                        if file_data.get("encoding") == "base64":
                            file_content = base64.b64decode(file_data["content"]).decode("utf-8", errors="ignore")
                            for skill in SKILL_SYNONYMS:
                                if _text_has_skill(file_content, skill):
                                    # Don't duplicate same repo+skill+file
                                    existing = [e for e in evidence_map[skill] if e["repo"]==repo_name and e["type"]==f"file:{fname}"]
                                    if not existing:
                                        evidence_map[skill].append({
                                            "repo": repo_name,
                                            "type": f"file:{fname}",
                                            "detail": f"Found in {fname}",
                                            "url": repo_url
                                        })
                except Exception:
                    continue

    # 3. Compute evidence strength per skill
    result = {}
    for skill, evidence in evidence_map.items():
        if not evidence:
            result[skill] = {
                "evidence": [],
                "repos": [],
                "strength": "Not Found",
                "strength_score": 0
            }
            continue

        repos_found = list({e["repo"] for e in evidence})
        file_evidence = [e for e in evidence if e["type"].startswith("file:")]
        topic_evidence = [e for e in evidence if e["type"] == "topic"]

        # Strength scoring
        score = 0
        score += len(repos_found) * 20          # 20pts per repo
        score += len(file_evidence) * 15         # 15pts per file hit
        score += len(topic_evidence) * 10        # 10pts per topic tag
        score = min(100, score)

        if score >= 70:   strength = "Strong"
        elif score >= 40: strength = "Partial"
        elif score >= 10: strength = "Weak"
        else:             strength = "Not Found"

        result[skill] = {
            "evidence": evidence[:5],  # keep top 5 evidence items
            "repos": repos_found,
            "strength": strength,
            "strength_score": score
        }

    return result


# ══════════════════════════════════════════════════════════════════════
#  SKILL EVIDENCE ENGINE — Central source of truth
# ══════════════════════════════════════════════════════════════════════
def build_skill_matrix(
    resume_text: str,
    resume_skills: list,
    github_evidence: dict,
    target_role: str = "AI Engineer",
    role_skills: dict = None
) -> dict:
    """
    Build the central Skill Matrix — the single source of truth.

    Fix 3: Evidence and Readiness are now SEPARATE concepts.

    EVIDENCE  = what signals exist (resume mention + GitHub depth)
    READINESS = evidence × role_requirement × market_demand

    Returns per-skill dict with full traceable evidence chain.
    """
    matrix = {}
    role_skills = role_skills or {}

    # Normalize all inputs using canonical taxonomy
    normalized_resume_skills = normalize_skill_list(resume_skills)

    # All skills to evaluate = canonical skills + resume skills
    all_skills = set(SKILL_SYNONYMS.keys()) | set(normalized_resume_skills)

    for skill in sorted(all_skills):
        # ── STEP 1: Collect raw evidence (separate from readiness) ──────
        # Resume evidence
        resume_has = (
            skill in normalized_resume_skills or
            _text_has_skill(resume_text, skill)
        )

        # GitHub evidence — look up canonical skill
        gh_data = github_evidence.get(skill, {})
        if not gh_data:
            canonical = normalize_skill(skill)
            gh_data = github_evidence.get(canonical, {})

        gh_strength     = gh_data.get("strength", "Not Found")
        gh_evidence_items = gh_data.get("evidence", [])
        gh_repos        = gh_data.get("repos", [])

        # ── STEP 2: Compute evidence level (5 levels, traceable) ─────────
        # Evidence = purely what we found, NOT readiness yet
        # Check if strong file evidence exists (Dockerfile, config, requirements)
        # README mention alone does NOT qualify as "Confirmed"
        has_file_evidence = any(
            e.get("type","").startswith("file:") and
            "readme" not in e.get("type","").lower()
            for e in gh_evidence_items
        )

        if resume_has and gh_strength == "Strong" and has_file_evidence:
            evidence_level = "Confirmed"
            evidence_reason = f"Resume + GitHub file evidence in {', '.join(gh_repos[:2]) or 'repos'}"
        elif resume_has and gh_strength == "Strong" and not has_file_evidence:
            evidence_level = "Strong"
            evidence_reason = f"Resume mention + GitHub metadata/README in {', '.join(gh_repos[:2]) or 'repos'}"
        elif resume_has and gh_strength == "Partial":
            evidence_level = "Strong"
            evidence_reason = f"Resume mention + partial GitHub evidence"
        elif resume_has and gh_strength == "Weak":
            evidence_level = "Partial"
            evidence_reason = "Resume mention + weak GitHub signal (topic/description only)"
        elif resume_has and gh_strength == "Not Found":
            evidence_level = "Partial"
            evidence_reason = "Resume mention only — no GitHub evidence found"
        elif not resume_has and gh_strength in ("Strong", "Partial"):
            evidence_level = "Weak"
            evidence_reason = f"GitHub only — not on resume ({', '.join(gh_repos[:2])})"
        else:
            evidence_level = "Not Found"
            evidence_reason = "No evidence in resume or GitHub"

        # ── STEP 3: Compute readiness SEPARATELY from evidence ───────────
        # Readiness = evidence_score × role_weight × market_weight
        market = MARKET_DEMAND.get(skill, 0)
        role_required = skill in [normalize_skill(s) for s in role_skills.keys()]

        # Evidence score (0-100)
        evidence_score = {
            "Confirmed": 100,
            "Strong":    75,
            "Partial":   45,
            "Weak":      20,
            "Not Found": 0,
        }.get(evidence_level, 0)

        # Role weight
        role_weight = 1.3 if role_required else 1.0

        # Raw readiness = evidence score (role weight is for gap priority, not readiness)
        readiness = min(100, round(evidence_score * role_weight / 1.3))

        # ── STEP 4: Priority is NOT computed here (belongs in Phase 4/5 Gap Engine)
        # Priority requires: role requirements + market demand + readiness
        # These are computed AFTER the matrix is built, not inside it.
        # See compute_gap_priorities() for the priority computation.

        # ── STEP 5: Build traceable evidence chain ────────────────────────
        evidence_trace = []
        if resume_has:
            evidence_trace.append({
                "source": "Resume",
                "detail": f"Skill mentioned in uploaded resume",
                "strength": "Direct"
            })
        for ev in gh_evidence_items[:3]:
            evidence_trace.append({
                "source":   "GitHub",
                "repo":     ev.get("repo", ""),
                "file":     ev.get("type", "").replace("file:", ""),
                "detail":   ev.get("detail", ""),
                "strength": gh_strength,
                "url":      ev.get("url", "")
            })

        matrix[skill] = {
            # ── Evidence (Phase 1 — what we found) ───────────────────
            "resume":           resume_has,
            "github_strength":  gh_strength,
            "github_evidence":  gh_evidence_items,
            "github_repos":     gh_repos,
            "evidence_level":   evidence_level,    # Confirmed/Strong/Partial/Weak/Not Found
            "evidence_reason":  evidence_reason,   # Human-readable explanation
            "evidence_trace":   evidence_trace,    # Full traceable chain

            # ── Readiness (computed from evidence only, no role/market yet) ──
            "readiness":        readiness,

            # ── Market context (stored for Phase 4/5 use) ──────────────
            "market_demand":    market,            # Hiring demand % (NOT user proficiency)
            "role_required":    role_required,

            # ── Backward compat alias ─────────────────────────────────
            "confidence":       evidence_level,
            # priority is NOT stored here — computed in compute_gap_priorities()
        }

    return matrix


# ══════════════════════════════════════════════════════════════════════
#  GAP + PRIORITY ENGINE
# ══════════════════════════════════════════════════════════════════════
def compute_gap_priorities(skill_matrix: dict) -> list:
    """
    Rank skill gaps by:
      role_weight × market_demand × (1 - readiness) × evidence_factor

    Bug fix: priority_label is computed HERE from priority_score.
    build_skill_matrix() does NOT store "priority" — that belongs here.
    """
    gaps = []
    for skill, data in skill_matrix.items():
        readiness = data.get("readiness", 0)
        if readiness >= 90:
            continue  # already strong — skip

        role_required = data.get("role_required", False)
        market_demand = data.get("market_demand", 0)
        evidence_level = data.get("evidence_level", data.get("confidence", "Not Found"))

        role_w = 1.5 if role_required else 1.0
        market_w = market_demand / 100
        gap_w = (100 - readiness) / 100
        evidence_factor = {
            "Confirmed": 0.1,
            "Strong":    0.3,
            "Partial":   0.7,
            "Weak":      0.9,
            "Not Found": 1.0,
        }.get(evidence_level, 1.0)

        priority_score = round(role_w * market_w * gap_w * evidence_factor * 100)

        if priority_score < 5:
            continue

        # Compute priority_label from score — NOT from matrix["priority"]
        if priority_score >= 60:
            priority_label = "Critical"
        elif priority_score >= 40:
            priority_label = "High"
        elif priority_score >= 20:
            priority_label = "Medium"
        else:
            priority_label = "Low"

        gaps.append({
            "skill":          skill,
            "priority_score": priority_score,
            "priority_label": priority_label,   # computed here, not from matrix
            "readiness":      readiness,
            "market_demand":  market_demand,
            "evidence_level": evidence_level,
            "confidence":     evidence_level,   # alias for backward compat
            "role_required":  role_required,
        })

    return sorted(gaps, key=lambda x: -x["priority_score"])


# ══════════════════════════════════════════════════════════════════════
#  SKILL MATRIX DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════
CONFIDENCE_COLOR = {
    "Confirmed": "#22C55E",
    "Strong":    "#22C55E",
    "Partial":   "#F59E0B",
    "Weak":      "#F97316",
    "Not Found": "#EF4444",  # fixed: was "None"
}

CONFIDENCE_ICON = {
    "Confirmed": "✅",
    "Strong":    "✅",
    "Partial":   "⚠️",
    "Weak":      "🟠",
    "Not Found": "❌",        # fixed: was "None"
}

PRIORITY_COLOR = {
    "Critical": "#EF4444",
    "High":     "#F97316",
    "Medium":   "#F59E0B",
    "Low":      "#6B7280",
    "None":     "#D1D5DB",
}



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
    # openai/gpt-oss-20b — verified current Groq production model (Sept 2026)
    return ChatGroq(model="openai/gpt-oss-20b", api_key=groq_key)

llm = get_llm()

def ask_llm(prompt: str) -> str:
    try:
        return llm.invoke([HumanMessage(content=prompt)]).content
    except Exception as e:
        return f"ERROR: {str(e)}"

def ask_openai_direct(prompt: str, system: str = "") -> str:
    """Wrapper — uses Groq LLaMA for all calls."""
    return ask_llm(prompt)

# ── Prototype Dataset ─────────────────────────────────────────────────
# Source: Manually curated from LinkedIn/Glassdoor/Naukri (Q1-Q3 2026)
# Geography: India + US | Note: Demand estimates, not authoritative data
# Replace with live job-scraping pipeline for production use.
ROLE_MARKET_DATA = {
    "AI Engineer": {
        "demand":"Very High","demand_trend":"↑ 42% YoY",
        "salary_india":"₹8L – ₹24L","salary_us":"$90K – $160K",
        "top_companies":["Google","OpenAI","Microsoft","Anthropic","Startups"],
        "skills":{"python":95,"git":90,"langchain":82,"llm":78,"fastapi":71,"docker":65,"sql":63,"pytorch":58,"aws":54,"kubernetes":42},
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
        "skills":{"python":95,"langchain":90,"openai api":85,"prompt engineering":88,"rag":82,"vector database":78,"fastapi":70,"docker":65,"langgraph":72,"git":88},
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
    """
    Portfolio Score from real repo signals.

    Bug fix: Code Quality now uses test/CI signals, NOT stars.
    Stars = Popularity. Code Quality = evidence of tests or CI config.

    Categories:
    - Deployment   (3pts): Has live demo / homepage link
    - Documentation(2pts): Has description
    - Originality  (2pts): Not a fork
    - Consistency  (2pts): Pushed within last 180 days
    - Code Quality (2pts): Has test/CI topics or meaningful description
    """
    repos = github_data.get("repos", [])
    top = sorted(repos, key=lambda r: (
        not r.get("fork", False), r.get("pushed_at", "")
    ), reverse=True)[:8]

    cp = {"Deployment":0, "Documentation":0, "Originality":0, "Consistency":0, "Code Quality":0}
    cm = {"Deployment":3, "Documentation":2, "Originality":2, "Consistency":2, "Code Quality":2}
    scored = []; ts = 0; ms = 0; now = datetime.utcnow()

    for r in top:
        dep  = 3 if r.get("homepage") else 0
        doc  = 2 if r.get("description") else 0
        orig = 2 if not r.get("fork") else 0
        recent = False
        if r.get("pushed_at"):
            try:
                recent = (now - datetime.strptime(
                    r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")).days <= 180
            except Exception:
                pass
        cons = 2 if recent else 0

        # Code Quality — real signals only
        topics = [t.lower() for t in (r.get("topics") or [])]
        repo_name = r.get("name", "").lower()
        has_quality = (
            any(t in topics for t in ["testing","ci","pytest","unittest","github-actions"]) or
            any(kw in repo_name for kw in ["test","ci","pipeline"])
        )
        qual = 2 if has_quality else (1 if len(r.get("description") or "") > 50 else 0)

        s = dep + doc + orig + cons + qual
        for k, v in zip(cp.keys(), [dep, doc, orig, cons, qual]):
            cp[k] += v
        scored.append({
            "name": r["name"], "score": s, "max": 11,
            "description": r.get("description"),
            "deployed": bool(r.get("homepage")),
            "stars": r.get("stargazers_count", 0),
            "recently_updated": recent,
            "has_quality": has_quality,
            "url": r.get("html_url", ""),
        })
        ts += s; ms += 11

    n = len(top) or 1
    bd = {cat: round((cp[cat] / (cm[cat] * n)) * 100) for cat in cp}
    ps = round((ts / ms) * 100) if ms else 0
    st2 = [cat for cat, p in bd.items() if p >= 60]
    wk  = [cat for cat, p in bd.items() if p < 40]
    if len(github_data.get("languages", [])) >= 3: st2.append("Language Diversity")
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
    return {"score":total,"categories":{
                "Contact Info":        {"score":contact_score, "max":15},  # max 15 (email+phone+linkedin+github = 5+4+3+3)
                "Resume Sections":     {"score":section_score, "max":20},
                "Skills Coverage":     {"score":skills_score,  "max":20},
                "Keywords & Verbs":    {"score":kw_score,       "max":20},
                "Formatting & Length": {"score":fmt,            "max":17}, # max 17 (capped)
            },
            "sections":sections,"found_keywords":found_kw,"has_email":has_email,"has_phone":has_phone,
            "has_linkedin":has_linkedin,"has_github_link":has_github,"word_count":wc,"verb_count":vc,"quant_count":qc}

# ══════════════════════════════════════════════════════════════════════
#  PHASE 1 — Resume Intelligence: robust skill extraction
# ══════════════════════════════════════════════════════════════════════

# CANONICAL_SKILLS removed — SKILL_SYNONYMS above is the ONE taxonomy.
# normalize_skill and normalize_skill_list are defined in the Skill Evidence Engine.

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
    """Structured, professional resume analysis with recruiter-grade output format."""
    evidence_block = "No additional evidence retrieved."
    if evidence and any(evidence.values()):
        evidence_block = format_evidence_for_prompt(evidence)

    prompt = f"""You are a senior technical recruiter and career strategist at a top tech firm.

Analyze the resume below and return ONLY the structured assessment.
Do NOT output reasoning, thinking, or analysis process.
Do NOT invent anything not present in the resume.
Do NOT mention the candidate's name.
Be specific, evidence-based, and recruiter-readable.

Use EXACTLY these section headers (copy them exactly):

##CAREER_FIT##
##ROLE_MATCH##
##STRENGTHS##
##GAPS##
##PRIORITY_ACTIONS##
##FINAL_VERDICT##

---

##CAREER_FIT##
State the single best-fit career path in one line.
Then list 4-6 specific skills/projects from the resume that justify this fit as bullet points.

##ROLE_MATCH##
List exactly 5 roles with match level and one-sentence evidence.
Format each line as: ROLE | MATCH | EVIDENCE
Example: AI Engineer | Strong | LangChain + RAG projects + Python

##STRENGTHS##
List 3-5 specific strengths with evidence from the resume.
Each strength must cite a specific skill, project, or achievement.
NOT generic. Example: "RAG implementation in devpath-agent project shows production LLM engineering."

##GAPS##
List 3-4 specific gaps — not generic advice.
Each gap must explain WHY it matters for their target roles.
Example: "No evidence of model evaluation or ML experimentation — critical for ML Engineer roles."

##PRIORITY_ACTIONS##
List 4-5 ranked actions as P0/P1/P2.
P0 = do this week. P1 = this month. P2 = next 60 days.
Each action must be specific and achievable.
Example: "P0 — Add quantified outcomes to 3 project bullets (e.g., reduced latency by 40%)"

##FINAL_VERDICT##
One short paragraph. Recruiter-style summary.
State readiness level, strongest asset, and single most important improvement.

---

RESUME:
{resume_text[:3000]}

EXTRACTED SKILLS:
{', '.join(skills[:20]) if skills else 'none detected'}

RETRIEVED EVIDENCE (use only where relevant):
{evidence_block}
"""
    return ask_llm_clean(prompt)


def render_structured_analysis(analysis_text: str):
    """Parse ##SECTION## headers and render each as a styled card."""
    if not analysis_text or analysis_text.strip().startswith("ERROR"):
        st.error(f"Analysis failed: {analysis_text}")
        return

    # Section config: marker → (display title, icon, color)
    SECTIONS = {
        "CAREER_FIT":       ("Career Fit",          "🎯", "#E91E63"),
        "ROLE_MATCH":       ("Role Match",           "💼", "#7C3AED"),
        "STRENGTHS":        ("Key Strengths",        "📈", "#22C55E"),
        "GAPS":             ("Gaps & Improvements",  "⚠️", "#F59E0B"),
        "PRIORITY_ACTIONS": ("Priority Action Plan", "🚀", "#E91E63"),
        "FINAL_VERDICT":    ("Final Verdict",        "📌", "#1E1E2E"),
    }

    # Parse sections
    parsed = {k: "" for k in SECTIONS}
    current = None
    for line in analysis_text.split("\n"):
        stripped = line.strip()
        # Match ##SECTION_NAME##
        if stripped.startswith("##") and stripped.endswith("##"):
            key = stripped.strip("#").strip()
            if key in SECTIONS:
                current = key
                continue
        if current is not None:
            parsed[current] += line + "\n"

    # Render each section
    for key, (title, icon, color) in SECTIONS.items():
        body = parsed[key].strip()
        if not body:
            continue

        st.markdown(f"""
        <div style="background:white;border:1px solid #F0EEF8;border-left:4px solid {color};
             border-radius:14px;padding:20px 24px;margin-bottom:16px;
             box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-size:15px;font-weight:700;color:#1E1E2E;margin-bottom:12px;">
                {icon} {title}
            </div>
        """, unsafe_allow_html=True)

        # Special rendering for Role Match — detect table format
        if key == "ROLE_MATCH":
            lines = [l.strip() for l in body.split("\n") if "|" in l and l.strip()]
            if lines:
                st.markdown("""
                <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead><tr>
                    <th style="text-align:left;padding:8px 12px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Role</th>
                    <th style="text-align:center;padding:8px 12px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Match</th>
                    <th style="text-align:left;padding:8px 12px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Evidence</th>
                </tr></thead><tbody>""", unsafe_allow_html=True)
                for row in lines:
                    parts = [p.strip() for p in row.split("|")]
                    if len(parts) >= 3:
                        role = parts[0]; match = parts[1]; evidence = parts[2]
                        mc = "#22C55E" if "Strong" in match else "#F59E0B" if "Good" in match else "#9090A8"
                        st.markdown(f"""
                        <tr style="border-bottom:1px solid #F0EEF8;">
                            <td style="padding:10px 12px;font-weight:600;color:#1E1E2E;">{role}</td>
                            <td style="padding:10px 12px;text-align:center;">
                                <span style="background:{mc}18;color:{mc};border:1px solid {mc}44;
                                border-radius:20px;padding:3px 12px;font-size:12px;font-weight:700;">{match}</span>
                            </td>
                            <td style="padding:10px 12px;color:#4A4A5A;font-size:12px;">{evidence}</td>
                        </tr>""", unsafe_allow_html=True)
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.markdown(body)

        # Special rendering for Priority Actions — color P0/P1/P2
        elif key == "PRIORITY_ACTIONS":
            for line in body.split("\n"):
                line = line.strip()
                if not line: continue
                if line.startswith("P0"):
                    badge_color = "#EF4444"; badge_bg = "#FEF2F2"
                elif line.startswith("P1"):
                    badge_color = "#F59E0B"; badge_bg = "#FFFBEB"
                elif line.startswith("P2"):
                    badge_color = "#6B7280"; badge_bg = "#F9FAFB"
                else:
                    st.markdown(f'<div style="font-size:13px;color:#4A4A5A;padding:4px 0;">{line}</div>', unsafe_allow_html=True)
                    continue
                priority = line[:2]; text = line[3:].strip(" —-")
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid #F5F3FF;">
                    <span style="background:{badge_bg};color:{badge_color};border:1px solid {badge_color}44;
                        border-radius:6px;padding:2px 8px;font-size:11px;font-weight:800;flex-shrink:0;">{priority}</span>
                    <span style="font-size:13px;color:#1E1E2E;line-height:1.5;">{text}</span>
                </div>""", unsafe_allow_html=True)

        # Default rendering for other sections
        else:
            # Convert bullet lines to styled bullets
            lines = body.split("\n")
            for line in lines:
                line = line.strip()
                if not line: continue
                if line.startswith(("-", "•", "*")):
                    text = line.lstrip("-•* ").strip()
                    st.markdown(f'<div style="display:flex;gap:8px;padding:5px 0;"><span style="color:{color};font-size:14px;flex-shrink:0;">▸</span><span style="font-size:13px;color:#1E1E2E;line-height:1.5;">{text}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="font-size:13px;color:#4A4A5A;padding:4px 0;line-height:1.5;">{line}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# SKILL_SYNONYMS is defined in the Skill Evidence Engine above — ONE canonical definition.
# _expand and _matches now use the canonical SKILL_SYNONYMS and normalize_skill.

def _expand(skill: str) -> set:
    """Expand a skill to all its synonyms using the canonical taxonomy."""
    canonical = normalize_skill(skill)
    related = {canonical, skill.lower()}
    synonyms = SKILL_SYNONYMS.get(canonical, set())
    related |= synonyms
    return related

def _matches(claimed: str, evidence: set) -> bool:
    """Check if a claimed skill matches any evidence using canonical expansion."""
    for c in _expand(claimed):
        for e in evidence:
            if c == e or (len(c) > 3 and (c in e or e in c)):
                return True
    return False

def compute_overlap(claimed: list, evidence: list) -> dict:
    """
    Compute skill overlap using canonical normalization.
    Fix: uses normalize_skill() instead of fuzzy substring matching.
    All comparisons happen at canonical skill level.
    """
    # Normalize both lists to canonical form
    claimed_canonical  = {normalize_skill(s): s for s in claimed if s.strip()}
    evidence_canonical = {normalize_skill(s) for s in evidence if s.strip()}

    verified   = sorted(orig for canon, orig in claimed_canonical.items() if canon in evidence_canonical)
    unverified = sorted(orig for canon, orig in claimed_canonical.items() if canon not in evidence_canonical)
    extra      = sorted(evidence_canonical - set(claimed_canonical.keys()))
    score      = round((len(verified) / len(claimed_canonical)) * 100) if claimed_canonical else 0

    return {
        "verified":   verified,
        "unverified": unverified,
        "extra":      extra,
        "score":      score,
    }

def compute_market_readiness(user_skills: list, role_skills: dict) -> dict:
    """
    Compute market readiness using canonical skill normalization.
    Fix: no more fuzzy substring matching. normalize_skill() for all comparisons.
    """
    # Normalize user skills to canonical set
    user_canonical = {normalize_skill(s) for s in user_skills if s.strip()}
    matched = {}; missing = {}

    for skill, pct in role_skills.items():
        skill_canonical = normalize_skill(skill)
        found = skill_canonical in user_canonical
        if found: matched[skill] = pct
        else:     missing[skill] = pct

    td = sum(role_skills.values())
    md = sum(matched.values())
    rs = round((md / td) * 100) if td else 0

    return {
        "score":                rs,
        "matched":              matched,
        "missing":              missing,
        "priority_gaps":        sorted(missing.items(), key=lambda x: -x[1]),
        "total_skills_required":len(role_skills),
        "skills_you_have":      len(matched),
    }

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
    "skill_matrix":None,"github_evidence_map":None,"gap_priorities":None,
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

def sbar(skill, pct, have_it=None, show_status=False, label="Hiring Demand"):
    """Render a skill bar. pct = market hiring demand (NOT user proficiency)."""
    bc = "#22C55E" if have_it else "#E91E63" if have_it is False else "#7C3AED"
    sh = f'<span style="font-size:14px;">{"✅" if have_it else "🟡" if have_it is None else "❌"}</span>' if show_status else ""
    st.markdown(f"""
    <div class="skill-row">
        <div class="skill-row-top">
            <span class="skill-name">{skill.title()}</span>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:10px;color:#9090A8;font-weight:600;">{label}</span>
                <span class="skill-pct">{pct}%</span>
                {sh}
            </div>
        </div>
        <div class="skill-bar-track">
            <div style="width:{pct}%;background:{bc};height:6px;border-radius:99px;"></div>
        </div>
    </div>""", unsafe_allow_html=True)


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

    # ── Gap Priority Panel ─────────────────────────────────────────────
    st.markdown("<br>",unsafe_allow_html=True)
    if st.session_state.get("gap_priorities"):
        cs("🎯 Priority Skill Gaps","Computed from Resume + GitHub + Market demand · Not LLM-guessed")
        gaps = st.session_state.gap_priorities[:5]
        for gap in gaps:
            pc = PRIORITY_COLOR.get(gap["priority_label"], "#9090A8")
            conf_c = CONFIDENCE_COLOR.get(gap["confidence"], "#9090A8")
            bw = gap["market_demand"]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #F8F7FF;">
                <span style="background:{pc}18;color:{pc};border:1px solid {pc}44;
                    border-radius:6px;padding:2px 8px;font-size:10px;font-weight:800;width:58px;text-align:center;flex-shrink:0;">
                    {gap["priority_label"]}
                </span>
                <span style="font-size:13px;font-weight:600;color:#1E1E2E;flex:1;">{gap["skill"].title()}</span>
                <div style="width:80px;background:#F0EEF8;border-radius:99px;height:5px;">
                    <div style="width:{bw}%;background:{pc};height:5px;border-radius:99px;"></div>
                </div>
                <span style="font-size:11px;color:#9090A8;width:30px;">{bw}%</span>
                <span style="background:{conf_c}18;color:{conf_c};border:1px solid {conf_c}44;
                    border-radius:20px;padding:2px 8px;font-size:10px;font-weight:600;flex-shrink:0;">
                    {gap["confidence"]}
                </span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:11px;color:#9090A8;margin-top:6px;">Top {len(gaps)} of {len(st.session_state.gap_priorities)} gaps · Run GitHub Analysis + Resume to compute</div>', unsafe_allow_html=True)
        ce()
    else:
        cs("📌 Next Steps")
        actions=[("🐙","Analyze GitHub","GitHub Intelligence"),
                 ("📄","Upload Resume","Resume Intelligence"),
                 ("🌉","Reality Check","Verify your claims"),
                 ("💼","Job Match","See your fit")]
        cols=st.columns(4)
        for i,(icon,title,desc) in enumerate(actions):
            with cols[i]:
                st.markdown(f'<div style="background:rgba(233,30,99,0.03);border:1px solid rgba(233,30,99,0.1);border-radius:14px;padding:14px;text-align:center;"><div style="font-size:22px;margin-bottom:6px;">{icon}</div><div style="font-size:13px;font-weight:700;color:#1E1E2E;margin-bottom:3px;">{title}</div><div style="font-size:11px;color:#9090A8;">{desc}</div></div>',unsafe_allow_html=True)
        ce()

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
            with st.spinner("🔍 Retrieving evidence from knowledge base..."):
                rag_evidence = {"jobs":[], "learning":[], "career":[]}
                if RAG_AVAILABLE:
                    try:
                        devpath_rag.initialize()
                        # Retrieve matching jobs
                        rag_evidence["jobs"] = devpath_rag.retrieve_jobs(
                            "AI Engineer", st.session_state.resume_skills or [], n=3
                        )
                        # Retrieve learning for skill gaps
                        rag_evidence["learning"] = devpath_rag.retrieve_learning_resources(
                            st.session_state.resume_skills or [], n=3
                        )
                        # Retrieve career knowledge
                        rag_evidence["career"] = devpath_rag.retrieve_career_knowledge(
                            "resume tips ATS keywords improvements", n=2
                        )
                    except Exception:
                        pass
                if any(rag_evidence.values()):
                    job_names = [j["company"] for j in rag_evidence["jobs"][:3]]
                    st.markdown(f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;
                        border-radius:10px;padding:10px 16px;margin-bottom:8px;">
                        <span style="font-size:12px;font-weight:700;color:#16A34A;">
                        🔍 RAG Retrieved: {len(rag_evidence["jobs"])} jobs · {len(rag_evidence["learning"])} resources · {len(rag_evidence["career"])} career articles
                        {"· Matching: " + ", ".join(job_names) if job_names else ""}
                        </span></div>''', unsafe_allow_html=True)
            with st.spinner("🤖 Generating AI analysis..."):
                st.session_state.resume_analysis = generate_structured_resume_analysis(
                    text, st.session_state.resume_skills, evidence=rag_evidence
                )
            # Rebuild Skill Matrix if GitHub evidence already exists
            if st.session_state.github_evidence_map:
                st.session_state.skill_matrix = build_skill_matrix(
                    resume_text=st.session_state.resume_text or "",
                    resume_skills=st.session_state.resume_skills,
                    github_evidence=st.session_state.github_evidence_map,
                    target_role=st.session_state.get("market_role","AI Engineer"),
                )
                st.session_state.gap_priorities = compute_gap_priorities(st.session_state.skill_matrix)

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

                # Build GitHub Evidence Map (deep skill inspection)
                with st.spinner("🔍 Building skill evidence map from repos..."):
                    gh_token = os.getenv("GITHUB_TOKEN","") or st.secrets.get("GITHUB_TOKEN","")
                    st.session_state.github_evidence_map = fetch_github_evidence(username, gh_token)

                # Build Skill Matrix if resume is also loaded
                if st.session_state.resume_skills and st.session_state.github_evidence_map:
                    st.session_state.skill_matrix = build_skill_matrix(
                        resume_text=st.session_state.resume_text or "",
                        resume_skills=st.session_state.resume_skills,
                        github_evidence=st.session_state.github_evidence_map,
                        target_role=st.session_state.get("market_role","AI Engineer"),
                    )
                    st.session_state.gap_priorities = compute_gap_priorities(st.session_state.skill_matrix)

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

        # ── Skill Matrix Table (if available) ─────────────────────────
        if st.session_state.get("skill_matrix"):
            st.markdown("<br>",unsafe_allow_html=True)
            cs("📊 Skill Evidence Matrix","Every skill — Resume status · GitHub depth · Market demand · Readiness")
            sm = st.session_state.skill_matrix
            # Show only skills that appear in resume or have github evidence
            relevant = {k:v for k,v in sm.items() if v["resume"] or v["github_strength"] != "Not Found"}
            if relevant:
                st.markdown("""
                <table style="width:100%;border-collapse:collapse;font-size:12px;">
                <thead><tr>
                    <th style="text-align:left;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Skill</th>
                    <th style="text-align:center;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Resume</th>
                    <th style="text-align:center;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">GitHub</th>
                    <th style="text-align:center;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Market</th>
                    <th style="text-align:center;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Confidence</th>
                    <th style="text-align:center;padding:8px 10px;background:#F8F7FF;color:#6B6880;font-weight:700;border-bottom:2px solid #F0EEF8;">Repos</th>
                </tr></thead><tbody>""", unsafe_allow_html=True)

                for skill, data in sorted(relevant.items(), key=lambda x: -x[1]["readiness"]):
                    r_icon = "✅" if data["resume"] else "—"
                    gh_icon = CONFIDENCE_ICON.get(data["github_strength"], "—")
                    conf_color = CONFIDENCE_COLOR.get(data["confidence"], "#9090A8")
                    repos_str = ", ".join(data["github_repos"][:2]) if data["github_repos"] else "—"
                    market = data["market_demand"]
                    market_bar = f'<div style="background:#F0EEF8;border-radius:99px;height:4px;width:60px;display:inline-block;vertical-align:middle;"><div style="width:{market}%;background:#7C3AED;height:4px;border-radius:99px;"></div></div> {market}%'
                    st.markdown(f"""
                    <tr style="border-bottom:1px solid #F8F7FF;">
                        <td style="padding:8px 10px;font-weight:600;color:#1E1E2E;">{skill.title()}</td>
                        <td style="padding:8px 10px;text-align:center;">{r_icon}</td>
                        <td style="padding:8px 10px;text-align:center;">{gh_icon} {data["github_strength"]}</td>
                        <td style="padding:8px 10px;text-align:center;">{market_bar}</td>
                        <td style="padding:8px 10px;text-align:center;">
                            <span style="background:{conf_color}18;color:{conf_color};border:1px solid {conf_color}44;
                                border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;">
                                {data["confidence"]}
                            </span>
                        </td>
                        <td style="padding:8px 10px;font-size:11px;color:#6B6880;">{repos_str}</td>
                    </tr>""", unsafe_allow_html=True)

                st.markdown("</tbody></table>", unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:11px;color:#9090A8;margin-top:8px;">{len(relevant)} skills analyzed</div>', unsafe_allow_html=True)
            ce()
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
    ph("📈 Market Intelligence","Market benchmark based on prototype dataset · Skills weighted by role demand · Not live job board data.")
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
    if st.session_state.ats_score is not None:
        user_context += f"ATS Score: {st.session_state.ats_score}/100\n"
    if st.session_state.portfolio:
        user_context += f"Portfolio Score: {st.session_state.portfolio['portfolio_score']}/100\n"
    if st.session_state.reality_check:
        user_context += f"Credibility Score: {st.session_state.reality_check['score']}%\n"
    if st.session_state.get("market_readiness"):
        user_context += f"Market Readiness: {st.session_state.market_readiness['score']}%\n"
    # Use Skill Matrix for rich, specific context
    if st.session_state.get("skill_matrix") and st.session_state.get("gap_priorities"):
        sm = st.session_state.skill_matrix
        confirmed = [k for k,v in sm.items() if v["confidence"] in ("Confirmed","Strong")]
        partial = [k for k,v in sm.items() if v["confidence"] == "Partial" and v["resume"]]
        critical = [g["skill"] for g in st.session_state.gap_priorities if g["priority_label"] in ("Critical","High")][:4]
        if confirmed: user_context += f"Confirmed skills (resume+GitHub): {', '.join(confirmed[:8])}\n"
        if partial: user_context += f"Claimed but no GitHub evidence: {', '.join(partial[:5])}\n"
        if critical: user_context += f"Critical gaps (market demand × role fit): {', '.join(critical)}\n"
    elif st.session_state.resume_skills or st.session_state.github_skills:
        all_skills = list(set((st.session_state.resume_skills or []) + (st.session_state.github_skills or [])))
        user_context += f"Known skills: {', '.join(all_skills[:12])}\n"
        if st.session_state.reality_check and st.session_state.reality_check.get("unverified"):
            user_context += f"Unverified claims: {', '.join(st.session_state.reality_check['unverified'][:5])}\n"

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