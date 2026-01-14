"""CLI commands for gnosisllm-knowledge."""

from gnosisllm_knowledge.cli.commands.load import load_command
from gnosisllm_knowledge.cli.commands.search import search_command
from gnosisllm_knowledge.cli.commands.setup import setup_command

__all__ = ["setup_command", "load_command", "search_command"]
