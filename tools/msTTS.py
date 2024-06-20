import pyttsx3
import wave


def save_speech_to_wav(text, output_filename):
    engine = pyttsx3.init()

    # Set properties before adding anything to speak
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)

    # Get list of voices and select the desired one
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'Hazel' in voice.name:
            engine.setProperty('voice', voice.id)
            break

    # Save the speech to a WAV file
    engine.save_to_file(text, output_filename)
    engine.runAndWait()

# Example usage
with open("./../texts/smallText.txt", "r") as f:
    text_to_speak = f.read()
output_file = "output.wav"
save_speech_to_wav(text_to_speak, output_file)

print(f"Speech has been saved to {output_file}")
