


def predict_language(text: str, k = 10, threshold = 0.01) -> list[dict[str, float]]:
    """
    Predict the language of the given text using langdetect library. Mapping to list of dicts

    :param text: The text to predict the language for.
    :return: {'predictions': [{'lang': 'es', 'confidence': 0.8267212}, {'lang': 'pl', 'confidence': 0.034933474}, {'lang': 'eo', 'confidence': 0.029082965}, {'lang': 'fr', 'confidence': 0.02504085}, {'lang': 'ca', 'confidence': 0.0125150o', 'confidence': 0.029082965}, {'lan11}]}
    """
    from langdetect import DetectorFactory, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = 0  # For consistent results
    try:
        detected_langs = detect_langs(text)
        # The langdetect library does not provide confidence scores directly.
        # Here we return a dummy confidence score for the detected language.
        return [{'lang': lang.lang, 'confidence': lang.prob} for lang in detected_langs]
    except LangDetectException:
        return []
    except Exception as e:
        raise e
    

    