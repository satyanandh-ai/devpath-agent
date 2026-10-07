# DevPath RAG Engine — RAG-2 (retrieval + reranking + evidence pack)
# Real semantic embeddings (fastembed / BAAI/bge-small-en-v1.5)
# Persistent ChromaDB. Single source of truth — app.py not wired in yet.

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from fastembed import TextEmbedding
import json
import os
import re
import math
from collections import Counter

# ══════════════════════════════════════════════════════════════════════
#  STEP 4 — REAL EMBEDDINGS (replaces DevPathEmbedding hash function)
# ══════════════════════════════════════════════════════════════════════
class FastEmbedFunction(EmbeddingFunction):
    """Real semantic embeddings via fastembed (ONNX, no PyTorch).
    Model: BAAI/bge-small-en-v1.5 — locked decision, RAG-1."""

    _model = None  # loaded once, shared across instances

    def __init__(self):
        if FastEmbedFunction._model is None:
            FastEmbedFunction._model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def __call__(self, input: Documents) -> Embeddings:
        texts = [str(t) for t in input]
        vectors = list(FastEmbedFunction._model.embed(texts))
        return [v.tolist() for v in vectors]


# ══════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE (raw source data)
# ══════════════════════════════════════════════════════════════════════
JOB_INTELLIGENCE = [
    {"id":"j1","role":"AI Engineer","company":"Google","skills":["python","langchain","llm","fastapi","docker","gcp"],"salary_india":"₹15L–₹30L","demand":"Very High","text":"Google AI Engineer requires Python LangChain LLM integration FastAPI Docker GCP. Build AI-powered products at scale."},
    {"id":"j2","role":"AI Engineer","company":"Microsoft","skills":["python","azure","docker","pytorch","fastapi","git"],"salary_india":"₹12L–₹25L","demand":"Very High","text":"Microsoft AI Engineer requires Python Azure Docker PyTorch FastAPI Git. Build intelligent applications."},
    {"id":"j3","role":"AI Engineer","company":"OpenAI","skills":["python","pytorch","llm","rag","langchain","kubernetes"],"salary_india":"₹20L–₹40L","demand":"Extremely High","text":"OpenAI AI Engineer needs Python PyTorch LLM RAG LangChain Kubernetes. Research and production systems."},
    {"id":"j4","role":"AI Engineer","company":"Anthropic","skills":["python","pytorch","llm","rag","aws","docker"],"salary_india":"₹18L–₹35L","demand":"Extremely High","text":"Anthropic AI Engineer Python PyTorch LLM safety RAG AWS Docker. Safety-focused AI development."},
    {"id":"j5","role":"AI Engineer","company":"AI Startup","skills":["python","langchain","fastapi","docker","sql","git"],"salary_india":"₹8L–₹18L","demand":"High","text":"AI Engineer startup Python LangChain FastAPI Docker SQL Git. Build AI agents and APIs."},
    {"id":"j6","role":"AI Engineer Intern","company":"Startups","skills":["python","fastapi","langchain","git","sql"],"salary_india":"₹15K–₹40K/month","demand":"High","text":"AI Engineer Intern Python FastAPI LangChain Git SQL. Build AI features and REST APIs."},
    {"id":"j7","role":"ML Engineer","company":"Amazon","skills":["python","pytorch","tensorflow","aws","docker","mlflow"],"salary_india":"₹12L–₹22L","demand":"High","text":"Amazon ML Engineer Python PyTorch TensorFlow AWS SageMaker Docker MLflow. Production ML systems."},
    {"id":"j8","role":"ML Engineer","company":"Meta","skills":["python","pytorch","spark","kubernetes","mlflow","git"],"salary_india":"₹15L–₹28L","demand":"High","text":"Meta ML Engineer Python PyTorch Spark Kubernetes MLflow Git. Large-scale ML infrastructure."},
    {"id":"j9","role":"ML Engineer","company":"NVIDIA","skills":["python","cuda","pytorch","tensorflow","docker","aws"],"salary_india":"₹14L–₹26L","demand":"High","text":"NVIDIA ML Engineer Python CUDA PyTorch TensorFlow Docker AWS. GPU-accelerated machine learning."},
    {"id":"j10","role":"MLOps Engineer","company":"Netflix","skills":["docker","kubernetes","python","mlflow","aws","ci/cd","airflow"],"salary_india":"₹14L–₹28L","demand":"Very High","text":"Netflix MLOps Docker Kubernetes Python MLflow AWS CI/CD Airflow. Scale ML pipelines to millions."},
    {"id":"j11","role":"MLOps Engineer","company":"Uber","skills":["kubernetes","docker","python","terraform","aws","mlflow","linux"],"salary_india":"₹12L–₹24L","demand":"Very High","text":"Uber MLOps Engineer Kubernetes Docker Python Terraform AWS MLflow Linux. Real-time ML infrastructure."},
    {"id":"j12","role":"GenAI Engineer","company":"Cohere","skills":["python","langchain","rag","vector databases","fastapi","docker","openai api"],"salary_india":"₹16L–₹32L","demand":"Extremely High","text":"Cohere GenAI Engineer Python LangChain RAG Vector Databases FastAPI Docker OpenAI API."},
    {"id":"j13","role":"GenAI Engineer","company":"Hugging Face","skills":["python","transformers","langchain","rag","pytorch","fastapi"],"salary_india":"₹14L–₹28L","demand":"Extremely High","text":"Hugging Face GenAI Python Transformers LangChain RAG PyTorch FastAPI. Open-source AI models."},
    {"id":"j14","role":"GenAI Engineer","company":"AI Startup","skills":["python","langchain","langgraph","rag","prompt engineering","fastapi","docker"],"salary_india":"₹10L–₹22L","demand":"Extremely High","text":"GenAI Engineer startup Python LangChain LangGraph RAG Prompt Engineering FastAPI Docker."},
    {"id":"j15","role":"Data Scientist","company":"McKinsey","skills":["python","sql","pandas","statistics","sklearn","tableau"],"salary_india":"₹10L–₹20L","demand":"High","text":"McKinsey Data Scientist Python SQL Pandas Statistics Scikit-learn Tableau. Data-driven consulting."},
    {"id":"j16","role":"Data Scientist","company":"Amazon","skills":["python","sql","spark","pandas","sklearn","aws","statistics"],"salary_india":"₹12L–₹22L","demand":"High","text":"Amazon Data Scientist Python SQL Spark Pandas Scikit-learn AWS Statistics. E-commerce analytics."},
    {"id":"j17","role":"Backend Engineer","company":"Razorpay","skills":["python","fastapi","postgresql","redis","docker","aws","git"],"salary_india":"₹8L–₹18L","demand":"High","text":"Razorpay Backend Engineer Python FastAPI PostgreSQL Redis Docker AWS Git. Fintech payments platform."},
    {"id":"j18","role":"Backend Engineer","company":"CRED","skills":["python","django","sql","redis","kubernetes","docker"],"salary_india":"₹10L–₹20L","demand":"High","text":"CRED Backend Engineer Python Django SQL Redis Kubernetes Docker. Consumer fintech products."},
    {"id":"j19","role":"Data Analyst","company":"Deloitte","skills":["sql","excel","python","tableau","statistics","power bi"],"salary_india":"₹5L–₹10L","demand":"Medium-High","text":"Deloitte Data Analyst SQL Excel Python Tableau Statistics Power BI. Business intelligence consulting."},
    {"id":"j20","role":"Data Analyst","company":"Amazon","skills":["sql","python","tableau","pandas","statistics","excel"],"salary_india":"₹6L–₹12L","demand":"Medium-High","text":"Amazon Data Analyst SQL Python Tableau Pandas Statistics Excel. E-commerce data analytics."},
]

