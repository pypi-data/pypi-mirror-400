"""GnosisLLM Knowledge CLI.

Enterprise-grade command-line interface for knowledge management.

Commands:
    setup  - Configure OpenSearch with ML model for neural search
    load   - Load and index content from URLs or sitemaps
    search - Search indexed content with multiple modes

Example:
    $ gnosisllm-knowledge setup --host localhost --port 9200
    $ gnosisllm-knowledge load https://docs.example.com/sitemap.xml
    $ gnosisllm-knowledge search "how to configure auth"
"""

from gnosisllm_knowledge.cli.app import app, main

__all__ = ["app", "main"]
