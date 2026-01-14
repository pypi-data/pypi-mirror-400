"""
Matching Utilities Module

This module provides utility functions for string matching, including exact match, pattern match,
and fuzzy match, which can be used across different modules in the application.
"""

import re
import difflib
from typing import Dict, List, Tuple, Any, Callable, Optional, TypeVar, Set

T = TypeVar('T')

def exact_match(query: str, targets: Dict[str, T]) -> Optional[Tuple[str, T]]:
    """
    Find an exact match for the query in the targets dictionary keys.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.

    Returns:
        Optional[Tuple[str, T]]: A tuple containing the matched key and its value, or None if no match found.
    """
    if query in targets:
        return query, targets[query]
    return None

def pattern_match(query: str, targets: Dict[str, T], ignore_case: bool = True) -> List[Tuple[str, T]]:
    """
    Find all targets where the query is a substring of the key or matches a regex pattern.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.
        ignore_case (bool): Whether to ignore case when matching.

    Returns:
        List[Tuple[str, T]]: List of tuples containing matched keys and their values.
    """
    results = []
    flags = re.IGNORECASE if ignore_case else 0
    
    for key, value in targets.items():
        if re.search(query, key, flags):
            results.append((key, value))
    
    return results

def fuzzy_match(query: str, targets: Dict[str, T], 
                threshold: float = 0.7, 
                normalize: bool = True) -> List[Tuple[str, T, float]]:
    """
    Find targets that fuzzy match the query based on similarity ratio.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.
        threshold (float): The minimum similarity ratio required for a match (between 0 and 1).
        normalize (bool): Whether to normalize strings (lowercase, replace special chars with spaces) before matching.

    Returns:
        List[Tuple[str, T, float]]: List of tuples containing matched keys, their values, and similarity scores,
                                   sorted by similarity score in descending order.
    """
    results = []
    
    # Normalize the query if requested
    norm_query = normalize_string(query) if normalize else query
    query_words = set(norm_query.split())
    
    for key, value in targets.items():
        norm_key = normalize_string(key) if normalize else key
        key_words = set(norm_key.split())
        
        # Word-level matching
        match_count = 0
        for q_word in query_words:
            for k_word in key_words:
                similarity = difflib.SequenceMatcher(None, q_word, k_word).ratio()
                if similarity > threshold or q_word in k_word or k_word in q_word:
                    match_count += 1
                    break
        
        # Calculate word match score
        word_match_score = match_count / len(query_words) if query_words else 0
        
        # Calculate overall string similarity
        string_similarity = difflib.SequenceMatcher(None, norm_query, norm_key).ratio()
        
        # Combine scores (give more weight to word matching)
        combined_score = (0.7 * word_match_score + 0.3 * string_similarity)
        
        if combined_score >= threshold:
            results.append((key, value, combined_score))
    
    # Sort results by score in descending order
    return sorted(results, key=lambda x: x[2], reverse=True)

def word_match(query: str, 
              targets: Dict[str, T],
              threshold_ratio: float = 0.5,
              word_similarity_threshold: float = 0.7,
              normalize: bool = True) -> List[Tuple[str, T, float]]:
    """
    Find targets that match the query based on word-level matching.
    
    This method is particularly useful when you want to match based on
    individual words rather than the entire string.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.
        threshold_ratio (float): The minimum ratio of matched words required (between 0 and 1).
        word_similarity_threshold (float): The minimum similarity ratio for individual words.
        normalize (bool): Whether to normalize strings before matching.

    Returns:
        List[Tuple[str, T, float]]: List of tuples containing matched keys, their values, and scores,
                                   sorted by score in descending order.
    """
    results = []
    
    # Normalize the query if requested
    norm_query = normalize_string(query) if normalize else query
    query_words = set(norm_query.split())
    
    if not query_words:
        return []
    
    for key, value in targets.items():
        norm_key = normalize_string(key) if normalize else key
        key_words = set(norm_key.split())
        
        if not key_words:
            continue
        
        # Count matching words
        match_count = 0
        for q_word in query_words:
            for k_word in key_words:
                # Check direct containment
                if q_word in k_word or k_word in q_word:
                    match_count += 1
                    break
                    
                # Check similarity
                similarity = difflib.SequenceMatcher(None, q_word, k_word).ratio()
                if similarity > word_similarity_threshold:
                    match_count += 1
                    break
        
        # Calculate match score
        match_score = match_count / len(query_words)
        
        if match_score >= threshold_ratio:
            results.append((key, value, match_score))
    
    # Sort results by score in descending order
    return sorted(results, key=lambda x: x[2], reverse=True)

