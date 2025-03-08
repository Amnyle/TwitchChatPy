from pathlib import Path
from openai import OpenAI
import random
import os
import platform
import pygame
import time

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]

speech_file_path = Path(__file__).parent / "speech.mp3"

pygame.mixer.init()  # Initialize the mixer

def play_audio(file_path):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load(str(file_path))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def play_voice(text):
    try:
        # Make sure previous file handle is closed
        pygame.mixer.music.unload()
        
        # Wait a moment to ensure file is released
        time.sleep(0.1)
        
        # Use consistent file path
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(str(speech_file_path))
    except PermissionError:
        print(f"Permission error. Waiting and trying again...")
        time.sleep(1)
        # Try one more time with a different filename
        alt_path = Path(__file__).parent / f"speech_{int(time.time())}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice= random.choice(voices),
            input=text,
        ) as response:
            response.stream_to_file(str(alt_path))
        return alt_path
    return speech_file_path

def test_play_voice(text):
    print("Starting test...")
    file_to_play = play_voice(text)
    play_audio(file_to_play)
    print("Test completed.")

# test_play_voice("Hello, this is a test of the AI voice system.")
# test_play_voice("This is another test of the AI voice system.")
