from melo.api import TTS
import subprocess
import unidic
import gc
import os


class MeloTTS:
    def __init__(self, device, model):
        if model == "myshell-ai/MeloTTS-English-v2":
            self.language = "EN_V2"
            self.speakerID = "EN-US"
        elif model == "myshell-ai/MeloTTS-English-v3":
            self.language = "EN_NEWEST"
            self.speakerID = "EN-Newest"
        else:
            raise IndexError

        if not os.path.exists(unidic.DICDIR):
            subprocess.run(["python", "-m", "unidic", "download"], check=True)
        self.speed = 1
        self.model = TTS(language=self.language, device=device)
        self.speakerIDS = self.model.hps.data.spk2id
        print(self.speakerIDS)

    def textToMP3(self, text, output):
        self.model.tts_to_file(text, self.speakerIDS[self.speakerID], output, speed=self.speed)
        gc.collect()


if __name__ == "__main__":
    tts = MeloTTS(device="cpu", model="myshell-ai/MeloTTS-English-v3")
    tts.textToMP3("Hello world!", output="hello.mp3")
