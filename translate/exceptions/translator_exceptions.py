class TranslatorExceptions(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class LangDoesNotExists(TranslatorExceptions):
    def __init__(self):
        super().__init__(
            'Requested language does not exists\nTry to run \'lang\' command to be familiar with supported languages')


class EnglishNotFound(TranslatorExceptions):
    def __init__(self):
        super().__init__('Either source language or destination language has to be English')


class InvalidApiKey(TranslatorExceptions):
    def __init__(self):
        super().__init__('Make sure that your API Key is valid')
