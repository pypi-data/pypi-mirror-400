from .matching import match_strings_with_dom_content
from .matching import normalize_spacing
from .matching import rank_match
from .matching import remove_punctuation_and_spaces
from .matching import replace_with_best_matches
from .matching import select_best_match

__all__ = [
    "rank_match",
    "select_best_match",
    "match_strings_with_dom_content",
    "replace_with_best_matches",
    "remove_punctuation_and_spaces",
    "normalize_spacing",
]
