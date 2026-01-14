"""Claude API integration for finding working locators."""

import base64
import re
from typing import Optional
from playwright.sync_api import Page, Locator
import anthropic
import logging


logger = logging.getLogger(__name__)


class ClaudeFinder:
    """
    Interfaces with Anthropic Claude API to find element locators.
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """
        Initialize Claude API client.

        Args:
            api_key: Anthropic API key.
            model: Claude model to use.
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized ClaudeFinder with model: {model}")

    def find_locator(
        self,
        screenshot_path: str,
        html_snapshot: str,
        element_description: str,
        failed_locator: str
    ) -> Optional[str]:
        """
        Send screenshot + HTML + description to Claude and return new locator.

        Args:
            screenshot_path: Path to screenshot image.
            html_snapshot: HTML content of the page.
            element_description: Human-readable description of element.
            failed_locator: The locator that failed (for context).

        Returns:
            Playwright locator string or None if Claude couldn't find it.
        """
        logger.info(f"Asking Claude to find locator for: {element_description}")

        try:
            prompt = self._build_prompt(element_description, failed_locator, html_snapshot)

            # Convert screenshot to base64
            with open(screenshot_path, 'rb') as f:
                screenshot_b64 = base64.b64encode(f.read()).decode()

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_b64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Parse Claude's response
            response_text = message.content[0].text
            logger.debug(f"Claude response: {response_text}")

            locator_str = self._parse_locator_response(response_text)

            if locator_str:
                logger.info(f"Claude found locator: {locator_str}")
            else:
                logger.warning("Claude could not generate a valid locator")

            return locator_str

        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return None

    def _build_prompt(self, element_description: str, failed_locator: str, html: str) -> str:
        """
        Construct the prompt for Claude with all necessary context.

        Args:
            element_description: Description of element to find.
            failed_locator: The locator that failed.
            html: HTML snapshot of the page.

        Returns:
            Prompt string for Claude.
        """
        # Truncate HTML to avoid token limits (first 20000 chars to capture more context)
        html_truncated = html[:20000] if len(html) > 20000 else html

        return f"""You are a Playwright locator expert. A locator failed and you must find the correct one by analyzing the HTML.

**Failed Locator (WRONG):**
{failed_locator}

**What we're looking for:**
{element_description}

**Page HTML:**
{html_truncated}

**YOUR TASK:**
Search through the HTML above and find the element for "{element_description}". Look for <input> tags that could be a search field.

**STEP 1:** Find the element in the HTML
Look for: <input type="search"> or similar search-related elements

**STEP 2:** Extract its attributes
What is the element's:
- id attribute? (most important)
- name attribute?
- class attribute?
- placeholder attribute? (check if it exists)
- data-testid?

**STEP 3:** Choose the best locator
1. If it has id="xyz" → return: page.locator("#xyz")
2. If it has data-testid="xyz" → return: page.get_by_test_id("xyz")
3. If it has placeholder="xyz" → return: page.get_by_placeholder("xyz")
4. If it has name="xyz" → return: page.locator("[name='xyz']")

**CRITICAL RULE:**
- ALWAYS prefer id if it exists
- Do NOT use get_by_placeholder() unless you see placeholder="..." in the HTML
- Use EXACT attribute values from the HTML

**Output:**
YOU MUST return ONLY the locator code. Nothing else.
Do NOT add any explanation, reasoning, or additional text.
Do NOT say "I recommend" or "I suggest" - just return the code.

CORRECT OUTPUT:
page.locator("#searchInput")

WRONG OUTPUT (do not do this):
Based on the HTML, I recommend: page.locator("#searchInput")
"""

    def _parse_locator_response(self, response: str) -> Optional[str]:
        """
        Extract the locator string from Claude's response.

        Args:
            response: Claude's text response.

        Returns:
            Locator string or None if invalid.
        """
        # Remove any markdown code blocks
        response = response.strip()
        if response.startswith("```"):
            match = re.search(r"```(?:python)?\n(.+?)\n```", response, re.DOTALL)
            if match:
                response = match.group(1).strip()

        # Remove any extra text, keep only lines that start with "page."
        lines = response.split('\n')
        locator_line = None

        for line in lines:
            line = line.strip()
            # Look for lines with page. and a locator method
            if "page." in line and any(method in line for method in [
                "get_by_role", "get_by_label", "get_by_text",
                "get_by_placeholder", "locator", "get_by_test_id"
            ]):
                # Extract just the page.xxx(...) part
                # Match from 'page.' to the end of the method call
                match = re.search(r'(page\.\w+\([^)]*\))', line)
                if match:
                    locator_line = match.group(1)
                    break
                elif line.startswith("page."):
                    locator_line = line
                    break

        if not locator_line:
            logger.warning(f"Could not extract locator from response: {response}")
            return None

        # Validate format
        locator_methods = [
            "get_by_role",
            "get_by_label",
            "get_by_text",
            "get_by_placeholder",
            "locator",
            "get_by_test_id"
        ]

        if any(method in locator_line for method in locator_methods):
            return locator_line.strip()

        return None

    def locator_string_to_playwright(self, page: Page, locator_str: str) -> Optional[Locator]:
        """
        Convert a locator string to an actual Playwright Locator object.

        Args:
            page: Playwright Page object.
            locator_str: Locator string from Claude.

        Returns:
            Playwright Locator object or None if conversion fails.
        """
        # Fix common quoting issues in get_by_role()
        # Claude sometimes returns: get_by_role(button, ...) instead of get_by_role("button", ...)
        locator_str = self._fix_get_by_role_quotes(locator_str)

        # Use eval with restricted namespace for safety
        namespace = {
            "page": page,
            "Locator": Locator
        }

        try:
            # Remove "page." prefix if present for evaluation
            if locator_str.startswith("page."):
                eval_str = locator_str
            else:
                eval_str = f"page.{locator_str}"

            locator = eval(eval_str, {"__builtins__": {}}, namespace)
            logger.debug(f"Successfully converted locator string to Playwright Locator")
            return locator

        except Exception as e:
            logger.error(f"Failed to convert locator string '{locator_str}': {e}")
            return None

    def _fix_get_by_role_quotes(self, locator_str: str) -> str:
        """
        Fix missing quotes around the role parameter in get_by_role().

        Claude sometimes returns: get_by_role(button, name="...")
        Should be: get_by_role("button", name="...")

        Args:
            locator_str: The locator string to fix.

        Returns:
            Fixed locator string with proper quoting.
        """
        # Match get_by_role with unquoted role parameter
        # Pattern: get_by_role(word_without_quotes, ...)
        pattern = r'get_by_role\((\w+)(?=\s*,|\s*\))'

        def replace_unquoted_role(match):
            role = match.group(1)
            # If it's already quoted or is a keyword, leave it
            if role in ['True', 'False', 'None']:
                return f'get_by_role({role}'
            # Otherwise, add quotes
            return f'get_by_role("{role}"'

        fixed_str = re.sub(pattern, replace_unquoted_role, locator_str)

        if fixed_str != locator_str:
            logger.info(f"Fixed unquoted role parameter: {locator_str} -> {fixed_str}")

        return fixed_str
