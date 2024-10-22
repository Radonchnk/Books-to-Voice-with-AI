# from tools.RVCPython.infer import Infer
from concurrent.futures import ThreadPoolExecutor, as_completed

from triton.language.extra.cuda import num_threads

from tools.fileMerging import FileMerger
from tools.tiny_tools import *
import shutil
import threading
import torch


class TextToVoiceProcessor:
    def __init__(self, input_text_name, temp_folder, text_folder, voiced_folder, chunk_size, max_retries, retry_delay,
                 max_simultaneous_threads, use_gpu, continue_generation=0, not_generated="", settings=""):
        self.input_text_name = input_text_name
        self.temp_folder = temp_folder
        self.text_folder = text_folder
        self.voiced_folder = voiced_folder
        self.chunk_size = int(chunk_size)
        self.max_retries = int(max_retries)
        self.retry_delay = int(retry_delay)
        self.max_simultaneous_threads = int(max_simultaneous_threads)
        self.chunks = []
        self.tools = ToolsSet()
        self.len = 0
        self.time_start = time.time()


        # For continuing generation
        self.continue_generation = continue_generation
        self.not_generated = not_generated
        self.settings = settings

        # Allows to use CPU+GPU
        self.lock = threading.Lock()
        self.cpu_ready = threading.Event()
        self.gpu_ready = threading.Event()
        self.cpu_ready.set()
        self.gpu_ready.set()

        # Initialise models
        # self.CPU_voice_changer = Infer("./model.pth", device="cpu")

        if torch.cuda.is_available() and int(use_gpu):
            # self.GPU_voice_changer = Infer("./model.pth", device="cuda")
            # self.voiceChangingModel = Infer('./model.pth', device="cuda")
            self.useGPU = True
            print("""
                       _____          _       
                      / ____|        | |      
                     | |    _   _  __| | __ _ 
                     | |   | | | |/ _` |/ _` |
                     | |___| |_| | (_| | (_| |
                      \_____\__,_|\__,_|\__,_|""")
        else:
            self.useGPU = False
            # self.voiceChangingModel = Infer('./model.pth', device="cpu")
            print("GPU not available, using CPU only")
            print("""
              ____ ___  _   _ 
             / ___|    \ | | | 
            | |   | |> | | | | 
            | |_  |___/| |_| | 
             \____| |   \___/ """)

    def _send_tts_request(self, idx):

        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # This piece of code related to usafe of GPU+CPU

                # in this vatiable cpu or gpu vatiation of a model loaded
                voice_chainger_model = None
                # This variable is passed down to the voice clear 1 - gpu used, 0 - cpu used
                device = None

                with self.lock:
                    if self.useGPU and self.gpu_ready.is_set():
                        self.gpu_ready.clear()
                        # voice_chainger_model = self.GPU_voice_changer
                        device = "cuda"
                    elif self.cpu_ready.is_set():
                        self.cpu_ready.clear()
                        # voice_chainger_model = self.CPU_voice_changer
                        device = "cpu"

                if voice_chainger_model is None:
                    time.sleep(1)  # Wait a bit before trying again
                    continue

                print(f"Processing chunk {idx}... On {device}")

                # Get text file name fom the file
                text_file = os.path.join(self.temp_folder, f"chunk{idx}.txt")
                # Read text which is going to be voiced
                with open(file=text_file, encoding="utf-8") as f:
                    text = f.readlines()
                    text = " ".join(text)

                # self.tools.Espeak(self.temp_folder, text, f'chunk_before_convert{idx}')
                audioData = self.tools.EspeakOutputWithAudioArray(text)

                # calling specific voice clearer based on device
                # audioData = self.voiceChangingModel.changeVoiceAndStoreAudioArray(audioData)
                # self.voiceChangingModel.saveAudioSegment(audioData, os.path.join(self.temp_folder, f"chunk{idx}.mp3"))
                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

                print(f"Chunk {idx} processed successfully.")

                # says if GPU/CPU is ready
                with self.lock:
                    if device == "cuda":
                        self.gpu_ready.set()
                    else:
                        self.cpu_ready.set()

                return
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

                # says if GPU/CPU is ready
                with self.lock:
                    if device == "cuda":
                        self.gpu_ready.set()
                    else:
                        self.cpu_ready.set()


    def process_chunks(self):
        # TODO - Comment eSpeak
        if not self.continue_generation:

            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

            if not os.path.exists(self.voiced_folder):
                os.makedirs(self.voiced_folder)

            with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
                input_text = f.read()

            sentences = self.tools.divide_into_sentences(input_text)
            self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
            self.len = len(self.chunks)

            # Creating the metadata file
            self.tools.create_metadata_file(folder_path=self.temp_folder, generation_method="Espeak TTS",
                                            total_chunks=self.len, settings=self.settings)

            # Creates chunks of text which are voiced
            self.tools.create_text_chunks(text_array=self.chunks, folder_path=self.temp_folder)

            with ThreadPoolExecutor(max_workers=self.max_simultaneous_threads) as executor:
                futures = [executor.submit(self._send_tts_request, idx) for idx in range(self.len)]
                for future in as_completed(futures):
                    future.result()

        else:

            with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
                input_text = f.read()

            sentences = self.tools.divide_into_sentences(input_text)
            self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
            self.len = len(self.chunks)

            with ThreadPoolExecutor(max_workers=self.max_simultaneous_threads) as executor:
                futures = [executor.submit(self._send_tts_request, idx) for idx in self.not_generated]
                for future in as_completed(futures):
                    future.result()

        for file in os.listdir(self.temp_folder):
            if "before_convert" in file or ".wav" in file:
                os.remove(os.path.join(self.temp_folder, file))

        # Clear up data from metadata and text before merge
        self.tools.clear_metadata_and_texts(folder_path=self.temp_folder, total_chunks=self.len)

        start = time.time()
        fileMerger = FileMerger(self.temp_folder, self.input_text_name, self.max_simultaneous_threads)
        audio = fileMerger.mergeManager()
        fileMerger.saveFile(audio)
        end = time.time()
        shutil.rmtree(self.voiced_folder)
        print("Temporary folder removed.")
        print("Text has been voiced and saved to 'voices' directory.")
        print(f"Time taken to merge files {end - start}")


if __name__ == "__main__":
    processor = TextToVoiceProcessor(
        input_text_name="alphabet",
        text_folder="texts",
        temp_folder="temp",
        voiced_folder="voices",
        chunk_size=10,
        max_retries=1000,
        retry_delay=600,
        max_simultaneous_threads=4
    )
    processor.process_chunks()
