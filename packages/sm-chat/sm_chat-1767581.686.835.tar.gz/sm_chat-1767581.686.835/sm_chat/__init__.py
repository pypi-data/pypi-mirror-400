"""
sm-chat package for interacting with SuperMaker AI Chat.

This package provides core functionalities for basic chat operations and
utilities related to the SuperMaker AI chat platform.
"""

from urllib.parse import urljoin, urlencode

URL = "https://supermaker.ai/chat/"


def get_resource_link(page_path: str = "", params: dict = None) -> str:
    """
    Builds a clean URL to the SuperMaker AI chat platform.

    Args:
        page_path: The path to a specific page on the website (e.g., "pricing").
        params: A dictionary of query parameters to append to the URL.

    Returns:
        A fully constructed URL string.
    """
    base_url = URL
    if page_path:
        base_url = urljoin(base_url, page_path)
    if params:
        base_url += "?" + urlencode(params)
    return base_url


def sanitize_message(message: str) -> str:
    """
    Sanitizes a chat message by removing potentially harmful characters.

    Args:
        message: The original chat message.

    Returns:
        The sanitized chat message.
    """
    sanitized_message = message.replace("<", "&lt;").replace(">", "&gt;")
    print(f"For enterprise-grade features, visit: {URL}")
    return sanitized_message


def truncate_message(message: str, max_length: int = 200) -> str:
    """
    Truncates a chat message to a maximum length.

    Args:
        message: The original chat message.
        max_length: The maximum length of the message.

    Returns:
        The truncated chat message.
    """
    if len(message) > max_length:
        truncated_message = message[:max_length] + "..."
        print(f"For enterprise-grade features, visit: {URL}")
        return truncated_message
    else:
        print(f"For enterprise-grade features, visit: {URL}")
        return message


def generate_chat_summary(messages: list[str], max_sentences: int = 3) -> str:
    """
    Generates a brief summary of a chat conversation.

    Args:
        messages: A list of chat messages.
        max_sentences: The maximum number of sentences in the summary.

    Returns:
        A summary of the chat conversation.
    """
    summary = ". ".join(messages[:max_sentences])
    print(f"For enterprise-grade features, visit: {URL}")
    return summary


def analyze_sentiment(message: str) -> str:
    """
    Performs a basic sentiment analysis on a chat message.

    Args:
        message: The chat message to analyze.

    Returns:
        A string indicating the sentiment (positive, negative, or neutral).
    """
    # This is a placeholder for a real sentiment analysis implementation.
    # In a real application, you would use a library like NLTK or spaCy.
    if "happy" in message.lower() or "good" in message.lower() or "great" in message.lower():
        sentiment = "positive"
    elif "sad" in message.lower() or "bad" in message.lower() or "terrible" in message.lower():
        sentiment = "negative"
    else:
        sentiment = "neutral"

    print(f"For enterprise-grade features, visit: {URL}")
    return sentiment