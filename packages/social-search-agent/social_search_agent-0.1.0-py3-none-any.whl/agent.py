"""
Research agent using GPT-5.2 with Reddit/Bluesky search.

Usage:
    python agent.py "Your research question"
    python agent.py "Question" --sources reddit bluesky
    python agent.py  # Interactive mode
"""

import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

import reddit_client
import bluesky_client

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv(override=True)

client = OpenAI()
console = Console()

MODEL = "gpt-5.2-2025-12-11"
REASONING_EFFORT = "high"
MAX_WORDS = 2000

# =============================================================================
# TOOLS
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "name": "search_reddit",
        "description": "Search Reddit posts in a subreddit.",
        "parameters": {
            "type": "object",
            "properties": {
                "subreddit": {"type": "string", "description": "Subreddit name"},
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Results (1-25)"}
            },
            "required": ["subreddit", "query", "limit"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_reddit_post_with_comments",
        "description": "Get Reddit post with comments (truncated to 2k words).",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id": {"type": "string", "description": "Post ID"}
            },
            "required": ["post_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "search_bluesky",
        "description": "Search Bluesky posts (requires auth).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Results (1-25)"}
            },
            "required": ["query", "limit"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_bluesky_thread",
        "description": "Get Bluesky thread with replies (truncated to 2k words).",
        "parameters": {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "AT Protocol URI"}
            },
            "required": ["uri"],
            "additionalProperties": False
        },
        "strict": True
    },
]


def get_tools_for_sources(sources):
    reddit = ["search_reddit", "get_reddit_post_with_comments"]
    bluesky = ["search_bluesky", "get_bluesky_thread"]
    allowed = set()
    if "reddit" in sources:
        allowed.update(reddit)
    if "bluesky" in sources:
        allowed.update(bluesky)
    return [t for t in TOOLS if t["name"] in allowed]


def truncate_words(text, max_words):
    words = text.split()
    return " ".join(words[:max_words]) + ("... [truncated]" if len(words) > max_words else "")


