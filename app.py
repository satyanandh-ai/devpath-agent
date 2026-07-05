# DevPath Agent - Professional UI (Pure Streamlit)

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

st.set_page_config(
    page_title="DevPath Agent",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS that actually works in Streamlit ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Background */
.stApp { background-color: #F8F8FF; }

/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #5B4FE9 0%, #7B6FF7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 32px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(91, 79, 233, 0.3) !important;
    font-family: 'Inter', sans-serif !important;
}
div.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(91, 79, 233, 0.45) !important;
    transform: translateY(-2px) !important;
}

/* Inputs */
div[data-testid="stTextInput"] input {
    border: 2px solid #E8E6FF !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
    background: white !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #5B4FE9 !important;
    box-shadow: 0 0 0 3px rgba(91,79,233,0.1) !important;
}
div[data-testid="stTextArea"] textarea {
    border: 2px solid #E8E6FF !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
    background: white !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #5B4FE9 !important;
    box-shadow: 0 0 0 3px rgba(91,79,233,0.1) !important;
}

/* Labels */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #2D2D3F !important;
    margin-bottom: 6px !important;
}

/* Tabs */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #6B6B80 !important;
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 12px 20px !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #5B4FE9 !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #5B4FE9 !important;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    border: 2px dashed #C4BEFF !important;
    border-radius: 12px !important;
    background: white !important;
    padding: 8px !important;
}

/* Spinner color */
div[data-testid="stSpinner"] {
    color: #5B4FE9 !important;
}

/* Success / error */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}

