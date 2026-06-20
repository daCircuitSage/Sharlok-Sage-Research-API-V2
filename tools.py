from langchain.tools import tool

import os
import re
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

from urllib.parse import urlparse
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> list:
    """
    Search the web and return structured results.

    Returns:
        list[dict]: [{title, url, content}]
    """

    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content")
        })

    return results



@tool
def web_scraper(url: str) -> dict:
    """
    Scrape and clean webpage content.
    """

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, timeout=10, headers=headers)

        if resp.status_code != 200:
            return {"url": url, "content": "", "error": f"HTTP {resp.status_code}"}

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        return {
            "url": url,
            "content": text[:4000]
        }

    except Exception as e:
        return {
            "url": url,
            "content": "",
            "error": str(e)
        }


@tool
def dedup_tool(documents: list, threshold: float = 0.9) -> list:
    """
    Remove duplicate and similar documents.
    """

    seen_urls = set()
    filtered = []

    # URL dedup
    for doc in documents:
        url = doc.get("url")

        if url in seen_urls:
            continue

        seen_urls.add(url)
        filtered.append(doc)

    if len(filtered) <= 1:
        return filtered

    texts = [doc.get("content", "") for doc in filtered]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)

    similarity_matrix = cosine_similarity(vectors)

    keep = []
    removed = set()

    for i in range(len(filtered)):
        if i in removed:
            continue

        keep.append(filtered[i])

        for j in range(i + 1, len(filtered)):
            if similarity_matrix[i][j] > threshold:
                removed.add(j)

    return keep


@tool
def credibility_tool(document: dict) -> dict:
    """
    Score source credibility (0-10).
    """

    url = document.get("url", "")
    content = document.get("content", "")

    score = 5.0
    reasons = []

    domain = urlparse(url).netloc.lower()

    if ".gov" in domain:
        score += 3
        reasons.append("Government source (+3)")
    elif ".edu" in domain:
        score += 2.5
        reasons.append("Educational source (+2.5)")
    elif any(x in domain for x in ["reuters", "bbc", "apnews", "cnn", "nytimes"]):
        score += 2
        reasons.append("Reputed news source (+2)")
    elif any(x in domain for x in ["blog", "medium"]):
        score -= 1
        reasons.append("Blog source (-1)")
    else:
        reasons.append("General source (0)")

    word_count = len(content.split())

    if word_count > 1500:
        score += 1.5
        reasons.append("High-quality long content (+1.5)")
    elif word_count < 300:
        score -= 1
        reasons.append("Short content (-1)")

    if "according to" in content.lower():
        score += 0.5
        reasons.append("Cites sources (+0.5)")

    score = max(0, min(10, round(score, 2)))

    return {
        "url": url,
        "score": score,
        "reason": "; ".join(reasons)
    }


@tool
def fact_verification_tool(documents: list) -> dict:
    """
    Verify facts by frequency across sources.
    """

    all_claims = []

    for doc in documents:
        content = doc.get("content", "")

        sentences = re.split(r"[.!?]", content)

        for s in sentences:
            if any(char.isdigit() for char in s):
                s = s.strip().lower()
                if len(s) > 10:
                    all_claims.append(s)

    if not all_claims:
        return {
            "fact": "No clear factual claims found",
            "confidence": 0.0,
            "supporting_sources": 0
        }

    counter = Counter(all_claims)

    best_fact, count = counter.most_common(1)[0]

    confidence = round(min(1.0, count / len(documents)), 2)

    return {
        "fact": best_fact,
        "confidence": confidence,
        "supporting_sources": count
    }



@tool
def report_generator_tool(data: dict) -> dict:
    """
    Generate final markdown research report.
    """

    query = data.get("query", "Research Report")
    facts = data.get("facts", [])
    sources = data.get("sources", [])
    confidence = data.get("confidence", 0)
    contradictions = data.get("contradictions", [])

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"# {query}\n\n"
    md += f"**Generated:** {created_at}\n\n"
    md += f"**Confidence:** {confidence}\n\n"

    md += "## Key Facts\n"
    for i, f in enumerate(facts, 1):
        md += f"{i}. {f}\n"

    md += "\n## Sources\n"
    for i, s in enumerate(sources, 1):
        md += f"{i}. {s}\n"

    md += "\n## Contradictions\n"
    if contradictions:
        for c in contradictions:
            md += f"- {c}\n"
    else:
        md += "None detected.\n"

    md += "\n## Conclusion\n"
    md += "Generated using multi-source verified research pipeline.\n"

    return {
        "title": query,
        "markdown": md,
        "created_at": created_at
    }