"""Gemini API wrapper for XML prompt generation."""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from .config import ConfigManager

# Load environment variables
load_dotenv()

# Meta-prompt for Gemini to generate Claude-friendly XML prompts
META_PROMPT = """You are a prompt engineering expert for Anthropic Claude Code (CLI agent).

Your task is to transform the user's natural language input into a well-structured XML prompt that Claude Code can understand and execute effectively.

Rules:
1. Output ONLY the XML block. No markdown code blocks, no explanations, no surrounding text.
2. Analyze the user's intent and expand it into specific, actionable instructions.
3. Use the following XML structure:

<purpose>
{Summarize the user's intent in one clear sentence}
</purpose>
<instructions>
1. {Specific instruction 1}
2. {Specific instruction 2}
...
</instructions>

4. If the user's request involves code, include relevant details like:
   - Programming language
   - File paths if mentioned
   - Specific requirements or constraints

5. Keep instructions concise but comprehensive.
6. Number each instruction for clarity.
7. If context is needed, add a <context> tag before <instructions>.

Remember: Output ONLY the raw XML. No ``` markers, no "Here's the prompt:", nothing else."""


class GeminiClient:
    """Client for interacting with Gemini API."""

    def __init__(self, api_key: str | None = None):
        """Initialize the Gemini client.

        Args:
            api_key: Gemini API key. If not provided, reads from config or env var.

        Priority order:
            1. Explicit parameter
            2. ~/.cheater/config file
            3. GEMINI_API_KEY environment variable
        """
        config = ConfigManager()
        self.api_key = (
            api_key
            or config.get("api_key")
            or os.getenv("GEMINI_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Run 'cheater config set' or set GEMINI_API_KEY environment variable."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def generate_xml_prompt(self, user_input: str) -> str:
        """Convert user's natural language input to XML prompt.

        Args:
            user_input: Natural language instruction from user.

        Returns:
            XML-formatted prompt for Claude Code.

        Raises:
            Exception: If API call fails.
        """
        chat = self.model.start_chat(history=[])

        # Send meta-prompt as system context
        response = chat.send_message(
            f"{META_PROMPT}\n\nUser's input to transform:\n{user_input}"
        )

        # Clean up the response - remove any accidental markdown
        result: str = str(response.text).strip()

        # Remove markdown code blocks if present
        if result.startswith("```xml"):
            result = result[6:]
        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        return result.strip()


def generate_xml_prompt(user_input: str) -> str:
    """Convenience function to generate XML prompt.

    Args:
        user_input: Natural language instruction from user.

    Returns:
        XML-formatted prompt for Claude Code.
    """
    client = GeminiClient()
    return client.generate_xml_prompt(user_input)
