from tools.RVCPython.downloadModel import downloadRVCModels
from tools.RVCPython.modules.vc.modules import VC
from tools.RVCPython.configs.config import Config
from pydub import AudioSegment
import os, gc

class Infer:
    def __init__(self,
                 modelPath,
                 index_path="",
                 device="cpu:0",
                 f0method="harvest",
                 index_rate=0.5,
                 filter_radius=3,
                 resample_sr=0.001,
                 rms_mix_rate=1,
                 protect=0.33,
                 f0up_key=0,
                 version="v2"):
        self.index_path = index_path
        self.device = device
        self.f0method = f0method
        self.index_rate = index_rate
        self.filter_radius = filter_radius
        self.resample_sr = resample_sr
        self.rms_mix_rate = rms_mix_rate
        self.protect = protect
        self.f0up_key = f0up_key
        self.version = version
        self.frameRate = 0

        self.libDir = os.path.dirname(os.path.abspath(__file__))
        downloadRVCModels(self.libDir)
        self.config = Config(self.libDir, self.device)
        print(f"Loading model on {device}")
        self.vc = VC(self.libDir, self.config)

        self.vc.get_vc(modelPath, version)

    def changeVoiceAndStoreAudioArray(self, inputAudio):
        frameRate = inputAudio.frame_rate
        self.frameRate = frameRate
        audioArr = self.vc.vc_single(
            sid=1,
            input_audio=inputAudio,
            f0_up_key=self.f0up_key,
            f0_method=self.f0method,
            file_index=self.index_path,
            index_rate=self.index_rate,
            filter_radius=self.filter_radius,
            resample_sr=self.resample_sr,
            rms_mix_rate=self.rms_mix_rate,
            protect=self.protect,
            f0_file="",
            file_index2="",

        )
        print(audioArr)
        gc.collect()
        return audioArr

    def saveAudioSegment(self, audioSegment, outputFile="./output.mp3"):
        audioSegment.export(outputFile, format="mp3")


if __name__ == '__main__':
    model = Infer("./model.pth", device="cpu")
    audio = AudioSegment.from_mp3('./chunk0.mp3')
    converted = model.changeVoiceAndStoreAudioArray(audio)
    model.saveAudioSegment(converted)
