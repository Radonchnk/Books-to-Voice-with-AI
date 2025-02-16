import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.tts import AiModels
from tools.tiny_tools import *
from tools.fileMerging import FileMerger
import shutil
from pydub import AudioSegment
import threading
import torch


class TextToVoiceProcessorSelfHosted:
    def __init__(self, input_text_name="", temp_folder="", text_folder="", voiced_folder="", chunk_size="", max_retries="", retry_delay="", language="", model_path="", description="", attempt_use_gpu=1, continue_generation = 0, not_generated = "", settings = ""):
        gc.enable()
        self.input_text_name = input_text_name
        self.temp_folder = temp_folder
        self.text_folder = text_folder
        self.voiced_folder = voiced_folder
        self.chunk_size = int(chunk_size)
        self.max_retries = int(max_retries)
        self.retry_delay = int(retry_delay)
        self.language = language
        self.chunks = []
        self.len = 0
        self.time_start = time.time()
        self.tools = ToolsSet()
        self.description = description

        # Allows to use CPU+GPU
        self.lock = threading.Lock()
        self.cpu_ready = threading.Event()
        self.gpu_ready = threading.Event()
        self.cpu_ready.set()
        self.gpu_ready.set()

        # For continuing generaion
        self.continue_generation = continue_generation
        self.not_generated = not_generated
        self.settings = settings

        # Initialise models
        self.cpuTTS = AiModels(model_path, "cpu", self.description)

        if torch.cuda.is_available() and int(attempt_use_gpu):
            self.gpuTTS = AiModels(model_path, "cuda", self.description)
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
            print("GPU not available, using CPU only")

    def _send_tts_request(self, idx):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                tts = None
                device = None

                with self.lock:
                    if self.useGPU and self.gpu_ready.is_set():
                        self.gpu_ready.clear()
                        tts = self.gpuTTS
                        device = "cuda"
                    elif self.cpu_ready.is_set():
                        self.cpu_ready.clear()
                        tts = self.cpuTTS
                        device = "cpu"

                if tts is None:
                    time.sleep(1)  # Wait a bit before trying again
                    continue

                print(f"Processing chunk {idx + 1}/{self.len} on {device}...")

                text_file = os.path.join(self.temp_folder, f"chunk{idx}.txt")
                output_wav_file = os.path.join(self.temp_folder, f'chunk{idx}.wav')
                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')

                # Read text which is going to be voiced
                with open(file=text_file, encoding="utf-8") as f:
                    text = f.readlines()
                    text = " ".join(text)

                print(f"Text of the processed chunk:\n{text}")
                # Call model and process text
                tts.textToMP3(text, output_wav_file)

                chunk_audio = AudioSegment.from_wav(output_wav_file)
                chunk_audio.export(output_mp3_file, format='mp3')

                # Check if AI succeeded to generate the output
                if not os.path.exists(output_wav_file):
                    raise f"Could not generate WAV file for the chunk {idx}"

                os.remove(output_wav_file)

                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

                with self.lock:
                    if device == "cuda":
                        self.gpu_ready.set()
                    else:
                        self.cpu_ready.set()
                gc.collect()
                return

            except Exception as e:
                print(f"Error processing chunk {idx} on {device}:\n {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)
                gc.collect()
                with self.lock:
                    if device == "cuda":
                        self.gpu_ready.set()
                    else:
                        self.cpu_ready.set()
                gc.collect()

        if retry_count == self.max_retries:
            print("Using ESPEAK to replace unprocessed chunk")
            self.tools.Espeak(self.temp_folder, text, f'chunk{idx}')
            self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

            with self.lock:
                if device == "cuda":
                    self.gpu_ready.set()
                else:
                    self.cpu_ready.set()
            gc.collect()
    def process_chunks(self):
        if not self.continue_generation:
            # Create temp folder
            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

            # Create output folder
            if not os.path.exists(self.voiced_folder):
                os.makedirs(self.voiced_folder)


            with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
                input_text = f.read()

            sentences = self.tools.divide_into_sentences(input_text)
            self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
            self.len = len(self.chunks)

            # Creating the metadata file
            self.tools.create_metadata_file(folder_path=self.temp_folder, generation_method="Self Hosted TTS",
                                            total_chunks=self.len, settings=self.settings)

            self.tools.create_text_chunks(text_array=self.chunks, folder_path=self.temp_folder)

            for chunk_id in range(self.len):
                self._send_tts_request(idx=chunk_id)
        else:

            with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
                input_text = f.read()

            sentences = self.tools.divide_into_sentences(input_text)
            self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
            self.len = len(self.chunks)

            for chunk_id in self.not_generated:
                self._send_tts_request(chunk_id)

        # Clear up data from metadata and text before merge
        self.tools.clear_metadata_and_texts(folder_path=self.temp_folder, total_chunks=self.len)
        start = time.time()
        output_file = self.voiced_folder + "/" + self.input_text_name + ".mp3"
        fileMerger = FileMerger(input_folder=self.temp_folder, output_file=output_file)
        fileMerger.execute()
        end = time.time()
        shutil.rmtree(self.temp_folder)
        print("Temporary folder removed.")
        print("Text has been voiced and saved to 'voices' directory.")
        print(f"Time taken to merge files {end-start}")


if __name__ == "__main__":
    processor = TextToVoiceProcessorSelfHosted(
        input_text_name="smallText",
        text_folder="texts",
        temp_folder="temp",
        voiced_folder="voices",
        chunk_size=1000,
        max_retries=1000,
        retry_delay=600,
        language="en",
        model_path="parler-tts/parler-tts-mini-espresso",
    )
    processor.process_chunks()
