import customtkinter as ctk
import pyttsx3
import sounddevice as sd
import numpy as np
import wave
from tkinter import filedialog, simpledialog, messagebox
from pydub import AudioSegment
from pydub.playback import play
from pydub import effects
import os
import subprocess
import platform
import urllib.request
import zipfile
import shutil

# Initialize pyttsx3 for speech synthesis
tts_engine = pyttsx3.init()

# Function to check and install FFmpeg if not present
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def install_ffmpeg():
    if platform.system() == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg.zip"
        
        # Download the FFmpeg zip file
        urllib.request.urlretrieve(url, zip_path)
        
        # Extract FFmpeg files
        extract_path = os.path.join(os.getcwd(), "ffmpeg")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Remove the zip file after extraction
        os.remove(zip_path)
        
        # Find ffmpeg.exe in the extracted directory
        ffmpeg_bin_path = None
        for root, dirs, files in os.walk(extract_path):
            if 'ffmpeg.exe' in files:
                ffmpeg_bin_path = os.path.join(root, 'ffmpeg.exe')
                break
        
        # Check if ffmpeg.exe was found
        if ffmpeg_bin_path:
            # Add FFmpeg to the PATH environment variable
            os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_bin_path)
            messagebox.showinfo("FFmpeg Installation", "FFmpeg installed and added to PATH successfully.")
        else:
            messagebox.showerror("FFmpeg Installation Error", "ffmpeg.exe not found in extracted files.")
    else:
        messagebox.showinfo("FFmpeg Installation", "Please install FFmpeg manually. Visit https://ffmpeg.org/download.html")


# Function to get available voices and map them to user-friendly names
def get_available_voices():
    voices = tts_engine.getProperty('voices')
    available_voice_map = {}
    
    for i, voice in enumerate(voices):
        name = voice.languages[0].lower() if voice.languages else voice.name.lower()
        if "male" in name:
            available_voice_map['Man'] = i
        elif "female" in name:
            available_voice_map['Woman'] = i
        else:
            available_voice_map[name.capitalize()] = i
    
    return available_voice_map

# Set pyttsx3 voice, rate, and volume properties
def set_tts_properties(voice_type, rate, volume):
    available_voices = get_available_voices()
    
    if voice_type in available_voices:
        voice_index = available_voices[voice_type]
        tts_engine.setProperty('voice', tts_engine.getProperty('voices')[voice_index].id)
    else:
        tts_engine.setProperty('voice', tts_engine.getProperty('voices')[0].id)
    
    tts_engine.setProperty('rate', rate)
    tts_engine.setProperty('volume', volume)

# Custom echo effect using pydub
def apply_echo(sound):
    return sound.overlay(sound, delay=500)

# Custom reverb effect using convolution
def apply_reverb(sound):
    return effects.high_pass_filter(sound, 500).overlay(effects.low_pass_filter(sound, 2000), gain_during_overlay=-6)

# Change pitch using pydub
def change_pitch(sound, pitch_factor):
    new_sample_rate = int(sound.frame_rate * (2.0 ** pitch_factor))
    return sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(44100)

import tempfile  # for temporary file management
import os
from pydub import AudioSegment

# Set the path to the ffmpeg executable and ffprobe explicitly
ffmpeg_path = (r"your\ffmpeg.exe")
ffprobe_path = (r"your\ffprobe.exe")

# Assign FFmpeg and FFprobe paths for pydub
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def speak_text_with_pitch():
    text = text_entry.get("1.0", "end-1c")
    voice_type = selected_voice.get()
    rate = get_rate_value()
    volume = volume_slider.get()
    pitch = pitch_slider.get() - 1.0  # Normalize pitch between -1.0 and 1.0
    apply_reverb_effect = reverb_var.get()
    apply_echo_effect = echo_var.get()

    # Set the text-to-speech properties
    set_tts_properties(voice_type, rate, volume)

    # Use pyttsx3 to synthesize the speech and save to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        temp_wav_path = temp_wav_file.name
        tts_engine.save_to_file(text, temp_wav_path)
        tts_engine.runAndWait()

    # Load the audio file using pydub
    sound = AudioSegment.from_wav(temp_wav_path)
    
    # Apply pitch change
    sound_with_pitch = change_pitch(sound, pitch)
    
    # Apply effects if selected
    if apply_reverb_effect:
        sound_with_pitch = apply_reverb(sound_with_pitch)
    if apply_echo_effect:
        sound_with_pitch = apply_echo(sound_with_pitch)
    
    # Play the sound with pitch modification and effects
    play(sound_with_pitch)

    # Clean up temporary file
    os.remove(temp_wav_path)

