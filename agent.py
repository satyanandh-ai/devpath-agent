# DevPath Agent - Hackathon Polish Version

from dotenv import load_dotenv
import os
import requests
import PyPDF2
import textwrap
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Pretty Print Helper ───────────────────────────────────────────────
def print_box(title: str, content: str, width: int = 70):
    """Prints content inside a clean box."""
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)
    wrapped = textwrap.fill(content, width=width - 4)
    for line in wrapped.split("\n"):
        print(f"  {line}")
    print("═" * width + "\n")

def print_section(title: str, content: str, width: int = 70):
    """Prints a section with a header."""
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")
    for line in content.split("\n"):
        wrapped_lines = textwrap.wrap(line, width=width - 4)
        if wrapped_lines:
            for wl in wrapped_lines:
                print(f"  {wl}")
        else:
            print()
    print()

# ── TOOL 1: Skills for Role ──────────────────────────────────────────
@tool
def get_skills_for_role(role: str) -> str:
    """Returns the required skills for a given job role."""
    skills_db = {
        "backend developer": "Python, FastAPI, SQL, REST APIs, Docker, Git",
        "machine learning": "Python, NumPy, Pandas, Scikit-learn, TensorFlow, SQL, Cloud (AWS/GCP)",
        "data analyst": "Python, SQL, Excel, Power BI, Statistics, Pandas",
        "frontend developer": "HTML, CSS, JavaScript, React, Git",
        "data scientist": "Python, NumPy, Pandas, Scikit-learn, TensorFlow, Statistics, SQL",
    }
    role = role.lower()
    for key in skills_db:
        if key in role:
            return f"Skills needed for {role}: {skills_db[key]}"
    return "Role not found. Try: backend developer, machine learning, data analyst"

# ── TOOL 2: GitHub Analyzer ──────────────────────────────────────────
@tool
def analyze_github(username: str) -> str:
    """Analyzes a GitHub profile and returns repo information."""
    try:
        url = f"https://api.github.com/users/{username}"
        user_response = requests.get(url, timeout=10)

        if user_response.status_code == 404:
            return f"ERROR: GitHub user '{username}' not found. Please check the username."
        if user_response.status_code != 200:
            return f"ERROR: Could not reach GitHub API. Status: {user_response.status_code}"

        user_data = user_response.json()

        repos_url = f"https://api.github.com/users/{username}/repos"
        repos_response = requests.get(repos_url, timeout=10)
        repos = repos_response.json()

        if not repos or len(repos) == 0:
            return f"GitHub user '{username}' exists but has no public repositories."

        # Extract languages used
        languages = set()
        repo_info = []
        for repo in repos[:5]:
            lang = repo.get('language') or 'Unknown'
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
        return f"ERROR: Unexpected error: {str(e)}"

# ── PDF Reader ────────────────────────────────────────────────────────
def read_pdf(filepath: str) -> str:
    filepath = filepath.strip().strip('"').strip("'")
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
        if not text.strip():
            return "ERROR: Could not extract text from PDF."
        return text[:2000]
    except FileNotFoundError:
        return f"ERROR: File not found at: {filepath}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# ── Direct LLM Call ───────────────────────────────────────────────────
def ask_llm(prompt: str) -> str:
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"ERROR: LLM call failed: {str(e)}"

# ── Agent ─────────────────────────────────────────────────────────────
tools = [get_skills_for_role, analyze_github]
agent = create_react_agent(llm, tools)

def ask_agent(query: str) -> str:
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        return result["messages"][-1].content
    except Exception as e:
        return f"ERROR: Agent failed: {str(e)}"

# ══════════════════════════════════════════════════════════════════════
#                         MAIN PROGRAM
# ══════════════════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("          🚀 DevPath Agent — Your AI Career Co-Pilot")
print("═" * 70)
print("""
  Commands:
    github:<username>    → Analyze any GitHub profile
    resume:<filepath>    → Analyze your resume PDF
    bridge:<github> <goal> → Find your skill gap (THE MAGIC!)
    Or just ask anything about your career!
""")

