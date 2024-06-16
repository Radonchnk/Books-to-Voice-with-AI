import os
import json

from customtkinter import *

from tools.TEXTtoVOICEgtts import *
from tools.TEXTtoVOICEespeak import *
from tools.TEXTtoVOICEttsfree import *

class ContinueBook(CTk):
    def __init__(self, root_instance, book_path, *args, **kwargs):
        # Simular structure in other applications
        super().__init__(*args, **kwargs)

        self.root_instance = root_instance
        self.book_path = book_path

        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.title("Continue book")

        # Set size of window
        width = 500
        height = 300

        # Get the screen width and height
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()

        # Place window in center of screen
        x = (screenWidth - width) // 2
        y = (screenHeight - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.frame = CTkFrame(master=self)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Bind close button to goBack function
        self.protocol("WM_DELETE_WINDOW", self.goBackEvent)

        # Setups main buttons

        # Places buttons
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        self.restartGeneration()

        self.frame.grid_columnconfigure(0, weight=1)

        self.frame.grid_propagate(False)

        # Setup min and max size
        self.minsize(500, 300)
        self.maxsize(800, 500)

    def restartGeneration(self):

        metadata = os.path.join(self.book_path, "metadata.json")

        with open(metadata) as f:
            data = json.load(f)

        generation_method = data['generation_method']

        self.label = CTkLabel(master=self.frame, text=f"Book generated using: {generation_method}")
        self.label.grid(row=0, column=0, pady=12, padx=10, columnspan=3)
        self.label.configure(font=("Roboto", 18))

        audioFiles = [int(file[5:-4]) for file in os.listdir(self.book_path) if
                     file[-3:] == "mp3"]

        textFiles = [int(file[5:-4]) for file in os.listdir(self.book_path) if
                     file[-3:] == "txt"]

        notGenerated = [x for x in textFiles if x not in audioFiles]
        notGenerated.sort()

        self.label = CTkLabel(master=self.frame, text=f"Left to generate: {len(notGenerated)}/{len(textFiles)}")
        self.label.grid(row=1, column=0, pady=12, padx=10, columnspan=3)
        self.label.configure(font=("Roboto", 18))

        self.submitSelfHostedTTsButton = CTkButton(master=self.frame, text="Submit",
                                                   command=lambda: self.submitParameters(generation_method, data, notGenerated))
        self.submitSelfHostedTTsButton.grid(row=2, column=0, pady=12, padx=10, columnspan=3)

    def submitParameters(self, generation_method, data, notGenerated):
        if generation_method == "Self Hosted TTS":
            values = data["settings"]
            processor = TextToVoiceProcessorTTSfree(continue_generation=1, not_generated=notGenerated ,**values)
            processor.process_chunks()

    def goBackEvent(self):
        # Call the method in the root instance to show the main window
        self.root_instance.openMainWindow()

        # Close the window
        self.destroy()
