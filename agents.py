import ast
import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from tools import (
    dedup_tool,
    fact_verification_tool,
    report_generator_tool,
    web_scraper,
    web_search,
)

load_dotenv()

llm = ChatMistralAI(
    model=os.getenv("MISTRAL_MODEL", "mistral-small-2506"),
    temperature=0.1,
)


def _invoke_tool(tool, **kwargs):
    if hasattr(tool, "invoke"):
        return tool.invoke(kwargs)
    return tool(**kwargs)


def _clean_json_like_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return text.strip()


def _parse_list_output(text: str) -> List[str]:
    cleaned = _clean_json_like_text(text)
    for parser in (json.loads, ast.literal_eval):
        try:
            result = parser(cleaned)
            if isinstance(result, list):
                return [str(item).strip() for item in result if str(item).strip()]
        except Exception:
            pass

    lines = []
    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("-", "*")):
            line = line[1:].strip()
        lines.append(line)
    return lines


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a research planner.
Break a topic into 5-8 specific subtopics that cover different angles.
Return ONLY a JSON array of strings.
            """,
        ),
        (
            "human",
            "Topic: {topic}"
        ),
    ]
)

planner_chain = planner_prompt | llm | StrOutputParser()


query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a query generator.
For each subtopic, return ONLY a JSON array of 3-5 high-quality search queries.
            """,
        ),
        (
            "human",
            "Subtopic: {subtopic}"
        ),
    ]
)

query_chain = query_prompt | llm | StrOutputParser()


synth_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a research synthesis assistant.
Summarize the provided documents into key facts, contradictions, and evidence.
Return a JSON object with keys:
- facts: list[string]
- contradictions: list[string]
- evidence_summary: string
            """,
        ),
        (
            "human",
            "Documents:\n{documents}"
        ),
    ]
)

synth_chain = synth_prompt | llm | StrOutputParser()


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a senior research analyst and professional report writer.
Use only the provided research data.
Do NOT invent facts or sources.
If information is missing, say so clearly.
            """,
        ),
        (
            "human",
            """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Data:
{research}

Structure:
1. Introduction
2. Key Findings
3. Contradictions / Conflicting Information
4. Conclusion
5. Sources
            """
        ),
    ]
)

writer_chain = writer_prompt | llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a strict research critic.
Evaluate factual accuracy, completeness, clarity, and missing information.
Return JSON with keys:
- score: number
- strengths: list[string]
- weaknesses: list[string]
- improvements: list[string]
            """,
        ),
        (
            "human",
            "Report:\n{report}"
        ),
    ]
)

critic_chain = critic_prompt | llm | StrOutputParser()


def build_research_plan(topic: str) -> List[str]:
    raw = planner_chain.invoke({"topic": topic})
    return _parse_list_output(raw)


def generate_search_queries(subtopic: str) -> List[str]:
    raw = query_chain.invoke({"subtopic": subtopic})
    return _parse_list_output(raw)


def source_collector(topic: str) -> List[Dict[str, Any]]:
    plan = build_research_plan(topic)
    all_queries = []
    for subtopic in plan:
        all_queries.extend(generate_search_queries(subtopic))

    collected = []
    for query in all_queries:
        search_results = _invoke_tool(web_search, query=query)
        if isinstance(search_results, list):
            collected.extend(search_results)

    return _invoke_tool(dedup_tool, documents=collected)


def source_researcher(topic: str, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scraped = []
    for item in search_results[:8]:
        url = item.get("url")
        if not url:
            continue
        doc = _invoke_tool(web_scraper, url=url)
        if doc.get("content"):
            scraped.append(
                {
                    "title": item.get("title", ""),
                    "url": url,
                    "content": doc.get("content", ""),
                }
            )

    return _invoke_tool(dedup_tool, documents=scraped)


def synthesize_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    payload = json.dumps(documents, ensure_ascii=False, indent=2)
    response = synth_chain.invoke({"documents": payload})
    try:
        return json.loads(_clean_json_like_text(response))
    except Exception:
        return {
            "facts": _parse_list_output(response),
            "contradictions": [],
            "evidence_summary": response,
        }


def build_final_report(topic: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    synthesis = synthesize_documents(documents)
    facts = synthesis.get("facts", [])
    contradictions = synthesis.get("contradictions", [])
    sources = [doc.get("url") for doc in documents if doc.get("url")]

    verification = _invoke_tool(fact_verification_tool, documents=documents)
    confidence = float(verification.get("confidence", 0.0))

    report_meta = _invoke_tool(
        report_generator_tool,
        data={
            "query": topic,
            "facts": facts,
            "sources": sources,
            "confidence": confidence,
            "contradictions": contradictions,
        },
    )

    final_report = writer_chain.invoke(
        {
            "topic": topic,
            "research": (
                "Key facts:\n- "
                + "\n- ".join(facts)
                + "\n\nContradictions:\n- "
                + "\n- ".join(contradictions)
                + "\n\nSources:\n"
                + "\n".join(sources)
            ),
        }
    )

    crit = critic_chain.invoke({"report": final_report})
    try:
        critic_data = json.loads(_clean_json_like_text(crit))
    except Exception:
        critic_data = {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
        }

    return {
        "topic": topic,
        "plan": synthesis.get("evidence_summary", ""),
        "report": final_report,
        "report_meta": report_meta,
        "confidence": confidence,
        "verification": verification,
        "critic": critic_data,
        "documents": documents,
    }
