"""Prompt loader utility for reading prompts from text files."""

import os
from pathlib import Path
from typing import Optional


class PromptLoader:
    """Loads prompts from text files in the prompts directory."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Optional custom prompts directory path.
                        If None, uses default src/prompts/ directory.
        """
        if prompts_dir:
            self._prompts_dir = Path(prompts_dir)
        else:
            # Get the src/prompts directory relative to this file
            # This file is in src/infrastructure/ai/prompts/
            # We need to go up to src/prompts/
            current_file = Path(__file__)
            src_dir = current_file.parent.parent.parent.parent
            self._prompts_dir = src_dir / "prompts"

        if not self._prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory not found: {self._prompts_dir}"
            )

    def _load_prompt_file(self, filename: str) -> str:
        """
        Load a prompt file and return its contents.

        Args:
            filename: Name of the prompt file (e.g., "agent_instruction.txt")

        Returns:
            Contents of the prompt file as a string

        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        prompt_path = self._prompts_dir / filename

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}"
            )

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def load_agent_instruction(self, country_list: str) -> str:
        """
        Load the main agent instruction prompt.

        Args:
            country_list: List of available countries to inject into the prompt

        Returns:
            Formatted agent instruction prompt
        """
        prompt = self._load_prompt_file("agent_instruction.txt")
        return prompt.format(country_list=country_list)

    def load_agent_description(self) -> str:
        """
        Load the agent description.

        Returns:
            Agent description string
        """
        return self._load_prompt_file("agent_description.txt")

