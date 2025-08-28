# digital_skeptic/main.py
import argparse
import sys
from .fetch import fetch_article
from .analyze import analyze_article
from .report import to_markdown
from .llm import LLMClient
import os


def parse_args():
    p = argparse.ArgumentParser(description="Digital Skeptic – Critical Article Analyzer")
    p.add_argument("url", help="URL of the news article to analyze")
    p.add_argument("--out", "-o", help="Output file (Markdown). If omitted, prints to stdout")
    p.add_argument("--enable-llm", action="store_true", help="Enable LLM-enhanced analysis")
    p.add_argument(
        "--llm-provider",
        default="openai",
        choices=["openai", "perplexity"],
        help="LLM provider to use (openai or perplexity)",
    )
    p.add_argument("--llm-model", default="openai", choices=["openai", "perplexity", "groq"],
        help="LLM provider to use (openai / perplexity / groq)")
    p.add_argument("--openai-base-url", default=None, help="Override base URL for OpenAI-compatible API")
    return p.parse_args()


def main():
    args = parse_args()

    # Step 1: Fetch article text
    fetched = fetch_article(args.url)
    if not fetched.text:
        print("[warn] Unable to extract article text; analysis may be limited.", file=sys.stderr)

    # Step 2: Initialize LLM if enabled
    llm = None
    if args.enable_llm:
        # Pass provider to LLMClient so it knows whether to call OpenAI or Perplexity
        llm = LLMClient(
            model=args.llm_model,
            provider=args.llm_provider,
            base_url=args.openai_base_url,
        )

    # Step 3: Analyze article
    result = analyze_article(
        title=fetched.title or "Untitled",
        url=fetched.url,
        text=fetched.text,
        enable_llm=bool(llm),
        llm=llm,
    )

    # Step 4: Generate Markdown report
    md = to_markdown(result)

    # Step 5: Write or print
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✓ Report written to {args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()