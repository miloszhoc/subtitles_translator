import requests
import uuid
from translate.exceptions import translator_exceptions


# translate subtitles using Microsoft Translator
class SubtitlesTranslatorMicrosoft:
    def __init__(self, api_key, dest_lang):
        self._subscriptionKey = api_key
        self.dest_lang = dest_lang

    def _construct_request(self, content):
        text = r"""{}""".format(content)

        url = r'https://api.cognitive.microsofttranslator.com/translate?'
        query_params = 'api-version=3.0&' + 'to={}&'.format(self.dest_lang) + 'textType=plain'
        full_url = url + query_params

        headers = {'Ocp-Apim-Subscription-Key': self._subscriptionKey,
                   'Content-Type': 'application/json',
                   'Content-Length': '1',
                   'X-ClientTraceId': str(uuid.uuid4())}

        body = [{"Text": text}]

        r = requests.post(full_url, headers=headers,
                          json=body)
        if r.status_code == 200:
            return r.json()[0]['translations'][0]['text']
        else:
            raise translator_exceptions.InvalidApiKey

    # returns translated part of subtitles
    def translate(self, content):
        try:
            assert isinstance(content, list)
        except AssertionError:
            print("Error while translation")
            exit()
        else:
            return self._construct_request(' '.join(content))