def save_text_with_pitch():
    text = text_entry.get("1.0", "end-1c")
    voice_type = selected_voice.get()
    rate = get_rate_value()
    volume = volume_slider.get()
    pitch = pitch_slider.get() - 1.0  # Normalize pitch between -1.0 and 1.0
    apply_reverb_effect = reverb_var.get()
    apply_echo_effect = echo_var.get()

    # Set the text-to-speech properties
    set_tts_properties(voice_type, rate, volume)

    # Use pyttsx3 to synthesize the speech and save to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        temp_wav_path = temp_wav_file.name
        tts_engine.save_to_file(text, temp_wav_path)
        tts_engine.runAndWait()

    # Load the audio file using pydub
    sound = AudioSegment.from_wav(temp_wav_path)
    
    # Apply pitch change
    sound_with_pitch = change_pitch(sound, pitch)

    # Apply effects if selected
    if apply_reverb_effect:
        sound_with_pitch = apply_reverb(sound_with_pitch)
    if apply_echo_effect:
        sound_with_pitch = apply_echo(sound_with_pitch)

    # Ask the user where to save the modified audio
    file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        sound_with_pitch.export(file_path, format="mp3")
    
    # Clean up temporary file
    os.remove(temp_wav_path)


# Record voice and save to WAV file
def record_voice():
    duration = simpledialog.askfloat("Input", "Enter recording duration in seconds:", minvalue=1.0, maxvalue=30.0)
    if not duration:
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if not file_path:
        return

    fs = 44100  # Sample rate
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait for recording to finish
    print("Recording finished.")
    
    # Save recording to a .wav file
    with wave.open(file_path, 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)  # Sample width in bytes
        f.setframerate(fs)
        f.writeframes(np.array(recording * 32767, dtype=np.int16).tobytes())
    
    print(f"Saved recording to {file_path}")

# GUI setup
app = ctk.CTk()
app.title("Text to Speech with Dark/Light Mode")
app.geometry("600x800")

# Dark/Light mode toggle button
def toggle_mode():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
    else:
        ctk.set_appearance_mode("Dark")

mode_button = ctk.CTkButton(app, text="Toggle Dark/Light Mode", command=toggle_mode)
mode_button.pack(pady=10)

# Text input field
text_entry = ctk.CTkTextbox(app, width=500, height=100)
text_entry.pack(pady=20)

# Voice selection dropdown with multiple languages
selected_voice = ctk.StringVar(value="Man")
available_voice_map = get_available_voices()
voice_menu = ctk.CTkOptionMenu(app, variable=selected_voice, values=list(available_voice_map.keys()))
voice_menu.pack(pady=10)

# Volume and pitch sliders
volume_slider = ctk.CTkSlider(app, from_=0.0, to=1.0, number_of_steps=10, width=300)
volume_slider.set(1.0)  # Default volume
volume_slider.pack(pady=10)

pitch_slider = ctk.CTkSlider(app, from_=0.5, to=2.0, number_of_steps=10, width=300)
pitch_slider.set(1.0)  # Default pitch (1.0 is neutral)
pitch_slider.pack(pady=10)

# Rate selection dropdown (speed control)
selected_rate = ctk.StringVar(value="Normal")
rate_menu = ctk.CTkOptionMenu(app, variable=selected_rate, values=["Slow", "Normal", "Fast"])
rate_menu.pack(pady=10)

# Reverb and Echo effect options
reverb_var = ctk.BooleanVar()
echo_var = ctk.BooleanVar()
reverb_checkbox = ctk.CTkCheckBox(app, text="Reverb", variable=reverb_var)
echo_checkbox = ctk.CTkCheckBox(app, text="Echo", variable=echo_var)
reverb_checkbox.pack(pady=10)
echo_checkbox.pack(pady=10)

# Get rate based on the selected value
def get_rate_value():
    if selected_rate.get() == "Slow":
        return 100
    elif selected_rate.get() == "Normal":
        return 150
    elif selected_rate.get() == "Fast":
        return 200
    return 150  # Default rate

# Speak and save buttons
speak_button = ctk.CTkButton(app, text="Speak Text", command=speak_text_with_pitch)
speak_button.pack(pady=10)

save_button = ctk.CTkButton(app, text="Save as MP3", command=save_text_with_pitch)
save_button.pack(pady=10)

# Record voice button
record_button = ctk.CTkButton(app, text="Record Voice", command=record_voice)
record_button.pack(pady=20)

# Run the app
app.mainloop()
