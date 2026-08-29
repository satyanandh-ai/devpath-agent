# test_rag1.py — RAG-1 standalone retrieval test
# Run with: python test_rag1.py
# Verifies: real semantic retrieval + persistence, before touching app.py

from rag_engine import rag

def show_results(title, query, results):
    print(f"\n{'='*70}\nQUERY: {query}\n{title}\n{'='*70}")
    if not results:
        print("  (no results)")
        return
    for i, r in enumerate(results, 1):
        print(f"\n  Evidence {i}")
        print(f"  Source: {r['metadata'].get('source')}")
        print(f"  Similarity: {r['similarity']}  (distance: {r['distance']})")
        print(f"  Content: {r['document'][:150]}")

if __name__ == "__main__":
    print("Initializing RAG (first run builds persistent Chroma DB at ./devpath_chroma_db)...")
    rag.initialize()

    print("\nCollection stats:", rag.get_stats())

    show_results("CAREER collection", "What skills are required for an AI Engineer?",
                 rag.retrieve("career", "What skills are required for an AI Engineer?", n=3))

    show_results("JOBS collection", "AI Engineer with LangChain and RAG experience",
                 rag.retrieve("jobs", "AI Engineer with LangChain and RAG experience", n=3))

    show_results("INTERVIEWS collection", "how to evaluate a RAG system",
                 rag.retrieve("interviews", "how to evaluate a RAG system", n=3))

    show_results("LEARNING collection", "learn AWS deployment",
                 rag.retrieve("learning", "learn AWS deployment", n=3))

    print("\n\n--- Run this script again (without deleting ./devpath_chroma_db) ---")
    print("--- to confirm the collections persist across restarts. ---")