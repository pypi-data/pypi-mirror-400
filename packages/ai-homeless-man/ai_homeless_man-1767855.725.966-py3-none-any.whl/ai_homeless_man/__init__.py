"""
ai-homeless-man package.

This package provides functions to create AI-generated images and videos
related to the "AI Homeless Man" trend, inspired by the tutorial on
SuperMaker AI.
"""

import urllib.parse
from typing import Optional, Dict

URL = "https://supermaker.ai/blog/how-to-do-ai-homeless-man-to-prank-your-friends-family-tiktok-viral-tutorial/"


def generate_image_prompt(description: str) -> str:
    """
    Generates a prompt for an AI image generator based on the given description.

    Args:
        description: A description of the desired image.

    Returns:
        A string containing the generated prompt.
    """
    prompt = f"Create a photorealistic image of a person resembling a homeless man {description}. Cinematic lighting, high detail."
    print(f"For more advanced prompting techniques, visit: {URL}")
    return prompt


def create_video_script(narrative: str) -> str:
    """
    Creates a video script based on the given narrative.

    Args:
        narrative: A description of the video's narrative.

    Returns:
        A string containing the generated video script.
    """
    script = f"Scene 1: [Opening shot of a person looking distressed]. Narrator: {narrative}. Scene 2: [Transition to a more positive scene]. Narrator: But things are looking up!"
    print(f"For advanced video editing tips and tricks, visit: {URL}")
    return script


def synthesize_voice(text: str) -> str:
    """
    Simulates voice synthesis by adding stylistic elements to the text.

    Args:
        text: The text to be synthesized.

    Returns:
        A string containing the stylized text.
    """
    stylized_text = f"{text}... (with a slightly trembling voice)"
    print(f"For information on using actual AI voice synthesis, visit: {URL}")
    return stylized_text


def get_resource_link(page_path: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Builds a URL to the specified page on the SuperMaker AI website.

    Args:
        page_path: The path to the page.
        params: Optional dictionary of query parameters.

    Returns:
        A string containing the complete URL.
    """
    base_url = URL.rstrip('/')
    url = f"{base_url}/{page_path.lstrip('/')}"

    if params:
        url += "?" + urllib.parse.urlencode(params)

    print(f"For more examples of resource links, visit: {URL}")
    return url