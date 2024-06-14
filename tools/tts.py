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
        self.tokeniser = AutoTokenizer.from_pretrained(modelName, use_fast=False)

    def textToSpeech(self, text, description, run=0):
        inputIDs = self.tokeniser(description, return_tensors="pt").input_ids.to(self.device)
        promptInputIDs = self.tokeniser(text, return_tensors="pt").input_ids.to(self.device)
        set_seed(42)
        generation = self.model.generate(input_ids=inputIDs, prompt_input_ids=promptInputIDs, max_length=2580)
        audioArr = generation.cpu().numpy().squeeze()
        if str(audioArr) == "0.0" and run != 2:
            run += 1
            return self.textToSpeech(text, description, run=run)
        return audioArr

    def saveToFile(self, waveform, fileName):
        if len(waveform.shape) == 1:
            waveform = waveform.reshape(-1, 1)
        try:
            sf.write(fileName, waveform, samplerate=self.model.config.sampling_rate)
            # saves WAV file to output path
        except IndexError:
            raise IndexError
            # if error is there

    def replaceNumbersWithWords(self, text):
        numberPattern = re.compile(r'\b\d+\b')

        def numberToWords(match):
            number = int(match.group())
            return num2words(number)

        result = numberPattern.sub(numberToWords, text)
        return result


class TextToSpeach:
    def __init__(self, model):
        self.tts = model
        # self.tts = Model(model_name)

    def textToMP3(self, text, outputFile, description):
        if torch.cuda.is_available():
            print("""CUDA IS USED""")

        description = "Jenny speaks at an average pace with an animated delivery in a very confined sounding environment with clear audio quality."

        waveformOutput = self.tts.textToSpeech(text, description)

        self.tts.saveToFile(waveformOutput, outputFile)


if __name__ == "__main__":
    tts = Model("parler-tts/parler-tts-mini-expresso")
    waveform = tts.textToSpeech("printed and bound in the united states of america.", "Jenny speaks at \
    an average pace with an animated delivery in a very confined sounding environment with clear audio quality.")
    tts.saveToFile(waveform, "output.wav")
