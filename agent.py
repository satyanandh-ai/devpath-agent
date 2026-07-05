# DevPath Agent - Professional UI Version

import streamlit as st
import requests
import PyPDF2
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="DevPath Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Professional CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F7F7FB;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top Navigation Bar ── */
.navbar {
    background: #ffffff;
    border-bottom: 1px solid #EBEBF0;
    padding: 0 48px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 700;
    color: #1A1A2E;
    letter-spacing: -0.3px;
}
.navbar-brand span {
    color: #5B4FE9;
}
.navbar-badge {
    background: linear-gradient(135deg, #5B4FE9, #7C6FF7);
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}

/* ── Hero Section ── */
.hero {
    background: #ffffff;
    padding: 64px 48px 48px;
    border-bottom: 1px solid #EBEBF0;
    text-align: center;
}
.hero-icon {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #EEF0FD, #DDD9FB);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    margin: 0 auto 24px;
}
.hero h1 {
    font-size: 40px;
    font-weight: 700;
    color: #1A1A2E;
    letter-spacing: -1px;
    margin: 0 0 12px;
    line-height: 1.15;
}
.hero h1 span { color: #5B4FE9; }
.hero p {
    font-size: 17px;
    color: #6B6B80;
    margin: 0 auto;
    max-width: 520px;
    line-height: 1.6;
    font-weight: 400;
}
.hero-pills {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 24px;
    flex-wrap: wrap;
}
.hero-pill {
    background: #F0EFFE;
    color: #5B4FE9;
    border: 1px solid #DDD9FB;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
}

/* ── Tab Navigation ── */
.tab-nav {
    background: #ffffff;
    border-bottom: 1px solid #EBEBF0;
    padding: 0 48px;
    display: flex;
    gap: 0;
}
.tab-btn {
    padding: 16px 24px;
    font-size: 14px;
    font-weight: 500;
    color: #6B6B80;
    border: none;
    background: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
}
.tab-btn.active {
    color: #5B4FE9;
    border-bottom: 2px solid #5B4FE9;
    font-weight: 600;
}

/* ── Main Content Area ── */
.content-area {
    padding: 40px 48px;
    max-width: 900px;
    margin: 0 auto;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #EBEBF0;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #1A1A2E;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-desc {
    font-size: 13px;
    color: #9090A0;
    margin-bottom: 20px;
    line-height: 1.5;
}

/* ── Streamlit Input Override ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #F7F7FB !important;
    border: 1.5px solid #EBEBF0 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    color: #1A1A2E !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #5B4FE9 !important;
    box-shadow: 0 0 0 3px rgba(91,79,233,0.08) !important;
}
.stTextInput label, .stTextArea label, .stFileUploader label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #4A4A5A !important;
    margin-bottom: 6px !important;
}

/* ── Button Override ── */
.stButton > button {
    background: linear-gradient(135deg, #5B4FE9, #7C6FF7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    letter-spacing: 0.1px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4A3FD8, #6B5FE6) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(91,79,233,0.3) !important;
}

/* ── Result Box ── */
.result-box {
    background: #F7F7FB;
    border: 1px solid #EBEBF0;
    border-left: 4px solid #5B4FE9;
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
}
.result-label {
    font-size: 11px;
    font-weight: 600;
    color: #5B4FE9;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

/* ── Success / Error Banners ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px !important;
    font-size: 14px !important;
}

/* ── File Uploader ── */
.stFileUploader > div {
    background: #F7F7FB !important;
    border: 2px dashed #DDD9FB !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #5B4FE9 !important;
}

/* ── Tab Override ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-bottom: 1px solid #EBEBF0 !important;
    gap: 0px !important;
    padding: 0 48px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #6B6B80 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 16px 20px !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #5B4FE9 !important;
    border-bottom: 2px solid #5B4FE9 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: #5B4FE9 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 0 !important;
}

/* ── Two-col layout ── */
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

/* ── Stat Pills ── */
.stat-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
}
.stat-pill {
    background: #F0EFFE;
    border: 1px solid #DDD9FB;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #5B4FE9;
}

/* ── Footer ── */
.footer {
    background: #ffffff;
    border-top: 1px solid #EBEBF0;
    padding: 20px 48px;
    text-align: center;
    font-size: 12px;
    color: #9090A0;
    margin-top: 60px;
}
.footer span { color: #5B4FE9; font-weight: 600; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #EBEBF0; margin: 24px 0; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">⚡ Dev<span>Path</span> Agent</div>
    <div class="navbar-badge">AGENTIC ARENA 2026</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-icon">⚡</div>
    <h1>Your AI Career <span>Co-Pilot</span></h1>
    <p>Analyze your GitHub, review your resume, and get a personalized roadmap — all from a single prompt.</p>
    <div class="hero-pills">
        <div class="hero-pill">🐙 GitHub Analyzer</div>
        <div class="hero-pill">📄 Resume Review</div>
        <div class="hero-pill">🌉 Bridge Plan</div>
        <div class="hero-pill">💬 Career Chat</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LLM Setup ─────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found! Add it in Streamlit Cloud → Settings → Secrets.")
        st.stop()
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

llm = get_llm()

# ── Tools ─────────────────────────────────────────────────────────────
@tool
def get_skills_for_role(role: str) -> str:
    """Returns the required technical skills for ANY given job role using AI knowledge."""
    prompt = (
        f"List the top 8-10 technical skills required for a '{role}' role in 2026. "
        f"Reply with ONLY a comma-separated list of skill names, no explanation, no numbering."
    )
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return f"Skills needed for {role}: {response.content.strip()}"
    except Exception as e:
        return f"ERROR: Could not fetch skills for '{role}': {str(e)}"

@tool
def analyze_github(username: str) -> str:
    """Analyzes a GitHub profile and returns repo information."""
    try:
        url = f"https://api.github.com/users/{username}"
        user_response = requests.get(url, timeout=10)
        if user_response.status_code == 404:
            return f"ERROR: GitHub user '{username}' not found."
        if user_response.status_code != 200:
            return f"ERROR: GitHub API error. Status: {user_response.status_code}"
        user_data = user_response.json()
        repos_url = f"https://api.github.com/users/{username}/repos"
        repos = requests.get(repos_url, timeout=10).json()
        if not repos:
            return f"User '{username}' has no public repositories."
        languages = set()
        repo_info = []
        for repo in repos[:5]:
            lang = repo.get("language") or "Unknown"
            languages.add(lang)
            repo_info.append(
                f"- {repo['name']}: {repo.get('description') or 'No description'} "
                f"(Stars: {repo['stargazers_count']}, Language: {lang})"
            )
        result = f"GitHub Profile: {username}\n"
        result += f"Name: {user_data.get('name', 'N/A')}\n"
        result += f"Total Public Repos: {len(repos)}\n"
        result += f"Languages Used: {', '.join(languages - {'Unknown'})}\n"
        result += "Top Repositories:\n" + "\n".join(repo_info)
        return result
    except requests.exceptions.ConnectionError:
        return "ERROR: No internet connection."
    except requests.exceptions.Timeout:
        return "ERROR: GitHub API timed out."
    except Exception as e:
        return f"ERROR: {str(e)}"

# ── Helpers ───────────────────────────────────────────────────────────
def read_pdf(uploaded_file) -> str:
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text[:2000] if text.strip() else "ERROR: Could not extract text."
    except Exception as e:
        return f"ERROR: {str(e)}"

def ask_llm(prompt: str) -> str:
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"ERROR: {str(e)}"

def ask_agent(query: str) -> str:
    try:
        tools = [get_skills_for_role, analyze_github]
        agent = create_react_agent(llm, tools)
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        return result["messages"][-1].content
    except Exception as e:
        return f"ERROR: {str(e)}"

# ── Tabs ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🐙  GitHub Analyzer",
    "📄  Resume Analyzer",
    "🌉  Bridge Plan",
    "💬  Career Chat"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — GitHub Analyzer
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-title">🐙 Analyze a GitHub Profile</div>
        <div class="card-desc">Enter any GitHub username to get an instant developer profile breakdown — tech stack, project quality, and skill assessment.</div>
    </div>
    """, unsafe_allow_html=True)

    github_username = st.text_input(
        "GitHub Username",
        placeholder="e.g. satyanandh-ai",
        key="github_input"
    )

    if st.button("Analyze Profile →", key="github_btn"):
        if github_username.strip():
            with st.spinner(f"Fetching profile of '{github_username}'..."):
                query = f"Use the analyze_github tool to analyze GitHub profile of {github_username}. Tell me: 1) what kind of developer they are 2) their main skills 3) quality of their projects"
                result = ask_agent(query)
            if "ERROR" in result:
                st.error(result)
            else:
                st.success("✅ Analysis complete!")
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">GitHub Analysis</div>
                """, unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a GitHub username.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — Resume Analyzer
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-title">📄 Resume Analyzer</div>
        <div class="card-desc">Upload your resume PDF for an instant AI-powered review — skills extraction, job match suggestions, and an ATS compatibility score.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"], key="resume_upload")

    if uploaded_file is not None:
        st.success(f"✅ {uploaded_file.name} uploaded successfully")
        if st.button("Analyze Resume →", key="resume_btn"):
            with st.spinner("Reading your resume..."):
                resume_text = read_pdf(uploaded_file)
            if resume_text.startswith("ERROR"):
                st.error(resume_text)
            else:
                with st.spinner("AI is reviewing your resume..."):
                    prompt = f"""You are a professional career advisor and resume expert.

Analyze this resume and provide:

1. SKILLS FOUND - List all technical and soft skills
2. JOB ROLES - Top 5 job roles this person can apply for right now
3. IMPROVEMENTS - Top 5 specific improvements to strengthen the resume
4. ATS SCORE - Give a score out of 10 with explanation

Resume:
{resume_text}

Be specific, honest, and helpful."""
                    result = ask_llm(prompt)

                st.success("✅ Resume analysis complete!")
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"""
                    <div class="result-box">
                        <div class="result-label">AI Analysis</div>
                    """, unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="result-box">
                        <div class="result-label">Extracted Text Preview</div>
                    """, unsafe_allow_html=True)
                    st.text_area("", resume_text[:500] + "...", height=280, key="preview", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — Bridge Plan
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-title">🌉 Personalized Bridge Plan</div>
        <div class="card-desc">Cross-reference your current GitHub skills against your target role and get a step-by-step 30-60-90 day roadmap to bridge the gap.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        bridge_github = st.text_input("GitHub Username", placeholder="e.g. satyanandh-ai", key="bridge_github")
    with col2:
        bridge_goal = st.text_input("Target Role", placeholder="e.g. MLOps Engineer", key="bridge_goal")

    st.markdown("""
    <div style="font-size:12px; color:#9090A0; margin: -8px 0 16px;">
    💡 Works with any role: Backend Developer, LLM Engineer, Data Scientist, DevOps, etc.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Build My Roadmap →", key="bridge_btn"):
        if bridge_github.strip() and bridge_goal.strip():
            with st.spinner("Fetching your GitHub profile..."):
                github_data = analyze_github.invoke({"username": bridge_github})
            if "ERROR" in github_data:
                st.error(github_data)
            else:
                with st.spinner(f"Researching skills for '{bridge_goal}'..."):
                    required_skills = get_skills_for_role.invoke({"role": bridge_goal})
                if "ERROR" in required_skills:
                    st.error(required_skills)
                else:
                    with st.spinner("Building your personalized bridge plan..."):
                        prompt = f"""You are a career advisor helping a developer level up.

CURRENT SKILLS (from their GitHub):
{github_data}

TARGET CAREER GOAL: {bridge_goal}
REQUIRED SKILLS FOR GOAL: {required_skills}

Do a CROSS-REFERENCE analysis:

1. SKILLS THEY ALREADY HAVE - What skills match the goal?
2. SKILL GAPS - What skills are missing?
3. BRIDGE PLAN - Specific 30-60-90 day action plan
4. FIRST STEP - What to do TODAY

Be specific. Use their actual GitHub projects as reference."""
                        result = ask_llm(prompt)

                    st.success("✅ Your roadmap is ready!")
                    st.markdown(f"""
                    <div class="result-box">
                        <div class="result-label">Your Personalized Bridge Plan — {bridge_github} → {bridge_goal}</div>
                    """, unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please fill in both your GitHub username and target role.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — Career Chat
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-title">💬 Career Chat</div>
        <div class="card-desc">Ask anything — interview prep, skill advice, job search strategy, salary negotiation, or career decisions. Your AI advisor is ready.</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick prompt suggestions
    st.markdown("""
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px;">
        <div style="background:#F0EFFE; border:1px solid #DDD9FB; border-radius:8px; padding:8px 14px; font-size:12px; color:#5B4FE9; font-weight:500; cursor:pointer;">💡 Skills for AI internship?</div>
        <div style="background:#F0EFFE; border:1px solid #DDD9FB; border-radius:8px; padding:8px 14px; font-size:12px; color:#5B4FE9; font-weight:500; cursor:pointer;">📝 How to write a cold email?</div>
        <div style="background:#F0EFFE; border:1px solid #DDD9FB; border-radius:8px; padding:8px 14px; font-size:12px; color:#5B4FE9; font-weight:500; cursor:pointer;">🚀 Switch to ML from web dev?</div>
    </div>
    """, unsafe_allow_html=True)

    career_question = st.text_area(
        "Your question",
        placeholder="e.g. What skills should I learn to get an AI internship in 2026?",
        height=120,
        key="career_chat",
        label_visibility="collapsed"
    )

    if st.button("Ask Agent →", key="chat_btn"):
        if career_question.strip():
            with st.spinner("Agent is thinking..."):
                result = ask_agent(career_question)
            st.success("✅ Done!")
            st.markdown(f"""
            <div class="result-box">
                <div class="result-label">Agent Response</div>
            """, unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please type your question.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ⚡ <span>DevPath Agent</span> · Built with LangChain + LangGraph + Groq + Streamlit ·
    Agentic Arena 2026 · <span>Ch. Satyanand</span> · ALIET Vijayawada
</div>
""", unsafe_allow_html=True)
