from melo.api import TTS
import gc


class MeloTTS:
    def __init__(self, device):
        self.speed = 1
        self.model = TTS(language="EN_V2", device=device)
        self.speakerIDS = self.model.hps.data.spk2id

    def textToMP3(self, text, output):
        self.model.tts_to_file(text, self.speakerIDS["EN-US"], output, speed=self.speed)
        gc.collect()


if __name__ == "__main__":
    tts = MeloTTS(device="cpu")
    tts.textToMP3("Hello world!", output="hello.mp3")