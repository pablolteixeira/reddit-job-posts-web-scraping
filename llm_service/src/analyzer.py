"""
Job post analyzer using Ollama with Llama 3.1 model.
"""
import os
import json
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import ollama

load_dotenv()


def clean_and_extract_text(title: str, body: str) -> Tuple[str, str, List[str]]:
    """
    Analyze a job post using Ollama's Llama 3.1 model to extract structured information.

    Args:
        title: Job post title
        body: Job post body text

    Returns:
        Tuple of (cleaned_title, cleaned_text, tags)
    """
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # Create structured prompt for extraction
    prompt = f"""You are a job post analyzer. Extract and clean the following information from this job posting.

TITLE: {title}

BODY: {body}

Please provide your analysis in this EXACT JSON format (no extra text):
{{
    "cleaned_title": "A concise, professional version of the title",
    "cleaned_text": "A cleaned summary of the job description with key details",
    "tags": ["tag1", "tag2", "tag3"]
}}

Tags should include: job type, experience level, key technologies/skills, remote/location info, and any other relevant categories.

Response:"""

    try:
        # Call Ollama API
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured information from job posts. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.3,  # Lower temperature for more consistent output
                "num_predict": 500   # Limit output length
            }
        )

        # Extract response content
        content = response['message']['content']

        # Try to parse JSON from response
        result = parse_llm_response(content, title, body)

        return result

    except Exception as e:
        print(f"Error analyzing job post with Ollama: {e}")
        # Return fallback values
        return (
            title[:200],  # Truncated title
            body[:500] if body else "No description provided",
            ["unprocessed", "error"]
        )


def parse_llm_response(content: str, original_title: str, original_body: str) -> Tuple[str, str, List[str]]:
    """
    Parse the LLM response and extract structured data.

    Args:
        content: Raw LLM response
        original_title: Original job title (fallback)
        original_body: Original job body (fallback)

    Returns:
        Tuple of (cleaned_title, cleaned_text, tags)
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)

        # Extract fields with fallbacks
        cleaned_title = data.get("cleaned_title", original_title)[:200]
        cleaned_text = data.get("cleaned_text", original_body)[:1000]
        tags = data.get("tags", ["unprocessed"])

        # Ensure tags is a list
        if not isinstance(tags, list):
            tags = ["unprocessed"]

        # Limit tags to 10
        tags = tags[:10]

        return (cleaned_title, cleaned_text, tags)

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from LLM response: {e}")
        print(f"Response content: {content[:200]}")

        # Fallback: basic text extraction
        return (
            original_title[:200],
            original_body[:1000] if original_body else "No description",
            ["parsing_failed"]
        )