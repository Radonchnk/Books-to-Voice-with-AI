import gc
import torch
from pydub import AudioSegment
from rvc_python.infer import infer_file


class VoiceChange:
    def __init__(self, use_gpu):
        use_gpu = int(use_gpu)
        if torch.cuda.is_available() and use_gpu:
            self.device = "cuda"
            print("""
               _____          _       
              / ____|        | |      
             | |    _   _  __| | __ _ 
             | |   | | | |/ _` |/ _` |
             | |___| |_| | (_| | (_| |
              \_____\__,_|\__,_|\__,_|""")
        else:
            self.device = "cpu"
            print("CPU is used")
        print(f"Voice changer is loaded on {'cuda' if torch.cuda.is_available() and use_gpu else 'cpu'}")

    def changeVoice(self, audioInput, output):
        try:
            print("Inference STARTED. From:", audioInput)
            self.convToWav(audioInput)
            audioInput = audioInput.replace(".mp3",".wav")
            output = output.replace(".mp3",".wav")
            # Calling the model to change
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
            gc.collect()
        except Exception as e:
            print(e)

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

    @classmethod
    def is_gpu_available(cls):
        if torch.cuda.is_available():
            return True
        else:
            return False


if __name__ == "__main__":
    # VoiceChange().convToMp3("./chunk0.wav")
    VoiceChange().changeVoice("./chunk0.mp3", "./output.mp3")
