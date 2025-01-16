
from concurrent.futures import ThreadPoolExecutor, as_completed

from tools.fileMerging import FileMerger
from tools.tiny_tools import *
import shutil
import threading


class TextToVoiceProcessor:
    def __init__(self, input_text_name, temp_folder, text_folder, voiced_folder, chunk_size, max_retries, retry_delay,
                 max_simultaneous_threads, continue_generation=0, not_generated="", settings=""):
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

    def _send_tts_request(self, idx):

        retry_count = 0
        while retry_count <= self.max_retries:
            try:

                print(f"Processing chunk {idx}... ")

                # Get text file name fom the file
                text_file = os.path.join(self.temp_folder, f"chunk{idx}.txt")
                # Read text which is going to be voiced
                with open(file=text_file, encoding="utf-8") as f:
                    text = f.readlines()
                    text = " ".join(text)

                self.tools.Espeak(temp_folder=self.temp_folder, text=text, output_filename=f"chunk{idx}")

                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

                print(f"Chunk {idx} processed successfully.")

                return
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

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

        #for file in os.listdir(self.temp_folder):
        #    if "before_convert" in file or ".wav" in file:
        #        os.remove(os.path.join(self.temp_folder, file))

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
