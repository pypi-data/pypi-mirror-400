# fonada_asr/languages.py
from typing import Dict, Set

# ----------------------------------------------------------------------
# Master language map (canonical ISO code -> human-readable name)
# ----------------------------------------------------------------------
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "as": "Assamese",
    "bn": "Bengali",
    "brx": "Bodo",
    "doi": "Dogri",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "kok": "Konkani",
    "ks": "Kashmiri",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mni": "Manipuri",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sat": "Santali",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
}

# ----------------------------------------------------------------------
# Synonyms / aliases (for robust user input)
# ----------------------------------------------------------------------
SYNONYMS: Dict[str, str] = {
    name.lower(): code for code, name in SUPPORTED_LANGUAGES.items()
}
# Add a few explicit alternate spellings
SYNONYMS.update({
    "oriya": "or",
    "odia (oriya)": "or",
    "assamese": "as",
})

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def supported_codes() -> Set[str]:
    """Return set of all supported language codes."""
    return set(SUPPORTED_LANGUAGES.keys())

def supported_languages() -> Dict[str, str]:
    """Return dict of code -> language name."""
    return SUPPORTED_LANGUAGES.copy()

def normalize_language(lang: str) -> str:
    """
    Normalize a language input to canonical ISO code.
    Accepts 'hi', 'Hindi', 'HINDI', etc. → 'hi'.
    """
    if not lang:
        return "hi"
    candidate = lang.strip().lower()
    # Already a known ISO code
    if candidate in SUPPORTED_LANGUAGES:
        return candidate
    # Match via synonyms (case-insensitive)
    return SYNONYMS.get(candidate, candidate)

def is_supported_language(lang: str) -> bool:
    """Check if the provided language (code or name) is supported."""
    if not lang:
        return False
    return normalize_language(lang) in SUPPORTED_LANGUAGES

def validate_language(lang_code: str) -> str:
    """
    Validate that a given code or name corresponds to a supported language.
    Raises ValueError if not supported.
    """
    normalized = normalize_language(lang_code)
    if normalized not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
        raise ValueError(
            f"Unsupported language '{lang_code}'. Supported codes: {supported}"
        )
    return normalized