INTERVIEW_INTELLIGENCE = [
    {"id":"i1","role":"AI Engineer","question":"Explain how RAG (Retrieval Augmented Generation) works and when you would use it.","difficulty":"Medium","topic":"LLM","hint":"Cover: retrieval from vector DB, context injection, generation step, use cases vs fine-tuning"},
    {"id":"i2","role":"AI Engineer","question":"What is the difference between fine-tuning and prompt engineering? When would you choose each?","difficulty":"Medium","topic":"LLM","hint":"Cost, data requirements, use cases, latency, speed of iteration"},
    {"id":"i3","role":"AI Engineer","question":"How would you design a production-grade AI agent that handles errors gracefully?","difficulty":"Hard","topic":"System Design","hint":"Tool calling, retry logic, fallbacks, monitoring, logging, circuit breakers"},
    {"id":"i4","role":"AI Engineer","question":"Explain LangChain's agent loop. What is ReAct?","difficulty":"Medium","topic":"LangChain","hint":"Reason + Act cycle, tool calling, observation loop, final answer"},
    {"id":"i5","role":"AI Engineer","question":"What are the main challenges in deploying LLM applications to production?","difficulty":"Hard","topic":"Production","hint":"Latency, cost, hallucinations, rate limits, prompt injection, monitoring"},
    {"id":"i6","role":"AI Engineer","question":"How do you evaluate the quality of an LLM output?","difficulty":"Medium","topic":"Evaluation","hint":"BLEU, ROUGE, human eval, G-Eval, LLM-as-judge approaches"},
    {"id":"i7","role":"AI Engineer","question":"Describe the difference between LangChain and LangGraph.","difficulty":"Medium","topic":"LangChain","hint":"LangGraph adds stateful multi-agent workflows, cycles, conditional edges, state management"},
    {"id":"i8","role":"AI Engineer","question":"What is vector similarity search? Name 3 vector databases.","difficulty":"Easy","topic":"RAG","hint":"Cosine similarity, Euclidean distance. ChromaDB, Pinecone, Weaviate, Qdrant"},
    {"id":"i9","role":"ML Engineer","question":"Explain the bias-variance tradeoff with examples.","difficulty":"Medium","topic":"ML Theory","hint":"Underfitting vs overfitting, model complexity, regularization techniques"},
    {"id":"i10","role":"ML Engineer","question":"How do you handle class imbalance in a classification problem?","difficulty":"Medium","topic":"ML Practice","hint":"SMOTE, class weights, precision-recall tradeoff, resampling strategies"},
    {"id":"i11","role":"ML Engineer","question":"What is gradient descent and its main variants?","difficulty":"Medium","topic":"Deep Learning","hint":"SGD, Adam, RMSprop - learning rate, momentum, adaptive learning rates"},
    {"id":"i12","role":"ML Engineer","question":"How would you deploy a PyTorch model to production?","difficulty":"Hard","topic":"MLOps","hint":"ONNX export, FastAPI serving, Docker, Kubernetes, monitoring, A/B testing"},
    {"id":"i13","role":"MLOps Engineer","question":"What is the difference between Docker and Kubernetes?","difficulty":"Medium","topic":"DevOps","hint":"Container vs orchestration, scaling, service discovery, load balancing"},
    {"id":"i14","role":"MLOps Engineer","question":"Explain CI/CD pipeline for an ML project.","difficulty":"Medium","topic":"MLOps","hint":"Testing, model validation, automated deployment, rollback, data validation"},
    {"id":"i15","role":"MLOps Engineer","question":"How do you monitor a deployed ML model in production?","difficulty":"Hard","topic":"Monitoring","hint":"Data drift, concept drift, performance metrics, alerting, retraining triggers"},
    {"id":"i16","role":"GenAI Engineer","question":"What is prompt injection and how do you defend against it?","difficulty":"Hard","topic":"LLM Security","hint":"Input validation, system prompts, output filtering, sandboxing"},
    {"id":"i17","role":"GenAI Engineer","question":"Explain the architecture of a multi-agent system using LangGraph.","difficulty":"Hard","topic":"Agents","hint":"Nodes, edges, state, supervisor agent, conditional routing, tool calling"},
    {"id":"i18","role":"GenAI Engineer","question":"What are the tradeoffs between different embedding models?","difficulty":"Medium","topic":"RAG","hint":"Speed, accuracy, dimensions, cost, domain specificity, multilingual support"},
    {"id":"i19","role":"Data Scientist","question":"Explain p-value and statistical significance.","difficulty":"Medium","topic":"Statistics","hint":"Null hypothesis, Type I error, alpha threshold 0.05, interpretation pitfalls"},
    {"id":"i20","role":"Data Scientist","question":"How would you approach a problem with missing data?","difficulty":"Medium","topic":"Data Engineering","hint":"MCAR/MAR/MNAR types, imputation strategies, dropping vs filling approaches"},
    {"id":"i21","role":"Backend Engineer","question":"Explain REST API design best practices.","difficulty":"Medium","topic":"API Design","hint":"HTTP methods, status codes, versioning, pagination, authentication, idempotency"},
    {"id":"i22","role":"Backend Engineer","question":"How does FastAPI handle async requests?","difficulty":"Medium","topic":"FastAPI","hint":"async/await, event loop, Starlette foundation, uvicorn workers, concurrency"},
    {"id":"i23","role":"General","question":"Describe a project where you faced a technical challenge and how you solved it.","difficulty":"Medium","topic":"Behavioral","hint":"STAR method: Situation, Task, Action, Result with quantified impact"},
    {"id":"i24","role":"General","question":"How do you keep up with AI/ML research and developments?","difficulty":"Easy","topic":"Behavioral","hint":"Papers, conferences, GitHub, communities, podcasts, implementing from scratch"},
    {"id":"i25","role":"General","question":"Walk me through your most impressive project end-to-end.","difficulty":"Medium","topic":"Behavioral","hint":"Problem, tech choices, challenges, results, what you'd do differently"},
]

