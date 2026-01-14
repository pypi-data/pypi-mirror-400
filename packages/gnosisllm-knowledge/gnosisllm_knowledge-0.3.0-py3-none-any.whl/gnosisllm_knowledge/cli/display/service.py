"""Rich-based display service for enterprise-grade CLI output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text


@dataclass
class StepProgress:
    """Represents a setup step with status tracking."""

    name: str
    description: str
    status: str = "pending"  # pending, running, success, failed, skipped


class ProgressContext(Protocol):
    """Protocol for multi-step progress tracking."""

    def update(self, step: int, status: str) -> None:
        """Update step status."""
        ...

    def complete(self, step: int) -> None:
        """Mark step as completed."""
        ...

    def fail(self, step: int, error: str) -> None:
        """Mark step as failed with error message."""
        ...

    def skip(self, step: int, reason: str) -> None:
        """Mark step as skipped with reason."""
        ...

    def stop(self) -> None:
        """Stop the progress display."""
        ...


class RichStepProgress:
    """Rich-based multi-step progress display using Live updates."""

    STATUS_ICONS = {
        "pending": "[dim]○[/dim]",
        "running": "[yellow]◐[/yellow]",
        "success": "[green]✓[/green]",
        "failed": "[red]✗[/red]",
        "skipped": "[dim]⊘[/dim]",
    }

    def __init__(self, console: Console, steps: list[StepProgress]) -> None:
        """Initialize progress display.

        Args:
            console: Rich console instance.
            steps: List of steps to track.
        """
        self._console = console
        self._steps = steps
        self._live = Live(self._build_table(), console=console, refresh_per_second=4)
        self._live.start()

    def _build_table(self) -> Table:
        """Build the progress table."""
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("Status", width=3)
        table.add_column("Step", style="cyan", width=20)
        table.add_column("Description")

        for step in self._steps:
            icon = self.STATUS_ICONS.get(step.status, "○")
            style = "dim" if step.status in ("pending", "skipped") else ""
            table.add_row(icon, step.name, step.description, style=style)

        return table

    def _refresh(self) -> None:
        """Refresh the live display."""
        self._live.update(self._build_table())

    def update(self, step: int, status: str) -> None:
        """Update step status."""
        if 0 <= step < len(self._steps):
            self._steps[step].status = status
            self._refresh()

    def complete(self, step: int) -> None:
        """Mark step as completed."""
        self.update(step, "success")

    def fail(self, step: int, error: str) -> None:
        """Mark step as failed."""
        if 0 <= step < len(self._steps):
            self._steps[step].status = "failed"
            original_desc = self._steps[step].description.split(" - ")[0]
            self._steps[step].description = f"{original_desc} - {error}"
            self._refresh()

    def skip(self, step: int, reason: str) -> None:
        """Mark step as skipped."""
        if 0 <= step < len(self._steps):
            self._steps[step].status = "skipped"
            original_desc = self._steps[step].description.split(" (")[0]
            self._steps[step].description = f"{original_desc} ({reason})"
            self._refresh()

    def stop(self) -> None:
        """Stop the live display."""
        self._live.stop()


@dataclass
class SearchResultDisplay:
    """Data for displaying a search result."""

    rank: int
    title: str
    content_preview: str
    score: float
    url: str | None = None
    collection_id: str | None = None
    highlights: list[str] = field(default_factory=list)


class RichDisplayService:
    """Rich-based terminal display service for enterprise-grade CLI UX."""

    BORDER_STYLES = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red",
    }

    def __init__(self, console: Console | None = None) -> None:
        """Initialize display service.

        Args:
            console: Optional Rich console. Creates new if not provided.
        """
        self._console = console or Console()

    @property
    def console(self) -> Console:
        """Get the underlying console."""
        return self._console

    def header(self, title: str, subtitle: str | None = None) -> None:
        """Display a styled header.

        Args:
            title: Main title text.
            subtitle: Optional subtitle.
        """
        self._console.print()
        panel_content = f"[bold]{title}[/bold]"
        if subtitle:
            panel_content += f"\n[dim]{subtitle}[/dim]"

        self._console.print(
            Panel(
                panel_content,
                box=box.ROUNDED,
                border_style="blue",
                padding=(0, 2),
            )
        )
        self._console.print()

    def info(self, message: str) -> None:
        """Display informational message."""
        self._console.print(f"[blue]ℹ[/blue] {message}")

    def success(self, message: str) -> None:
        """Display success message."""
        self._console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        """Display error message."""
        self._console.print(f"[red]✗[/red] {message}")

    def warning(self, message: str) -> None:
        """Display warning message."""
        self._console.print(f"[yellow]⚠[/yellow] {message}")

    def table(
        self,
        title: str,
        rows: list[tuple[str, ...]],
        headers: list[str] | None = None,
    ) -> None:
        """Display a formatted table.

        Args:
            title: Table title.
            rows: List of row tuples.
            headers: Optional column headers. Defaults to ["Setting", "Value"].
        """
        table = Table(title=title, box=box.ROUNDED)

        if headers:
            for i, header in enumerate(headers):
                style = "cyan" if i == 0 else "green" if i == 1 else ""
                table.add_column(header, style=style)
        else:
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

        for row in rows:
            table.add_row(*row)

        self._console.print(table)

    def progress(self, steps: list[StepProgress]) -> RichStepProgress:
        """Create multi-step progress display.

        Args:
            steps: List of steps to track.

        Returns:
            Progress context for updating step status.
        """
        return RichStepProgress(self._console, steps)

    def progress_bar(
        self,
        description: str = "Processing",
        total: int | None = None,
    ) -> Progress:
        """Create a progress bar for batch operations.

        Args:
            description: Description text.
            total: Total items (None for indeterminate).

        Returns:
            Rich Progress instance.
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self._console,
        )

    def confirm(self, message: str, default: bool = False) -> bool:
        """Prompt for yes/no confirmation.

        Args:
            message: Confirmation message.
            default: Default value if Enter is pressed.

        Returns:
            True if confirmed, False otherwise.
        """
        return Confirm.ask(message, default=default)

    def prompt(self, message: str, default: str | None = None) -> str:
        """Prompt for text input.

        Args:
            message: Prompt message.
            default: Optional default value.

        Returns:
            User input string.
        """
        return Prompt.ask(message, default=default or "")

    def panel(self, content: str, title: str, style: str = "info") -> None:
        """Display a styled panel/box.

        Args:
            content: Panel content.
            title: Panel title.
            style: Style name (info, success, warning, error).
        """
        border_style = self.BORDER_STYLES.get(style, "blue")
        self._console.print(Panel(content, title=title, border_style=border_style))

    def newline(self) -> None:
        """Print an empty line."""
        self._console.print()

    def rule(self, title: str = "") -> None:
        """Print a horizontal rule.

        Args:
            title: Optional title in the rule.
        """
        self._console.rule(title)

    def search_results(
        self,
        results: list[SearchResultDisplay],
        query: str,
        total_hits: int,
        duration_ms: float,
        mode: str,
    ) -> None:
        """Display search results in a beautiful format.

        Args:
            results: List of search results to display.
            query: Original search query.
            total_hits: Total number of hits.
            duration_ms: Search duration in milliseconds.
            mode: Search mode used.
        """
        # Analytics table
        self.table(
            "Search Analytics",
            [
                ("Query", query[:60] + "..." if len(query) > 60 else query),
                ("Mode", mode),
                ("Total Hits", str(total_hits)),
                ("Duration", f"{duration_ms:.1f}ms"),
            ],
        )

        self.newline()

        if not results:
            self.warning("No results found.")
            return

        # Results panel
        result_text = Text()
        for i, result in enumerate(results):
            if i > 0:
                result_text.append("\n\n")

            # Title line with score
            score_pct = result.score * 100 if result.score <= 1 else result.score
            result_text.append(f"{result.rank}. ", style="bold cyan")
            result_text.append(result.title or "Untitled", style="bold")
            result_text.append(f"  Score: {score_pct:.1f}%", style="dim green")
            result_text.append("\n")

            # Separator
            result_text.append("─" * 60, style="dim")
            result_text.append("\n")

            # Content preview
            result_text.append(result.content_preview)

            # URL if available
            if result.url:
                result_text.append(f"\nURL: ", style="dim")
                result_text.append(result.url, style="blue underline")

            # Collection if available
            if result.collection_id:
                result_text.append(f"\nCollection: ", style="dim")
                result_text.append(result.collection_id, style="magenta")

        self._console.print(
            Panel(
                result_text,
                title=f"Results (Top {len(results)})",
                border_style="green",
                padding=(1, 2),
            )
        )

    def format_error_with_suggestion(
        self,
        error: str,
        suggestion: str | None = None,
        command: str | None = None,
    ) -> None:
        """Display an error with a helpful suggestion.

        Args:
            error: Error message.
            suggestion: Optional suggestion text.
            command: Optional command to run.
        """
        content = f"[red]{error}[/red]"
        if suggestion:
            content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
        if command:
            content += f"\n\n[dim]Run:[/dim] [cyan]{command}[/cyan]"

        self._console.print(
            Panel(content, title="Error", border_style="red", padding=(1, 2))
        )

    def loading_spinner(self, message: str) -> Any:
        """Create a loading spinner context.

        Args:
            message: Loading message.

        Returns:
            Context manager for spinner.
        """
        return self._console.status(message, spinner="dots")

    def json_output(self, data: dict[str, Any]) -> None:
        """Output data as formatted JSON.

        Args:
            data: Dictionary to output as JSON.
        """
        import json

        self._console.print(json.dumps(data, indent=2, default=str))

    def agentic_result(
        self,
        answer: str | None,
        sources: list[Any],
        reasoning_steps: list[Any] | None = None,
        duration_ms: float = 0.0,
        query: str | None = None,
        conversation_id: str | None = None,
        verbose: bool = False,
    ) -> None:
        """Display agentic search result with answer and sources.

        Args:
            answer: AI-generated answer text.
            sources: List of source documents (SearchResultItem).
            reasoning_steps: Optional reasoning steps for verbose mode.
            duration_ms: Search duration in milliseconds.
            query: Original query for reference.
            conversation_id: Conversation ID for multi-turn.
            verbose: Show detailed reasoning steps.
        """
        # Answer panel
        if answer:
            answer_content = answer
            if query:
                answer_content = f"[dim]Query: {query[:60]}{'...' if len(query) > 60 else ''}[/dim]\n\n{answer}"

            self._console.print(
                Panel(
                    answer_content,
                    title=f"Answer ({duration_ms:.0f}ms)",
                    border_style="green",
                    padding=(1, 2),
                )
            )
        else:
            self.warning("No answer generated by the agent.")

        self.newline()

        # Reasoning steps (if verbose)
        if verbose and reasoning_steps:
            self._console.print("[bold]Reasoning Steps:[/bold]")
            for i, step in enumerate(reasoning_steps, 1):
                tool = getattr(step, "tool", "unknown")
                action = getattr(step, "action", "")
                output = getattr(step, "output", "")
                self._console.print(f"  {i}. [cyan]{tool}[/cyan] → {action}")
                if output:
                    output_preview = output[:100] + "..." if len(output) > 100 else output
                    self._console.print(f"     [dim]{output_preview}[/dim]")
            self.newline()

        # Sources
        if sources:
            self._console.print(f"[bold]Sources ({len(sources)}):[/bold]")
            for i, item in enumerate(sources[:5], 1):
                score = getattr(item, "score", 0.0)
                score_pct = score * 100 if score <= 1 else score
                title = getattr(item, "title", "Untitled") or "Untitled"
                url = getattr(item, "url", None)

                self._console.print(
                    f"  {i}. [bold]{title}[/bold] "
                    f"[dim]({score_pct:.1f}%)[/dim]"
                )
                if url:
                    self._console.print(f"     [blue]{url}[/blue]")

        # Conversation info
        if conversation_id:
            self.newline()
            self.info(f"[dim]Conversation ID: {conversation_id}[/dim]")

    def agentic_status(
        self,
        flow_agent_id: str | None,
        conversational_agent_id: str | None,
        embedding_model_id: str | None,
        llm_model: str = "gpt-4o",
    ) -> None:
        """Display agentic search configuration status.

        Args:
            flow_agent_id: Flow agent ID if configured.
            conversational_agent_id: Conversational agent ID if configured.
            embedding_model_id: Embedding model ID.
            llm_model: LLM model name for reasoning.
        """
        status_rows = []

        # Flow agent
        if flow_agent_id:
            status_rows.append(("Flow Agent", "[green]Configured[/green]"))
            status_rows.append(("  ID", f"[dim]{flow_agent_id}[/dim]"))
        else:
            status_rows.append(("Flow Agent", "[yellow]Not configured[/yellow]"))

        # Conversational agent
        if conversational_agent_id:
            status_rows.append(("Conversational Agent", "[green]Configured[/green]"))
            status_rows.append(("  ID", f"[dim]{conversational_agent_id}[/dim]"))
        else:
            status_rows.append(("Conversational Agent", "[yellow]Not configured[/yellow]"))

        # Embedding model
        if embedding_model_id:
            status_rows.append(("Embedding Model", "[green]Configured[/green]"))
            status_rows.append(("  ID", f"[dim]{embedding_model_id}[/dim]"))
        else:
            status_rows.append(("Embedding Model", "[red]Not configured[/red]"))

        # LLM model
        status_rows.append(("LLM Model", llm_model))

        self.table("Agentic Search Configuration", status_rows)

        if not flow_agent_id and not conversational_agent_id:
            self.newline()
            self.format_error_with_suggestion(
                error="No agents configured.",
                suggestion="Run agentic setup to create agents.",
                command="gnosisllm-knowledge agentic setup",
            )

    def memory_status(
        self,
        llm_model_id: str | None,
        embedding_model_id: str | None,
        llm_model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        """Display agentic memory configuration status.

        Args:
            llm_model_id: LLM model ID if configured.
            embedding_model_id: Embedding model ID if configured.
            llm_model: LLM model name for fact extraction.
            embedding_model: Embedding model name.
        """
        status_rows = []

        # LLM Model
        if llm_model_id:
            status_rows.append(("LLM Model", "[green]Configured[/green]"))
            status_rows.append(("  ID", f"[dim]{llm_model_id}[/dim]"))
            status_rows.append(("  Model", llm_model))
        else:
            status_rows.append(("LLM Model", "[red]Not configured[/red]"))

        # Embedding Model
        if embedding_model_id:
            status_rows.append(("Embedding Model", "[green]Configured[/green]"))
            status_rows.append(("  ID", f"[dim]{embedding_model_id}[/dim]"))
            status_rows.append(("  Model", embedding_model))
        else:
            status_rows.append(("Embedding Model", "[red]Not configured[/red]"))

        self.table("Agentic Memory Configuration", status_rows)

        if not llm_model_id or not embedding_model_id:
            self.newline()
            self.format_error_with_suggestion(
                error="Memory models not configured.",
                suggestion="Run memory setup to create connectors and models.",
                command="gnosisllm-knowledge memory setup --openai-key sk-...",
            )
