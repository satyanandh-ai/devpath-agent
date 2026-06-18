# DevPath Agent - Streamlit UI (Dynamic Skills Version)

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
    layout="wide"
)

# ── LLM Setup ─────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

llm = get_llm()

# ── TOOL 1: Dynamic Skills Lookup (No more hardcoded dictionary!) ────
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

# ── TOOL 2: GitHub Analyzer ──────────────────────────────────────────
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
        return "ERROR: No internet connection. Please check your network."
    except requests.exceptions.Timeout:
        return "ERROR: GitHub API timed out. Please try again."
    except Exception as e:
        return f"ERROR: {str(e)}"

# ── Helper Functions ──────────────────────────────────────────────────
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
#                         UI LAYOUT
# ══════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────
st.title("🚀 DevPath Agent")
st.subheader("Your Autonomous AI Career Co-Pilot")
st.caption("Powered by LLaMA 3.3 + LangGraph + Groq")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🐙 GitHub Analyzer",
    "📄 Resume Analyzer",
    "🌉 Bridge Plan",
    "💬 Career Chat"
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — GitHub Analyzer
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.header("🐙 GitHub Profile Analyzer")
    st.write("Enter any GitHub username to analyze their developer profile.")

    github_username = st.text_input(
        "GitHub Username",
        placeholder="e.g. satyanandh-ai",
        key="github_input"
    )

    if st.button("🔍 Analyze GitHub Profile", key="github_btn"):
        if github_username.strip():
            with st.spinner(f"Fetching GitHub profile of '{github_username}'..."):
                query = f"Use the analyze_github tool to analyze GitHub profile of {github_username}. Tell me: 1) what kind of developer they are 2) their main skills 3) quality of their projects"
                result = ask_agent(query)

            if "ERROR" in result:
                st.error(result)
            else:
                st.success("✅ Analysis Complete!")
                st.markdown(result)
        else:
            st.warning("Please enter a GitHub username!")

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — Resume Analyzer
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.header("📄 Resume Analyzer")
    st.write("Upload your resume PDF for instant AI-powered analysis.")

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        key="resume_upload"
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        if st.button("🔍 Analyze Resume", key="resume_btn"):
            with st.spinner("Reading your resume..."):
                resume_text = read_pdf(uploaded_file)

            if resume_text.startswith("ERROR"):
                st.error(resume_text)
            else:
                with st.spinner("AI is analyzing your resume..."):
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

                st.success("✅ Resume Analysis Complete!")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Analysis Result")
                    st.markdown(result)
                with col2:
                    st.markdown("### Resume Text Preview")
                    st.text_area("Extracted Text", resume_text[:500] + "...", height=300)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — Bridge Plan
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.header("🌉 Personalized Bridge Plan")
    st.write("Cross-reference your GitHub with your career goal to get a custom roadmap!")
    st.caption("💡 Try any role: Backend Developer, MLOps Engineer, Data Engineer, LLM Engineer, etc.")

    col1, col2 = st.columns(2)
    with col1:
        bridge_github = st.text_input(
            "Your GitHub Username",
            placeholder="e.g. satyanandh-ai",
            key="bridge_github"
        )
    with col2:
        bridge_goal = st.text_input(
            "Your Career Goal",
            placeholder="e.g. MLOps Engineer",
            key="bridge_goal"
        )

    if st.button("🌉 Build My Bridge Plan", key="bridge_btn"):
        if bridge_github.strip() and bridge_goal.strip():
            with st.spinner("🔍 Fetching your GitHub profile..."):
                github_data = analyze_github.invoke({"username": bridge_github})

            if "ERROR" in github_data:
                st.error(github_data)
            else:
                with st.spinner(f"🎯 Researching required skills for '{bridge_goal}'..."):
                    required_skills = get_skills_for_role.invoke({"role": bridge_goal})

                if "ERROR" in required_skills:
                    st.error(required_skills)
                else:
                    with st.spinner("🌉 Building your personalized bridge plan..."):
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

                    st.success("✅ Your Bridge Plan is Ready!")
                    st.markdown(result)
        else:
            st.warning("Please fill in both fields!")

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — Career Chat
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.header("💬 Career Chat")
    st.write("Ask anything about your career, skills, or job search!")

    career_question = st.text_area(
        "Ask your career question",
        placeholder="e.g. What skills should I learn to get an AI internship?",
        height=100,
        key="career_chat"
    )

    if st.button("💬 Ask Agent", key="chat_btn"):
        if career_question.strip():
            with st.spinner("🤖 Agent is thinking..."):
                result = ask_agent(career_question)

            st.success("✅ Done!")
            st.markdown(result)
        else:
            st.warning("Please type your question!")

# ── Footer ────────────────────────────────────────────────────────────
st.divider()
st.caption("🚀 DevPath Agent | Built with LangChain + LangGraph + Groq + Streamlit | Agentic Arena 2026 | Ch. Satyanand | ALIET Vijayawada")