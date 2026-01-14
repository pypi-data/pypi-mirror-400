"""Setup command for configuring OpenSearch with neural search.

Creates:
- OpenAI embedding connector
- Model group and deployed ML model
- Ingest pipeline for automatic embedding generation
- Search pipeline for hybrid scoring
- Knowledge index with k-NN vector mapping
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from opensearchpy import AsyncOpenSearch

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig
from gnosisllm_knowledge.backends.opensearch.setup import OpenSearchSetupAdapter
from gnosisllm_knowledge.cli.display.service import RichDisplayService, StepProgress
from gnosisllm_knowledge.cli.utils.config import CliConfig

if TYPE_CHECKING:
    pass


async def setup_command(
    display: RichDisplayService,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    use_ssl: bool | None = None,
    verify_certs: bool | None = None,
    force: bool = False,
    no_sample_data: bool = False,
    no_hybrid: bool = False,
) -> None:
    """Execute the setup command.

    Args:
        display: Display service for output.
        host: OpenSearch host (overrides env).
        port: OpenSearch port (overrides env).
        username: OpenSearch username (overrides env).
        password: OpenSearch password (overrides env).
        use_ssl: Enable SSL (overrides env).
        verify_certs: Verify SSL certificates (overrides env).
        force: Clean up existing resources first.
        no_sample_data: Skip sample data ingestion.
        no_hybrid: Skip hybrid search pipeline.
    """
    # Load configuration from environment
    cli_config = CliConfig.from_env()

    # CLI arguments override environment variables (only if explicitly provided)
    final_host = host if host is not None else cli_config.opensearch_host
    final_port = port if port is not None else cli_config.opensearch_port
    final_username = username if username is not None else cli_config.opensearch_username
    final_password = password if password is not None else cli_config.opensearch_password
    final_use_ssl = use_ssl if use_ssl is not None else cli_config.opensearch_use_ssl
    final_verify_certs = verify_certs if verify_certs is not None else cli_config.opensearch_verify_certs

    # Validate required config
    if not cli_config.openai_api_key:
        display.format_error_with_suggestion(
            error="OPENAI_API_KEY is required for setup.",
            suggestion="Set the OPENAI_API_KEY environment variable.",
            command="export OPENAI_API_KEY=sk-...",
        )
        sys.exit(1)

    # Display header
    display.header(
        "GnosisLLM Knowledge Setup",
        f"Configuring OpenSearch at {final_host}:{final_port}",
    )

    # Show configuration
    display.table(
        "Configuration",
        [
            ("Host", f"{final_host}:{final_port}"),
            ("SSL", "Enabled" if final_use_ssl else "Disabled"),
            ("Auth", "Configured" if final_username else "None"),
            ("Hybrid Search", "Disabled" if no_hybrid else "Enabled"),
            ("Force Recreate", "Yes" if force else "No"),
        ],
    )

    display.newline()

    # Create OpenSearch config
    opensearch_config = OpenSearchConfig(
        host=final_host,
        port=final_port,
        username=final_username,
        password=final_password,
        use_ssl=final_use_ssl,
        verify_certs=final_verify_certs,
        openai_api_key=cli_config.openai_api_key,
        embedding_model=cli_config.openai_embedding_model,
        embedding_dimension=cli_config.openai_embedding_dimension,
    )

    # Create OpenSearch client
    http_auth = None
    if final_username and final_password:
        http_auth = (final_username, final_password)

    client = AsyncOpenSearch(
        hosts=[{"host": final_host, "port": final_port}],
        http_auth=http_auth,
        use_ssl=final_use_ssl,
        verify_certs=final_verify_certs,
        ssl_show_warn=False,
    )

    try:
        # Health check
        display.info("Checking OpenSearch connection...")

        adapter = OpenSearchSetupAdapter(client, opensearch_config)

        if not await adapter.health_check():
            display.format_error_with_suggestion(
                error=f"Cannot connect to OpenSearch at {final_host}:{final_port}",
                suggestion="Ensure OpenSearch is running and accessible.",
                command=f"curl http{'s' if final_use_ssl else ''}://{final_host}:{final_port}",
            )
            sys.exit(1)

        # Get cluster info
        try:
            cluster_stats = await adapter.get_cluster_stats()
            display.success(
                f"Connected to OpenSearch {cluster_stats.get('cluster_name', 'cluster')} "
                f"({cluster_stats.get('node_count', 0)} nodes)"
            )
        except Exception:
            display.success("Connected to OpenSearch")

        display.newline()

        # Force cleanup if requested
        if force:
            display.warning("Force mode: cleaning up existing resources...")
            cleanup_result = await adapter.cleanup()
            for step in cleanup_result.steps_completed or []:
                display.info(f"  {step}")
            display.newline()

        # Get setup steps
        step_defs = adapter.get_setup_steps()

        # Filter steps based on options
        if no_hybrid:
            step_defs = [s for s in step_defs if s[0] != "search_pipeline"]

        # Create progress display
        steps = [StepProgress(name=name, description=desc) for name, desc in step_defs]
        progress = display.progress(steps)

        # Execute setup
        setup_options = {
            "force_recreate": False,  # Already handled above
        }

        try:
            result = await adapter.setup(**setup_options)

            # Update progress based on result
            for i, (step_name, _) in enumerate(step_defs):
                # Normalize step name for matching (replace underscores with spaces)
                normalized_name = step_name.replace("_", " ")

                # Check if step was completed
                step_completed = any(
                    normalized_name in completed.lower()
                    for completed in (result.steps_completed or [])
                )
                step_error = None
                for error in result.errors or []:
                    if normalized_name in error.lower() or step_name in error.lower():
                        step_error = error
                        break

                if step_error:
                    progress.fail(i, step_error.split(": ")[-1][:40])
                elif step_completed:
                    progress.complete(i)
                else:
                    progress.skip(i, "Skipped")

            progress.stop()

        except Exception as e:
            progress.stop()
            display.format_error_with_suggestion(
                error=f"Setup failed: {e}",
                suggestion="Check OpenSearch logs for more details.",
            )
            sys.exit(1)

        display.newline()

        # Display result
        if result.success:
            model_id = adapter.model_id or (result.data or {}).get("model_id")

            content = f"Model ID: [cyan]{model_id}[/cyan]\n\n"
            content += "Add to your .env file:\n"
            content += f"  [green]OPENSEARCH_MODEL_ID={model_id}[/green]"

            if not no_sample_data:
                content += "\n\nTest your setup:\n"
                content += '  [dim]gnosisllm-knowledge search "test query"[/dim]'

            display.panel(content, title="Setup Complete", style="success")

        else:
            error_content = "Setup completed with errors:\n\n"
            for error in result.errors or []:
                error_content += f"[red]• {error}[/red]\n"

            display.panel(error_content, title="Setup Incomplete", style="warning")
            sys.exit(1)

    finally:
        await client.close()
