#!/usr/bin/env python3
"""Obsidian Pilot - Phase 4: AI Assistant Smart Routing"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

# AI assistant configurations
AI_ASSISTANTS = {
    "hermes": {
        "name": "Hermes Agent",
        "api_type": "hermes",
        "cost_per_token": 0.0000003,
        "strengths": ["coding", "server-ops", "general-assistant"],
        "description": "Best for coding tasks and server management",
    },
    "codex": {
        "name": "Codex CLI",
        "api_type": "openai",
        "cost_per_token": 0.0000002,
        "strengths": ["coding", "batch-processing", "automation"],
        "description": "Best for fast batch processing and automation",
    },
    "openclaw": {
        "name": "OpenClaw",
        "api_type": "openclaw",
        "cost_per_token": 0.0000004,
        "strengths": ["general", "research", "writing"],
        "description": "Best for research and writing tasks",
    },
}


def build_knowledge_graph(vault_path):
    """Build a knowledge graph from notes using TF-IDF similarity."""
    if not HAS_NETWORKX or not HAS_SKLEARN:
        print("Warning: networkx or sklearn not installed. Using basic linking.")
        return None
    
    vault = Path(vault_path).resolve()
    md_files = list(vault.rglob('*.md'))
    
    # Collect all note texts
    notes = []
    for md_file in md_files:
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        try:
            content = md_file.read_text(encoding='utf-8')
            if len(content.strip()) > 100:  # Skip very short notes
                notes.append({
                    'file': md_file,
                    'title': md_file.stem,
                    'content': content,
                })
        except:
            pass
    
    if not notes:
        return None
    
    # Build TF-IDF matrix
    texts = [n['content'] for n in notes]
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Compute similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Build graph
    G = nx.DiGraph()
    for i, note in enumerate(notes):
        G.add_node(note['title'], file=str(note['file']), content=note['content'])
        
        # Find top 3 similar notes
        similarities = similarity_matrix[i]
        top_indices = similarities.argsort()[::-1][1:4]  # Skip self
        
        for j in top_indices:
            if similarities[j] > 0.3:  # Threshold for linking
                G.add_edge(note['title'], notes[j]['title'], weight=similarities[j])
    
    return G


def compress_context(vault_path, query, max_tokens=500):
    """Compress relevant notes into a concise context for AI assistants."""
    vault = Path(vault_path).resolve()
    md_files = list(vault.rglob('*.md'))
    
    relevant_notes = []
    query_lower = query.lower()
    
    for md_file in md_files:
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        try:
            content = md_file.read_text(encoding='utf-8')
            # Simple keyword matching (could be improved with embeddings)
            score = 0
            for word in query_lower.split():
                if len(word) > 3 and word in content.lower():
                    score += 1
            
            if score > 0:
                relevant_notes.append({
                    'file': md_file,
                    'score': score,
                    'content': content[:1000],  # First 1000 chars
                })
        except:
            pass
    
    # Sort by relevance and compress
    relevant_notes.sort(key=lambda x: x['score'], reverse=True)
    compressed_parts = []
    total_chars = 0
    
    for note in relevant_notes[:5]:  # Top 5 notes
        title = note['file'].stem
        content_preview = note['content'][:300]
        part = f"[{title}] {content_preview}\n\n"
        
        if total_chars + len(part) <= max_tokens * 4:  # Rough token estimate
            compressed_parts.append(part)
            total_chars += len(part)
        else:
            break
    
    compressed_context = "\n".join(compressed_parts)
    return compressed_context


def recommend_assistant(task_type):
    """Recommend the best AI assistant for a given task type."""
    task_lower = task_type.lower()
    
    scores = {}
    for key, assistant in AI_ASSISTANTS.items():
        score = 0
        for strength in assistant['strengths']:
            if strength in task_lower:
                score += 1
        scores[key] = score
    
    if not scores or max(scores.values()) == 0:
        # Default recommendation
        return "hermes", "General purpose assistant"
    
    best = max(scores, key=scores.get)
    return best, AI_ASSISTANTS[best]['description']


def check_local_knowledge(vault_path, query):
    """Check if the answer exists in local knowledge base."""
    vault = Path(vault_path).resolve()
    md_files = list(vault.rglob('*.md'))
    
    query_lower = query.lower()
    best_match = None
    best_score = 0
    
    for md_file in md_files:
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        try:
            content = md_file.read_text(encoding='utf-8')
            score = 0
            for word in query_lower.split():
                if len(word) > 3 and word in content.lower():
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    'file': md_file,
                    'title': md_file.stem,
                    'score': score,
                    'content': content,
                }
        except:
            pass
    
    if best_match and best_score > 0:
        # Extract relevant section
        content = best_match['content']
        lines = content.split('\n')
        
        # Find the most relevant paragraph
        best_para = ""
        current_para = ""
        para_score = 0
        
        for line in lines:
            if line.strip() == "":
                if current_para and para_score > 0:
                    if len(current_para) > len(best_para):
                        best_para = current_para
                current_para = ""
                para_score = 0
            else:
                current_para += line + "\n"
                for word in query_lower.split():
                    if len(word) > 3 and word in current_para.lower():
                        para_score += 1
        
        if current_para and para_score > 0 and len(current_para) > len(best_para):
            best_para = current_para
        
        if best_para:
            return {
                'found': True,
                'source': best_match['title'],
                'answer': best_para[:500],  # Limit length
                'score': best_score,
            }
    
    return {'found': False}


def show_routing_report(results, graph_stats, dry_run=True):
    """Display smart routing report."""
    print("\n" + "=" * 60)
    print("AI Assistant Smart Routing Report")
    print("=" * 60)
    
    print(f"\nKnowledge Graph Nodes: {graph_stats.get('nodes', 0)}")
    print(f"Knowledge Graph Edges: {graph_stats.get('edges', 0)}")
    
    if results:
        print(f"\nLocal Knowledge Matches: {len(results)}")
        for r in results:
            if r['found']:
                print(f"  ✓ {r['source']} (score: {r['score']})")
            else:
                print(f"  ✗ No local match")
    
    print("\n" + "-" * 60)
    if dry_run:
        print("DRY RUN: No API calls made.")
        print("Run with --apply to test routing.")
    else:
        print("Routing would be tested:")
        for r in results:
            if not r['found']:
                assistant, desc = recommend_assistant(r.get('task', ''))
                print(f"  Task -> {AI_ASSISTANTS[assistant]['name']} ({desc})")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot - AI Assistant Smart Routing")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--query", "-q", help="Test query to route")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show report without making API calls")
    parser.add_argument("--build-graph", action="store_true", help="Build knowledge graph")
    parser.add_argument("--compress", action="store_true", help="Compress context for AI assistants")
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"Smart routing analysis for: {vault_path}")
    
    # Build knowledge graph if requested
    graph = None
    if args.build_graph:
        print("\nBuilding knowledge graph...")
        graph = build_knowledge_graph(str(vault_path))
        if graph:
            print(f"  Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        else:
            print("  Graph building skipped (missing dependencies)")
    
    # Check local knowledge for query
    if args.query:
        print(f"\nTesting query: '{args.query}'")
        result = check_local_knowledge(str(vault_path), args.query)
        
        if result['found']:
            print(f"\n✓ Found in local knowledge!")
            print(f"  Source: {result['source']}")
            print(f"  Answer preview: {result['answer'][:200]}...")
        else:
            print(f"\n✗ No local match found")
            assistant, desc = recommend_assistant(args.query)
            print(f"  Recommended: {AI_ASSISTANTS[assistant]['name']} ({desc})")
            
            # Compress context
            if args.compress:
                compressed = compress_context(str(vault_path), args.query)
                print(f"\n  Compressed context ({len(compressed)} chars):")
                print(f"  {compressed[:300]}...")
    
    # Show routing report
    results = []
    if args.query:
        results.append(check_local_knowledge(str(vault_path), args.query))
    
    graph_stats = {}
    if graph:
        graph_stats = {'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges()}
    
    show_routing_report(results, graph_stats, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
