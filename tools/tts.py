from tools.AIModels.ParlerTTS import ParlerTTSModel
# Import other models here


class AiModels:
    def __init__(self, modelName, device, description=""):
        if modelName == "parler-tts/parler-tts-mini-expresso":
            self.model = ParlerTTSModel(modelName, device, description)
        else:
            raise "That model is not found, please try with another model"

    def textToSpeech(self, text):
        return self.model.textToSpeech(text)

    def textToMP3(self, text, output):
        self.model.textToMP3(text, output)

    def saveFile(self, waveform, filename):
        self.model.saveToFile(waveform, filename)
