import os

class FileMerger:
    def __init__(self, input_folder, output_file):
        self.input_folder = input_folder
        # get files, store in order
        self.input_files = [os.path.join(self.input_folder, x) for x in sorted(os.listdir(self.input_folder), key=lambda x: int(x[5:-4]))]
        self.output_file = output_file

    def execute(self):
        with open(self.output_file, "wb") as output:

            # get mp3 header
            with open(self.input_files[0], "rb") as f:

                header = f.read(76)

            output.write(header)

            # one by one dump data into putput
            for file in self.input_files:
                with open(file, "rb") as f:
                    f.seek(76)
                    data = f.read()

                    output.write(data)


if __name__ == "__main__":
    a = FileMerger(input_folder="/home/rad/Books-to-Voice-with-AI/tempCOPY", output_file="output.mp3")
    a.execute()
