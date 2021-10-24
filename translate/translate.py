from translate.subtitles_translator import SubtitlesTranslatorMicrosoft
from translate.exceptions import translator_exceptions
from translate import srt_parser


class Translator:
    def __init__(self, api_key, srt_file):
        self.api_key = api_key
        self.subtitles_parser = srt_parser.SrtParser(srt_file)

    def translate_all(self, dest_lang, out_file):
        try:
            s_t = SubtitlesTranslatorMicrosoft(self.api_key, dest_lang=dest_lang)
        except translator_exceptions.LangDoesNotExists as e:
            print(e.message)
        else:
            try:
                for line in self.subtitles_parser.entire_subtitles(s_t.translate):
                    with open(out_file, 'a+', encoding='utf-8') as f:
                        f.write(line)
            except translator_exceptions.InvalidApiKey as e:
                print(e.message)
            else:
                return 'Translated'
