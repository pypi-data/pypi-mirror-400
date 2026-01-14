import json
from typing import Optional

import click
from coze_coding_utils.runtime_ctx.context import new_context
from rich.console import Console
from rich.table import Table

from ..core.config import Config
from ..knowledge import (
    ChunkConfig,
    DataSourceType,
    KnowledgeClient,
    KnowledgeDocument,
)
from .constants import RUN_MODE_HEADER, RUN_MODE_TEST

console = Console()


@click.group()
def knowledge():
    """Knowledge Base tools."""
    pass


@knowledge.command()
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--dataset", "-d", multiple=True, help="Dataset names (tables) to search in")
@click.option("--top-k", "-k", default=5, help="Number of results to return")
@click.option("--min-score", "-m", default=0.0, help="Minimum similarity score")
@click.option("--mock", is_flag=True, help="Use mock mode")
@click.option(
    "--header",
    "-H",
    multiple=True,
    help="Custom HTTP headers (format: 'Key: Value')",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose logs")
def search(
    query: str,
    dataset: tuple,
    top_k: int,
    min_score: float,
    mock: bool,
    header: tuple,
    verbose: bool,
):
    """Search for knowledge chunks."""
    try:
        from .utils import parse_headers

        config = Config()
        ctx = None
        custom_headers = parse_headers(header) or {}

        if mock:
            ctx = new_context(method="knowledge.search", headers=custom_headers)
            custom_headers[RUN_MODE_HEADER] = RUN_MODE_TEST
            console.print("[yellow]🧪 Mock mode enabled[/yellow]")

        client = KnowledgeClient(
            config, ctx=ctx, custom_headers=custom_headers, verbose=verbose
        )

        dataset_list = list(dataset) if dataset else None

        response = client.search(
            query=query,
            table_names=dataset_list,
            top_k=top_k,
            min_score=min_score,
        )

        if response.code != 0:
            console.print(f"[red]Error {response.code}: {response.msg}[/red]")
            return

        table = Table(title="Search Results")
        table.add_column("Score", style="cyan", no_wrap=True)
        table.add_column("Content", style="green")
        table.add_column("Chunk ID", style="dim")
        table.add_column("Doc ID", style="dim")

        for chunk in response.chunks:
            table.add_row(
                f"{chunk.score:.4f}",
                chunk.content,
                chunk.chunk_id or "",
                chunk.doc_id or "",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.Abort()


@knowledge.command()
@click.option("--dataset", "-d", required=True, help="Dataset name (table) to add to")
@click.option("--content", "-c", multiple=True, help="Raw text content to add")
@click.option("--url", "-u", multiple=True, help="Web URL to add")
@click.option("--chunk-separator", default="\n", help="Chunk separator")
@click.option("--max-tokens", default=500, help="Max tokens per chunk")
@click.option("--remove-extra-spaces", is_flag=True, help="Normalize extra spaces")
@click.option("--remove-urls-emails", is_flag=True, help="Strip URLs and emails")
@click.option("--mock", is_flag=True, help="Use mock mode")
@click.option(
    "--header",
    "-H",
    multiple=True,
    help="Custom HTTP headers (format: 'Key: Value')",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose logs")
def add(
    dataset: str,
    content: tuple,
    url: tuple,
    chunk_separator: str,
    max_tokens: int,
    remove_extra_spaces: bool,
    remove_urls_emails: bool,
    mock: bool,
    header: tuple,
    verbose: bool,
):
    """Add documents to knowledge base."""
    try:
        from .utils import parse_headers

        config = Config()
        ctx = None
        custom_headers = parse_headers(header) or {}

        if mock:
            ctx = new_context(method="knowledge.add", headers=custom_headers)
            custom_headers[RUN_MODE_HEADER] = RUN_MODE_TEST
            console.print("[yellow]🧪 Mock mode enabled[/yellow]")

        client = KnowledgeClient(
            config, ctx=ctx, custom_headers=custom_headers, verbose=verbose
        )

        documents = []
        for text in content:
            documents.append(
                KnowledgeDocument(
                    source=DataSourceType.TEXT,
                    raw_data=text,
                )
            )
        for u in url:
            documents.append(
                KnowledgeDocument(
                    source=DataSourceType.URL,
                    url=u,
                )
            )

        if not documents:
            console.print("[red]No content or URL provided to add.[/red]")
            return

        chunk_config = ChunkConfig(
            separator=chunk_separator,
            max_tokens=max_tokens,
            remove_extra_spaces=remove_extra_spaces,
            remove_urls_emails=remove_urls_emails,
        )

        response = client.add_documents(
            documents=documents,
            table_name=dataset,
            chunk_config=chunk_config,
        )

        if response.code != 0:
            console.print(f"[red]Error {response.code}: {response.msg}[/red]")
            return

        table = Table(title="Add Documents Result")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Code", str(response.code))
        table.add_row("Message", response.msg)
        if response.doc_ids:
            table.add_row("Doc IDs", ", ".join(response.doc_ids))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.Abort()
