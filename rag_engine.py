# DevPath RAG Knowledge Engine
# 4 Collections: Jobs, Interview, Learning, Career Intelligence
# Uses ChromaDB in-memory + custom hash embedding (no model download needed)

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import hashlib
import numpy as np
import json

# ══════════════════════════════════════════════════════════════════════
#  CUSTOM EMBEDDING — works offline, no ONNX model download
# ══════════════════════════════════════════════════════════════════════
class DevPathEmbedding(EmbeddingFunction):
    """Word-level + trigram hash embedding. Fast, offline, no dependencies."""
    def __init__(self):
        self.dim = 256

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            vec = np.zeros(self.dim, dtype=float)
            text_lower = str(text).lower()
            # Word-level hashing
            for w in text_lower.split():
                h = int(hashlib.sha256(w.encode()).hexdigest(), 16) % self.dim
                vec[h] += 1.0
            # Trigram hashing for partial matches
            for i in range(len(text_lower) - 2):
                tg = text_lower[i:i+3]
                h = int(hashlib.md5(tg.encode()).hexdigest(), 16) % self.dim
                vec[h] += 0.3
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

# ══════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE
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
#  RAG ENGINE
# ══════════════════════════════════════════════════════════════════════
class DevPathRAG:
    def __init__(self):
        self._client = None
        self._ef = None
        self._initialized = False
        self._collections = {}

    def _get_client(self):
        if self._client is None:
            self._client = chromadb.Client()
            self._ef = DevPathEmbedding()
        return self._client, self._ef

    def initialize(self):
        if self._initialized:
            return
        client, ef = self._get_client()

        collections_data = [
            ("jobs",      [(j["id"],j["text"],{"role":j["role"],"company":j["company"],"skills":json.dumps(j["skills"]),"salary_india":j["salary_india"],"demand":j["demand"]}) for j in JOB_INTELLIGENCE]),
            ("interviews",[(q["id"],f"{q['question']} {q['hint']}",{"role":q["role"],"question":q["question"],"difficulty":q["difficulty"],"topic":q["topic"],"hint":q["hint"]}) for q in INTERVIEW_INTELLIGENCE]),
            ("learning",  [(r["id"],r["text"],{"skill":r["skill"],"resource":r["resource"],"url":r["url"],"difficulty":r["difficulty"],"time":r["time"]}) for r in LEARNING_INTELLIGENCE]),
            ("career",    [(c["id"],c["text"],{"topic":c["topic"]}) for c in CAREER_INTELLIGENCE]),
        ]

        for name, data in collections_data:
            try:
                col = client.get_collection(name)
            except Exception:
                col = client.create_collection(name, embedding_function=ef)
                ids=[d[0] for d in data]; docs=[d[1] for d in data]; metas=[d[2] for d in data]
                col.add(ids=ids, documents=docs, metadatas=metas)
            self._collections[name] = col

        self._initialized = True

    def retrieve_jobs(self, role: str, user_skills: list, n: int = 5) -> list:
        self.initialize()
        query = f"{role} {' '.join(user_skills[:8])}"
        col = self._collections["jobs"]
        n = min(n, col.count())
        results = col.query(query_texts=[query], n_results=n)
        jobs = []
        for i, meta in enumerate(results["metadatas"][0]):
            dist = results["distances"][0][i]
            jobs.append({
                "company": meta["company"], "role": meta["role"],
                "skills": json.loads(meta.get("skills","[]")),
                "salary_india": meta["salary_india"], "demand": meta["demand"],
                "relevance_score": max(10, round((1 - min(dist, 1.0)) * 100))
            })
        return jobs

    def retrieve_interview_questions(self, role: str, n: int = 5) -> list:
        self.initialize()
        col = self._collections["interviews"]
        n = min(n, col.count())
        results = col.query(query_texts=[f"{role} interview technical questions"], n_results=n)
        return [{"question":m["question"],"difficulty":m["difficulty"],"topic":m["topic"],"hint":m["hint"],"role":m["role"]} for m in results["metadatas"][0]]

    def retrieve_learning_resources(self, skills: list, n: int = 4) -> list:
        self.initialize()
        if not skills: return []
        col = self._collections["learning"]
        n = min(n, col.count())
        results = col.query(query_texts=[" ".join(skills[:5])], n_results=n)
        return [{"skill":m["skill"],"resource":m["resource"],"url":m["url"],"difficulty":m["difficulty"],"time":m["time"]} for m in results["metadatas"][0]]

    def retrieve_career_knowledge(self, query: str, n: int = 3) -> list:
        self.initialize()
        col = self._collections["career"]
        n = min(n, col.count())
        results = col.query(query_texts=[query], n_results=n)
        return [{"topic":m["topic"],"content":doc} for m,doc in zip(results["metadatas"][0],results["documents"][0])]

    def get_stats(self) -> dict:
        self.initialize()
        return {k: v.count() for k,v in self._collections.items()}

# Singleton
rag = DevPathRAG()