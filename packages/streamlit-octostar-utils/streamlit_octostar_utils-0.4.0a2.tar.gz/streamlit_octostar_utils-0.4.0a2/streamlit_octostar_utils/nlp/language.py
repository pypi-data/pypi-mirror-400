import re
from typing import Optional

import py3langid as langid

from iso639 import Lang
from iso639.exceptions import InvalidLanguageValue

FLAIR_MODELS = {
    "en": "flair/ner-english-large",
    "es": "flair/ner-spanish-large",
    "de": "flair/ner-german-large",
    "nl": "flair/ner-dutch-large",
    "fr": "flair/ner-multi",
    "it": "flair/ner-multi",
    "pt": "flair/ner-multi",
    "pl": "flair/ner-multi",
    "ru": "flair/ner-multi",
    "sv": "flair/ner-multi",
    "no": "flair/ner-multi",
    "da": "flair/ner-multi",
}

SPACY_MODELS = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
    "nl": "nl_core_news_sm",
    "pl": "pl_core_news_sm",
    "ru": "ru_core_news_sm",
    "sv": "sv_core_news_sm",
    "no": "nb_core_news_sm",
    "da": "da_core_news_sm",
    "fi": "fi_core_news_sm",
    "el": "el_core_news_sm",
    "zh": "zh_core_web_sm",
    "ja": "ja_core_news_sm",
    "ko": "ko_core_news_sm",
    "ar": "ar_core_news_sm",
    "ca": "ca_core_news_sm",
}


def to_name(alpha2: str) -> str:
    if not alpha2:
        raise ValueError("Language code must be a non-empty string.")
    return Lang(alpha2).name


def to_alpha2(language_name: str) -> str:
    if not language_name:
        raise ValueError("Language name must be a non-empty string.")

    name = re.sub(r'\b\w+', lambda m: m.group(0).capitalize(), language_name)
    return Lang(name).pt1


def detect_language(text, min_confidence=None):
    detector = langid.langid.LanguageIdentifier.from_pickled_model(
        langid.langid.MODEL_FILE, norm_probs=True
    )
    detected_lang, confidence = detector.classify(text)
    if min_confidence and confidence < min_confidence:
        return None, confidence
    detected_lang = to_name(detected_lang)
    return detected_lang, confidence


def is_language_available(language: Optional[str], type: str) -> bool:
    if not language:
        return False

    try:
        lang_code = to_alpha2(language)

    except InvalidLanguageValue:
        lang_code = language

    match type:
        case "spacy":
            return SPACY_MODELS.get(lang_code, None) is not None

        case "flair":
            return FLAIR_MODELS.get(lang_code, None) is not None


def load_language_model(language, type):
    from flair.models import SequenceTagger
    from spacy_download import load_spacy

    match type:
        case "spacy":
            if is_language_available(language, "spacy"):
                model_name = SPACY_MODELS.get(to_alpha2(language), SPACY_MODELS["en"])
                return load_spacy(model_name)

            raise Exception(f"SpaCy model for language '{language}' is not available.")

        case "flair":
            if is_language_available(language, "flair"):
                model_name = FLAIR_MODELS.get(language, "flair/ner-multi")
                return SequenceTagger.load(model_name)

            raise Exception(f"Flair model for language '{language}' is not available.")
