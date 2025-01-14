from tools.AIModels.ParlerTTS import ParlerTTSModel
from tools.AIModels.MeloTTS import MeloTTS
# Import other models here


class AiModels:
    def __init__(self, modelName, device, description=""):
        if modelName == "parler-tts/parler-tts-mini-expresso":
            self.model = ParlerTTSModel(modelName, device, description)
        elif modelName == "myshell-ai/MeloTTS-English-v2":
            self.model = MeloTTS(device, modelName)
        elif modelName == "myshell-ai/MeloTTS-English-v3":
            self.model = MeloTTS(device, modelName)
        else:
            print("That model is not found, please try with another model")
            raise "That model is not found, please try with another model"
        print(f"Using {modelName}")

    def textToMP3(self, text, output):
        self.model.textToMP3(text, output)
