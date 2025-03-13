import argparse
import asyncio
import openai
import pandas as pd
import aiofiles
from playwright.async_api import async_playwright

# OpenAI API Key
openai.api_key = "your-api-key"

async def summarize_content(content):
    """Use OpenAI to summarize content asynchronously."""
    try:
        response = await asyncio.to_thread(openai.ChatCompletion.create,
            model="gpt-4",
            messages=[{"role": "user", "content": f"Summarize this: {content}"}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Summary not available"

async def search_google(query, max_results=5):
    """Perform an asynchronous Google search and return top results."""
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com")

        # Input search query
        await page.fill("input[name='q']", query)
        await page.press("input[name='q']", "Enter")
        await page.wait_for_selector("h3", timeout=5000)

        search_results = await page.locator("h3").all()
        links = await page.locator("h3 >> xpath=..").evaluate_all("elements => elements.map(e => e.href)")

        tasks = []
        for i in range(min(max_results, len(search_results))):
            title = await search_results[i].text_content()
            url = links[i] if i < len(links) else "No URL found"
            tasks.append(summarize_content(title))  # Async summarization

        summaries = await asyncio.gather(*tasks)

        for i in range(len(tasks)):
            results.append({"Query": query, "Title": search_results[i].text_content(), "URL": links[i], "Summary": summaries[i]})

        await browser.close()

    return results

async def main():
    # 🎯 CLI Argument Parser
    parser = argparse.ArgumentParser(description="AI-powered Google Search Automation")
    parser.add_argument("--queries", nargs="+", required=True, help="List of search queries (separate with space)")
    parser.add_argument("--output", type=str, default="results.json", help="Output file name (.json or .xlsx)")
    parser.add_argument("--max_results", type=int, default=5, help="Number of search results per query")

    args = parser.parse_args()

    # Run searches in parallel
    all_results = await asyncio.gather(*[search_google(q, args.max_results) for q in args.queries])

    # Flatten list
    flat_results = [item for sublist in all_results for item in sublist]

    # Save to JSON or Excel
    df = pd.DataFrame(flat_results)
    if args.output.endswith(".json"):
        async with aiofiles.open(args.output, "w") as f:
            await f.write(df.to_json(indent=4))
    elif args.output.endswith(".xlsx"):
        df.to_excel(args.output, index=False)
    else:
        print("Invalid output format. Use .json or .xlsx")

    print(f"Search results saved to {args.output}")

# Run script
if __name__ == "__main__":
    asyncio.run(main())