from concurrent.futures import ThreadPoolExecutor
from gtts import gTTS
from tools.tiny_tools import *
from tools.fileMerging import FileMerger


class TextToVoiceProcessorGTTS:
    def __init__(self, input_text_name, temp_folder, text_folder, voiced_folder, chunk_size, max_retries, retry_delay,
                 max_simultaneous_threads, language):
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

    def _send_tts_request(self, text, idx):
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # TODO - Comment
                print(f"Processing chunk {idx}...")
                tts = gTTS(text, lang=self.language, slow=False)

                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')
                tts.save(output_mp3_file)

                self.tools.time_manager(self.time_start, idx, self.len)

                print(f"Chunk {idx} processed successfully.")
                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)
                return
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)
                time.sleep(self.retry_delay)

        if retry_count == self.max_retries:
            # if something went silly - attempt is made to
            print("Using ESPEAK to replace unprocessed chunk")
            self.tools.Espeak(self.temp_folder, text, f'chunk{idx}')

            self.tools.time_manager(time_start=self.time_start, chunks_done=idx, chunks_total=self.len)

    def process_chunks(self):
        # TODO - Comment
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
    processor = TextToVoiceProcessorGTTS(
        input_text_name="alphabet",
        text_folder="texts",
        temp_folder="temp",
        voiced_folder="voices",
        chunk_size=10,
        max_retries=1000,
        retry_delay=600,
        max_simultaneous_threads=4,
        language="en"
    )
    processor.process_chunks()