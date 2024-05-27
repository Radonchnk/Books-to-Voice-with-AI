from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

class TextToSpeach:
    def __init__(self, path, model_name):
        self.path = path
        self.model_name = model_name

        self.model_manager = ModelManager(self.path)

        self.model_path, self.config_path, self.model_item = self.model_manager.download_model(model_name)

        self.voc_path, self.voc_config_path, _ = self.model_manager.download_model(self.model_item["default_vocoder"])

        self.syn = Synthesizer(
            tts_checkpoint=self.model_path,
            tts_config_path=self.config_path,
            vocoder_checkpoint=self.voc_path,
            vocoder_config=self.voc_config_path
        )
    def textToMP3(self, text, ouput_file):
        ouputs = self.syn.tts(text)
        self.syn.save_wav(ouputs, ouput_file)

if __name__ == "__main__":
    tts = TextToSpeach("/home/rad/PycharmProjects/PDFtoVOICE/venv/lib/python3.10/site-packages/TTS/.models.json",
                       "tts_models/en/ljspeech/tacotron2-DDC")
    tts.textToMP3("i love apples", "../voices/output.mp3")