LEARNING_INTELLIGENCE = [
    {"id":"l1","skill":"docker","resource":"Docker Official Get Started","url":"https://docs.docker.com/get-started/","difficulty":"Beginner","time":"1 week","text":"Docker containerization basics build images run containers docker-compose networking volumes"},
    {"id":"l2","skill":"docker","resource":"Dockerizing ML Projects","url":"https://towardsdatascience.com","difficulty":"Intermediate","time":"3 days","text":"Docker ML projects multi-stage builds optimize image size production deployment"},
    {"id":"l3","skill":"aws","resource":"AWS Cloud Practitioner Free Tier","url":"https://aws.amazon.com/training/","difficulty":"Beginner","time":"2 weeks","text":"AWS fundamentals EC2 S3 Lambda IAM VPC RDS free tier cloud services"},
    {"id":"l4","skill":"aws","resource":"Deploy FastAPI to AWS EC2","url":"https://aws.amazon.com/ec2/","difficulty":"Intermediate","time":"3 days","text":"Deploy Python FastAPI AWS EC2 configure nginx SSL domain production deployment"},
    {"id":"l5","skill":"kubernetes","resource":"Kubernetes Official Tutorial","url":"https://kubernetes.io/docs/tutorials/","difficulty":"Intermediate","time":"2 weeks","text":"Kubernetes pods deployments services ingress ConfigMaps Secrets scaling orchestration"},
    {"id":"l6","skill":"langchain","resource":"LangChain Python Docs","url":"https://python.langchain.com","difficulty":"Beginner","time":"3 days","text":"LangChain chains agents tools memory prompts LLM integration callbacks"},
    {"id":"l7","skill":"langgraph","resource":"LangGraph Official Tutorial","url":"https://langchain-ai.github.io/langgraph/","difficulty":"Intermediate","time":"1 week","text":"LangGraph stateful agents nodes edges supervisor pattern multi-agent workflows"},
    {"id":"l8","skill":"pytorch","resource":"PyTorch 60 Minute Blitz","url":"https://pytorch.org/tutorials/","difficulty":"Beginner","time":"1 week","text":"PyTorch tensors autograd neural networks training loop GPU acceleration deep learning"},
    {"id":"l9","skill":"fastapi","resource":"FastAPI Official Documentation","url":"https://fastapi.tiangolo.com","difficulty":"Beginner","time":"3 days","text":"FastAPI routes Pydantic models dependency injection async OpenAPI documentation"},
    {"id":"l10","skill":"rag","resource":"Build Production RAG with LangChain","url":"https://python.langchain.com/docs/","difficulty":"Intermediate","time":"1 week","text":"RAG pipeline load documents chunk embed store vector DB retrieve generate production"},
    {"id":"l11","skill":"mlflow","resource":"MLflow Getting Started Guide","url":"https://mlflow.org/docs/","difficulty":"Beginner","time":"3 days","text":"MLflow experiment tracking log metrics model registry deployment lifecycle"},
    {"id":"l12","skill":"sql","resource":"SQLZoo Interactive SQL Tutorial","url":"https://sqlzoo.net","difficulty":"Beginner","time":"1 week","text":"SQL SELECT JOIN GROUP BY subqueries window functions indexes PostgreSQL MySQL"},
    {"id":"l13","skill":"ci/cd","resource":"GitHub Actions Complete Guide","url":"https://docs.github.com/en/actions","difficulty":"Intermediate","time":"3 days","text":"GitHub Actions workflows automated testing deployment pipelines secrets CI/CD"},
    {"id":"l14","skill":"prompt engineering","resource":"Prompt Engineering Guide","url":"https://www.promptingguide.ai","difficulty":"Beginner","time":"2 days","text":"Prompt engineering chain of thought few-shot zero-shot system prompts structured outputs"},
    {"id":"l15","skill":"vector databases","resource":"ChromaDB Quickstart","url":"https://docs.trychroma.com","difficulty":"Beginner","time":"2 days","text":"ChromaDB vector database collections embeddings semantic search metadata filtering"},
    {"id":"l16","skill":"tensorflow","resource":"TensorFlow Keras Tutorials","url":"https://www.tensorflow.org/tutorials","difficulty":"Beginner","time":"1 week","text":"TensorFlow Keras models layers training evaluation deployment SavedModel"},
    {"id":"l17","skill":"pandas","resource":"Pandas Official User Guide","url":"https://pandas.pydata.org/docs/","difficulty":"Beginner","time":"3 days","text":"Pandas DataFrames groupby merge pivot time series data cleaning transformation"},
    {"id":"l18","skill":"kubernetes","resource":"K8s for ML Engineers","url":"https://kubernetes.io","difficulty":"Advanced","time":"3 weeks","text":"Kubernetes ML workloads GPU scheduling resource limits auto-scaling Helm charts"},
]

