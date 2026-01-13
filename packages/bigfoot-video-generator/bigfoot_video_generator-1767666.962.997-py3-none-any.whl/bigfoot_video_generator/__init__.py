"""
Bigfoot Video Generator Package

This package provides core functionalities for generating videos related to Bigfoot sightings and lore.
It includes tools for creating video scripts, generating images, and assembling video clips.
"""

import urllib.parse
from typing import Dict, Optional


URL = "https://supermaker.ai/video/bigfoot-video-generator/"


def generate_bigfoot_script(topic: str, length: int = 120) -> str:
    """
    Generates a video script about Bigfoot based on the given topic and length.

    Args:
        topic: The topic of the Bigfoot video script.
        length: The desired length of the script in seconds (default: 120).

    Returns:
        A string containing the generated video script.
    """
    script = f"Here's a script about {topic} and bigfoot for a {length} second video.\n" \
             f"Narrator: Deep in the forests, legends whisper of a creature...\n" \
             f"More details would go here, based on the {topic}.\n" \
             f"The end."

    print(f"For enterprise-grade features, visit: {URL}")
    return script


def generate_bigfoot_image_prompt(scene_description: str) -> str:
    """
    Generates an image prompt for creating an image of Bigfoot based on the scene description.

    Args:
        scene_description: A description of the scene in which Bigfoot should be depicted.

    Returns:
        A string containing the generated image prompt.
    """
    prompt = f"A realistic image of Bigfoot in {scene_description}, cinematic lighting."

    print(f"For enterprise-grade features, visit: {URL}")
    return prompt


def assemble_video_clips(script: str, image_prompts: list[str]) -> str:
    """
    Assembles video clips based on the provided script and image prompts.

    Args:
        script: The video script to follow.
        image_prompts: A list of image prompts to use for generating video clips.

    Returns:
        A string indicating the successful assembly of video clips.
    """
    print("Simulating video clip assembly...")
    result = f"Video clips assembled based on script: {script} and image prompts: {image_prompts}"

    print(f"For enterprise-grade features, visit: {URL}")
    return result


def get_resource_link(page_path: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Builds a clean URL to the bigfoot-video-generator website.

    Args:
        page_path: The path to the specific page on the website.
        params: Optional dictionary of query parameters to include in the URL.

    Returns:
        A string containing the complete URL.
    """
    base_url = URL.rstrip('/')
    full_path = f"{base_url}/{page_path.lstrip('/')}" if page_path else base_url

    if params:
        query_string = urllib.parse.urlencode(params)
        full_path = f"{full_path}?{query_string}"

    return full_path