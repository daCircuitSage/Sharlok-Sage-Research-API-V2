from pipleline import run_research_pipeline


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()
    if topic:
        result = run_research_pipeline(topic)
        print("\nResearch pipeline completed.")
        print(result["report"][:3000])
    else:
        print("No topic provided.")