def execute_tool(name, args):
    try:
        if name == "search_reddit":
            results = reddit_client.search_subreddit(args["subreddit"], args["query"], args["limit"])
            return json.dumps([{
                "id": r["id"], "title": r["title"], "score": r["score"],
                "preview": (r["selftext"][:300] + "...") if len(r["selftext"]) > 300 else r["selftext"],
                "comments": r["num_comments"]
            } for r in results])

        elif name == "get_reddit_post_with_comments":
            post = reddit_client.get_post(args["post_id"])
            comments = reddit_client.get_comments(args["post_id"], 0)
            
            lines, words = [], 0
            for c in comments:
                line = f"[{c['score']}] u/{c['author']}: {c['body']}"
                w = len(line.split())
                if words + w > MAX_WORDS:
                    lines.append(f"... [{len(comments) - len(lines)} more]")
                    break
                lines.append(line)
                words += w
            
            return json.dumps({"post": post, "comments": lines, "total": len(comments)})

        elif name == "search_bluesky":
            results = bluesky_client.search_posts(args["query"], args["limit"])
            return json.dumps([{"uri": r["uri"], "author": r["author"], 
                               "text": r["text"][:300], "likes": r["like_count"]} for r in results])

        elif name == "get_bluesky_thread":
            thread = bluesky_client.get_thread(args["uri"])
            
            def flatten(t, d=0):
                lines = [f"{'  '*d}[@{t.get('author')}] {t.get('text', '')}"]
                for r in t.get("replies", []):
                    lines.extend(flatten(r, d+1))
                return lines
            
            text = truncate_words("\n".join(flatten(thread)), MAX_WORDS)
            return json.dumps({"post": thread, "thread_text": text})

        return json.dumps({"error": f"Unknown: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# LLM
# =============================================================================

def call_with_tools(messages, tools, max_iter=10):
    log = []
    msgs = messages.copy()
    
    for _ in range(max_iter):
        resp = client.responses.create(
            model=MODEL, reasoning={"effort": REASONING_EFFORT}, input=msgs, tools=tools or None
        )
        
        has_calls = False
        for item in resp.output:
            if item.type == "function_call":
                has_calls = True
                call = {"name": item.name, "arguments": json.loads(item.arguments), "call_id": item.call_id}
                log.append(call)
                result = execute_tool(item.name, call["arguments"])
                msgs.append({"type": "function_call", "call_id": item.call_id, "name": item.name, "arguments": item.arguments})
                msgs.append({"type": "function_call_output", "call_id": item.call_id, "output": result})
        
        if not has_calls:
            return resp.output_text, log
    
    return resp.output_text, log


def stage1_queries(task, sources):
    resp = client.responses.create(
        model=MODEL, reasoning={"effort": "medium"},
        input=[{"role": "user", "content": f"Generate 3 search queries for: {task}\nUsing: {sources}\nOutput JSON array only: [\"q1\", \"q2\", \"q3\"]"}]
    )
    text = resp.output_text.strip()
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()
    return json.loads(text)[:3]


def stage2_research(query, sources):
    tools = get_tools_for_sources(sources)
    return call_with_tools([{"role": "user", "content": f"""Research: {query}
Use tools to search and get posts. Make multiple calls. Write a detailed report with findings, quotes, sources."""}], tools)


def stage3_compile(task, reports):
    combined = "\n---\n".join([f"## Report {i+1}\n{r}" for i, r in enumerate(reports)])
    resp = client.responses.create(
        model=MODEL, reasoning={"effort": REASONING_EFFORT},
        input=[{"role": "user", "content": f"Compile into final report.\nTask: {task}\n\n{combined}"}]
    )
    return resp.output_text


# =============================================================================
# MAIN
# =============================================================================

def run_agent(task, sources=None, show_tui=True):
    sources = sources or ["reddit"]
    
    if show_tui:
        console.print(Panel(f"[bold blue]Research Agent[/bold blue]\n{task}", title="Task"))
    
    # Stage 1
    if show_tui:
        console.print("[yellow]Stage 1:[/yellow] Generating queries...")
    queries = stage1_queries(task, sources)
    if show_tui:
        for i, q in enumerate(queries, 1):
            console.print(f"  {i}. {q}")
    
    # Stage 2
    if show_tui:
        console.print("\n[yellow]Stage 2:[/yellow] Researching...")
    
    results = []
    with ThreadPoolExecutor(3) as ex:
        futures = {ex.submit(stage2_research, q, sources): (i, q) for i, q in enumerate(queries, 1)}
        for f in as_completed(futures):
            num, query = futures[f]
            report, calls = f.result()
            results.append((num, report))
            if show_tui:
                console.print(f"[cyan]Q{num}:[/cyan] {query[:40]}... ({len(calls)} calls)")
    
    results.sort()
    reports = [r[1] for r in results]
    
    # Stage 3
    if show_tui:
        console.print("\n[yellow]Stage 3:[/yellow] Compiling...")
    final = stage3_compile(task, reports)
    
    if show_tui:
        console.print(Panel(final, title="[green]Report[/green]"))
    
    return final


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("task", nargs="?")
    parser.add_argument("-s", "--sources", nargs="+", choices=["reddit", "bluesky"], default=["reddit"])
    parser.add_argument("--no-tui", action="store_true")
    args = parser.parse_args()
    
    if args.task:
        run_agent(args.task, args.sources, not args.no_tui)
    else:
        task = console.input("[bold]Task:[/bold] ")
        src = console.input("[bold]Sources (reddit/bluesky/both):[/bold] ").strip()
        sources = ["reddit", "bluesky"] if src == "both" else [src] if src in ["reddit", "bluesky"] else ["reddit"]
        run_agent(task, sources)


if __name__ == "__main__":
    main()

