# The code is a voice-activated assistant that offers multiple functionalities, including opening Chrome, 
# checking the time, playing videos on YouTube, sending emails, fetching news, providing Wikipedia summaries, and 
# translating voice inputs. Additionally, it integrates with the GPT4All model to respond to user prompts when the 
# wake word "jarvis" is detected. The user can select a specific function or activate the continuous listening mode 
# for the wake word. When the wake word is recognized, the assistant listens to the user's prompt, processes it, and 
# responds using text-to-speech functionality.


import os
import sys
import time
import warnings
import speech_recognition as sr
import datetime
import subprocess
import pywhatkit
import webbrowser
import yagmail
from GoogleNews import GoogleNews
import wikipedia
from google_trans_new import google_translator
from gpt4all import GPT4All
import whisper

# Constants
WAKE_WORD = 'jarvis'
MODEL_PATH = "/Users/YOUR_USERNAME_HERE/Library/Application Support/nomic.ai/GPT4All/ggml-model-gpt4all-falcon-q4_0.bin"
TINY_MODEL_PATH = os.path.expanduser('~/.cache/whisper/tiny.pt')
BASE_MODEL_PATH = os.path.expanduser('~/.cache/whisper/base.pt')

# Initialize
model = GPT4All(MODEL_PATH, allow_download=False)
r = sr.Recognizer()
tiny_model = whisper.load_model(TINY_MODEL_PATH)
base_model = whisper.load_model(BASE_MODEL_PATH)
source = sr.Microphone()
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribe', lineno=114)

if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()

# Initialize from JarvisPrototype
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
recognizer = sr.Recognizer()
googlenews = GoogleNews()

def listen_to_command():
    with sr.Microphone() as source:
        print("Clearing background noises... Please wait")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print('Listening...')
        recordedaudio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(recordedaudio, language='en_US')
            return text.lower()
        except Exception as ex:
            print(ex)
            return ""

def desk_to_paissant():
    text = listen_to_command()
    if 'chrome' in text:
        engine.say('Opening chrome..')
        engine.runAndWait()
        programName = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        subprocess.Popen([programName])
    elif 'time' in text:
        time = datetime.datetime.now().strftime('%I:%M %p')
        engine.say(time)
        engine.runAndWait()
    elif 'play' in text:
        engine.say('Opening youtube..')
        engine.runAndWait()
        pywhatkit.playonyt(text)
    elif 'youtube' in text:
        engine.say('Opening youtube')
        engine.runAndWait()
        webbrowser.open('www.youtube.com')

def email_assistant():
    text = listen_to_command()
    reciever = 'Receiver_email_id'
    sender = yagmail.SMTP('Sender_email_id')
    sender.send(to=reciever, subject='This is an automated mail', contents=text)

def music_and_news_ai():
    text = listen_to_command()
    if 'headlines' in text:
        engine.say('Getting news for you')
        engine.runAndWait()
        googlenews.get_news('Today news')
        a = googlenews.gettext()
        print(*a[1:5], sep=',')
    elif 'tech' in text:
        engine.say('Getting tech news for you')
        engine.runAndWait()
        googlenews.get_news('Tech')
        a = googlenews.gettext()
        print(*a[1:5], sep=',')
    elif 'politics' in text:
        engine.say('Getting political news for you')
        engine.runAndWait()
        googlenews.get_news('Politics')
        a = googlenews.gettext()
        print(*a[1:5], sep=',')
    elif 'sports' in text:
        engine.say('Getting sports news for you')
        engine.runAndWait()
        googlenews.get_news('Sports')
        a = googlenews.gettext()
        print(*a[1:5], sep=',')
    elif 'cricket' in text:
        engine.say('Getting cricket news for you')
        engine.runAndWait()
        googlenews.get_news('cricket')
        a = googlenews.gettext()
        print(*a[1:5], sep=',')

def virassitant():
    text = listen_to_command()
    wikisearch = wikipedia.summary(text)
    engine.say(wikisearch)
    engine.runAndWait()

def voice_translator():
    text = listen_to_command()
    langinput = input('Type the language you want to convert:')
    translator = google_translator()
    translate_text = translator.translate(text, lang_tgt=langinput)
    engine.say(translate_text)
    engine.runAndWait()

# Functions from the voice-activated assistant
def speak(text):
    """Convert text to speech."""
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        os.system(f"say '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()

def listen_for_wake_word(audio):
    """Detect the wake word and respond."""
    with open("wake_detect.wav", "wb") as f:
        f.write(audio.get_wav_data())
    result = tiny_model.transcribe('wake_detect.wav')
    text_input = result['text']
    if WAKE_WORD in text_input.lower().strip():
        print("Wake word detected. Please speak your prompt to GPT4All.")
        speak('Listening')
        return False
    return True

def prompt_gpt(audio):
    """Process the user's spoken prompt and get a response from GPT4All."""
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        result = base_model.transcribe('prompt.wav')
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
            return True
        else:
            print('User: ' + prompt_text)
            output = model.generate(prompt_text, max_tokens=200)
            print('GPT4All: ', output)
            speak(output)
            print('\nSay', WAKE_WORD, 'to wake me up. \n')
            return True
    except Exception as e:
        print("Prompt error: ", e)
        return True

def callback(recognizer, audio):
    """Callback function to process audio."""
    if listen_for_wake_word(audio):
        prompt_gpt(audio)

def start_listening():
    """Start the continuous listening loop."""
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    print('\nSay', WAKE_WORD, 'to wake me up. \n')
    r.listen_in_background(source, callback)
    while True:
        time.sleep(1)

if __name__ == "__main__":
    print("Choose what you want to do:")
    print("1. Desk to Paissant")
    print("2. Email Assistant")
    print("3. Music and News AI")
    print("4. Virassitant")
    print("5. Voice Translator")
    print("6. Start Voice-Activated Assistant")
    
    choice = input("Enter your choice (1/2/3/4/5/6): ")
    
    if choice == "1":
        desk_to_paissant()
    elif choice == "2":
        email_assistant()
    elif choice == "3":
        music_and_news_ai()
    elif choice == "4":
        virassitant()
    elif choice == "5":
        voice_translator()
    elif choice == "6":
        start_listening()
    else:
        print("Invalid choice!")