/* Columns gap */
div[data-testid="column"] { padding: 0 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── LLM Setup ─────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found! Add it to your .env file.")
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

# ══════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([1, 3, 1])
with col_m:
    st.markdown("""
    <div style="text-align:center; padding: 32px 24px 24px; background: white;
         border-radius: 20px; border: 1px solid #E8E6FF;
         box-shadow: 0 4px 24px rgba(91,79,233,0.08);">
        <div style="font-size:48px; margin-bottom:12px;">⚡</div>
        <h1 style="font-size:32px; font-weight:800; color:#1A1A2E;
            margin:0 0 8px; letter-spacing:-1px; font-family:Inter,sans-serif;">
            Dev<span style="color:#5B4FE9;">Path</span> Agent
        </h1>
        <p style="font-size:15px; color:#6B6B80; margin:0 0 20px;
           font-family:Inter,sans-serif; line-height:1.5;">
            Your Autonomous AI Career Co-Pilot
        </p>
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap;">
            <span style="background:#EEF0FD; color:#5B4FE9; border-radius:20px;
                padding:5px 14px; font-size:12px; font-weight:600;">🐙 GitHub</span>
            <span style="background:#EEF0FD; color:#5B4FE9; border-radius:20px;
                padding:5px 14px; font-size:12px; font-weight:600;">📄 Resume</span>
            <span style="background:#EEF0FD; color:#5B4FE9; border-radius:20px;
                padding:5px 14px; font-size:12px; font-weight:600;">🌉 Bridge</span>
            <span style="background:#EEF0FD; color:#5B4FE9; border-radius:20px;
                padding:5px 14px; font-size:12px; font-weight:600;">💬 Chat</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🐙  GitHub Analyzer",
    "📄  Resume Analyzer",
    "🌉  Bridge Plan",
    "💬  Career Chat"
])

# ── TAB 1: GitHub ─────────────────────────────────────────────────────
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border-radius:16px; padding:24px 28px;
         border:1px solid #E8E6FF; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#1A1A2E; margin-bottom:6px;">
            🐙 GitHub Profile Analyzer
        </div>
        <div style="font-size:13px; color:#9090A0; line-height:1.5;">
            Paste any GitHub username to get an instant developer profile —
            tech stack, project quality, and skill assessment.
        </div>
    </div>
    """, unsafe_allow_html=True)

    github_username = st.text_input("GitHub Username", placeholder="e.g. satyanandh-ai", key="github_input")

    if st.button("🔍  Analyze GitHub Profile", key="github_btn"):
        if github_username.strip():
            with st.spinner("Fetching profile..."):
                query = f"Use the analyze_github tool to analyze GitHub profile of {github_username}. Tell me: 1) what kind of developer they are 2) their main skills 3) quality of their projects"
                result = ask_agent(query)
            if "ERROR" in result:
                st.error(result)
            else:
                st.success("✅ Analysis complete!")
                st.markdown("""
                <div style="background:#F5F4FF; border-left:4px solid #5B4FE9;
                     border-radius:12px; padding:20px 24px; margin-top:16px;">
                <div style="font-size:11px; font-weight:700; color:#5B4FE9;
                     letter-spacing:1px; margin-bottom:12px;">GITHUB ANALYSIS</div>
                """, unsafe_allow_html=True)
                st.markdown(result)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter a GitHub username.")

# ── TAB 2: Resume ─────────────────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border-radius:16px; padding:24px 28px;
         border:1px solid #E8E6FF; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#1A1A2E; margin-bottom:6px;">
            📄 Resume Analyzer
        </div>
        <div style="font-size:13px; color:#9090A0; line-height:1.5;">
            Upload your PDF resume for an instant AI review —
            skills extraction, job match suggestions, and ATS compatibility score.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"], key="resume_upload")

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} ready")
        if st.button("📊  Analyze Resume", key="resume_btn"):
            with st.spinner("Reading resume..."):
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
                    st.markdown("""
                    <div style="background:#F5F4FF; border-left:4px solid #5B4FE9;
                         border-radius:12px; padding:20px 24px;">
                    <div style="font-size:11px; font-weight:700; color:#5B4FE9;
                         letter-spacing:1px; margin-bottom:12px;">AI ANALYSIS</div>
                    """, unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div style="background:#F5F4FF; border-left:4px solid #5B4FE9;
                         border-radius:12px; padding:20px 24px;">
                    <div style="font-size:11px; font-weight:700; color:#5B4FE9;
                         letter-spacing:1px; margin-bottom:12px;">TEXT PREVIEW</div>
                    """, unsafe_allow_html=True)
                    st.text_area("", resume_text[:400] + "...", height=260, label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 3: Bridge Plan ────────────────────────────────────────────────
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border-radius:16px; padding:24px 28px;
         border:1px solid #E8E6FF; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#1A1A2E; margin-bottom:6px;">
            🌉 Personalized Bridge Plan
        </div>
        <div style="font-size:13px; color:#9090A0; line-height:1.5;">
            Cross-reference your GitHub skills with your target role
            and get a custom 30-60-90 day roadmap to bridge the gap.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        bridge_github = st.text_input("GitHub Username", placeholder="e.g. satyanandh-ai", key="bridge_github")
    with col2:
        bridge_goal = st.text_input("Target Role", placeholder="e.g. MLOps Engineer", key="bridge_goal")

    st.caption("💡 Works with any role: Backend Dev, LLM Engineer, Data Scientist, DevOps, etc.")

    if st.button("🌉  Build My Roadmap", key="bridge_btn"):
        if bridge_github.strip() and bridge_goal.strip():
            with st.spinner("Fetching your GitHub profile..."):
                github_data = analyze_github.invoke({"username": bridge_github})
            if "ERROR" in github_data:
                st.error(github_data)
            else:
                with st.spinner(f"Researching skills for '{bridge_goal}'..."):
                    required_skills = get_skills_for_role.invoke({"role": bridge_goal})
                with st.spinner("Building your personalized roadmap..."):
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
                <div style="background:#F5F4FF; border-left:4px solid #5B4FE9;
                     border-radius:12px; padding:20px 24px; margin-top:16px;">
                <div style="font-size:11px; font-weight:700; color:#5B4FE9;
                     letter-spacing:1px; margin-bottom:12px;">
                BRIDGE PLAN — {bridge_github.upper()} → {bridge_goal.upper()}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(result)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please fill in both fields.")

# ── TAB 4: Career Chat ────────────────────────────────────────────────
with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border-radius:16px; padding:24px 28px;
         border:1px solid #E8E6FF; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#1A1A2E; margin-bottom:6px;">
            💬 Career Chat
        </div>
        <div style="font-size:13px; color:#9090A0; line-height:1.5;">
            Ask anything — interview prep, skill advice, job search strategy,
            salary negotiation, or career decisions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px;">
        <span style="background:#EEF0FD; color:#5B4FE9; border:1px solid #C4BEFF;
            border-radius:8px; padding:7px 14px; font-size:12px; font-weight:500;">
            💡 Skills for AI internship?
        </span>
        <span style="background:#EEF0FD; color:#5B4FE9; border:1px solid #C4BEFF;
            border-radius:8px; padding:7px 14px; font-size:12px; font-weight:500;">
            📝 How to write a cold email?
        </span>
        <span style="background:#EEF0FD; color:#5B4FE9; border:1px solid #C4BEFF;
            border-radius:8px; padding:7px 14px; font-size:12px; font-weight:500;">
            🚀 Switch to ML from web dev?
        </span>
    </div>
    """, unsafe_allow_html=True)

    career_question = st.text_area(
        "Your question",
        placeholder="e.g. What skills should I learn to get an AI internship in 2026?",
        height=130,
        key="career_chat",
        label_visibility="collapsed"
    )

    if st.button("💬  Ask Agent", key="chat_btn"):
        if career_question.strip():
            with st.spinner("Agent is thinking..."):
                result = ask_agent(career_question)
            st.success("✅ Done!")
            st.markdown("""
            <div style="background:#F5F4FF; border-left:4px solid #5B4FE9;
                 border-radius:12px; padding:20px 24px; margin-top:16px;">
            <div style="font-size:11px; font-weight:700; color:#5B4FE9;
                 letter-spacing:1px; margin-bottom:12px;">AGENT RESPONSE</div>
            """, unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please type your question.")

# ── Footer ────────────────────────────────────────────────────────────
<<<<<<< HEAD
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:20px; border-top:1px solid #E8E6FF;
     font-size:12px; color:#9090A0; font-family:Inter,sans-serif;">
    ⚡ <strong style="color:#5B4FE9;">DevPath Agent</strong> ·
    LangChain + LangGraph + Groq + Streamlit ·
    Agentic Arena 2026 ·
    <strong style="color:#5B4FE9;">Ch. Satyanand</strong> · ALIET Vijayawada
</div>
""", unsafe_allow_html=True)
=======
st.divider()
st.caption("🚀 DevPath Agent | Built with LangChain + LangGraph + Groq + Streamlit | Agentic Arena 2026 | Ch. Satyanand | ALIET Vijayawada")
>>>>>>> 4b94974785903d3c6d45d8b95b88e3ac1f26c625