CAREER_INTELLIGENCE = [
    {"id":"c1","topic":"ATS Rules","text":"ATS systems scan for exact keyword matches. Include role-specific keywords from job description. Use standard headers: Education Experience Skills Projects. Avoid tables columns images."},
    {"id":"c2","topic":"ATS Rules","text":"ATS prefers PDF or DOCX. Simple bullet points standard fonts. 15-20 relevant technical keywords naturally placed. One page for under 2 years experience."},
    {"id":"c3","topic":"Resume Tips","text":"Quantify achievements with numbers: Improved API response time by 40% beats improved performance. Recruiters spend 6-10 seconds on initial scan. Start bullets with action verbs."},
    {"id":"c4","topic":"Resume Tips","text":"Tailor resume to each job description. Mirror language from JD. Include GitHub link LinkedIn profile email phone number. Projects section is crucial for freshers."},
    {"id":"c5","topic":"GitHub Best Practices","text":"Every project needs README with description tech stack setup instructions screenshots demo link. 85% of recruiters check GitHub before interview. Pin 6 best repositories."},
    {"id":"c6","topic":"GitHub Best Practices","text":"Pin best repositories. Add topics tags to each repo. Include deployed demo link homepage URL. Keep commit history active. Write meaningful commit messages."},
    {"id":"c7","topic":"Portfolio Tips","text":"Quality over quantity: 3-4 strong deployed projects beat 20 incomplete repos. Show full-stack capability. End-to-end AI projects impress judges: data collection preprocessing model training API deployment."},
    {"id":"c8","topic":"Hiring Trends 2026","text":"Top skills in demand 2026: LangChain LangGraph RAG Vector Databases Agentic AI FastAPI Docker Kubernetes MLOps Prompt Engineering fine-tuning."},
    {"id":"c9","topic":"Interview Prep","text":"For AI Engineer roles understand transformer architecture attention mechanism fine-tuning vs RAG LLM evaluation prompt injection production deployment challenges latency optimization."},
    {"id":"c10","topic":"Interview Prep","text":"Behavioral questions use STAR method Situation Task Action Result. Prepare 5-7 stories: technical challenge teamwork failure learning leadership ownership."},
    {"id":"c11","topic":"Salary Negotiation","text":"Research salary ranges on Glassdoor LinkedIn Levels.fyi before negotiating. India entry-level AI Engineer 6L-12L. With strong projects 10L-18L. Senior roles 20L-40L."},
    {"id":"c12","topic":"Cold Outreach","text":"Cold email formula: specific compliment about their work brief intro with one achievement clear ask 15-minute call GitHub LinkedIn link. Under 150 words. Follow up once after 1 week."},
    {"id":"c13","topic":"LinkedIn Tips","text":"Professional photo keyword-rich headline not just Student detailed about section all projects skills endorsements 500+ connections activity posting original content."},
    {"id":"c14","topic":"Career Growth","text":"First job strategy: pick company with good mentorship culture code review practices. Skills matter more than title. Build projects outside work. Contribute to open source. Speak at meetups."},
    {"id":"c15","topic":"Internship Strategy","text":"Apply to 50+ internships minimum. Personalize first 2 lines of each email. Follow up after 1 week. LinkedIn cold outreach works better than job portals for AI roles."},
]


