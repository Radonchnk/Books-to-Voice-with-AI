import time

from pydub import AudioSegment
import os
from concurrent.futures import ThreadPoolExecutor
import math
import psutil

class FileMerger:
    def __init__(self, inputDirectory, outputFile, maxWorkers=4):
        self.inputDirectory = inputDirectory
        self.outputFile = outputFile
        self.fileNames = os.listdir(self.inputDirectory)
        self.files = []
        self.maxWorkers = maxWorkers
        self.enoughRam = self.__checkIfEnoughRam()

    def __loadFile(self, fileName):
        return AudioSegment.from_file(os.path.join(self.inputDirectory, fileName))

    def __loadFilesIntoList(self):
        with ThreadPoolExecutor(max_workers=self.maxWorkers) as executor:
            self.files = list(executor.map(self.__loadFile, self.fileNames))
        print(f"Loaded {len(self.files)} files")

    def __mergeFilesChunk(self, files):
        audio = AudioSegment.empty()
        for file in files:
            audio += file
        return audio

    def __mergeFilesOnRam(self):
        self.__loadFilesIntoList()

        chunkSize = math.ceil(len(self.files) / self.maxWorkers)
        chunks = [self.files[i:i + chunkSize] for i in range(0, len(self.files), chunkSize)]

        with ThreadPoolExecutor(max_workers=self.maxWorkers) as executor:
            merged_chunks = list(executor.map(self.__mergeFilesChunk, chunks))

        final_audio = AudioSegment.empty()
        for chunk in merged_chunks:
            final_audio += chunk

        return final_audio

    def saveFile(self, audio):
        audio.export(self.outputFile + ".mp3", format="mp3")

    def __checkIfEnoughRam(self):
        memoryInfo = psutil.virtual_memory()
        availableMemory = memoryInfo.available
        memoryRequired = self.__getDirectorySize()
        if availableMemory > memoryRequired:
            return True
        return False
    
    def __getDirectorySize(self):
        size = 0
        for dirpath, dirnames, filenames in os.walk(self.inputDirectory):
            for filename in filenames:
                filePath = os.path.join(dirpath, filename)
                size += os.path.getsize(filePath)
        return size

    def mergeManager(self):
        if self.enoughRam:
            return self.__mergeFilesOnRam()
        else:
            # CHANGE SOON!!!!!!!
            print("Not enough ram, saving to disk")
            return self.__mergeFilesOnRam()

if __name__ == "__main__":
    fileMerger = FileMerger('./../temp482', './smalltext', 12)
    start = time.time()
    audio = fileMerger.mergeManager()
    fileMerger.saveFile(audio)
    end = time.time()
    print(f"Time taken: {end - start}")