from tools.PDFtoTEXT import *
from tools.TEXTtoVOICEgtts import *
from tools.TEXTtoVOICEespeak import *
from tools.TEXTtoVOICESelfHosted import *
import random

def initialize_books_folder(folder_name):
    try:
        files = [file[:-4] for file in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, file))]
        return files
    except OSError as e:
        print(f"Error: {e}")
        return []

def select_book(books_list):
    if len(books_list) == 0:
        print("No Books")
        return None
    else:
        for i, book in enumerate(books_list):
            print(f"{i} <> {book}")
        try:
            index = int(input("Write an index: "))
            if index < 0 or index >= len(books_list):
                print("Invalid index")
                return None
            return books_list[index]
        except ValueError:
            print("Invalid input")
            return None

def select_text(texts_list):
    if len(texts_list) == 0:
        print("No texts")
        return None
    else:
        for i, text in enumerate(texts_list):
            print(f"{i} <> {text}")
        try:
            index = int(input("Write an index: "))
            if index < 0 or index >= len(texts_list):
                print("Invalid index")
                return None
            return texts_list[index]
        except ValueError:
            print("Invalid input")
            return None

def book_to_text(book_name, books_folder="books", texts_folder="texts"):
    try:
        book_converter = PDFtoTEXTConverter(
            book_name=book_name,
            books_folder=books_folder,
            texts_folder=texts_folder
        )
        book_converter.convert_to_text()
    except Exception as e:
        print(f"Error converting book to text: {e}")

def text_to_voice_espeak(path_to_text_file, text_folder="texts", temp_folder="temp", voiced_folder="voices",
                         chunk_size=1000, max_retries=1000, retry_delay=600, max_simultaneous_threads=4):
    processor = TextToVoiceProcessor(
        input_text_name=path_to_text_file,
        text_folder=text_folder,
        temp_folder=temp_folder,
        voiced_folder=voiced_folder,
        chunk_size=chunk_size, # Adjust chunk size as needed
        max_retries=max_retries, # Adjust max retries as needed
        retry_delay=retry_delay, # Adjust retry delay (in seconds) as needed
        max_simultaneous_threads=max_simultaneous_threads
    )
    processor.process_chunks()

def text_to_voice_gtts(path_to_text_file, text_folder="texts", temp_folder="temp", voiced_folder="voices",
                       chunk_size=1000, max_retries=1000, retry_delay=600, max_simultaneous_threads=4, language = "ru"):
    processor = TextToVoiceProcessorGTTS(
        input_text_name=path_to_text_file,
        text_folder=text_folder,
        temp_folder=temp_folder,
        voiced_folder=voiced_folder,
        chunk_size=chunk_size,  # Adjust chunk size as needed
        max_retries=max_retries,  # Adjust max retries as needed
        retry_delay=retry_delay,  # Adjust retry delay (in seconds) as needed
        max_simultaneous_threads=max_simultaneous_threads,
        language=language
    )
    processor.process_chunks()

def text_to_voice_free_tts(path_to_text_file, patho_to_models, model_path, text_folder="texts", temp_folder="temp",
                           voiced_folder="voices", chunk_size=1, max_retries=1, retry_delay=1,
                           max_simultaneous_threads=1, language = "us"):
    processor = TextToVoiceProcessorSelfHosted(
        input_text_name=path_to_text_file,
        text_folder=text_folder,
        temp_folder=temp_folder,
        voiced_folder=voiced_folder,
        chunk_size=chunk_size,  # Adjust chunk size as needed
        max_retries=max_retries,  # Adjust max retries as needed
        retry_delay=retry_delay,  # Adjust retry delay (in seconds) as needed
        max_simultaneous_threads=max_simultaneous_threads,
        language=language,
        patho_to_models=patho_to_models,
        model_path=model_path
    )
    processor.process_chunks()

def decision_chooser(choices):
    print("Here are your options:")
    for index, choice in enumerate(choices, start=1):
        print(f"{index}. {choice}")

    while True:
        try:
            decision = int(input("\nEnter the number of decision you want to make: "))
            if decision < 1:
                print("Please enter a valid number greater than 0.")
                continue
            return choices[decision-1]
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    choices = ["Use defult folders for books, texts, voices", "Use different folders for books, texts, voices"]
    decision = decision_chooser(choices)
    if decision == "Use different folders for books, texts, voices":
        text_folder = input("Write name of text folder: ")
        books_folder = input("Write name of books folder: ")
        voices_folder = input("Write name of voices folder: ")
    elif decision == "Use defult folders for books, texts, voices":
        text_folder = "texts"
        books_folder = "books"
        voices_folder = "voices"

    choices = ["Book to voice", "Text to voice"]
    decision = decision_chooser(choices)
    if decision == "Book to voice":
        books_list = initialize_books_folder(books_folder)
        book_name = select_book(books_list)
        if os.path.exists(f"{books_folder}/{book_name}.pdf"):
            book_to_text(book_name, books_folder, text_folder)
            text_name = book_name
        else:
            print(f"Book {books_folder}/{book_name}.pdf does not exist")
    elif decision == "Text to voice":
        texts_list = initialize_books_folder(text_folder)
        text_name = select_text(texts_list)
        if not os.path.exists(f"{text_folder}/{text_name}.txt"):
            print(f"Text {text_folder}/{text_name}.txt does not exist")

    #path_to_text_file = f"{text_folder}/{text_name}.txt"

    path_to_text_file = text_name

    choices = ["Use espeak to voice the text/book", "Use gtts to voice the text/book", "Use client side ai tts to voice the text/book"]
    decision = decision_chooser(choices)
    start_time = time.time()
    temp_folder = f"temp{random.randint(0,1000)}"
    print(temp_folder)
    if decision == "Use espeak to voice the text/book":
        text_to_voice_espeak(path_to_text_file=path_to_text_file, text_folder=text_folder, voiced_folder=voices_folder)
    elif decision == "Use gtts to voice the text/book":
        text_to_voice_gtts(path_to_text_file=path_to_text_file, text_folder=text_folder, voiced_folder=voices_folder, language="ru")
    elif decision == "Use client side ai tts to voice the text/book":
        patho_to_models = "/home/rad/PycharmProjects/PDFtoVOICE/venv/lib/python3.10/site-packages/TTS/.models.json"
        model_path = "tts_models/en/ljspeech/tacotron2-DDC"
        text_to_voice_free_tts(path_to_text_file=path_to_text_file, text_folder=text_folder, voiced_folder=voices_folder,temp_folder=temp_folder, model_path=model_path, patho_to_models=patho_to_models, max_simultaneous_threads=1)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")