user_input = input("  You: ").strip()
print()

# ── Route 1: GitHub ───────────────────────────────────────────────────
if user_input.lower().startswith("github:"):
    username = user_input[7:].strip()
    print(f"  🐙 Fetching GitHub profile of '{username}'...")

    query = f"Use the analyze_github tool to analyze GitHub profile of {username}. Tell me: 1) what kind of developer they are 2) their main skills 3) quality of their projects"
    result = ask_agent(query)

    if result.startswith("ERROR"):
        print_box("❌ Error", result)
    else:
        print_section("🐙 GitHub Analysis", result)

# ── Route 2: Resume ───────────────────────────────────────────────────
elif user_input.lower().startswith("resume:"):
    filepath = user_input[7:].strip()
    print(f"  📄 Reading resume from: {filepath}")

    resume_text = read_pdf(filepath)

    if resume_text.startswith("ERROR"):
        print_box("❌ Error", resume_text)
        print("  💡 Tip: Check the file path and try again!")
    else:
        print("  ✅ Resume loaded! Analyzing...\n")

        prompt = f"""You are a professional career advisor and resume expert.

Analyze this resume and provide:

1. 🛠️ SKILLS FOUND - List all technical and soft skills
2. 💼 JOB ROLES - Top 5 job roles this person can apply for right now
3. 📈 IMPROVEMENTS - Top 5 specific improvements to strengthen the resume
4. ⭐ ATS SCORE - Give a score out of 10 with explanation

Resume:
{resume_text}

Be specific, honest, and helpful."""

        result = ask_llm(prompt)
        print_section("📄 Resume Analysis", result)

# ── Route 3: BRIDGE (The Magic Feature!) ─────────────────────────────
elif user_input.lower().startswith("bridge:"):
    rest = user_input[7:].strip()
    parts = rest.split(" ", 1)

    if len(parts) < 2:
        print("  ❌ Usage: bridge:<github_username> <your career goal>")
        print("  Example: bridge:satyanandh-ai machine learning engineer")
    else:
        github_username = parts[0].strip()
        career_goal = parts[1].strip()

        print(f"  🔍 Analyzing GitHub: {github_username}")
        print(f"  🎯 Career Goal: {career_goal}")
        print(f"  🌉 Building your personalized bridge path...\n")

        # Step 1: Get GitHub data
        github_data = analyze_github.invoke({"username": github_username})

        # Step 2: Get required skills for goal
        required_skills = get_skills_for_role.invoke({"role": career_goal})

        # Step 3: Cross-reference and build bridge
        prompt = f"""You are a career advisor helping a developer level up.

CURRENT SKILLS (from their GitHub):
{github_data}

TARGET CAREER GOAL: {career_goal}
REQUIRED SKILLS FOR GOAL: {required_skills}

Now do a CROSS-REFERENCE analysis:

1. ✅ SKILLS THEY ALREADY HAVE - What skills from their GitHub match the goal?
2. ❌ SKILL GAPS - What skills are missing to reach their goal?
3. 🌉 BRIDGE PLAN - Give a specific 30-60-90 day action plan:
   - Week 1-4: What to learn first and how
   - Week 5-8: What to build as projects
   - Week 9-12: How to apply and what to showcase
4. 🎯 FIRST STEP - What should they do TODAY to start?

Be very specific. Use their actual GitHub projects as reference points."""

        result = ask_llm(prompt)
        print_section("🌉 Your Personalized Bridge Plan", result)

# ── Route 4: General Question ─────────────────────────────────────────
else:
    print("  🤖 Thinking...\n")
    result = ask_agent(user_input)
    print_section("🤖 Agent Answer", result)

print("═" * 70)
print("  DevPath Agent — Done! 🚀")
print("═" * 70 + "\n")