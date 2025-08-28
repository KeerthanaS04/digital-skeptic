# Digital Skeptic AI
**Digital Skeptic AI** is a tool to critically analyze online news articles.
It extracts article text, identifies claims, tone, red flags, entities, and can simulate opposing viewpoints using LLMs (OpenAI / Groq / Perplexity).

## Features
- Extracts full article text from a given URL
- Identifies core claims & potential red flags
- Detects tone & sentiment (neutral / sensational / partisan)
- Generates verification questions
- Highlights entities (people, orgs, locations)
- Can use LLM providers (OpenAI, Groq, Perplexity) for deeper analysis

## Installation
**1. Clone this repository**
```
git clone https://github.com/<your-username>/digital-skeptic.git
cd digital-skeptic
```

**2. Create a virtual environment (recommended)**
```
# PowerShell
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

## API Keys Setup
Create a `.env` file in the project root (same folder as `main.py`) with your API keys:
```
OPENAI_API_KEY=your_openai_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
GROQ_API_KEY=your_groq_key_here
```

## Basic run (heuristic-only, no LLM)
```
python -m digital_skeptic.main "https://www.reuters.com/world/china-economy-recovery-2025-08-01/"
```

## With LLM (Groq Example)
```
python -m digital_skeptic.main "https://www.reuters.com/world/china-economy-recovery-2025-08-01/" `
  --enable-llm --llm-provider groq --llm-model llama-3.1-70b-versatile
```

## Save report to file
```
python -m digital_skeptic.main "https://indianexpress.com/article/business/budget-five-major-takeaways-9811938/" `
  --out budget_report.md
```

## Example: Batch Analysis
Put your article URLs in examples/articles.txt, one per line.
Then run in PowerShell:
```
Get-Content .\examples\articles.txt | ForEach-Object {
    if ($_ -notmatch "^#") {
        Write-Host "Analyzing: $_"
        python -m digital_skeptic.main $_ --out ".\examples\report_$((Get-Random)).md"
    }
}
```

## Examples I have used
- 5 Working websites and 3 non-working websites are included
- Used working and non-working to get to analyze what type of results are showing.
