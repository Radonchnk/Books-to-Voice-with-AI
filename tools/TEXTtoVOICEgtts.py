import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from gtts import gTTS
import shutil


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

    def _send_tts_request(self, text, idx):
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                print(f"Processing chunk {idx}...")
                tts = gTTS(text, lang=self.language, slow=False)

                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')
                tts.save(output_mp3_file)

                print(f"Chunk {idx} processed successfully.")
                return
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

    def merge_audio_pairs(self):

        def concatenate_mp3_files(file1, file2, output_file):
            command = ["ffmpeg", "-i", "concat:{}|{}".format(file1, file2), "-c", "copy", "temp/temp.mp3"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if os.path.exists("temp/temp.mp3"):
                os.remove(file1)
                os.remove(file2)
                shutil.move(f"{self.temp_folder}/temp.mp3", output_file)

        def create_pairs(array):
            pairs = []
            for i in range(0, len(array) - 1, 2):
                pairs.append([array[i], array[i + 1]])
            if len(array) % 2 == 1:
                pairs.append([array[-1]])
            return pairs

        # read all files
        num_files = len(os.listdir(self.temp_folder))
        all_files = [f"chunk{x}.mp3" for x in range(num_files)]
        pairs = create_pairs(all_files)

        while len(os.listdir(self.temp_folder)) > 1:
            for i in range(len(pairs)):
                if len(pairs[i]) != 1:
                    chunk1_file = os.path.join(self.temp_folder, pairs[i][0])
                    chunk2_file = os.path.join(self.temp_folder, pairs[i][1])
                    print(f"merging {chunk1_file}, {chunk2_file}")
                    merged_chunk_file = os.path.join(self.temp_folder, f"chunk{i}.mp3")
                    print(f"success in merging {chunk1_file}, {chunk2_file}")

                    concatenate_mp3_files(chunk1_file, chunk2_file, merged_chunk_file)
                else:
                    chunk_file = os.path.join(self.temp_folder, pairs[i][0])
                    merged_chunk_file = os.path.join(self.temp_folder, f"chunk{i}.mp3")

                    shutil.move(chunk_file, merged_chunk_file)

            num_files = len(os.listdir(self.temp_folder))
            if num_files != 1:
                all_files = [f"chunk{x}.mp3" for x in range(num_files)]

                pairs = create_pairs(all_files)

    def process_chunks(self):
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        if not os.path.exists(self.voiced_folder):
            os.makedirs(self.voiced_folder)

        with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
            input_text = f.read()

        self.chunks = [input_text[i:i + self.chunk_size] for i in range(0, len(input_text), self.chunk_size)]

        with ThreadPoolExecutor(max_workers=self.max_simultaneous_threads) as executor:
            for idx, chunk in enumerate(self.chunks):
                executor.submit(self._send_tts_request, chunk, idx)

        self.merge_audio_pairs()

        final_output_file = os.path.join(self.voiced_folder, f'{self.input_text_name}.mp3')

        shutil.move(f"{self.temp_folder}/chunk0.mp3", final_output_file)

        os.rmdir(self.temp_folder)

        print("Temporary folder removed.")
        print("Text has been voiced and saved to 'voices' directory.")


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