import re

import chardet


class SrtParser:
    # To learn more about .srt files visit: https://en.wikipedia.org/wiki/SubRip

    def __init__(self, file):
        self._file = file

    def detect_encoding(self):
        with open(self._file, 'rb') as f:
            return chardet.detect(f.read())['encoding']

    # generator which reads srt file line by line
    def read_srt_file(self):
        try:
            encoding = self.detect_encoding()
            with open(self._file, 'r', encoding=encoding) as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            print('File does not exist.\nCheck your path or file name.')
            exit()

    def entire_subtitles(self, func):
        file_line = self.read_srt_file()
        text = []
        try:
            line = next(file_line)  # reads first line in file
            while True:  # runs until EOF
                while line != '\n':  # reads one group in file (until \n occurs)
                    if re.search('[^\W\d_]', line, flags=re.U):
                        text.append(line.rstrip('\n'))
                    else:
                        yield line
                    line = next(file_line)  # updating lines
                if len(text) > 0:
                    translated_line = func(text)
                    yield translated_line + '\n'  # write translated line to file
                yield '\n'  # empty line between groups
                text = []
                line = next(file_line)  # reads line in next group
        except StopIteration:
            translated_line = func(text)
            yield translated_line
