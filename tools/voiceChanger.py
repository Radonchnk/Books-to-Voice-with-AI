from rvc_python.infer import infer_file
import torch


class VoiceChange:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def changeVoice(self, audioInput, output):
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
            version="v2"
        )
        print(result)
        print("Inference completed. Output saved to:", result)


if __name__ == "__main__":
    VoiceChange().changeVoice("./chunk0.mp3", "./output.mp3")
