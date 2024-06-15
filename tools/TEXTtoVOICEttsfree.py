import os
import time
from concurrent.futures import ThreadPoolExecutor
from tools.tts import *
from tools.tiny_tools import *
import shutil
from pydub import AudioSegment


class TextToVoiceProcessorTTSfree:
    def __init__(self, input_text_name, temp_folder, text_folder, voiced_folder, chunk_size, max_retries, retry_delay,
                 attempt_use_gpu, max_simultaneous_threads, language, model_path, description=""):
        self.input_text_name = input_text_name
        self.temp_folder = temp_folder #+ str()
        self.text_folder = text_folder
        self.voiced_folder = voiced_folder
        self.chunk_size = int(chunk_size)
        self.max_retries = int(max_retries)
        self.retry_delay = int(retry_delay)

        self.attempt_use_gpu = int(attempt_use_gpu)
        self.max_simultaneous_threads = int(max_simultaneous_threads)

        self.language = language
        self.chunks = []
        self.len = 0
        self.time_start = time.time()
        self.tools = tools_set()
        self.description = description

        # Process available devices

        if self.attempt_use_gpu and TextToSpeach.is_gpu_available():
            # If GPU is there and USE_GPU load model using gpu
            self.GPUttsModel = Model(model_path, "cuda", self.description)
            self.tts = TextToSpeach(self.GPUttsModel)
            print("""
               _____          _       
              / ____|        | |      
             | |    _   _  __| | __ _ 
             | |   | | | |/ _` |/ _` |
             | |___| |_| | (_| | (_| |
              \_____\__,_|\__,_|\__,_|""")
        else:
            # Use cpu by default
            self.CPUttsModel = Model(model_path, "cpu", self.description)
            self.tts = TextToSpeach(self.CPUttsModel)


    def _send_tts_request(self, text, idx):
        retry_count = 0
        while retry_count < self.max_retries:
            try:

                print(f"Processing chunk {idx}/{self.len}...")

                output_wav_file = os.path.join(self.temp_folder, f'chunk{idx}.wav')
                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')

                print(f"Text of the processed chunk:\n{text}")
                # Call model an process text
                self.tts.textToMP3(text, output_wav_file)

                chunk_audio = AudioSegment.from_wav(output_wav_file)
                chunk_audio.export(output_mp3_file, format='mp3')

                # Check if AI succeeded to generate the output
                if not os.path.exists(output_wav_file):
                    raise f"Could not generate WAV file for the chunk {idx}"

                os.remove(output_wav_file)

                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)
                return

            except Exception as e:
                print(f"Error processing chunk {idx}:\n {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

        if retry_count == self.max_retries:
            # if something went silly - attempt is made to
            print("Using ESPEAK to replace unprocessed chunk")
            self.tools.Espeak(self.temp_folder, text, f'chunk{idx}')

            self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)


    def process_chunks(self):
        # This function is responcible for splitting text into chunks and making them into a text book


        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        if not os.path.exists(self.voiced_folder):
            os.makedirs(self.voiced_folder)

        with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
            input_text = f.read()

        sentences = self.tools.divide_into_sentences(input_text)
        self.chunks = self.tools.split_into_sub_arrays(sentences, self.chunk_size)
        self.len = len(self.chunks)

        with ThreadPoolExecutor(max_workers=self.max_simultaneous_threads) as executor:
            for idx, chunk in enumerate(self.chunks):
                executor.submit(self._send_tts_request, chunk, idx)

        self.tools.merge_audio_pairs(self.temp_folder)

        final_output_file = os.path.join(self.voiced_folder, f'{self.input_text_name}.mp3')

        shutil.move(f"{self.temp_folder}/chunk0.mp3", final_output_file)

        os.rmdir(self.temp_folder)

        print("Temporary folder removed.")
        print("Text has been voiced and saved to 'voices' directory.")


if __name__ == "__main__":
    processor = TextToVoiceProcessorTTSfree(
        input_text_name="smallText",
        text_folder="texts",
        temp_folder="temp",
        voiced_folder="voices",
        chunk_size=1000,
        max_retries=1000,
        retry_delay=600,
        max_simultaneous_threads=1,
        language="en",
        model_path="parler-tts/parler-tts-mini-jenny-30H",
    )
    processor.process_chunks()
