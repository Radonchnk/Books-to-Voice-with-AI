import torch
from transformers import AutoTokenizer, set_seed
from parler_tts import ParlerTTSForConditionalGeneration
import soundfile as sf
from num2words import num2words
import re
from unidecode import unidecode


class Model:
    def __init__(self, modelName, device, description):
        # set the device
        self.device = torch.device(device)
        # load the model and tokeniser
        self.model = ParlerTTSForConditionalGeneration.from_pretrained(modelName).to(self.device)
        self.tokeniser = AutoTokenizer.from_pretrained(modelName, use_fast=False)
        self.description = description

    def textToSpeech(self, text):
        # load and process input's
        inputIDs = self.tokeniser(self.description, return_tensors="pt").input_ids.to(self.device)
        promptInputIDs = self.tokeniser(text, return_tensors="pt").input_ids.to(self.device)
        set_seed(42)
        # generate the audio and store it in an audio array
        generation = self.model.generate(input_ids=inputIDs, prompt_input_ids=promptInputIDs, max_length=2580)
        audioArr = generation.cpu().numpy().squeeze()
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

    def textToMP3(self, text, outputFile):
        text = tts.replaceNumbersWithWords(text)
        text = unidecode(text)
        waveformOutput = self.tts.textToSpeech(text)

        self.tts.saveToFile(waveformOutput, outputFile)

    @classmethod
    def is_gpu_available(cls):
        if torch.cuda.is_available():
            return 1
        return 0


if __name__ == "__main__":
    tts = Model("parler-tts/parler-tts-mini-expresso", "cuda",
                "Jenny speaks at an average pace with an animated delivery in a very confined sounding environment with clear audio quality.")
    waveform = tts.textToSpeech("printed and bound in the united states of america.")
    tts.saveToFile(waveform, "output.wav")
