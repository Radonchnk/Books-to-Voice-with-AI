from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.tiny_tools import *
import shutil
from tools import voiceChanger
import threading


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

        self.voice_changer = voiceChanger.VoiceChange(use_gpu=use_gpu)

        # Initialise models
        self.CPU_voice_changer = voiceChanger.VoiceChange(use_gpu=0) # use cpu

        if voiceChanger.VoiceChange.is_gpu_available() and int(use_gpu):
            self.GPU_voice_changer =  voiceChanger.VoiceChange(use_gpu=1) # use gpu
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
                        voice_chainger_model = self.GPU_voice_changer
                        device = "cuda"
                    elif self.cpu_ready.is_set():
                        self.cpu_ready.clear()
                        voice_chainger_model = self.CPU_voice_changer
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

                self.tools.Espeak(self.temp_folder, text, f'chunk_before_convert{idx}')

                # calling specific voice clearer based on device
                voice_chainger_model.changeVoice(f"{self.temp_folder}/chunk_before_convert{idx}.mp3", f"{self.temp_folder}/chunk{idx}.mp3")
                os.remove(f'{self.temp_folder}/chunk_before_convert{idx}.mp3')

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

        self.tools.merge_audio_pairs(self.temp_folder)

        final_output_file = os.path.join(self.voiced_folder, f'{self.input_text_name}.mp3')

        shutil.move(f"{self.temp_folder}/chunk0.mp3", final_output_file)

        os.rmdir(self.temp_folder)

        print("Temporary folder removed.")
        print("Text has been voiced and saved to 'voices' directory.")


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
