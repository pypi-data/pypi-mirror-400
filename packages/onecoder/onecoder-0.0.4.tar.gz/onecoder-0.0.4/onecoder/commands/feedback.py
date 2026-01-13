import click
import asyncio
from typing import Optional
from pathlib import Path
from ..api_client import get_api_client
from ..config_manager import config_manager
from ..usage_logger import usage_logger

@click.command()
@click.option("--sentiment", type=click.Choice(["positive", "neutral", "negative"]), default="neutral", help="Sentiment of the feedback.")
@click.option("--category", type=click.Choice(["tooling", "process", "task", "other"]), default="other", help="Category of the feedback.")
@click.option("--issue-id", help="Associated Issue ID (e.g., 041).")
@click.option("--task-id", help="Associated Task ID.")
@click.option("--feature-request", is_flag=True, help="Submit as a feature request.")
@click.option("--include-usage", is_flag=True, help="Include recent CLI usage context.")
@click.argument("message")
def feedback(sentiment, category, issue_id, task_id, feature_request, include_usage, message):
    """Provide feedback on tools, sprints, or tasks."""
    asyncio.run(_submit_feedback(sentiment, category, issue_id, task_id, feature_request, include_usage, message))

async def _submit_feedback(sentiment, category, issue_id, task_id, feature_request, include_usage, message):
    token = config_manager.get_token()
    if not token:
        click.secho("Warning: Submitting as guest (not logged in).", fg="yellow")
    
    client = get_api_client(token)
    
    if feature_request:
        category = "tooling"
        message = f"[FEATURE REQUEST] {message}"
        
    context = {
        "issue_id": issue_id,
        "task_id": task_id
    }
    
    if include_usage:
        context["usage_history"] = usage_logger.get_recent_usage()
    
    payload = {
        "sentiment": sentiment,
        "category": category,
        "message": message,
        "context": context
    }
    
    try:
        # Submit to API
        await client.submit_feedback(payload)
        click.secho("✓ Feedback submitted successfully.", fg="green")
        
        # Knowledge Base lookup
        query = issue_id or message
        if query:
            await _suggest_knowledge(client, query)
            
    except Exception as e:
        click.secho(f"Error submitting feedback: {e}", fg="red")

async def _suggest_knowledge(client, query: str):
    """Suggest Time Travel logs from API Knowledge Base."""
    try:
        entries = await client.search_knowledge(query)
        if entries:
            click.secho("\n[Knowledge Base Suggestions]", fg="cyan", bold=True)
            for entry in entries:
                click.echo(f"  • {entry['title']}")
                # If it's a resolution category, highlight it
                if entry.get("category") == "resolution":
                    click.secho(f"    Resolution available: {entry.get('metadata', {}).get('tt_log', 'See log')}", fg="yellow")
    except Exception:
        # Silent fallback
        pass
