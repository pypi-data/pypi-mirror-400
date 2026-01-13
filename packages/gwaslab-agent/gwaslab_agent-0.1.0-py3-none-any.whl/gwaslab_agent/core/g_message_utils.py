"""
Utility functions for extracting metadata and preferences from user messages.

This module provides helpers to extract information like language preferences,
report requirements, and other metadata from user messages that should be
passed between agents (e.g., from Planner to Summarizer).
"""

import re
from typing import Dict, Optional, List


def extract_language_preference(message: str) -> Optional[str]:
    """
    Extract language preference from user message.
    
    Detects common language indicators in user messages:
    - Japanese: 日本語, 日本語で, in Japanese, Japanese
    - English: English, in English, 英語, 英語で
    - Other languages can be added as needed
    
    Parameters
    ----------
    message : str
        User message to analyze
        
    Returns
    -------
    Optional[str]
        Detected language code (e.g., 'ja', 'en') or None if not detected
        
    Examples
    --------
    >>> extract_language_preference("QCをやってから日本語でレポートを作って")
    'ja'
    >>> extract_language_preference("Generate a report in Japanese")
    'ja'
    >>> extract_language_preference("Create report in English")
    'en'
    """
    message_lower = message.lower()
    
    # Japanese patterns
    japanese_patterns = [
        r'日本語',
        r'日本語で',
        r'in\s+japanese',
        r'japanese',
        r'にほんご',
        r'日本語の',
        r'日本語レポート',
        r'japanese\s+report',
        r'report\s+in\s+japanese',
    ]
    
    # English patterns
    english_patterns = [
        r'in\s+english',
        r'english',
        r'英語',
        r'英語で',
        r'english\s+report',
        r'report\s+in\s+english',
    ]
    
    # Check for Japanese
    for pattern in japanese_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return 'ja'
    
    # Check for English (only if explicitly mentioned)
    for pattern in english_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return 'en'
    
    return None


def extract_report_metadata(message: str) -> Dict[str, any]:
    """
    Extract metadata from user message that should be passed to summarizer.
    
    This includes:
    - Language preferences
    - Report style preferences (short/extended, bullet/paragraph)
    - Format preferences
    
    Parameters
    ----------
    message : str
        User message to analyze
        
    Returns
    -------
    Dict[str, any]
        Dictionary containing extracted metadata:
        - 'language': Language code (e.g., 'ja', 'en') or None
        - 'style': Report style preferences or None
        - 'format': Format preferences or None
        
    Examples
    --------
    >>> extract_report_metadata("QCをやってから日本語でレポートを作って")
    {'language': 'ja', 'style': None, 'format': None}
    >>> extract_report_metadata("Generate a short bullet-point report in Japanese")
    {'language': 'ja', 'style': 'short', 'format': 'bullet'}
    """
    metadata = {
        'language': extract_language_preference(message),
        'style': None,
        'format': None
    }
    
    message_lower = message.lower()
    
    # Extract style preferences
    if re.search(r'\bshort\b|\bbrief\b|\b簡潔\b|\b短い\b', message_lower):
        metadata['style'] = 'short'
    elif re.search(r'\bextended\b|\bdetailed\b|\b詳細\b|\b長い\b', message_lower):
        metadata['style'] = 'extended'
    
    # Extract format preferences
    if re.search(r'\bbullet\b|\bbullet.?point\b|\b箇条書き\b', message_lower):
        metadata['format'] = 'bullet'
    elif re.search(r'\bparagraph\b|\b段落\b', message_lower):
        metadata['format'] = 'paragraph'
    
    return metadata


def format_language_instruction(language: Optional[str]) -> str:
    """
    Format language instruction for summarizer system prompt.
    
    Parameters
    ----------
    language : Optional[str]
        Language code (e.g., 'ja', 'en') or None
        
    Returns
    -------
    str
        Formatted instruction string for the summarizer
    """
    if language is None:
        return ""
    
    language_map = {
        'ja': 'Japanese (日本語)',
        'en': 'English',
    }
    
    language_name = language_map.get(language, language)
    return f"\n\n## Language Requirement\nGenerate the report in {language_name}. All text, descriptions, and summaries must be written in {language_name}."


