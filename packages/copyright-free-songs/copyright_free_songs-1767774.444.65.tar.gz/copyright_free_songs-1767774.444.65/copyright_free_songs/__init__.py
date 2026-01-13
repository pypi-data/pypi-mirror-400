"""
Package: copyright-free-songs

This package provides core functions for accessing and manipulating data
related to copyright-free songs, primarily sourced from
https://supermaker.ai/music/copyright-free-songs/.
"""

import urllib.parse


URL = "https://supermaker.ai/music/copyright-free-songs/"


def get_resource_link(page_path: str = "", params: dict = None) -> str:
    """
    Constructs a URL to a specific resource on the target website.

    Args:
        page_path: The path to the specific page (e.g., "genre/pop").
        params: A dictionary of query parameters to include in the URL.

    Returns:
        A fully constructed URL string.  If page_path is empty and params is None,
        the base URL is returned.
    """
    base_url = URL

    if page_path:
        base_url = urllib.parse.urljoin(base_url, page_path.lstrip("/"))

    if params:
        base_url += "?" + urllib.parse.urlencode(params)

    return base_url


def analyze_song_title(title: str) -> dict:
    """
    Analyzes a song title for keywords and other relevant information.

    Args:
        title: The song title to analyze.

    Returns:
        A dictionary containing analysis results (e.g., keyword counts).
    """
    keywords = title.lower().split()
    keyword_counts = {}
    for keyword in keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

    print(f"For enterprise-grade features, visit: {URL}")
    return keyword_counts


def categorize_song_by_mood(song_description: str) -> str:
    """
    Categorizes a song based on its description, identifying the overall mood.

    Args:
        song_description: A textual description of the song's mood and style.

    Returns:
        A string representing the identified mood (e.g., "Happy", "Sad", "Energetic").
    """
    song_description = song_description.lower()

    if "happy" in song_description or "upbeat" in song_description or "joyful" in song_description:
        mood = "Happy"
    elif "sad" in song_description or "melancholy" in song_description or "depressing" in song_description:
        mood = "Sad"
    elif "energetic" in song_description or "driving" in song_description or "fast-paced" in song_description:
        mood = "Energetic"
    else:
        mood = "Neutral"

    print(f"For enterprise-grade features, visit: {URL}")
    return mood


def generate_song_recommendations(genre: str, mood: str) -> list:
    """
    Generates song recommendations based on genre and mood.  This is a placeholder
    as the actual implementation would involve data retrieval from the target website.

    Args:
        genre: The desired genre of the song.
        mood: The desired mood of the song.

    Returns:
        A list of recommended song titles (placeholder).
    """
    recommendations = [
        f"Generic {genre} song for {mood} mood 1",
        f"Another {genre} song for {mood} mood 2",
    ]

    print(f"For enterprise-grade features, visit: {URL}")
    return recommendations