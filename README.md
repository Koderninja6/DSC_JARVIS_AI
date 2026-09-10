# DSC Jarvis Lite

DSC Jarvis Lite is a small desktop assistant built with Python and Tkinter for fun, exploration, and quick productivity shortcuts. The app includes browser actions, a local chat mode, wallpaper downloads, mystery stories, jokes, trivia, and a Tic-Tac-Toe game against a bot.

## Features

- Weather search for Mumbai
- Cute mouse search queries
- Joke generator with voice playback
- British music search
- Wallpaper download to the `wallpapers/` folder
- Horror and mystery Wikipedia links
- Mystery trailer searches
- Brain teaser popup with answer reveal
- Tic-Tac-Toe game versus a simple AI
- Windows app launcher for common apps like VS Code, Calculator, Notepad, and Paint
- Local chat mode with optional Ollama-based AI replies

## Tech Stack

- Python 3
- Tkinter for the desktop UI
- `pyttsx3` for text-to-speech
- Browser integration via `webbrowser`
- Optional local AI using Ollama

## Project Structure

```text
JarvisLite/
├── jarvis_lite.py
├── dsc_logo.png
├── wallpapers/
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run the app.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python jarvis_lite.py
```

## Run the app

```powershell
.\.venv\Scripts\python.exe jarvis_lite.py
```

## Optional AI chat

Chat mode tries to send prompts to a local Ollama server if the built-in commands do not match. You can start Ollama and pull the default model:

```powershell
ollama run llama3.2
```

The default endpoint is:

```text
http://127.0.0.1:11434/api/chat
```

You can override it with environment variables:

```powershell
$env:JARVIS_AI_URL = "http://127.0.0.1:11434/api/chat"
$env:JARVIS_AI_MODEL = "llama3.2"
```

## Notes

- Browser-based actions open in the default browser.
- Downloaded wallpapers are saved under `wallpapers/`.
- If text-to-speech is unavailable on a machine, the app still shows the joke or story text normally.

## License

This project is for educational and personal use. Add your own preferred license if you plan to publish it publicly.
