import subprocess
import os


class tools_set:
    def Espeak(self, temp_folder, text, output_filename):
        # Generate the WAV file using espeak
        temp_wav_file = os.path.join(temp_folder, f"{output_filename}.wav")
        subprocess.run(["espeak", text, "-w", temp_wav_file])

        # Convert the WAV file to MP3 using ffmpeg
        mp3_output_path = os.path.join(temp_folder, f'{output_filename}.mp3')
        subprocess.run(["ffmpeg", "-i", temp_wav_file, mp3_output_path])

        # Remove the intermediate WAV file
        os.remove(temp_wav_file)