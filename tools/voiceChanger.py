import torch
from pydub import AudioSegment
from rvc_python.infer import infer_file


class VoiceChange:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def changeVoice(self, audioInput, output):
        self.convToWav(audioInput)
        audioInput = audioInput.replace(".mp3",".wav")
        output = output.replace(".mp3",".wav")
        result = infer_file(
            input_path=audioInput,
            model_path="./model.pth",
            index_path="",
            device=self.device,
            f0method="harvest",
            f0up_key=0,
            opt_path=output,
            index_rate=0.5,
            filter_radius=3,
            resample_sr=0,
            rms_mix_rate=0.25,
            protect=0.33,
            version="v2",
        )
        self.convToMp3(output)
        print("Inference completed. Output saved to:", result)

    def convToWav(self, file):
        audioSegment = AudioSegment.from_mp3(file)
        self.file = file
        print("converting to wav")
        audioSegment.export(file.replace(".mp3",".wav"), format="wav")

    def convToMp3(self, file):
        file = file.replace(".mp3",".wav")
        audioSegment = AudioSegment.from_wav(file)
        print("converting back to mp3")
        audioSegment.export(file.replace(".wav",".mp3"), format="mp3")
        print(file)


if __name__ == "__main__":
    # VoiceChange().convToMp3("./chunk0.wav")
    VoiceChange().changeVoice("./chunk0.mp3", "./output.mp3")
