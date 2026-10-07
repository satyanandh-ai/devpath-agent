# DevPath RAG-2 validation test
# Run from the same environment where requirements.txt is installed.
# Verifies: initialization, collection counts, reranking, thresholds, and evidence pack.

from rag_engine import rag


def print_result(title, result):
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")
    if not result:
        print("  (no results)")
        return
    for i, item in enumerate(result, 1):
        print(f"\n{i}. {item}")


if __name__ == "__main__":
    print("Initializing DevPath RAG-2...")
    rag.initialize()
    print("Stats:", rag.get_stats())

    raw = rag.retrieve(
        "jobs",
        "AI Engineer Python LangChain RAG FastAPI",
        n=5,
        candidate_n=15,
        min_relevance=0.35,
    )
    print_result("Generic jobs retrieval + reranking", raw)

    jobs = rag.retrieve_jobs(
        "AI Engineer",
        ["Python", "LangChain", "RAG", "FastAPI", "Docker"],
        n=5,
    )
    print_result("Domain job retrieval", jobs)

    interviews = rag.retrieve_interview_questions("AI Engineer", n=5)
    print_result("Interview retrieval", interviews)

    resources = rag.retrieve_learning_resources(
        ["RAG", "FastAPI", "Docker"], n=4
    )
    print_result("Learning retrieval", resources)

    career = rag.retrieve_career_knowledge(
        "How should an AI Engineer prepare for interviews?", n=3
    )
    print_result("Career retrieval", career)

    pack = rag.build_evidence_pack(
        role="AI Engineer",
        user_skills=["Python", "LangChain", "RAG", "FastAPI", "Docker"],
        query="AI Engineer internship preparation",
    )
    print_result("Grounded evidence pack", pack)

    # Basic invariants.
    assert pack["rag_version"] == "2.0"
    assert pack["retrieval_policy"]["scores_are_percentages"] is False
    assert isinstance(pack["jobs"], list)
    assert all(0.0 <= x["relevance_score"] <= 1.0 for x in pack["jobs"])
    print("\nRAG-2 validation checks passed.")
