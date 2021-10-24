import requests


def show_all_languages_translation():
    languages = {}
    url = r'https://api.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation'
    r = requests.get(url).json()
    for key, val in r['translation'].items():
        languages[val['name']] = key
    return languages
