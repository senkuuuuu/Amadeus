<div align="center">
  <img src="logo.png" alt="logo">
</div>

Greetings fellow future-gadget lab members, this is the documentation for my side project, called Amadeus, as the name implies this application aims to recreate or at least give life to Amadeus from steins;gate 0

additionally, this application is made specifically for desktops and aims to recreate Amadeus as shown in the Viktor chondria university (see episode 2 of steins;gate 0 for context)

please keep in mind that this project is still a work in progress and that im just an enthusiastic fan of steins;gate franchise, furthermore im still newbie when it comes to programming as such expect a lot of limitaions from the application

I did my best to make it as anime-accurate as possible, with that said below contains the steps on how to properly install the app in your desktop and other technical information about the app

el psy kongroo -

### 🖥️ Installation
**OPTION 1: clone the repository and bundle the app yourself**
- Step 1: clone the repository
```
git https://github.com/senkuuuuu/Amadeus.git
```

- Step 2: Install dependencies, you can make a virtual environment if you want to
```
pip install -r requirements.txt
--------------or-------------
pip install pygame-ce==2.5.5 pygame_gui==0.6.14 pyaudio soundfile numpy sounddevice python-dotenv SpeechRecognition transformers torch git+https://github.com/Xtr4F/PyCharacterAI.git@5629da4820bcd15bbb991cf0e5cd23f54d106cdd
```

- Step 3: pull the files uploaded as LFS, install [git lfs](https://git-lfs.com/) then run
```
git lfs pull
```

- Step 4: create an account in unrealspeech then obtain your own auth key:
https://unrealspeech.com/

- Step 5: find your own character ai token/key. go to the link below to find how:
https://github.com/Xtr4F/PyCharacterAI

- Step 6: create your own .env file then add the following:
```
CHARACTER_AI_TOKEN = "your character ai token"
UNREAL_VOICE_AUTHORIZATION_KEY = "your unreal voice auth key"
```

- Step 7: use pyinstaller to bundle the codebase
```
pyinstaller --onefile --name=Amadeus --icon=logo.ico --add-data "resources;resources" --add-data "emotion_analysis/custom_models/amadeus_1/*;emotion_analysis/custom_models/amadeus_1" --windowed main.py
```
<br>

**OPTION 2: Install the readily  bundled version of the application _(COMING SOON)_**

Currently, the app requires API keys (for CharacterAI and UnrealSpeech), but I’m working to eliminate this dependency. Soon, the app will:

- Run fully offline – No internet or API keys needed _(if i managed to bundle a local GPT model in the app)_.
- Be easier to use – A simple install for less tech-savvy users.

This upgrade will make Amadeus truly accessible to everyone—no technical hurdles, just plug-and-play. If you’d like to support this project (and help speed up development!), consider [donating](https://ko-fi.com/makisekurisu22217) or sharing with fellow fans! Every bit of support keeps Amadeus evolving.

Stay tuned—exciting updates are on the way!


---

### ⭐ Features
| Feature                      | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| **Log-in system**            | Uses a file-based database controlled by the main app via SQLite. log in using the credentials listed below: <br>**username:** `salieri` <br>**password:** `steins;gate` <br>**note:** case-sensitive|
| **Seamless GUI design**      | Achieved through a combination of `asyncio`, `pygame`, and `pygame_gui`.    |
| **Voice input**              | Implemented using `PyAudio`, `wave`, and `SpeechRecognition` modules.       |
| **Expressive character animation** | Powered by emotion analysis using a custom-trained DistilBERT model (trained on 3,000+ data points). |
| **Lore-accurate responses**   | Enabled by integrating Character AI with the main app using `PyCharacterAI`. |

---

### ⛓️ Limitations
- fixed window size
- large download size (because of NLP Models)
---


## 📝 To do
- make window size flexible
- clone voice of makise kurisu
- further train the model for emotion analysis
- exchange characterai with well trained GPT
---

## 👀 Sneak Peek
**Log in window**


<img src="sneak_peeks\screenshot_1.jpg" alt="log_in_window">

**Main window with terminal on**


<img src="sneak_peeks\screenshot_2.jpg" alt="idle_1">

**Main window with terminal off**


<img src="sneak_peeks\screenshot_3.jpg" alt="idle_2">

**Start up animation**


<img src="sneak_peeks\startup.gif" alt="start_up_window">

**Main window animation**


<img src="sneak_peeks\idle.gif" alt="main_window">

for more detailed sneak peeks, you can visit my [ko-fi](https://ko-fi.com/makisekurisu22217) page

---


## 🎁 Support
support the development of our beloved amadeus, any form of support is welcomed, whether through code contributions or financial donations

ko-fi: https://ko-fi.com/makisekurisu22217 