def normalize_string(text: str) -> str:
    """
    Normalize a string by converting to lowercase and replacing special characters with spaces.

    Args:
        text (str): The string to normalize.

    Returns:
        str: The normalized string.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace common separators with spaces
    text = re.sub(r'[_\-.]', ' ', text)
    
    # Replace other non-alphanumeric characters with spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading and trailing spaces
    return text.strip()

def find_best_match(query: str, 
                   targets: Dict[str, T], 
                   match_type: str = 'auto',
                   threshold: float = 0.7) -> Tuple[Optional[str], Optional[T], Optional[float]]:
    """
    Find the best match for a query in the targets using the specified matching strategy.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.
        match_type (str): The matching strategy to use ('exact', 'pattern', 'fuzzy', 'word', or 'auto').
        threshold (float): The minimum similarity threshold for fuzzy and word matching.

    Returns:
        Tuple[Optional[str], Optional[T], Optional[float]]: A tuple containing the matched key, its value, and the score
                                                          (if applicable), or (None, None, None) if no match found.
    """
    if not query or not targets:
        return None, None, None
    
    # Try exact match first if auto or exact is specified
    if match_type in ('auto', 'exact'):
        exact_result = exact_match(query, targets)
        if exact_result:
            return exact_result[0], exact_result[1], 1.0
    
    # If not found and pattern match is allowed
    if match_type in ('auto', 'pattern'):
        pattern_results = pattern_match(query, targets)
        if pattern_results:
            return pattern_results[0][0], pattern_results[0][1], 0.9
    
    # If still not found and fuzzy match is allowed
    if match_type in ('auto', 'fuzzy'):
        fuzzy_results = fuzzy_match(query, targets, threshold)
        if fuzzy_results:
            return fuzzy_results[0][0], fuzzy_results[0][1], fuzzy_results[0][2]
    
    # If still not found and word match is allowed
    if match_type in ('auto', 'word'):
        word_results = word_match(query, targets, threshold_ratio=threshold)
        if word_results:
            return word_results[0][0], word_results[0][1], word_results[0][2]
    
    # No match found
    return None, None, None

def find_all_matches(query: str, 
                    targets: Dict[str, T], 
                    match_types: List[str] = None,
                    threshold: float = 0.7,
                    max_results: int = None) -> List[Tuple[str, T, float, str]]:
    """
    Find all matches for a query in the targets using multiple matching strategies.

    Args:
        query (str): The query string to match.
        targets (Dict[str, T]): Dictionary where keys are strings to match against and values are the associated data.
        match_types (List[str]): List of matching strategies to use. Defaults to ['exact', 'pattern', 'fuzzy', 'word'].
        threshold (float): The minimum similarity threshold for fuzzy and word matching.
        max_results (int): Maximum number of results to return. If None, return all matches.

    Returns:
        List[Tuple[str, T, float, str]]: List of tuples containing matched keys, their values, scores, and match types,
                                       sorted by score in descending order.
    """
    if not query or not targets:
        return []
    
    if match_types is None:
        match_types = ['exact', 'pattern', 'fuzzy', 'word']
    
    results = []
    
    # Collect results from all specified match types
    for match_type in match_types:
        if match_type == 'exact':
            exact_result = exact_match(query, targets)
            if exact_result:
                results.append((exact_result[0], exact_result[1], 1.0, 'exact'))
        
        elif match_type == 'pattern':
            pattern_results = pattern_match(query, targets)
            for key, value in pattern_results:
                results.append((key, value, 0.9, 'pattern'))
        
        elif match_type == 'fuzzy':
            fuzzy_results = fuzzy_match(query, targets, threshold)
            for key, value, score in fuzzy_results:
                results.append((key, value, score, 'fuzzy'))
        
        elif match_type == 'word':
            word_results = word_match(query, targets, threshold_ratio=threshold)
            for key, value, score in word_results:
                results.append((key, value, score, 'word'))
    
    # Sort results by score in descending order
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    
    # Remove duplicates (keep the first occurrence, which will be the one with the highest score)
    unique_results = []
    seen_keys = set()
    for result in sorted_results:
        if result[0] not in seen_keys:
            unique_results.append(result)
            seen_keys.add(result[0])
    
    # Limit results if max_results is specified
    if max_results is not None:
        return unique_results[:max_results]
    return unique_results
