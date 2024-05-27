import os
import fitz


class PDFtoTEXTConverter:
    def __init__(self, book_name, books_folder, texts_folder):
        self.book_name = book_name
        self.books_folder = books_folder  # Folder containing PDFs
        self.texts_folder = texts_folder  # Folder to store extracted texts

    def convert_to_text(self):
        # Create the texts folder if it doesn't exist
        os.makedirs(self.texts_folder, exist_ok=True)

        # Construct input and output paths
        input_pdf_path = os.path.join(self.books_folder, f'{self.book_name}.pdf')
        output_text_path = os.path.join(self.texts_folder, f'{self.book_name}.txt')

        # Check if the input PDF file exists
        if os.path.exists(input_pdf_path):
            # Open the PDF file using fitz
            doc = fitz.open(input_pdf_path)
            text = ""

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text("text")  # Specify "text" encoding

            doc.close()

            # Join text lines with a space and remove extra newlines
            text = " ".join(text.split("\n"))

            # Write extracted text to a text file
            with open(output_text_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)
            print(f"Conversion complete. Text saved in '{output_text_path}' file.")
        else:
            print("Error: The specified PDF file does not exist.")


if __name__ == "__main__":
    # Get the name of the book from user input
    book_name = input("Enter the name of the book: ")

    # Create an instance of the PDFtoTEXTConverter class with the book name
    pdf_converter = PDFtoTEXTConverter(book_name, "books", "texts")
    pdf_converter.convert_to_text()
