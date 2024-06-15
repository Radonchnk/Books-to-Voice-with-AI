import os
import time
from concurrent.futures import ThreadPoolExecutor
from tools.tts import *
from tools.tiny_tools import *
import shutil
from pydub import AudioSegment
from mutagen.mp3 import MP3


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

    def get_mp3_duration(self, mp3_path):
        audio = MP3(mp3_path)
        duration_in_seconds = int(audio.info.length)
        return duration_in_seconds

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return hours, minutes, seconds

    def _send_tts_request(self, text, idx):
        retry_count = 0
        while retry_count < self.max_retries:
            try:

                print(f"Processing chunk {idx}/{self.len}...")

                output_wav_file = os.path.join(self.temp_folder, f'chunk{idx}.wav')
                output_mp3_file = os.path.join(self.temp_folder, f'chunk{idx}.mp3')

                print(f"Text of the processed chunk:\n{text}")
                # Call model an process text
                self.tts.textToMP3(text, output_wav_file, self.description)

                chunk_audio = AudioSegment.from_wav(output_wav_file)
                chunk_audio.export(output_mp3_file, format='mp3')

                # Check if AI succeeded to generate the output
                if not os.path.exists(output_wav_file):
                    raise f"Could not generate WAV file for the chunk {idx}"

                os.remove(output_wav_file)

                print(f"Chunk {idx}/{self.len} processed successfully.")

                self._time_manager(idx)
                return

            except Exception as e:
                print(f"Error processing chunk {idx}:\n {e}")
                retry_count += 1
                print(f"Retrying chunk {idx} ({retry_count}/{self.max_retries})...")
                time.sleep(self.retry_delay)

        if retry_count == self.max_retries:
            # if smething went silly - attempt is made to
            print("Using ESPEAK to replace unprocessed chunk")
            self.tools.Espeak(self.temp_folder, text, f'chunk{idx}')

            self._time_manager(idx)


    def _time_manager(self, idx):
        # This punction prints how much ime is spent generating and estimated time
        time_taken = time.time() - self.time_start
        expected_time_seconds = (self.len - (idx + 1)) * (time_taken / (idx + 1))
        hours_left, minutes_left, seconds_left = self._format_time(expected_time_seconds)
        hours_spent, minutes_spent, seconds_spent = self._format_time(time_taken)

        print(f"\n\n\n======================================")
        print(f"Time spent: {hours_spent}:{minutes_spent}:{seconds_spent}")
        print(f"Expected time left: {hours_left}:{minutes_left}:{seconds_left}")
        print(f"======================================")

    def merge_audio_pairs(self):
        # This function merges
        def concatenate_mp3_files(file1, file2, output_file):
            command = ["ffmpeg", "-i", "concat:{}|{}".format(file1, file2), "-c", "copy", f"{self.temp_folder}/temp.mp3"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if os.path.exists(f"{self.temp_folder}/temp.mp3"):
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
        # all_files = [f"chunk{x}.mp3" for x in range(num_files)]
        all_files = [int(file[5:-4]) for file in os.listdir(self.temp_folder) if
                     os.path.isfile(os.path.join(self.temp_folder, file))]
        all_files = sorted(all_files)
        all_files = [f"chunk{x}.mp3" for x in all_files]
        pairs = create_pairs(all_files)

        while len(os.listdir(self.temp_folder)) > 1:
            for i in range(len(pairs)):
                if len(pairs[i]) != 1:
                    chunk1_file = os.path.join(self.temp_folder, pairs[i][0])
                    chunk2_file = os.path.join(self.temp_folder, pairs[i][1])
                    print(f"merging {chunk1_file}, {chunk2_file}")
                    merged_chunk_file = os.path.join(self.temp_folder, f"chunk{i}.mp3")

                    concatenate_mp3_files(chunk1_file, chunk2_file, merged_chunk_file)
                    print(f"success in merging {chunk1_file}, {chunk2_file}")
                else:
                    chunk_file = os.path.join(self.temp_folder, pairs[i][0])
                    merged_chunk_file = os.path.join(self.temp_folder, f"chunk{i}.mp3")

                    shutil.move(chunk_file, merged_chunk_file)

            num_files = len(os.listdir(self.temp_folder))
            if num_files != 1:
                all_files = [int(file[5:-4]) for file in os.listdir(self.temp_folder) if
                             os.path.isfile(os.path.join(self.temp_folder, file))]
                all_files = sorted(all_files)
                all_files = [f"chunk{x}.mp3" for x in all_files]

                pairs = create_pairs(all_files)

    def process_chunks(self):
        # This function is responcible for splitting text into chunks and making them into a text book

        def divide_into_sentences(text):
            sentences = []
            current_sentence = ""
            remove_characters = ["'"]
            sentence_endings = ['.', '!', '?']
            max_consecutive_numbers = 5
            consecutive_numbers_count = 0
            refuse_length = 1

            math_operations = {
                '+': 'plus',
                '-': 'minus',
                '*': 'times',
                '/': 'divided by',
                '%': 'percent',
                '?': 'minus',
                '=': 'equals'
            }

            for char in text:
                if char in remove_characters:
                    char = " "  # Replace apostrophes with spaces
                if char.isupper():
                    current_sentence += char.lower()  # Convert uppercase to lowercase
                else:
                    current_sentence += char

                if char.isdigit():
                    consecutive_numbers_count += 1
                    if consecutive_numbers_count > max_consecutive_numbers:
                        current_sentence = current_sentence[:-1]
                else:
                    consecutive_numbers_count = 0

                if char in math_operations:
                    current_sentence = current_sentence[:-1] + math_operations[char] + ' '

                if char in sentence_endings:
                    if len(current_sentence.strip()) > (refuse_length + 1):  # Skip single-letter sentences
                        sentences.append(current_sentence.strip())
                    current_sentence = ""

            if current_sentence and len(current_sentence.strip()) > 1:
                sentences.append(current_sentence.strip())

            return sentences

        def split_into_subarrays(strings, max_length):
            subarrays = []
            current_subarray = []

            current_length = 0
            for string in strings:
                if current_length + len(string) > max_length and current_subarray:
                    subarrays.append(' '.join(current_subarray))
                    current_subarray = []
                    current_length = 0

                current_subarray.append(string)
                current_length += len(string)

            if current_subarray:
                subarrays.append(''.join(current_subarray))

            return subarrays

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        if not os.path.exists(self.voiced_folder):
            os.makedirs(self.voiced_folder)

        with open(f"{self.text_folder}/{self.input_text_name}.txt", 'r', encoding='utf-8') as f:
            input_text = f.read()

        sentences = divide_into_sentences(input_text)
        self.chunks = split_into_subarrays(sentences, self.chunk_size)
        self.len = len(self.chunks)

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