# ══════════════════════════════════════════════════════════════════════
#  STEP 1 — CLEANING
# ══════════════════════════════════════════════════════════════════════
def clean_text(text: str) -> str:
    """Normalize whitespace, strip control characters."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()

def clean_and_validate(records: list, required_fields: list, content_field: str = "text") -> list:
    """Remove duplicates (by id and by exact-content match) and drop records
    missing required fields.

    `content_field` is whichever key holds the retrievable content for this
    collection — NOT all collections use "text" (interviews use "question").
    Passing the wrong content_field silently collapses every record to a
    single "duplicate" of empty string, which is the bug this fixes.
    """
    seen_ids = set()
    seen_texts = set()
    cleaned = []
    for r in records:
        if not all(r.get(f) for f in required_fields):
            continue  # missing required field — drop
        rid = r.get("id")
        if rid in seen_ids:
            continue  # duplicate id — drop
        text_key = clean_text(r.get(content_field, "")).lower()
        if text_key and text_key in seen_texts:
            continue  # duplicate content — drop (only when non-empty)
        seen_ids.add(rid)
        seen_texts.add(text_key)
        r = dict(r)  # don't mutate original
        if content_field in r:
            r[content_field] = clean_text(r[content_field])
        cleaned.append(r)
    return cleaned


# ══════════════════════════════════════════════════════════════════════
#  STEP 2 — STANDARDIZED METADATA
#  Every document gets: source, category, type (+ category-specific fields)
# ══════════════════════════════════════════════════════════════════════
def build_job_metadata(j: dict) -> dict:
    return {
        "source": "DevPath Job Intelligence",
        "category": "jobs",
        "type": "job_requirement",
        "role": j["role"],
        "company": j["company"],
        "skills": json.dumps(j["skills"]),
        "salary_india": j["salary_india"],
        "demand": j["demand"],
    }

def build_interview_metadata(q: dict) -> dict:
    return {
        "source": "DevPath Interview Intelligence",
        "category": "interviews",
        "type": "interview_question",
        "role": q["role"],
        "question": q["question"],
        "difficulty": q["difficulty"],
        "topic": q["topic"],
        "hint": q["hint"],
    }

def build_learning_metadata(r: dict) -> dict:
    return {
        "source": "DevPath Learning Intelligence",
        "category": "learning",
        "type": "learning_resource",
        "skill": r["skill"],
        "resource": r["resource"],
        "url": r["url"],
        "difficulty": r["difficulty"],
        "time": r["time"],
    }

def build_career_metadata(c: dict) -> dict:
    return {
        "source": "DevPath Career Intelligence",
        "category": "career",
        "type": "career_knowledge",
        "topic": c["topic"],
    }


# ══════════════════════════════════════════════════════════════════════
#  RAG ENGINE
# ══════════════════════════════════════════════════════════════════════
class DevPathRAG:
    """DevPath RAG-2 engine.

    Design goals:
    - real semantic retrieval with FastEmbed + ChromaDB
    - multi-query candidate expansion
    - deterministic lexical/skill/role reranking without another LLM call
    - no fake "similarity percentages"
    - metadata-aware filtering and source attribution
    - relevance thresholds so weak evidence can be rejected
    - backward-compatible retrieve_* methods for app.py
    """

    RAG_VERSION = "2.0"
    DEFAULT_PERSIST_PATH = "/tmp/devpath_chroma_db"
    DEFAULT_MIN_RELEVANCE = 0.42

    def __init__(self, persist_path: str = DEFAULT_PERSIST_PATH):
        self._persist_path = persist_path
        self._client = None
        self._ef = None
        self._initialized = False
        self._collections = {}

    def _get_client(self):
        if self._client is None:
            os.makedirs(self._persist_path, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self._persist_path)
            self._ef = FastEmbedFunction()
        return self._client, self._ef

    # ------------------------------------------------------------------
    # Normalization / deterministic ranking helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _norm(value) -> str:
        value = clean_text(value).lower()
        value = re.sub(r"[^a-z0-9+#./-]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @classmethod
    def _tokens(cls, value) -> set:
        text = cls._norm(value)
        if not text:
            return set()
        return set(re.findall(r"[a-z0-9]+(?:[+#./-][a-z0-9]+)*", text))

    @classmethod
    def _token_overlap(cls, query: str, document: str) -> float:
        q = cls._tokens(query)
        d = cls._tokens(document)
        if not q or not d:
            return 0.0
        return len(q & d) / max(1, len(q))

    @staticmethod
    def _skill_aliases(skill: str) -> set:
        s = clean_text(skill).lower()
        aliases = {
            "llm": {"llm", "llms", "large language model", "genai", "generative ai"},
            "vector database": {"vector database", "vector databases", "chromadb", "pinecone", "qdrant", "weaviate", "faiss"},
            "scikit-learn": {"scikit-learn", "sklearn", "scikit learn"},
            "github": {"github", "github.com"},
            "github-api": {"github api", "pygithub", "octokit"},
            "rest api": {"rest api", "restful api", "api development", "http api"},
            "ci/cd": {"ci/cd", "cicd", "github actions", "jenkins", "gitlab ci", "continuous integration"},
            "machine learning": {"machine learning", "ml"},
            "deep learning": {"deep learning", "dl", "neural network", "neural networks"},
            "openai api": {"openai api", "chatgpt api"},
            "langgraph": {"langgraph"},
            "langchain": {"langchain"},
            "fastapi": {"fastapi", "fast api"},
            "docker": {"docker", "dockerfile", "docker compose", "docker-compose", "containerization"},
        }
        return aliases.get(s, {s})

    @classmethod
    def _canonical_skill_set(cls, skills) -> set:
        out = set()
        for skill in skills or []:
            s = cls._norm(skill)
            if not s:
                continue
            out.add(s)
        return out

    @classmethod
    def _skill_match(cls, requested_skills, candidate_skills) -> tuple:
        requested = cls._canonical_skill_set(requested_skills)
        candidate = cls._canonical_skill_set(candidate_skills)
        if not requested or not candidate:
            return 0.0, []
        matched = []
        for skill in requested:
            aliases = cls._skill_aliases(skill)
            if any(alias in candidate or any(alias in c for c in candidate) for alias in aliases):
                matched.append(skill)
        return len(matched) / len(requested), sorted(matched)

    @classmethod
    def _role_match(cls, requested_role: str, candidate_role: str) -> float:
        q = cls._tokens(requested_role)
        c = cls._tokens(candidate_role)
        if not q or not c:
            return 0.0
        # Exact role phrase is strongest; token overlap is the fallback.
        if cls._norm(requested_role) == cls._norm(candidate_role):
            return 1.0
        overlap = len(q & c) / len(q)
        # Related role families are useful but should not look like exact matches.
        families = [
            ({"ai", "engineer"}, {"genai", "engineer"}),
            ({"ai", "engineer"}, {"ml", "engineer"}),
            ({"ai", "engineer"}, {"backend", "engineer"}),
            ({"genai", "engineer"}, {"ai", "engineer"}),
            ({"ml", "engineer"}, {"ai", "engineer"}),
        ]
        if any(q <= a and c <= b or q <= b and c <= a for a, b in families):
            return max(overlap, 0.65)
        return overlap

    @staticmethod
    def _distance_to_semantic_score(distance) -> float:
        """Convert Chroma distance to a bounded ranking score, not a percentage.

        We deliberately do not expose this as a probability or percent. The
        exact meaning of Chroma's distance depends on the configured metric.
        """
        try:
            d = max(0.0, float(distance))
        except (TypeError, ValueError):
            return 0.0
        return math.exp(-d)

    @classmethod
    def _combine_score(cls, semantic: float, lexical: float,
                       skill: float = 0.0, role: float = 0.0) -> float:
        # Weighted deterministic reranker. Semantic remains the largest signal.
        score = (
            0.55 * semantic +
            0.15 * lexical +
            0.20 * skill +
            0.10 * role
        )
        return round(max(0.0, min(1.0, score)), 4)

    @staticmethod
    def _dedupe(results: list) -> list:
        seen = set()
        out = []
        for item in results:
            meta = item.get("metadata", {})
            key = (
                item.get("id") or meta.get("id") or
                meta.get("company") or meta.get("resource") or
                item.get("document", "")
            )
            key = str(key).strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out

    # ------------------------------------------------------------------
    # Initialization / persistence
    # ------------------------------------------------------------------
    def initialize(self, force_reseed: bool = False):
        if self._initialized and not force_reseed:
            return

        client, ef = self._get_client()

        jobs = clean_and_validate(
            JOB_INTELLIGENCE, ["id", "text", "role", "company"], content_field="text"
        )
        interviews = clean_and_validate(
            INTERVIEW_INTELLIGENCE, ["id", "question", "role"], content_field="question"
        )
        learning = clean_and_validate(
            LEARNING_INTELLIGENCE, ["id", "text", "skill", "resource"], content_field="text"
        )
        career = clean_and_validate(
            CAREER_INTELLIGENCE, ["id", "text", "topic"], content_field="text"
        )

        collections_data = [
            ("jobs", [(j["id"], j["text"], build_job_metadata(j)) for j in jobs]),
            ("interviews", [(q["id"], f"{q['question']} {q['hint']}", build_interview_metadata(q)) for q in interviews]),
            ("learning", [(r["id"], r["text"], build_learning_metadata(r)) for r in learning]),
            ("career", [(c["id"], c["text"], build_career_metadata(c)) for c in career]),
        ]

        for name, data in collections_data:
            reseed = force_reseed
            col = None
            try:
                col = client.get_collection(name, embedding_function=ef)
                metadata = col.metadata or {}
                if metadata.get("devpath_rag_version") != self.RAG_VERSION:
                    reseed = True
            except Exception:
                pass

            if reseed:
                try:
                    client.delete_collection(name)
                except Exception:
                    pass
                col = None

            if col is None:
                col = client.create_collection(
                    name,
                    embedding_function=ef,
                    metadata={
                        "devpath_rag_version": self.RAG_VERSION,
                        "embedding_model": "BAAI/bge-small-en-v1.5",
                        "distance_note": "Chroma distance used for ranking; not a probability",
                    },
                )
                if data:
                    col.add(
                        ids=[d[0] for d in data],
                        documents=[d[1] for d in data],
                        metadatas=[d[2] for d in data],
                    )

            self._collections[name] = col

        self._initialized = True

    # ------------------------------------------------------------------
    # Core retrieval
    # ------------------------------------------------------------------
    def retrieve(self, collection_name: str, query: str, n: int = 5,
                 candidate_n: int | None = None, min_relevance: float = 0.0,
                 where: dict | None = None) -> list:
        """Retrieve and deterministically rerank evidence.

        Returned fields intentionally distinguish `semantic_score` from the
        old misleading similarity percentage. `similarity` is retained as a
        backward-compatible alias to the semantic score, but is NOT a percent.
        """
        self.initialize()
        if collection_name not in self._collections:
            raise ValueError(f"Unknown RAG collection: {collection_name}")

        query = clean_text(query)
        if not query:
            return []

        col = self._collections[collection_name]
        count = col.count()
        if count <= 0:
            return []

        n = max(1, min(int(n), count))
        candidate_n = max(n, min(int(candidate_n or max(12, n * 3)), count))

        kwargs = {"query_texts": [query], "n_results": candidate_n}
        if where:
            kwargs["where"] = where

        results = col.query(**kwargs)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        out = []
        for doc, meta, dist, rid in zip(docs, metas, dists, ids):
            semantic = self._distance_to_semantic_score(dist)
            lexical = self._token_overlap(query, doc)
            combined = self._combine_score(semantic, lexical)
            out.append({
                "id": rid,
                "document": doc,
                "metadata": meta or {},
                "distance": round(float(dist), 6),
                "semantic_score": round(semantic, 4),
                "lexical_score": round(lexical, 4),
                "relevance_score": combined,
                # Backward-compatible alias. Never describe this as a percent.
                "similarity": round(semantic, 4),
            })

        out = sorted(out, key=lambda x: x["relevance_score"], reverse=True)
        if min_relevance > 0:
            out = [x for x in out if x["relevance_score"] >= min_relevance]
        return out[:n]

    def _multi_query_retrieve(self, collection_name: str, queries: list,
                              n: int, candidate_n: int | None = None,
                              min_relevance: float = 0.0) -> list:
        candidates = []
        for query in queries:
            if clean_text(query):
                candidates.extend(
                    self.retrieve(
                        collection_name, query, n=max(n, 5),
                        candidate_n=candidate_n, min_relevance=0.0
                    )
                )
        candidates = self._dedupe(candidates)
        candidates.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        if min_relevance > 0:
            candidates = [x for x in candidates if x["relevance_score"] >= min_relevance]
        return candidates[:n]

    # ------------------------------------------------------------------
    # Public domain-specific retrieval
    # ------------------------------------------------------------------
    def retrieve_jobs(self, role: str, user_skills: list, n: int = 5,
                      min_relevance: float = DEFAULT_MIN_RELEVANCE) -> list:
        skills = [clean_text(s) for s in (user_skills or []) if clean_text(s)]
        role = clean_text(role) or "AI Engineer"
        skill_text = " ".join(skills[:12])
        queries = [
            f"{role}",
            f"{role} required skills {skill_text}" if skill_text else role,
            f"{role} Python AI software engineering {skill_text}" if skill_text else role,
        ]

        raw = self._multi_query_retrieve("jobs", queries, n=max(n, 5), candidate_n=15,
                                         min_relevance=0.0)
        jobs = []
        for r in raw:
            m = r["metadata"]
            job_skills = json.loads(m.get("skills", "[]"))
            skill_score, matched = self._skill_match(skills, job_skills)
            role_score = self._role_match(role, m.get("role", ""))
            final = self._combine_score(
                r["semantic_score"], r["lexical_score"], skill_score, role_score
            )
            if final < min_relevance:
                continue
            jobs.append({
                "id": r.get("id"),
                "company": m["company"],
                "role": m["role"],
                "skills": job_skills,
                "salary_india": m["salary_india"],
                "demand": m["demand"],
                "matched_skills": matched,
                "skill_match_score": round(skill_score, 4),
                "role_match_score": round(role_score, 4),
                "semantic_score": r["semantic_score"],
                "relevance_score": final,
                "source": m.get("source", "DevPath Job Intelligence"),
            })

        # One job can be returned by several query variants. Keep the best one.
        best = {}
        for job in jobs:
            key = job["id"] or f"{job['company']}::{job['role']}"
            if key not in best or job["relevance_score"] > best[key]["relevance_score"]:
                best[key] = job
        return sorted(best.values(), key=lambda x: x["relevance_score"], reverse=True)[:n]

    def retrieve_interview_questions(self, role: str, n: int = 5,
                                     topics: list | None = None) -> list:
        role = clean_text(role) or "AI Engineer"
        topic_text = " ".join(topics or [])
        queries = [
            f"{role} interview technical questions",
            f"{role} interview {topic_text}" if topic_text else f"{role} interview system design",
        ]
        raw = self._multi_query_retrieve("interviews", queries, n=n, candidate_n=12,
                                         min_relevance=0.35)
        return [{
            "id": r.get("id"),
            "question": r["metadata"]["question"],
            "difficulty": r["metadata"]["difficulty"],
            "topic": r["metadata"]["topic"],
            "hint": r["metadata"]["hint"],
            "role": r["metadata"]["role"],
            "relevance_score": r["relevance_score"],
            "source": r["metadata"].get("source"),
        } for r in raw]

    def retrieve_learning_resources(self, skills: list, n: int = 4,
                                    min_relevance: float = 0.35) -> list:
        skills = [clean_text(s) for s in (skills or []) if clean_text(s)]
        if not skills:
            return []
        queries = [f"learn {s}" for s in skills[:5]]
        raw = self._multi_query_retrieve("learning", queries, n=max(n, 5), candidate_n=10,
                                         min_relevance=min_relevance)
        out = []
        seen = set()
        for r in raw:
            m = r["metadata"]
            key = m.get("resource", r.get("id"))
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "id": r.get("id"),
                "skill": m["skill"],
                "resource": m["resource"],
                "url": m["url"],
                "difficulty": m["difficulty"],
                "time": m["time"],
                "relevance_score": r["relevance_score"],
                "source": m.get("source"),
            })
        return out[:n]

    def retrieve_career_knowledge(self, query: str, n: int = 3,
                                  min_relevance: float = 0.35) -> list:
        raw = self.retrieve("career", query, n=n, candidate_n=max(9, n * 3),
                            min_relevance=min_relevance)
        return [{
            "id": r.get("id"),
            "topic": r["metadata"]["topic"],
            "content": r["document"],
            "relevance_score": r["relevance_score"],
            "source": r["metadata"].get("source"),
        } for r in raw]

    def build_evidence_pack(self, *, role: str = "", user_skills: list | None = None,
                            query: str = "", job_n: int = 5,
                            resource_n: int = 4, career_n: int = 3) -> dict:
        """Return a source-attributed pack suitable for grounded LLM generation.

        This method does not generate claims. It only returns retrieved evidence.
        """
        role = clean_text(role)
        skills = list(user_skills or [])
        pack = {
            "rag_version": self.RAG_VERSION,
            "query": clean_text(query),
            "role": role,
            "retrieval_policy": {
                "semantic_embeddings": "BAAI/bge-small-en-v1.5",
                "reranking": "semantic + lexical + skill + role",
                "scores_are_percentages": False,
            },
            "jobs": self.retrieve_jobs(role, skills, n=job_n) if role else [],
            "learning": self.retrieve_learning_resources(skills, n=resource_n),
            "career": self.retrieve_career_knowledge(query or role, n=career_n) if (query or role) else [],
        }
        return pack

    def get_stats(self) -> dict:
        self.initialize()
        return {
            "rag_version": self.RAG_VERSION,
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "collections": {k: v.count() for k, v in self._collections.items()},
            "total_documents": sum(v.count() for v in self._collections.values()),
        }


# Singleton — used by app.py once RAG-1 is verified and wired in (not yet)
rag = DevPathRAG()
