from agents import build_final_report, source_collector, source_researcher


def run_research_pipeline(topic: str) -> dict:
    print("\n" + "=" * 60)
    print(f"Step 1/4 - Collecting research sources for: {topic}")
    print("=" * 60)
    search_results = source_collector(topic)

    print(f"Collected {len(search_results)} unique search results.")

    print("\n" + "=" * 60)
    print("Step 2/4 - Scraping and enriching top sources")
    print("=" * 60)
    scraped_docs = source_researcher(topic, search_results)

    print(f"Scraped {len(scraped_docs)} high-quality documents.")

    print("\n" + "=" * 60)
    print("Step 3/4 - Generating final report")
    print("=" * 60)
    result = build_final_report(topic, scraped_docs)

    print("\nFinal report preview:\n")
    print(result["report"][:4000])

    print("\n" + "=" * 60)
    print("Step 4/4 - Research critique")
    print("=" * 60)
    print(result["critic"])

    return result


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()
    if topic:
        output = run_research_pipeline(topic)
        with open("research_report.md", "w", encoding="utf-8") as f:
            f.write(output["report"])
        print("\nSaved report to research_report.md")
    else:
        print("No topic provided.")