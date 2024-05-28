import torch
from transformers import AutoTokenizer, set_seed
from parler_tts import ParlerTTSForConditionalGeneration
import soundfile as sf
from num2words import num2words
import re

class Model:
    def __init__(self, modelName):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ParlerTTSForConditionalGeneration.from_pretrained(modelName).to(self.device)
        self.tokeniser = AutoTokenizer.from_pretrained(modelName)

    def textToSpeech(self, text, description, run=0):
        inputIDs = self.tokeniser(description, return_tensors="pt").input_ids.to(self.device)
        promptInputIDs = self.tokeniser(text, return_tensors="pt").input_ids.to(self.device)
        set_seed(42)
        generation = self.model.generate(input_ids=inputIDs, prompt_input_ids=promptInputIDs)
        audioArr = generation.cpu().numpy().squeeze()
        if str(audioArr) == "0.0" and run != 2:
            run +=1
            return self.textToSpeech(text, description, run=run)
        return audioArr

    def saveToFile(self, waveform, fileName):
        if len(waveform.shape) == 1:
            waveform = waveform.reshape(-1, 1)
        try:
            sf.write(fileName, waveform, samplerate=self.model.config.sampling_rate)
            print(f"\nSpeech has been saved to {fileName}\n")
        except IndexError:
            print(f"\n\n\nFailed to save to {fileName}, perhaps there was no speech? Tries attempted 2\n\n\n")

    def replaceNumbersWithWords(self, text):
        numberPattern = re.compile(r'\b\d+\b')
        def numberToWords(match):
            number = int(match.group())
            return num2words(number)

        result = numberPattern.sub(numberToWords, text)
        return result


class TextToSpeach:
    def __init__(self, model_name):

        self.tts = Model(model_name)

    def textToMP3(self, text, ouput_file):
        if torch.cuda.is_available():
            print("""
          _____          _       
         / ____|        | |      
        | |    _   _  __| | __ _ 
        | |   | | | |/ _` |/ _` |
        | |___| |_| | (_| | (_| |
         \_____\__,_|\__,_|\__,_|""")

        description = "Jenny speaks at an average pace with an animated delivery in a very confined sounding environment with clear audio quality."

        waveform = self.tts.textToSpeech(text, description)

        self.tts.saveToFile(waveform, ouput_file)

if __name__ == "__main__":
    tts = TextToSpeach("/home/rad/PycharmProjects/PDFtoVOICE/venv/lib/python3.10/site-packages/TTS/.models.json",
                       "tts_models/en/ljspeech/tacotron2-DDC")
    tts.textToMP3("i love apples", "../voices/output.mp3")