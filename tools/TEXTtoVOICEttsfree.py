from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.tts import *
from tools.tiny_tools import *
import shutil
from pydub import AudioSegment
import threading


class TextToVoiceProcessorTTSfree:
    def __init__(self, input_text_name, temp_folder, text_folder, voiced_folder, chunk_size, max_retries, retry_delay,
                 max_simultaneous_threads, language, model_path, description="", attempt_use_gpu=1):
        self.input_text_name = input_text_name
        self.temp_folder = temp_folder
        self.text_folder = text_folder
        self.voiced_folder = voiced_folder
        self.chunk_size = int(chunk_size)
        self.max_retries = int(max_retries)
        self.retry_delay = int(retry_delay)
        self.max_simultaneous_threads = int(max_simultaneous_threads)
        self.language = language
        self.chunks = []
        self.len = 0
        self.time_start = time.time()
        self.tools = ToolsSet()
        self.description = description

        # Create thread management for the CPU and GPU model
        self.lock = threading.Lock()
        self.cpuReady = threading.Event()
        self.gpuReady = threading.Event()
        # Set them to ready
        self.cpuReady.set()
        self.gpuReady.set()

        # Initialise models
        self.cpuTTSModel = Model(model_path, "cpu", self.description)
        self.cpuTTS = TextToSpeach(self.cpuTTSModel)

        # If cuda is available and the user has chosen to use it, use cuda & cpu
        if TextToSpeach.is_gpu_available() and attempt_use_gpu == 1:
            self.gpuTTSModel = Model(model_path, "cuda", self.description)
            self.gpuTTS = TextToSpeach(self.gpuTTSModel)
            self.use_gpu = True
            print("""
               _____          _       
              / ____|        | |      
             | |    _   _  __| | __ _ 
             | |   | | | |/ _` |/ _` |
             | |___| |_| | (_| | (_| |
              \_____\__,_|\__,_|\__,_|""")
        else:
            self.use_gpu = False
            print("GPU not available, using CPU only")

    def _send_tts_request(self, text, idx):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                tts = None
                device = None
                # If the gpu is ready, use the gpu, if the cpu is ready, use that
                with self.lock:
                    if self.use_gpu and self.gpuReady.is_set():
                        self.gpuReady.clear()
                        tts = self.gpuTTS
                        device = "cuda"
                    elif self.cpuReady.is_set():
                        self.cpuReady.clear()
                        tts = self.cpuTTS
                        device = "cpu"

                if tts is None:
                    time.sleep(1)  # Wait a bit before trying again
                    continue

                print(f"Processing chunk {idx}/{self.len} on {device}...")

                output_wav_file = os.path.join(self.temp_folder, f'chunk{idx}.wav')
                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')

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
                        self.gpuReady.set()
                    else:
                        self.cpuReady.set()

                return

            except Exception as e:
                print(f"Error processing chunk {idx} on {device}:\n {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

        # if the amount of retries has reached the max, use ESPEAK
        if retry_count == self.max_retries:
            print("Using ESPEAK to replace unprocessed chunk")
            self.tools.Espeak(self.temp_folder, text, f'chunk{idx}')
            self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

            with self.lock:
                if device == "cuda":
                    self.gpuReady.set()
                else:
                    self.cpuReady.set()

    def process_chunks(self):
        # create temp folder
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        # create final output folder
        if not os.path.exists(self.voiced_folder):
            os.makedirs(self.voiced_folder)

        # open text file and read input
        with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
            input_text = f.read()

        sentences = self.tools.divide_into_sentences(input_text)
        # split it into chunks
        self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
        self.len = len(self.chunks)

        # Use threads to allow multiple chunks to be processed at once
        with ThreadPoolExecutor(max_workers=self.max_simultaneous_threads) as executor:
            futures = [executor.submit(self._send_tts_request, chunk, idx) for idx, chunk in enumerate(self.chunks)]
            for future in as_completed(futures):
                future.result()

        # Merge the audio files together
        self.tools.merge_audio_pairs(self.temp_folder)
        final_output_file = os.path.join(self.voiced_folder, f'{self.input_text_name}.mp3')
        shutil.move(f"{self.temp_folder}/chunk0.mp3", final_output_file)
        os.rmdir(self.temp_folder)

        print("Temporary folder removed.")
        print("Text has been voiced and saved to './voices' directory.")


if __name__ == "__main__":
    processor = TextToVoiceProcessorTTSfree(
        input_text_name="smallText",
        text_folder="texts",
        temp_folder="temp",
        voiced_folder="voices",
        chunk_size=1000,
        max_retries=1000,
        retry_delay=600,
        max_simultaneous_threads=2,
        language="en",
        model_path="parler-tts/parler-tts-mini-espresso",
    )
    processor.process_chunks()
