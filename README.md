# DSC Jarvis Lite

DSC Jarvis Lite is a Python and Tkinter desktop assistant with voice interaction, browser automation, local AI chat, and local image generation. Its command deck combines practical Windows shortcuts with creative tools such as image creation, image-to-image editing, stories, games, and browser searches.

## Features

- **Chat Mode:** Type commands, ask questions, or use the microphone from the desktop chat window.
- **Local AI fallback:** Unrecognized prompts are sent to Ollama instead of being limited to fixed commands.
- **Image generation:** Prompts beginning with `create` generate images locally with Stable Diffusion.
- **Image-to-image editing:** Choose an image, enter an edit instruction, and save the result locally.
- **Browser search:** Prompts beginning with `show` open Google Search; prompts beginning with `photo` open Google Images.
- **Voice output:** Responses, jokes, and stories are spoken with Microsoft Edge TTS Hindi male voice `hi-IN-MadhurNeural` at increased speed.
- **Remote phone voice chat:** Use a browser on a phone connected to the same Wi-Fi network.
- **Photo downloads:** Download up to 20 subject-based images into `wallpapers/`.
- **WhatsApp actions:** Open a configured contact chat and prepare or automatically send a message with PyAutoGUI.
- **Phone calling support:** Use Windows Phone Link and a `tel:` handler for calls through a paired phone.
- **Entertainment:** Mystery stories, Wikipedia articles, trailers, British music searches, brain teasers, and Tic-Tac-Toe.
- **Windows shortcuts:** Launch VS Code, Calculator, Notepad, Paint, File Explorer, Command Prompt, and PowerShell.
- **Live utilities:** Weather searches, jokes, wallpaper downloads, and quick web actions.

## Tech Stack

- Python 3
- Tkinter for the desktop UI
- `edge-tts` with the Hindi male voice (`hi-IN-MadhurNeural`) for text-to-speech
- Hugging Face Diffusers with `Lykon/dreamshaper-8` for local text-to-image and image-to-image generation
- PyTorch CPU backend for local image generation
- Pillow for image loading and saving
- Browser integration via `webbrowser`
- PyAutoGUI for optional WhatsApp Web keyboard automation
- Optional local AI using Ollama

## Project Structure

```text
JarvisLite/
├── jarvis_lite.py
├── dsc_logo.png
├── image_ai_model/       # optional local cache; ignored by Git
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

## Chat commands

Commands are recognized when their trigger word starts the prompt:

```text
create a futuristic city at sunset
photo snowy mountain lake
show latest Python tutorials
download 3 photos of red cars
```

Generated and edited images are saved as PNG files in `wallpapers/`. The first local image-generation request downloads the DreamShaper model if `image_ai_model/` is not present, then loads it; this may take several minutes and requires roughly 8 GB of disk space on a CPU-only computer. The model files are intentionally excluded from Git because they are too large for a normal GitHub repository.

For image-to-image editing in Chat Mode:

1. Click `Choose image`.
2. Enter an instruction such as `make the sky a sunset`.
3. Click `Edit image`.

The completed image path is shown in the chat and in a confirmation dialog.

## WhatsApp and phone calls

Dad is configured as a WhatsApp contact using the number `+91 xxxxxxxxxx`. In Chat Mode:

```text
call dad
send dad I will be home at 8 PM
```

`call dad` opens Dad's direct WhatsApp Web chat. `send dad ...` opens the chat with the message filled in and uses PyAutoGUI to press Enter after 8 seconds. WhatsApp Web must already be logged in, and its browser window must remain active. Change the delay when needed:

```powershell
$env:JARVIS_WHATSAPP_SEND_DELAY = "12"
```

Automatic WhatsApp voice calls are not supported by WhatsApp Web URLs. For normal phone calls, pair a phone with Windows Phone Link and configure a `tel:` link handler. The Windows Dialer alone reports “no telephone modem” when no phone, modem, or VoIP service is connected.

## Phone voice chat

When Jarvis starts, it hosts a mobile voice-chat page on port `8765` by default. Connect the phone and computer to the same Wi-Fi network, find the computer's local IPv4 address with `ipconfig`, and open this URL on the phone:

```text
http://YOUR-PC-IP:8765
```

Use Chrome or Edge on the phone, allow microphone access, and tap `MIC ON`. To use another port:

```powershell
$env:JARVIS_PORT = "9000"
python jarvis_lite.py
```

Windows Firewall may ask for permission the first time the app hosts the page. Allow private-network access so the phone can connect. The page uses the phone browser's speech recognition and sends the resulting commands to the running desktop app.

## Photo downloads

Chat mode and phone voice chat accept commands such as:

```text
download 1 photo of mountains
download 5 photos of mountains
download 3 images about red cars
download 1 photo for space
```

Downloaded files are saved in the `wallpapers/` folder. Requests are limited to 20 images per command. This extends Jarvis's command handling; it does not rewrite or self-modify the Python program.

## Notes

- Browser-based actions open in the default browser.
- Downloaded wallpapers are saved under `wallpapers/`.
- If text-to-speech is unavailable on a machine, the app still shows the joke or story text normally.


