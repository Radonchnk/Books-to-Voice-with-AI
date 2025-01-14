from customtkinter import *
from CTkMenuBar import *
import random
import json

from tools.TEXTtoVOICEgtts import *
from tools.TEXTtoVOICEespeak import *
from tools.TEXTtoVOICEttsfree import *

class VoiceProcessor(CTk):
    def __init__(self, root_instance, path_to_text_folder, text_file_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_instance = root_instance
        self.path_to_text_folder = path_to_text_folder
        self.text_file_name = text_file_name
        self.temp_folder = f"temp{random.randint(0, 1000)}"
        self.current_directory = os.getcwd()
        self.settings_file = "Settings"
        self.espeak_settings = "espeak_fields"
        self.google_settings = "gtts_fields"
        self.self_hosted_settings = "ai_tts_fields"
        self.current_window = ""
        self.row_frame_espeakTTs = []
        self.row_frame_googleTTs = []
        self.row_frame_selfHostedTTs = []

        set_appearance_mode("dark")
        set_default_color_theme("green")
        self.title("Voice Processor")

        # Set size of window
        width = 500
        height = 600

        # Get the screen width and height
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()

        # Place window in center of screen
        x = (screenWidth - width) // 2
        y = (screenHeight - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Bind close button to goBack function
        self.protocol("WM_DELETE_WINDOW", self.goBackEvent)

        # Setup main menu
        menu = CTkMenuBar(master=self)
        menu.add_cascade("←", command=self.goBackEvent)
        menu.add_cascade("Espeak TTS", command=self.espeakTTsPressEvent)
        menu.add_cascade("Google TTS", command=self.googleTTsPressEvent)
        menu.add_cascade("Self Hosted TTS", command=self.selfHostedTTsAiPressEvent)

        # Setup nn menu
        self.setupEspeakTTsMenu()

        self.setupGoogleTTsMenu()

        self.setupSelfHostedTTsAiMenu()

        # Place default on a screen
        self.selfHostedTTsAiPressEvent()

        # Set sizes
        self.minsize(width, height)
        self.maxsize(width, height)

    def load_settings_from_file(self, path_to_save):

        # standard fields for any settings
        data = {
            "input_text_name": self.text_file_name,
            "text_folder": self.path_to_text_folder,
            "temp_folder": self.temp_folder,
            "voiced_folder": self.path_to_text_folder
        }

        # updating custom settings
        paths = os.path.join(self.current_directory, self.settings_file, path_to_save + ".json")
        with open(paths, 'r', encoding="utf-8") as file:
            data.update(json.load(file))

        return data

    def setupEspeakTTsMenu(self):
        self.current_window = "Espeak TTS"

        fields = self.load_settings_from_file(self.espeak_settings)

        # Create a frame to hold the input fields
        self.frame_espeak = CTkFrame(self)
        self.frame_espeak.pack(pady=20)

        # Create input fields based on the fields dictionary
        input_entries = {}
        for field_name, default_value in fields.items():
            # Create a container for each row (label + entry)
            row_frame = CTkFrame(self.frame_espeak)
            row_frame.pack(fill='x', pady=5)
            self.row_frame_espeakTTs.append(row_frame)  # Store reference to row frame

            # Label for field name (on the left)
            label = CTkLabel(row_frame, text=field_name)
            label.pack(side='left', padx=10)

            # Entry for input (on the right)
            entry = CTkEntry(row_frame)
            entry.insert(0, default_value)  # Set default value
            entry.pack(side='right', padx=10, fill='x', expand=True)
            input_entries[field_name] = entry

        # Add a button at the end of the form
        self.submitEspeakButton = CTkButton(self.frame_espeak, text="Submit",
                                                command=lambda: self.submitParameters(input_entries))
        self.submitEspeakButton.pack(pady=10)

        # Forget placement
        self.frame_espeak.pack_forget()
        self.submitEspeakButton.pack_forget()

    def setupGoogleTTsMenu(self):
        self.current_window = "Google TTS"

        fields = self.load_settings_from_file(self.google_settings)

        # Create a frame to hold the input fields
        self.frame_googleTTs = CTkFrame(self)
        self.frame_googleTTs.pack(pady=20)

        # Create input fields based on the fields dictionary
        input_entries = {}
        for field_name, default_value in fields.items():
            # Create a container for each row (label + entry)
            row_frame = CTkFrame(self.frame_googleTTs)
            row_frame.pack(fill='x', pady=5)
            self.row_frame_googleTTs.append(row_frame)  # Store reference to row frame

            # Label for field name (on the left)
            label = CTkLabel(row_frame, text=field_name)
            label.pack(side='left', padx=10)

            # Entry for input (on the right)
            entry = CTkEntry(row_frame)
            entry.insert(0, default_value)  # Set default value
            entry.pack(side='right', padx=10, fill='x', expand=True)
            input_entries[field_name] = entry

        # Add a button at the end of the form
        self.submitGoogleTTsButton = CTkButton(self.frame_googleTTs, text="Submit",
                                            command=lambda: self.submitParameters(input_entries))
        self.submitGoogleTTsButton.pack(pady=10)

        # Forget placement
        self.frame_googleTTs.pack_forget()
        self.submitGoogleTTsButton.pack_forget()

    def setupSelfHostedTTsAiMenu(self):
        self.current_window = "Self Hosted TTS"

        fields = self.load_settings_from_file(self.self_hosted_settings)

        # Create a frame to hold the input fields
        self.frame_self_hosted = CTkFrame(self)
        self.frame_self_hosted.pack(pady=20)

        # Create input fields based on the fields dictionary
        input_entries = {}
        for field_name, default_value in fields.items():
            # Create a container for each row (label + entry)
            row_frame = CTkFrame(self.frame_self_hosted)
            row_frame.pack(fill='x', pady=5)
            self.row_frame_selfHostedTTs.append(row_frame)  # Store reference to row frame

            # Label for field name (on the left)
            label = CTkLabel(row_frame, text=field_name)
            label.pack(side='left', padx=10)

            # Entry for input (on the right)
            entry = CTkEntry(row_frame)
            entry.insert(0, default_value)  # Set default value
            entry.pack(side='right', padx=10, fill='x', expand=True)
            input_entries[field_name] = entry

        # Add a button at the end of the form
        self.submitSelfHostedTTsButton = CTkButton(self.frame_self_hosted, text="Submit",
                                               command=lambda: self.submitParameters(input_entries))
        self.submitSelfHostedTTsButton.pack(pady=10)

        # Forget placement
        self.frame_self_hosted.pack_forget()
        self.submitSelfHostedTTsButton.pack_forget()

    def forgetEveryPlacement(self):
        # When new menu needs to be shown. this function is called to clear space so new menu can be shown

        # Forget placement espeak
        self.frame_espeak.pack_forget()
        self.submitEspeakButton.pack_forget()

        # Forget placement google
        self.frame_googleTTs.pack_forget()
        self.submitGoogleTTsButton.pack_forget()

        # Forget placement self hosted
        self.frame_self_hosted.pack_forget()
        self.submitSelfHostedTTsButton.pack_forget()

    def espeakTTsPressEvent(self):
        self.forgetEveryPlacement()

        self.current_window = "Espeak TTS"

        # Show all input field frames for espeak
        self.frame_espeak.pack(pady=20)
        self.submitEspeakButton.pack(pady=10)


    def googleTTsPressEvent(self):
        self.forgetEveryPlacement()

        self.current_window = "Google TTS"

        # Show all input field frames for google
        self.frame_googleTTs.pack(pady=20)
        self.submitGoogleTTsButton.pack(pady=10)

    def selfHostedTTsAiPressEvent(self):
        self.forgetEveryPlacement()

        self.current_window = "Self Hosted TTS"

        # Show all input field frames for self hosted
        self.frame_self_hosted.pack(pady=20)
        self.submitSelfHostedTTsButton.pack(pady=10)

    def submitParameters(self, input_entries):
        # get every value from the the form
        values = {field_name: entry.get() for field_name, entry in input_entries.items()}
        if self.current_window == "Espeak TTS":
            processor = TextToVoiceProcessor(settings=values, **values)
            processor.process_chunks()
        elif self.current_window == "Google TTS":
            processor = TextToVoiceProcessorGTTS(**values)
            processor.process_chunks()
        elif self.current_window == "Self Hosted TTS":
            processor = TextToVoiceProcessorTTSfree(settings=values, **values)
            processor.process_chunks()

    def goBackEvent(self):
        # Call the method in the root instance to show the main window
        self.root_instance.openMainWindow()

        # Close the window
        self.destroy()
