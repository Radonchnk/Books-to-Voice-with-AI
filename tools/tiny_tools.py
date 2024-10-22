import subprocess
import os
from mutagen.mp3 import MP3
import shutil
import time
import json
from pydub import AudioSegment
import io


class ToolsSet:
    def Espeak(self, temp_folder, text, output_filename):
        # Generate the WAV file using espeak
        temp_wav_file = os.path.join(temp_folder, f"{output_filename}.wav")
        subprocess.run(["espeak", text, "-w", temp_wav_file])

        # Convert the WAV file to MP3 using ffmpeg
        mp3_output_path = os.path.join(temp_folder, f'{output_filename}.mp3')
        subprocess.run(["ffmpeg", "-i", temp_wav_file, mp3_output_path])

        # Remove the intermediate WAV file
        os.remove(temp_wav_file)

    def EspeakOutputWithAudioArray(self, text):
        command = f'espeak "{text}" --stdout'
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        audio_buffer = io.BytesIO(result.stdout)
        audio = AudioSegment.from_file(audio_buffer, format="wav")
        return audio

    @classmethod
    def get_mp3_duration(cls, mp3_path):
        audio = MP3(mp3_path)
        duration_in_seconds = int(audio.info.length)
        return duration_in_seconds


    @classmethod
    def format_time(cls, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return hours, minutes, seconds

    @classmethod
    def time_manager(cls, time_start, chunks_done, chunks_total):
        # This punction prints how much ime is spent generating and estimated time
        time_taken = time.time() - time_start
        expected_time_seconds = (chunks_total - (chunks_done + 1)) * (time_taken / (chunks_done + 1))
        hours_left, minutes_left, seconds_left = ToolsSet.format_time(expected_time_seconds)
        hours_spent, minutes_spent, seconds_spent = ToolsSet.format_time(time_taken)

        print(f"\n\n\n======================================")
        print(f"Chunks processed {chunks_done + 1}/{chunks_total}")
        print(f"Time spent: {str(hours_spent).zfill(2)}:{str(minutes_spent).zfill(2)}:{str(seconds_spent).zfill(2)}")
        print(f"Expected time left: {str(hours_left).zfill(2)}:{str(minutes_left).zfill(2)}:{str(seconds_left).zfill(2)}")
        print(f"======================================")

    @classmethod
    def divide_into_sentences(cls, text):
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

    @classmethod
    def split_into_sub_arrays(cls, strings, max_length):
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

    @classmethod
    def create_metadata_file(cls, folder_path, generation_method, total_chunks, settings):
        data = {
            "generation_method": generation_method,
            "total_chunks": total_chunks,
            "settings": settings
        }

        metadata_path = os.path.join(folder_path, "metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def create_text_chunks(cls, text_array, folder_path):
        for idx, chunk_text in enumerate(text_array):
            folder = os.path.join(folder_path, f"chunk{idx}.txt")
            with open(folder, "w") as f:
                # remove \n cuz buggy
                chunk_text = " ".join(chunk_text.split("\n"))
                f.write(chunk_text)
    @classmethod
    def clear_metadata_and_texts(cls, folder_path, total_chunks):
        metadata = os.path.join(folder_path, "metadata.json")
        os.remove(metadata)
        for idx in range(total_chunks):
            path = os.path.join(folder_path, f"chunk{idx}.txt")
            os.remove(path)