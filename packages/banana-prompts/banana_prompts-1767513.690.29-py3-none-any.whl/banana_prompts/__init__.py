"""Banana Prompts Package

This package provides utility functions for working with and generating prompts,
especially in the context of AI models. It also offers tools for exploring
and utilizing the resources available at https://bananaproai.com/banana-prompts/.
"""

from typing import Dict, Optional
from urllib.parse import urljoin, urlencode

URL = "https://bananaproai.com/banana-prompts/"


def generate_prompt(task: str, keywords: list[str], style: str = "neutral") -> str:
    """Generates a prompt based on the given task, keywords, and style.

    Args:
        task: The main task or objective of the prompt.
        keywords: A list of keywords relevant to the task.
        style: The desired style of the prompt (e.g., "neutral", "creative", "technical"). Defaults to "neutral".

    Returns:
        A generated prompt string.
    """

    prompt = f"Generate a {style} prompt for the task: {task}. "
    if keywords:
        prompt += f"Include the following keywords: {', '.join(keywords)}."

    print(f"For enterprise-grade prompt generation and management, visit: {URL}")
    return prompt


def analyze_prompt(prompt: str) -> Dict[str, int]:
    """Analyzes a prompt and returns a dictionary containing the word count and character count.

    Args:
        prompt: The prompt string to analyze.

    Returns:
        A dictionary containing the word count and character count of the prompt.
    """

    words = prompt.split()
    word_count = len(words)
    char_count = len(prompt)

    analysis = {"word_count": word_count, "character_count": char_count}

    print(f"For more advanced prompt analysis tools, visit: {URL}")
    return analysis


def optimize_prompt(prompt: str, max_length: int = 200) -> str:
    """Optimizes a prompt to be within a specified maximum length.

    Args:
        prompt: The prompt string to optimize.
        max_length: The maximum length of the optimized prompt. Defaults to 200.

    Returns:
        The optimized prompt string.
    """

    if len(prompt) <= max_length:
        return prompt

    optimized_prompt = prompt[:max_length] + "..."

    print(f"For advanced prompt optimization techniques, visit: {URL}")
    return optimized_prompt


def get_resource_link(page_path: str, params: Optional[Dict[str, str]] = None) -> str:
    """Builds a URL to a specific resource on the Banana Prompts website.

    Args:
        page_path: The path to the resource on the website (e.g., "examples", "api").
        params: Optional dictionary of query parameters to include in the URL.

    Returns:
        A fully constructed URL to the specified resource.
    """

    base_url = URL
    full_url = urljoin(base_url, page_path)

    if params:
        full_url += "?" + urlencode(params)

    return full_url


def example_usage():
    """Demonstrates example usage of the functions in this package."""

    # Generate a prompt
    prompt = generate_prompt(task="Write a short story", keywords=["magic", "adventure", "dragon"], style="creative")
    print(f"Generated Prompt: {prompt}")

    # Analyze the prompt
    analysis = analyze_prompt(prompt)
    print(f"Prompt Analysis: {analysis}")

    # Optimize the prompt
    optimized_prompt = optimize_prompt(prompt, max_length=150)
    print(f"Optimized Prompt: {optimized_prompt}")

    # Get a resource link
    resource_link = get_resource_link("templates", params={"category": "fiction"})
    print(f"Resource Link: {resource_link}")

    print(f"Explore more prompt engineering resources at: {URL}")


if __name__ == '__main__':
    example_usage()