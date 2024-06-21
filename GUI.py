import os
import requests
from customtkinter import *
from tools.PDFtoTEXT import *

from gui.voiceProcessor import VoiceProcessor
from gui.continueBook import ContinueBook


class App(CTk):
    def __init__(self, *args, **kwargs):
        # Simular structure in other applications
        super().__init__(*args, **kwargs)
        # Check if model exists and download it if not
        if not os.path.exists('model.pth'):
            self.downloadModel()

        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.title("Main menu")

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

        # Setups main buttons
        self.label = CTkLabel(master=self.frame, text="Book -> Audio")
        self.label.grid(row=0, column=0, pady=12, padx=10, columnspan=3)
        self.label.configure(font=("Roboto", 24))

        button1 = CTkButton(master=self.frame, text="Convert text to audio", command=self.getTextFromUser,
                            width=200,height=50)
        button1.configure(font=("Roboto", 18))

        button2 = CTkButton(master=self.frame, text="Convert book to audio", command=self.getBookFromUser, width=200,
                            height=50)
        button2.configure(font=("Roboto", 18))

        button3 = CTkButton(master=self.frame, text="Keep working on book", command=self.continueBookEvent, width=200,
                            height=50)
        button3.configure(font=("Roboto", 18))

        # Places buttons
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        button1.grid(row=1, column=0, pady=12, padx=(10, 10))
        button2.grid(row=2, column=0, pady=12, padx=(10, 10))
        button3.grid(row=3, column=0, pady=12, padx=(10, 10))

        self.frame.grid_columnconfigure(0, weight=1)

        self.frame.grid_propagate(False)

        # Setup min and max size
        self.minsize(500, 300)
        self.maxsize(800, 500)

    def downloadModel(self):
        url = "https://www.dropbox.com/scl/fi/8rgd80r8r6sr10uuyysmk/model.pth?rlkey=rhv7ev2r6ftsvis1o2o8of9ol&st=smoo4dw3&dl=1"
        print("Downloading eSpeak Cleanup model to your project root directory")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open("./model.pth", 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Successfully downloaded the model")

    def openMainWindow(self):
        # Show the main window
        self.deiconify()

    def getTextFromUser(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            # Get the directory path
            directory_path = os.path.dirname(file_path)

            # Get the file name
            file_name = os.path.basename(file_path)

            self.path_to_text_folder = directory_path
            self.text_file_name = file_name[:-4]

            # Hide the main window
            self.withdraw()

            # After text is recived processing starts
            self.voiceProcessor = VoiceProcessor(root_instance=self,
                                                 path_to_text_folder=directory_path, text_file_name=file_name[:-4])

    def getBookFromUser(self):
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

            # Hide the main window
            self.withdraw()

            # After PDF conversion and PDF to text conversion start processing
            self.voiceProcessor = VoiceProcessor(root_instance=self,
                                                 path_to_text_folder=directory_path, text_file_name=file_name[:-4])

    def continueBookEvent(self):
        # get path to folder with book in progress
        path_to_text_folder = filedialog.askdirectory()

        # Hide the main window
        self.withdraw()

        # After PDF conversion and PDF to text conversion start processing
        self.ContinueBook = ContinueBook(root_instance=self, book_path=path_to_text_folder)

if __name__ == "__main__":
    app = App()
    app.mainloop()
