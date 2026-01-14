try:
    import py3langid
    import iso639
    import spacy_download
    import spacy
    import flair
    import sumy
    import nltk
    import presidio_analyzer
except ImportError as e:
    raise ImportError(
        "The 'nlp' module requires additional dependencies. Please install them using:\n"
        "    pip install streamlit-octostar-utils[nlp]"
    )