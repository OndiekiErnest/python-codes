# process mic input, audio/video input to text
__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"

# pip install vosk
# pip install SpeechRecognition

from speech_recognition import Recognizer, AudioFile
# uses FFMPEG
from pydub import AudioSegment
import os


class STT():
    """ run about 50 minutes of file duration in a day
        Google's speech API blocks after 50 API calls
    """

    def __init__(self):
        # set constants
        self.chunksize = 60000
        # instantiate the online recognizer
        self.recognizer = Recognizer()

    def fTT(self, path: str, output=0):
        """ input a file whose speech will be converted to text
            the file gets chunked into 60s portions
            to fit inside Google's limits
            output: destination to store the text file
        """
        # use ffmpeg to convert to wav file
        file = AudioSegment.from_file(path)
        filename = "onlinetest.wav"

        # ------split into 60s chunks----------
        def split(source, chunksize):
            for i in range(0, len(source), chunksize):
                yield source[i:i + chunksize]
        # ----------------end nested------------------
        chunks = tuple(split(file, self.chunksize))
        print("[Chunks] :", len(chunks))
        result = []
        for chunk in chunks:
            # save/overwrite the 60s long chunk to a file
            chunk.export(filename, format="wav")

            with AudioFile(filename) as source:
                audio = self.recognizer.record(source)
                # create the ambient noise energy level
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
                print("[Done]")
            # make Google API calls
            try:
                text = self.recognizer.recognize_google(audio)
                print("[Text] :", text)
                # add to overall result
                result.append(text)
            except Exception as e:
                print("[Error] :", e)
        # delete test wav file
        os.remove(filename)
        if output:
            with open("results.txt", "w", encoding="utf-8") as file:
                file.writelines(result)


if __name__ == '__main__':
    stt = STT()
    stt.fTT("test.wav", output=1)
