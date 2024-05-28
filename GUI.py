import tkinter as tk
from tkinter import filedialog
import random

from tools.PDFtoTEXT import *
from tools.TEXTtoVOICEgtts import *
from tools.TEXTtoVOICEespeak import *
from tools.TEXTtoVOICEttsfree import *

class PDFtoVoiceApp:
    def __init__(self, root):
        self.root = root
        self.path_to_text_folder = ""
        self.text_file_name = ""
        self.temp_folder = f"temp{random.randint(0, 1000)}"
        self.current_window = None

        root.title("PDF to Voice App")
        # Create a frame to hold the buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)  # Add some padding

        # Create buttons
        self.book_to_voice_button = tk.Button(button_frame, text="Book to Voice", command=self.select_pdf)
        self.text_to_voice_button = tk.Button(button_frame, text="Text to Voice", command=self.select_text)

        # Pack buttons horizontally with some spacing
        self.book_to_voice_button.pack(side=tk.LEFT, padx=10)
        self.text_to_voice_button.pack(side=tk.LEFT, padx=10)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            # Get the directory path
            directory_path = os.path.dirname(file_path)

            # Get the file name
            file_name = os.path.basename(file_path)

            # Converting pdf to text in the same folder as a book
            converter = PDFtoTEXTConverter(
                book_name=file_name[:-4],  # file name => book name
                books_folder=directory_path,
                texts_folder=directory_path
            )
            converter.convert_to_text()

            self.path_to_text_folder = directory_path
            self.text_file_name = file_name[:-4]

            # After PDF conversion, display additional options
            self.display_voice_options()

    def select_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            # Get the directory path
            directory_path = os.path.dirname(file_path)

            # Get the file name
            file_name = os.path.basename(file_path)

            self.path_to_text_folder = directory_path
            self.text_file_name = file_name[:-4]

            # After selecting a text file, display additional options
            self.display_voice_options()

    def display_voice_options(self):
        # Close the current window, if any
        if self.current_window:
            self.current_window.destroy()

        # Create a new window for voice options
        voice_window = tk.Toplevel(self.root)
        self.current_window = voice_window
        voice_window.title("Voice Options")

        # Create a frame to hold the buttons
        button_frame = tk.Frame(voice_window)
        button_frame.pack(pady=20)  # Add some vertical spacing

        # Create buttons for voice options with horizontal spacing
        espeak_button = tk.Button(button_frame, text="Use espeak", command=lambda: self.voice_with("Use espeak"))
        gtts_button = tk.Button(button_frame, text="Use gTTS", command=lambda: self.voice_with("Use gTTS"))
        ai_tts_button = tk.Button(button_frame, text="Use AI TTS", command=lambda: self.voice_with("Use AI TTS"))

        # Pack buttons horizontally with spacing
        espeak_button.pack(side=tk.LEFT, padx=10)
        gtts_button.pack(side=tk.LEFT, padx=10)
        ai_tts_button.pack(side=tk.LEFT, padx=10)

    def voice_with(self, option):
        # Close the current window, if any
        if self.current_window:
            self.current_window.destroy()

        # Create a new window for voice settings
        settings_window = tk.Toplevel(self.root)
        self.current_window = settings_window
        settings_window.title(f"{option} Settings")

        # Define dictionaries with field names and default values for each option
        espeak_fields = {
            "input_text_name": self.text_file_name,
            "text_folder": self.path_to_text_folder,
            "temp_folder": self.temp_folder,
            "voiced_folder": self.path_to_text_folder,
            "chunk_size": 1,
            "max_retries": 5,
            "retry_delay": 1,
            "max_simultaneous_threads": 5
        }
        gtts_fields = {
            "input_text_name": self.text_file_name,
            "text_folder": self.path_to_text_folder,
            "temp_folder": self.temp_folder,
            "voiced_folder": self.path_to_text_folder,
            "chunk_size": 1,
            "max_retries": 5,
            "retry_delay": 1,
            "max_simultaneous_threads": 5,
            "language": "en"
        }
        ai_tts_fields = {
            "input_text_name": self.text_file_name,
            "text_folder": self.path_to_text_folder,
            "temp_folder": self.temp_folder,
            "voiced_folder": self.path_to_text_folder,
            "chunk_size": 10,
            "max_retries": 2,
            "retry_delay": 1,
            "max_simultaneous_threads": 1,
            "language": "en",
            "model_path": "parler-tts/parler-tts-mini-jenny-30H",
            "description": "Jenny speaks at an average pace with an animated delivery in a very confined sounding environment with clear audio quality."
        }

        # Get the appropriate fields based on the selected option
        if option == "Use espeak":
            fields = espeak_fields
        elif option == "Use gTTS":
            fields = gtts_fields
        elif option == "Use AI TTS":
            fields = ai_tts_fields

        row = 0  # Row counter for grid layout

        # Create input fields based on the fields dictionary
        input_entries = {}
        for field_name, default_value in fields.items():
            # Label for field name (on the left)
            label = tk.Label(settings_window, text=field_name)
            label.grid(row=row, column=0, sticky="w", padx=10)  # Left-align label

            # Entry for input (on the right)
            entry = tk.Entry(settings_window)
            entry.insert(0, default_value)  # Set default value
            entry.grid(row=row, column=1, padx=10)  # Right-align entry
            input_entries[field_name] = entry

            row += 1  # Move to the next row for the next input field

        # Create a "Next" button
        def next_button_callback():
            # Retrieve values from input fields
            values = {field_name: entry.get() for field_name, entry in input_entries.items()}
            if option == "Use espeak":
                processor = TextToVoiceProcessor(**values)
                processor.process_chunks()
            elif option == "Use gTTS":
                processor = TextToVoiceProcessorGTTS(**values)
                processor.process_chunks()
            elif option == "Use AI TTS":
                processor = TextToVoiceProcessorTTSfree(**values)
                processor.process_chunks()

        next_button = tk.Button(settings_window, text="Next", command=next_button_callback)
        next_button.grid(row=row, columnspan=2, pady=10)  # Span two columns for the button


if __name__ == "__main__":
    root = tk.Tk()

    app = PDFtoVoiceApp(root)
    root.mainloop()
