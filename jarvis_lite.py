from __future__ import annotations

import json
import asyncio
import os
import random
import re
import shutil
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, END, LEFT, NORMAL, DISABLED, Button, Canvas, Entry, Frame, Label, Listbox, PhotoImage, Scrollbar, StringVar, Text, Tk, Toplevel, filedialog, messagebox
from tkinter import ttk


APP_DIR = Path(__file__).resolve().parent
WALLPAPER_DIR = APP_DIR / "wallpapers"
OPEN_SOURCE_AI_URL = os.environ.get("JARVIS_AI_URL", "http://127.0.0.1:11434/api/chat")
OPEN_SOURCE_AI_MODEL = os.environ.get("JARVIS_AI_MODEL", "llama3.2")
VOICE_CHAT_PORT = int(os.environ.get("JARVIS_PORT", "8765"))
EDGE_TTS_VOICE = "hi-IN-MadhurNeural"
IMAGE_AI_MODEL = "Lykon/dreamshaper-8"
IMAGE_AI_MODEL_DIR = APP_DIR / "image_ai_model"
WHATSAPP_SEND_DELAY = float(os.environ.get("JARVIS_WHATSAPP_SEND_DELAY", "8"))
WHATSAPP_CONTACTS = {
    "dad": "91xxxxxxxxxxx",
}

WEATHER_CITIES = ["Mumbai"]
BRITISH_SONGS = [
    "Mr. Brightside - The Killers",
    "Back to Black - Amy Winehouse",
    "Don't Look Back in Anger - Oasis",
    "Dreams - The Cranberries",
    "Somebody Else - The 1975",
    "Yellow - Coldplay",
    "Dog Days Are Over - Florence + The Machine",
]
MYSTERY_TRAILERS = [
    "Knives Out official trailer",
    "The Prestige official trailer",
    "Murder on the Orient Express official trailer",
    "The Girl with the Dragon Tattoo official trailer",
    "Sherlock Holmes official trailer",
]
HORROR_MYSTERY_ARTICLES = [
    "Horror fiction",
    "Gothic fiction",
    "Ghost story",
    "Unsolved mystery",
    "Detective fiction",
    "Urban legend",
    "Paranormal investigation",
    "Murder mystery",
]
WINDOWS_APPS = {
    "Visual Studio Code": ["code"],
    "Calculator": ["calc.exe"],
    "Notepad": ["notepad.exe"],
    "Paint": ["mspaint.exe"],
    "File Explorer": ["explorer.exe"],
    "Command Prompt": ["cmd.exe"],
    "PowerShell": ["powershell.exe"],
}
ENGLISH_MYSTERY_FALLBACKS = [
    (
        "The Mystery of the Old Mansion",
        "Every new moon, an abandoned mansion outside the village filled with lights. Aarav went inside to discover the truth and found a hidden room containing old maps and an unfinished diary. The last page said, 'What you are looking for is beneath the mansion.' Then a soft knock came from under the floor.",
    ),
    (
        "The Midnight Train",
        "Every night, Mira heard a train whistle from the station's closed platform. One night she went there and found an old train waiting in the fog. Inside, she found a ticket dated tomorrow with her own home address on it. When she turned it over, one message was written on the back: 'Come back.'",
    ),
    (
        "The Voice in the Locked Room",
        "In Ravi's new house, one room was always locked. Every night, he heard someone reading inside it. When he finally opened the door, the room was empty, but an open book on the desk carried today's date. The next page described Ravi's arrival in detail, even recording what he was thinking at that moment.",
    ),
    (
        "The Mirror Lake",
        "At night, a strange city appeared reflected in a village lake. Kabir spent the night beside the water with his camera. At midnight, the city's streets lit up, and the same camera appeared in a house window. The next morning, Kabir found himself standing inside that house in every photograph.",
    ),
]
ENGLISH_MYSTERY_SEARCHES = ["mystery story", "ghost story", "horror story", "detective mystery"]
BRAIN_TEASERS = [
    ("I have cities, but no houses; forests, but no trees; and water, but no fish. What am I?", "A map."),
    ("What has many keys but cannot open a single lock?", "A piano."),
    ("What gets wetter the more it dries?", "A towel."),
    ("What can travel around the world while staying in one corner?", "A stamp."),
    ("What has a head and a tail but no body?", "A coin."),
]


class JarvisLite:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("DSC Jarvis Lite")
        self.root.geometry("980x680")
        self.root.minsize(820, 580)
        self.root.configure(bg="#07121f")

        self.logo_photo = None
        self._image_pipeline = None
        logo_path = APP_DIR / "dsc_logo.png"
        if logo_path.exists():
            try:
                raw_logo = PhotoImage(file=str(logo_path))
                width = raw_logo.width()
                height = raw_logo.height()
                max_side = max(width, height)
                if max_side > 80:
                    scale = max(1, max_side // 64)
                    self.logo_photo = raw_logo.subsample(scale, scale)
                else:
                    self.logo_photo = raw_logo
                try:
                    self.root.wm_iconphoto(True, self.logo_photo)
                except Exception:
                    pass
            except Exception:
                self.logo_photo = None

        self.status = StringVar(value="Systems ready. Pick a command to begin.")
        self.last_action = StringVar(value="Awaiting instruction")
        self._build_styles()
        self._build_ui()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Panel.TFrame", background="#0d2230")
        style.configure("Title.TLabel", background="#07121f", foreground="#effcff", font=("Bahnschrift", 25, "bold"))
        style.configure("Subtitle.TLabel", background="#07121f", foreground="#6e9caf", font=("Consolas", 10))
        style.configure("Section.TLabel", background="#0d2230", foreground="#8cffc1", font=("Consolas", 11, "bold"))
        style.configure("Status.TLabel", background="#040b13", foreground="#4de3ff", font=("Consolas", 10))
        style.configure("Action.TButton", background="#123448", foreground="#e7faff", font=("Bahnschrift", 10, "bold"), padding=(12, 12), borderwidth=0)
        style.map("Action.TButton", background=[("active", "#1b6173")], foreground=[("active", "#ffffff")])
        style.configure("Chat.TButton", background="#153f56", foreground="#4de3ff", font=("Consolas", 10, "bold"), padding=(12, 7), borderwidth=1, relief="solid")
        style.map("Chat.TButton", background=[("active", "#1f7180")], foreground=[("active", "#ffffff")])

    def _build_ui(self) -> None:
        header = Frame(self.root, bg="#07121f")
        header.pack(fill="x", padx=34, pady=(28, 20))

        logo_row = Frame(header, bg="#07121f")
        logo_row.pack(anchor="w")
        if self.logo_photo is not None:
            Label(logo_row, image=self.logo_photo, bg="#07121f").pack(side="left", padx=(0, 10))
        Label(logo_row, text="DSC JARVIS LITE", bg="#07121f", fg="#effcff", font=("Bahnschrift", 25, "bold")).pack(side="left", anchor="w")
        Label(header, text="// COMMAND DECK ONLINE", bg="#07121f", fg="#6e9caf", font=("Consolas", 10)).pack(anchor="w", pady=(3, 0))

        content = Frame(self.root, bg="#07121f")
        content.pack(fill=BOTH, expand=True, padx=34)

        command_panel = ttk.Frame(content, style="Panel.TFrame")
        command_panel.pack(side=LEFT, fill="y", padx=(0, 16))
        command_canvas = Canvas(command_panel, bg="#0d2230", highlightthickness=0, width=250)
        command_canvas.pack(side=LEFT, fill="y", expand=True)
        command_scrollbar = Scrollbar(command_panel, orient="vertical", command=command_canvas.yview, bg="#176077", activebackground="#4de3ff", troughcolor="#040b13", width=14, relief="flat", borderwidth=0, highlightthickness=0)
        command_scrollbar.pack(side="right", fill="y")
        command_canvas.configure(yscrollcommand=command_scrollbar.set)
        commands = ttk.Frame(command_canvas, style="Panel.TFrame", padding=22)
        command_window = command_canvas.create_window((0, 0), window=commands, anchor="nw")

        def update_command_scrollregion(event=None) -> None:
            command_canvas.configure(scrollregion=command_canvas.bbox("all"))
            command_canvas.itemconfigure(command_window, width=command_canvas.winfo_width())

        commands.bind("<Configure>", update_command_scrollregion)
        command_canvas.bind("<Configure>", update_command_scrollregion)
        command_canvas.bind_all("<MouseWheel>", lambda event: command_canvas.yview_scroll(-int(event.delta / 120), "units"))

        ttk.Label(commands, text="COMMAND DECK", style="Section.TLabel").pack(anchor="w", pady=(0, 15))

        actions = [
            ("🌦  Open random weather", self.open_weather),
            ("🐭  Search cute mouse", self.search_mouse),
            ("😂  Tell a joke + speak", self.tell_joke),
            ("🎵  Open British song", self.open_song),
            ("🖼  Download wallpaper", self.download_wallpaper),
            ("📖  Horror / mystery Wiki", self.open_wikipedia),
            ("🎬  Mystery trailer", self.open_trailer),
            ("🧠  Brain teaser", self.brain_teaser),
            ("❌  Tic-Tac-Toe vs bot", self.open_tic_tac_toe),
            ("🪟  Open Windows app", self.open_windows_app),
            ("📚  Tell English mystery story", self.tell_english_story),
            ("🎮  Open CrazyGames", self.open_crazygames),
        ]
        for label, command in actions:
            ttk.Button(commands, text=label, command=command, style="Action.TButton", width=25).pack(fill="x", pady=4)

        stage = ttk.Frame(content, style="Panel.TFrame", padding=24)
        stage.pack(side=LEFT, fill=BOTH, expand=True)
        mission_header = Frame(stage, bg="#0d2230")
        mission_header.pack(fill="x")
        ttk.Label(mission_header, text="MISSION LOG", style="Section.TLabel").pack(side=LEFT, anchor="w")
        ttk.Button(mission_header, text="CHAT MODE  ◇", command=self.open_chat_mode, style="Chat.TButton").pack(side="right", anchor="e")

        self.action_label = Label(stage, textvariable=self.last_action, bg="#0d2230", fg="#ffcf70", font=("Bahnschrift", 18, "bold"), wraplength=560, justify=LEFT)
        self.action_label.pack(anchor="w", pady=(22, 14))

        self.log = Listbox(stage, bg="#040b13", fg="#8cffc1", selectbackground="#164b5d", selectforeground="#ffffff", relief="flat", borderwidth=0, font=("Consolas", 10), height=15, highlightthickness=1, highlightcolor="#1f6174")
        self.log.pack(fill=BOTH, expand=True)
        self._log("BOOT", "All systems nominal")
        self._log("TIP", "Actions open in your default browser")

        footer = Frame(self.root, bg="#040b13")
        footer.pack(fill="x", side="bottom")
        Label(footer, textvariable=self.status, bg="#040b13", fg="#4de3ff", font=("Consolas", 10), anchor="w").pack(fill="x", padx=34, pady=13)

    def _log(self, kind: str, message: str) -> None:
        self.log.insert(END, f"[{datetime.now():%H:%M:%S}] {kind:<5} {message}")
        self.log.see(END)

    def _set_action(self, title: str, detail: str = "") -> None:
        self.last_action.set(title)
        self.status.set(detail or title)
        self._log("RUN", detail or title)

    def _open_search(self, query: str, label: str) -> None:
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(query))
        self._set_action(label, f"Opened search: {query}")

    def _open_image_search(self, query: str) -> None:
        webbrowser.open("https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote(query))
        self._set_action("Image search opened", f"Opened Google Images for: {query}")

    def _open_whatsapp_call(self, contact: str) -> None:
        normalized_contact = contact.casefold()
        phone_number = WHATSAPP_CONTACTS.get(normalized_contact)
        if phone_number:
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_number}")
            self._set_action("WhatsApp contact opened", f"Opened {contact} in WhatsApp Web; press the voice-call button")
            return
        webbrowser.open("https://web.whatsapp.com/")
        self._set_action("WhatsApp opened", f"Find {contact} in WhatsApp Web and press the voice-call button")

    def _open_whatsapp_message(self, contact: str, message: str) -> bool:
        phone_number = WHATSAPP_CONTACTS.get(contact.casefold())
        if not phone_number:
            webbrowser.open("https://web.whatsapp.com/")
            self._set_action("WhatsApp opened", f"Find {contact} and send the prepared message")
            return False
        url = "https://web.whatsapp.com/send?" + urllib.parse.urlencode({"phone": phone_number, "text": message})
        webbrowser.open(url)
        threading.Thread(target=self._auto_send_whatsapp, args=(contact,), daemon=True).start()
        self._set_action("WhatsApp message queued", f"WhatsApp will press Send for {contact} after {WHATSAPP_SEND_DELAY:g} seconds")
        return True

    def _auto_send_whatsapp(self, contact: str) -> None:
        try:
            import pyautogui

            time.sleep(WHATSAPP_SEND_DELAY)
            pyautogui.press("enter")
            self.root.after(0, lambda: self._set_action("WhatsApp send attempted", f"Pressed Send for {contact} in the active browser window"))
        except Exception as error:
            self.root.after(0, lambda: self._set_action("WhatsApp auto-send unavailable", str(error)))

    def open_chat_mode(self) -> None:
        chat = Toplevel(self.root)
        chat.title("Jarvis Chat Mode")
        chat.geometry("720x620")
        chat.minsize(460, 420)
        chat.configure(bg="#0d2230")
        chat.transient(self.root)

        Label(chat, text="CHAT MODE", bg="#0d2230", fg="#4de3ff", font=("Bahnschrift", 18, "bold")).pack(anchor="w", padx=24, pady=(22, 3))
        Label(chat, text="Ask Jarvis to run an action or just say hello.", bg="#0d2230", fg="#6e9caf", font=("Consolas", 10)).pack(anchor="w", padx=24, pady=(0, 14))
        transcript_frame = Frame(chat, bg="#0d2230")
        transcript_frame.pack(fill=BOTH, expand=True, padx=24, pady=(0, 10))
        transcript = Text(transcript_frame, bg="#040b13", fg="#8cffc1", insertbackground="#ffffff", wrap="word", font=("Consolas", 10), relief="flat", state=DISABLED)
        transcript.pack(side=LEFT, fill=BOTH, expand=True)
        transcript_scrollbar = Scrollbar(transcript_frame, command=transcript.yview, bg="#176077", activebackground="#4de3ff", troughcolor="#040b13", width=14, relief="flat", borderwidth=0, highlightthickness=0)
        transcript_scrollbar.pack(side="right", fill="y")
        transcript.configure(yscrollcommand=transcript_scrollbar.set)
        transcript.bind("<MouseWheel>", lambda event: transcript.yview_scroll(-int(event.delta / 120), "units"))

        def write_message(speaker: str, text: str) -> None:
            transcript.config(state=NORMAL)
            transcript.insert(END, f"{speaker}: {text}\n\n")
            transcript.config(state=DISABLED)
            transcript.see(END)

        write_message("JARVIS", "Chat channel open. What shall we explore?")
        bottom = Frame(chat, bg="#0d2230")
        bottom.pack(side="bottom", fill="x", padx=24, pady=15)
        Label(bottom, text="COMMAND INPUT", bg="#0d2230", fg="#4de3ff", font=("Consolas", 10, "bold")).pack(anchor="w", pady=(0, 6))
        input_row = Frame(bottom, bg="#0d2230")
        input_row.pack(fill="x")
        entry = Entry(input_row, bg="#040b13", fg="#ffffff", insertbackground="#4de3ff", font=("Consolas", 11), relief="flat")
        entry.pack(side=LEFT, fill="x", expand=True, ipady=8, padx=(0, 10))
        selected_image = {"path": None}

        def choose_image() -> None:
            path = filedialog.askopenfilename(
                parent=chat,
                title="Choose image to edit",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
            )
            if path:
                selected_image["path"] = path
                image_button.config(text="Image selected")
                write_message("JARVIS", f"Image selected: {Path(path).name}. Enter an edit prompt, then press Edit image.")

        def edit_image() -> None:
            image_path = selected_image["path"]
            prompt = entry.get().strip()
            if not image_path:
                messagebox.showinfo("Image edit", "Choose an image first.", parent=chat)
                return
            if not prompt:
                messagebox.showinfo("Image edit", "Enter an editing instruction first.", parent=chat)
                return
            entry.delete(0, END)
            write_message("YOU", f"Edit image: {prompt}")
            write_message("JARVIS", "Preparing the local image-editing model. CPU generation may take a few minutes...")
            threading.Thread(target=self._edit_image, args=(chat, write_message, image_path, prompt), daemon=True).start()

        def process_message(text: str) -> None:
            if not text:
                return
            write_message("YOU", text)
            response = self._chat_response(text)
            self._log("CHAT", text)
            if response is None:
                write_message("JARVIS", "Thinking with the open-source AI...")
                threading.Thread(target=self._fetch_ai_reply, args=(chat, write_message, text), daemon=True).start()
            else:
                write_message("JARVIS", response)
                threading.Thread(target=self._speak, args=(response,), daemon=True).start()

        def send_message(event=None) -> str:
            text = entry.get().strip()
            if text:
                entry.delete(0, END)
                process_message(text)
            return "break"

        voice_button = Button(input_row, text="Voice", command=lambda: listen_for_command(), bg="#176077", fg="#ffffff", activebackground="#21879a", relief="flat", borderwidth=0, padx=10, pady=8)
        voice_button.pack(side=LEFT, padx=(0, 5))
        image_button = Button(input_row, text="Choose image", command=choose_image, bg="#176077", fg="#ffffff", activebackground="#21879a", relief="flat", borderwidth=0, padx=10, pady=8)
        image_button.pack(side=LEFT, padx=(0, 5))
        edit_button = Button(input_row, text="Edit image", command=edit_image, bg="#176077", fg="#ffffff", activebackground="#21879a", relief="flat", borderwidth=0, padx=10, pady=8)
        edit_button.pack(side=LEFT, padx=(0, 5))
        send = Button(input_row, text="Send", command=send_message, bg="#1f7180", fg="#ffffff", activebackground="#2b9aae", relief="flat", borderwidth=0, padx=14, pady=8)
        send.pack(side=LEFT)
        entry.bind("<Return>", send_message)
        entry.focus_set()

        def listen_for_command() -> None:
            voice_button.config(state=DISABLED, text="Listening...")
            write_message("JARVIS", "Listening through your microphone...")
            threading.Thread(target=self._listen_for_command, args=(chat, entry, voice_button, process_message), daemon=True).start()

    def _listen_for_command(self, chat: Toplevel, entry: Entry, voice_button: Button, process_message) -> None:
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            with sr.Microphone() as microphone:
                recognizer.adjust_for_ambient_noise(microphone, duration=0.5)
                audio = recognizer.listen(microphone, timeout=6, phrase_time_limit=12)
            spoken_text = recognizer.recognize_google(audio)

            def apply_result() -> None:
                if not chat.winfo_exists():
                    return
                entry.delete(0, END)
                entry.insert(0, spoken_text)
                process_message(spoken_text)
                entry.delete(0, END)
                voice_button.config(state=NORMAL, text="Voice")

            chat.after(0, apply_result)
        except Exception as error:
            error_text = "Microphone or speech recognition is unavailable."
            if error.__class__.__name__ == "WaitTimeoutError":
                error_text = "I did not hear a command before the listening window closed."
            elif error.__class__.__name__ == "UnknownValueError":
                error_text = "I could not make out those words. Please try again."

            def show_error() -> None:
                if chat.winfo_exists():
                    messagebox.showwarning("Voice input", error_text, parent=chat)
                    voice_button.config(state=NORMAL, text="Voice")

            chat.after(0, show_error)

    def _chat_response(self, text: str) -> str | None:
        message = text.lower()
        create_match = re.match(r"^\s*create(?:\s+(.+))?\s*$", text, re.IGNORECASE)
        if create_match:
            prompt = (create_match.group(1) or "a beautiful landscape").strip()
            threading.Thread(target=self._create_image, args=(prompt,), daemon=True).start()
            return f"Creating an image of: {prompt}"
        photo_match = re.match(r"^\s*photo\s+(.+?)\s*$", text, re.IGNORECASE)
        if photo_match:
            query = photo_match.group(1).strip()
            self._open_image_search(query)
            return f"Showing image results for: {query}"
        show_match = re.match(r"^\s*show\s+(.+?)\s*$", text, re.IGNORECASE)
        if show_match:
            query = show_match.group(1).strip()
            self._open_search(query, "Search result opened")
            return f"Showing browser results for: {query}"
        send_match = re.match(r"^\s*send\s+(\S+)\s+(.+?)\s*$", text, re.IGNORECASE)
        if send_match:
            contact, outgoing_message = send_match.groups()
            if self._open_whatsapp_message(contact, outgoing_message):
                return f"Message prepared for {contact}. Sending automatically in {WHATSAPP_SEND_DELAY:g} seconds."
            return f"WhatsApp Web opened. Find {contact}, then send: {outgoing_message}"
        call_match = re.match(r"^\s*call\s+(.+?)\s*$", text, re.IGNORECASE)
        if call_match:
            contact = call_match.group(1).strip()
            self._open_whatsapp_call(contact)
            if contact.casefold() in WHATSAPP_CONTACTS:
                return f"Opened WhatsApp chat for {contact}. Press the voice-call button to call."
            return f"WhatsApp Web opened for {contact}. Select that contact and press the voice-call button."
        download_match = re.search(r"\bdownload\s+(\d+)\s+(?:photos?|images?)\b(?:\s+(?:of|about|for)\s+(.+))?", message)
        if download_match:
            count = min(max(int(download_match.group(1)), 1), 20)
            subject = (download_match.group(2) or "nature architecture").strip(" .,!?")
            self.download_photos(count, subject)
            return f"Starting download of {count} photo{'s' if count != 1 else ''} about {subject}."
        if "crazygames" in message or "crazy games" in message:
            self.open_crazygames()
            return "Opening CrazyGames in your browser."
        if "story" in message or "mystery story" in message or "ghost story" in message or "horror story" in message:
            self.tell_english_story()
            return "An English mystery story is opening on screen and will be read aloud."
        if "visual studio code" in message or "vs code" in message or "vscode" in message:
            return self.launch_windows_app("Visual Studio Code")
        if "calculator" in message:
            return self.launch_windows_app("Calculator")
        if "notepad" in message:
            return self.launch_windows_app("Notepad")
        if "paint" in message:
            return self.launch_windows_app("Paint")
        if "file explorer" in message or "explorer" in message:
            return self.launch_windows_app("File Explorer")
        if "command prompt" in message or message.strip() in ("cmd", "command line"):
            return self.launch_windows_app("Command Prompt")
        if "powershell" in message:
            return self.launch_windows_app("PowerShell")
        if "open app" in message or "open application" in message or message.strip() in ("apps", "applications"):
            self.open_windows_app()
            return "Opening the Windows app list."
        if "weather" in message:
            self.open_weather()
            return "Opening a random weather forecast."
        if "mouse" in message:
            self.search_mouse()
            return "Searching for something fluffy."
        if "joke" in message:
            self.tell_joke()
            return "Fetching a joke and preparing the voice channel."
        if "song" in message or "music" in message:
            self.open_song()
            return "Opening a random British song."
        if "wallpaper" in message:
            self.download_wallpaper()
            return "Starting a wallpaper download."
        if "wikipedia" in message or "article" in message:
            self.open_wikipedia()
            return "Opening a random Wikipedia article."
        if "trailer" in message or "mystery" in message:
            self.open_trailer()
            return "Opening a mystery trailer search."
        if "teaser" in message or "riddle" in message:
            self.brain_teaser()
            return "Launching a brain teaser."
        if "tic" in message or "tac" in message or "game" in message:
            self.open_tic_tac_toe()
            return "Opening Tic-Tac-Toe."
        if re.search(r"\b(?:hello|hi|hey)\b", message):
            return "Hello. I am Jarvis. All systems are ready."
        return None

    def handle_remote_chat(self, text: str) -> str:
        result = {"response": None}
        finished = threading.Event()

        def process() -> None:
            result["response"] = self._chat_response(text)
            finished.set()

        self.root.after(0, process)
        finished.wait(timeout=10)
        response = result["response"]
        if response:
            return response
        return self._request_ai_reply(text)

    def _request_ai_reply(self, prompt: str) -> str:
        fallback = "Open-source AI is unavailable. Start Ollama and run: ollama run llama3.2"
        try:
            payload = json.dumps({
                "model": OPEN_SOURCE_AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are Jarvis Lite, a concise and helpful desktop assistant."},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }).encode("utf-8")
            request = urllib.request.Request(
                OPEN_SOURCE_AI_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "").strip() or fallback
        except Exception:
            return fallback

    def _fetch_ai_reply(self, chat: Toplevel, write_message, prompt: str) -> None:
        reply = "Open-source AI is unavailable. Start Ollama and run: ollama run llama3.2"
        try:
            payload = json.dumps({
                "model": OPEN_SOURCE_AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are Jarvis Lite, a concise and helpful desktop assistant."},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }).encode("utf-8")
            request = urllib.request.Request(
                OPEN_SOURCE_AI_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
            reply = result.get("message", {}).get("content", "").strip() or reply
        except Exception:
            self._log("NOTE", "Open-source AI endpoint unavailable")

        def display_reply() -> None:
            if chat.winfo_exists():
                write_message("JARVIS", reply)
                threading.Thread(target=self._speak, args=(reply,), daemon=True).start()

        chat.after(0, display_reply)

    def open_crazygames(self) -> None:
        webbrowser.open("https://www.crazygames.com/")
        self._set_action("CrazyGames opened", "Opening https://www.crazygames.com/ in your browser")

    def open_windows_app(self) -> None:
        app_window = Toplevel(self.root)
        app_window.title("Open Windows App")
        app_window.geometry("420x430")
        app_window.resizable(False, False)
        app_window.configure(bg="#17212b")
        app_window.transient(self.root)
        Label(app_window, text="WINDOWS APP LAUNCHER", bg="#17212b", fg="#7ee2a8", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        Label(app_window, text="Select an installed app to open", bg="#17212b", fg="#91a2ad", font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 14))

        app_list = Listbox(app_window, bg="#0c1116", fg="#7ee2a8", selectbackground="#2b5960", selectforeground="#ffffff", relief="flat", borderwidth=0, font=("Segoe UI", 11), height=11, activestyle="none")
        app_list.pack(fill=BOTH, expand=True, padx=24)
        for app_name in WINDOWS_APPS:
            app_list.insert(END, app_name)

        def launch_selected(event=None) -> str:
            selection = app_list.curselection()
            if not selection:
                return "break"
            app_name = app_list.get(selection[0])
            self.launch_windows_app(app_name)
            return "break"

        Button(app_window, text="Open selected app", command=launch_selected, bg="#2b5960", fg="#ffffff", activebackground="#3c7376", activeforeground="#ffffff", relief="flat", borderwidth=0, padx=18, pady=9, font=("Segoe UI", 10, "bold")).pack(pady=18)
        app_list.bind("<Double-1>", launch_selected)
        app_list.bind("<Return>", launch_selected)
        app_list.selection_set(0)

    def launch_windows_app(self, app_name: str) -> str:
        for executable in WINDOWS_APPS[app_name]:
            resolved = shutil.which(executable)
            if resolved:
                subprocess.Popen([resolved], creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
                self._set_action(f"Opened {app_name}", f"Launched {app_name}")
                return f"Opening {app_name}."

        if app_name == "Visual Studio Code":
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Microsoft VS Code" / "Code.exe",
            ]
            for candidate in candidates:
                if candidate.exists():
                    subprocess.Popen([str(candidate)], creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
                    self._set_action("Opened Visual Studio Code", f"Launched {candidate}")
                    return "Opening Visual Studio Code."

        message = f"{app_name} was not found on this computer."
        self._set_action("App unavailable", message)
        messagebox.showwarning("Windows app", message)
        return message

    def tell_english_story(self) -> None:
        story_window = Toplevel(self.root)
        story_window.title("English Mystery Story")
        story_window.geometry("620x390")
        story_window.minsize(480, 320)
        story_window.configure(bg="#17212b")
        story_window.transient(self.root)

        Label(story_window, text="ENGLISH MYSTERY STORY", bg="#17212b", fg="#7ee2a8", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=24, pady=(22, 3))
        title_label = Label(story_window, text="Searching the API for a mystery story...", bg="#17212b", fg="#f1c56d", font=("Segoe UI", 19, "bold"), wraplength=560, justify=LEFT)
        title_label.pack(anchor="w", padx=24, pady=(0, 14))
        story_frame = Frame(story_window, bg="#17212b")
        story_frame.pack(fill=BOTH, expand=True, padx=24)
        story_text = Text(story_frame, bg="#0c1116", fg="#f3f7f8", insertbackground="#ffffff", relief="flat", borderwidth=0, wrap="word", font=("Nirmala UI", 14), padx=16, pady=14)
        story_text.insert("1.0", "Loading a story from the Wikipedia API...")
        story_text.config(state=DISABLED)
        story_text.pack(side=LEFT, fill=BOTH, expand=True)
        story_scrollbar = Scrollbar(story_frame, orient="vertical", command=story_text.yview, bg="#3d7460", activebackground="#7ee2a8", troughcolor="#0c1116", width=14, relief="flat", borderwidth=0, highlightthickness=0)
        story_scrollbar.pack(side="right", fill="y")
        story_text.configure(yscrollcommand=story_scrollbar.set)
        story_text.bind("<MouseWheel>", lambda event: story_text.yview_scroll(-int(event.delta / 120), "units"))

        story_state = {"text": ""}
        play_button = Button(story_window, text="🔊  Play story again", state=DISABLED, command=lambda: threading.Thread(target=self._speak, args=(story_state["text"],), daemon=True).start(), bg="#2b5960", fg="#ffffff", activebackground="#3c7376", activeforeground="#ffffff", relief="flat", borderwidth=0, padx=18, pady=9, font=("Segoe UI", 10, "bold"))
        play_button.pack(pady=18)
        threading.Thread(target=self._fetch_english_mystery_story, args=(story_window, title_label, story_text, play_button, story_state), daemon=True).start()

    def _fetch_english_mystery_story(self, story_window: Toplevel, title_label: Label, story_text: Text, play_button: Button, story_state: dict[str, str]) -> None:
        title, story = random.choice(ENGLISH_MYSTERY_FALLBACKS)
        try:
            search_params = urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": random.choice(ENGLISH_MYSTERY_SEARCHES),
                "srlimit": "10",
                "format": "json",
                "utf8": "1",
            })
            request = urllib.request.Request(
                "https://en.wikipedia.org/w/api.php?" + search_params,
                headers={"User-Agent": "Jarvis Lite/1.0"},
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                search_data = json.loads(response.read().decode("utf-8"))
            results = search_data.get("query", {}).get("search", [])
            if results:
                title = random.choice(results)["title"]
                extract_params = urllib.parse.urlencode({
                    "action": "query",
                    "prop": "extracts",
                    "exintro": "1",
                    "explaintext": "1",
                    "exchars": "2200",
                    "titles": title,
                    "format": "json",
                    "formatversion": "2",
                })
                request = urllib.request.Request(
                    "https://en.wikipedia.org/w/api.php?" + extract_params,
                    headers={"User-Agent": "Jarvis Lite/1.0"},
                )
                with urllib.request.urlopen(request, timeout=8) as response:
                    pages = json.loads(response.read().decode("utf-8")).get("query", {}).get("pages", [])
                api_story = pages[0].get("extract", "").strip() if pages else ""
                if len(api_story) >= 80:
                    story = api_story
        except Exception:
            self._log("NOTE", "English story API unavailable; using a local mystery story")

        story_state["text"] = story

        def display_story() -> None:
            if not story_window.winfo_exists():
                return
            title_label.config(text=title)
            story_text.config(state="normal")
            story_text.delete("1.0", END)
            story_text.insert("1.0", story)
            story_text.config(state=DISABLED)
            play_button.config(state=NORMAL)
            self._set_action(f"English mystery story: {title}", "Story displayed on screen and being spoken")
            threading.Thread(target=self._speak, args=(story,), daemon=True).start()

        story_window.after(0, display_story)

    def open_weather(self) -> None:
        city = random.choice(WEATHER_CITIES)
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(f"weather {city}"))
        self._set_action(f"Weather: {city}", f"Opening a live forecast for {city}")

    def search_mouse(self) -> None:
        queries = ["cute mouse", "baby mouse", "fluffy mouse", "mouse doing something adorable"]
        self._open_search(random.choice(queries), "Mouse reconnaissance")

    def tell_joke(self) -> None:
        self._set_action("Fetching a joke...", "Connecting to the joke service")
        threading.Thread(target=self._fetch_joke, daemon=True).start()

    def _fetch_joke(self) -> None:
        try:
            request = urllib.request.Request("https://icanhazdadjoke.com/", headers={"Accept": "application/json", "User-Agent": "Jarvis Lite"})
            with urllib.request.urlopen(request, timeout=8) as response:
                joke = json.loads(response.read().decode("utf-8"))["joke"]
        except Exception:
            joke = "Why did the computer go to the doctor? It had a virus."
        self.root.after(0, lambda: self._show_joke(joke))

    def _show_joke(self, joke: str) -> None:
        self._set_action("Joke delivered", joke)
        self._speak(joke)
        messagebox.showinfo("Jarvis says", joke)

    def _speak(self, text: str) -> None:
        try:
            import edge_tts
            import pygame

            audio_path = APP_DIR / f".jarvis_speech_{threading.get_ident()}.mp3"
            asyncio.run(edge_tts.Communicate(text, EDGE_TTS_VOICE, rate="+35%").save(str(audio_path)))
            pygame.mixer.init()
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                threading.Event().wait(0.1)
            pygame.mixer.quit()
            audio_path.unlink(missing_ok=True)
        except Exception:
            self._log("NOTE", "Jarvis voice is unavailable; text remains on screen")

    def _wallpaper_folder_link(self) -> str:
        WALLPAPER_DIR.mkdir(exist_ok=True)
        return WALLPAPER_DIR.resolve().as_uri()

    def _open_wallpaper_folder(self) -> None:
        webbrowser.open(self._wallpaper_folder_link())

    def _create_image(self, prompt: str) -> None:
        try:
            import torch
            from diffusers import StableDiffusionPipeline

            model_source = str(IMAGE_AI_MODEL_DIR) if IMAGE_AI_MODEL_DIR.exists() else IMAGE_AI_MODEL
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_source,
                torch_dtype=torch.float32,
                safety_checker=None,
            ).to("cpu")
            result = pipeline(
                prompt=prompt,
                guidance_scale=7.5,
                num_inference_steps=20,
            ).images[0]
            WALLPAPER_DIR.mkdir(exist_ok=True)
            output_path = WALLPAPER_DIR / f"created_{datetime.now():%Y%m%d_%H%M%S}.png"
            result.save(output_path)

            def report_success() -> None:
                folder_link = self._wallpaper_folder_link()
                message = f"Image generation finished.\n\nSaved to:\n{output_path}\n\nOpen folder:\n{folder_link}"
                self._set_action("Image created", f"Saved image to {output_path} | Folder: {folder_link}")
                self._open_wallpaper_folder()
                messagebox.showinfo("Image generation complete", message, parent=self.root)

            self.root.after(0, report_success)
        except Exception as error:
            self.root.after(0, lambda: self._set_action("Image creation failed", str(error)))

    def _edit_image(self, chat: Toplevel, write_message, image_path: str, prompt: str) -> None:
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline
            from PIL import Image

            if self._image_pipeline is None:
                model_source = str(IMAGE_AI_MODEL_DIR) if IMAGE_AI_MODEL_DIR.exists() else IMAGE_AI_MODEL
                self._image_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                    model_source,
                    torch_dtype=torch.float32,
                    safety_checker=None,
                ).to("cpu")

            source_image = Image.open(image_path).convert("RGB").resize((512, 512))
            result = self._image_pipeline(
                prompt=prompt,
                image=source_image,
                strength=0.65,
                guidance_scale=7.5,
                num_inference_steps=20,
            ).images[0]
            WALLPAPER_DIR.mkdir(exist_ok=True)
            output_path = WALLPAPER_DIR / f"edited_{datetime.now():%Y%m%d_%H%M%S}.png"
            result.save(output_path)
            message = f"Image edit complete. Saved to {output_path}\nFolder: {self._wallpaper_folder_link()}"
            self._open_wallpaper_folder()
        except Exception as error:
            message = f"Image editing failed: {error}"
            self._log("NOTE", message)

        chat.after(0, lambda: write_message("JARVIS", message) if chat.winfo_exists() else None)

    def open_song(self) -> None:
        song = random.choice(BRITISH_SONGS)
        self._open_search(song + " official video", f"Now playing: {song}")

    def download_wallpaper(self) -> None:
        self._set_action("Downloading wallpaper...", "Finding a random high-resolution image")
        threading.Thread(target=self._download_wallpaper, daemon=True).start()

    def download_photos(self, count: int, subject: str) -> None:
        count = min(max(count, 1), 20)
        self._set_action("Downloading photos...", f"Finding {count} image(s) about {subject}")
        threading.Thread(target=self._download_photos, args=(count, subject), daemon=True).start()

    def _download_photos(self, count: int, subject: str) -> None:
        WALLPAPER_DIR.mkdir(exist_ok=True)
        downloaded = 0
        photo_urls = self._search_photo_urls(subject, count)
        for index, url in enumerate(photo_urls, start=1):
            path = WALLPAPER_DIR / f"photo_{datetime.now():%Y%m%d_%H%M%S}_{index}.jpg"
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Jarvis Lite/1.0"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    path.write_bytes(response.read())
                downloaded += 1
            except Exception:
                continue

        def report() -> None:
            if downloaded:
                folder_link = self._wallpaper_folder_link()
                self._set_action("Photos downloaded", f"Saved {downloaded} photo(s) | Folder: {folder_link}")
                self._open_wallpaper_folder()
            else:
                self._set_action("Download failed", "No photos could be downloaded")

        self.root.after(0, report)

    def _search_photo_urls(self, subject: str, count: int) -> list[str]:
        params = urllib.parse.urlencode({
            "action": "query",
            "generator": "search",
            "gsrsearch": subject,
            "gsrnamespace": "6",
            "gsrlimit": str(min(count, 20)),
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "1920",
            "format": "json",
            "formatversion": "2",
        })
        request = urllib.request.Request(
            "https://commons.wikimedia.org/w/api.php?" + params,
            headers={"User-Agent": "Jarvis Lite/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                pages = json.loads(response.read().decode("utf-8")).get("query", {}).get("pages", [])
            urls = []
            for page in pages:
                imageinfo = page.get("imageinfo", [])
                if imageinfo:
                    urls.append(imageinfo[0].get("thumburl") or imageinfo[0].get("url", ""))
            return [url for url in urls if url]
        except Exception:
            self._log("NOTE", "Wikimedia image search unavailable")
            return []

    def _download_wallpaper(self) -> None:
        WALLPAPER_DIR.mkdir(exist_ok=True)
        path = WALLPAPER_DIR / f"wallpaper_{datetime.now():%Y%m%d_%H%M%S}.jpg"
        url = f"https://loremflickr.com/1920/1080/nature,architecture?lock={random.randint(1, 99999)}"
        try:
            urllib.request.urlretrieve(url, path)

            def report_success() -> None:
                folder_link = self._wallpaper_folder_link()
                self._set_action("Wallpaper saved", f"Saved to {path} | Folder: {folder_link}")
                self._open_wallpaper_folder()

            self.root.after(0, report_success)
        except Exception as error:
            self.root.after(0, lambda: self._set_action("Download failed", str(error)))

    def open_wikipedia(self) -> None:
        article = random.choice(HORROR_MYSTERY_ARTICLES)
        url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(article.replace(" ", "_"))
        webbrowser.open(url)
        self._set_action("Dark knowledge unlocked", f"Opened the Wikipedia article: {article}")

    def open_trailer(self) -> None:
        trailer = random.choice(MYSTERY_TRAILERS)
        self._open_search(trailer, f"Mystery screening: {trailer.replace(' official trailer', '')}")

    def brain_teaser(self) -> None:
        question, answer = random.choice(BRAIN_TEASERS)
        self._set_action("Brain teaser", question)
        teaser = Toplevel(self.root)
        teaser.title("Brain teaser")
        teaser.geometry("480x260")
        teaser.configure(bg="#17212b")
        teaser.transient(self.root)
        Label(teaser, text="BRAIN TEASER", bg="#17212b", fg="#f1c56d", font=("Segoe UI", 11, "bold")).pack(pady=(24, 12))
        Label(teaser, text=question, bg="#17212b", fg="#f3f7f8", font=("Segoe UI", 14, "bold"), wraplength=410, justify="center").pack(padx=25)
        answer_label = Label(teaser, text="", bg="#17212b", fg="#9fe0d0", font=("Segoe UI", 12), wraplength=410)
        answer_label.pack(pady=(14, 8))

        def show_answer() -> None:
            answer_label.config(text=f"Answer: {answer}")
            show_button.config(state=DISABLED)
            self._set_action("Teaser answer revealed", answer)

        show_button = Button(teaser, text="Show answer", command=show_answer, bg="#2b5960", fg="#ffffff", activebackground="#3c7376", activeforeground="#ffffff", relief="flat", borderwidth=0, padx=18, pady=8, font=("Segoe UI", 10, "bold"))
        show_button.pack(pady=(4, 18))

    def open_tic_tac_toe(self) -> None:
        game = Toplevel(self.root)
        game.title("Tic-Tac-Toe vs Jarvis")
        game.geometry("390x500")
        game.resizable(False, False)
        game.configure(bg="#17212b")
        game.transient(self.root)

        board = [""] * 9
        cells = []
        turn_label = StringVar(value="Your move: X")
        Label(game, text="TIC-TAC-TOE", bg="#17212b", fg="#f1c56d", font=("Segoe UI", 18, "bold")).pack(pady=(24, 4))
        Label(game, textvariable=turn_label, bg="#17212b", fg="#9fe0d0", font=("Segoe UI", 10)).pack(pady=(0, 14))
        grid = Frame(game, bg="#17212b")
        grid.pack()

        def winner(state: list[str]) -> str | None:
            lines = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
            for first, second, third in lines:
                if state[first] and state[first] == state[second] == state[third]:
                    return state[first]
            return "draw" if all(state) else None

        def minimax(state: list[str], maximizing: bool) -> int:
            result = winner(state)
            if result == "O":
                return 1
            if result == "X":
                return -1
            if result == "draw":
                return 0
            scores = []
            for index, value in enumerate(state):
                if not value:
                    state[index] = "O" if maximizing else "X"
                    scores.append(minimax(state, not maximizing))
                    state[index] = ""
            return max(scores) if maximizing else min(scores)

        def finish(result: str) -> None:
            for cell in cells:
                cell.config(state=DISABLED)
            message = "You win!" if result == "X" else "Jarvis wins!" if result == "O" else "A draw."
            turn_label.set(message)
            self._set_action("Tic-Tac-Toe complete", message)

        def bot_move() -> None:
            available = [index for index, value in enumerate(board) if not value]
            if not available:
                return
            best_score = -2
            best_index = available[0]
            for index in available:
                board[index] = "O"
                score = minimax(board, False)
                board[index] = ""
                if score > best_score:
                    best_score, best_index = score, index
            board[best_index] = "O"
            cells[best_index].config(text="O", state=DISABLED, disabledforeground="#f1c56d")
            result = winner(board)
            if result:
                finish(result)
            else:
                turn_label.set("Your move: X")

        def user_move(index: int) -> None:
            if board[index] or winner(board):
                return
            board[index] = "X"
            cells[index].config(text="X", state=DISABLED, disabledforeground="#9fe0d0")
            result = winner(board)
            if result:
                finish(result)
            else:
                turn_label.set("Jarvis is thinking...")
                game.after(250, bot_move)

        for index in range(9):
            cell = Button(grid, text="", command=lambda index=index: user_move(index), width=4, height=2, bg="#1d2e38", fg="#ffffff", activebackground="#2b5960", relief="flat", borderwidth=0, font=("Segoe UI", 22, "bold"))
            cell.grid(row=index // 3, column=index % 3, padx=5, pady=5)
            cells.append(cell)

        Button(game, text="New game", command=lambda: reset_game(), bg="#2b5960", fg="#ffffff", activebackground="#3c7376", activeforeground="#ffffff", relief="flat", borderwidth=0, padx=18, pady=8, font=("Segoe UI", 10, "bold")).pack(pady=18)

        def reset_game() -> None:
            board[:] = [""] * 9
            for cell in cells:
                cell.config(text="", state=NORMAL)
            turn_label.set("Your move: X")


VOICE_CHAT_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Jarvis Voice Link</title>
<style>
    :root { color-scheme: dark; --bg: #07121f; --panel: #0d2230; --line: #1c5265; --cyan: #4de3ff; --mint: #8cffc1; --amber: #ffcf70; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: radial-gradient(circle at 80% 0%, #12384b 0, var(--bg) 42%); color: #effcff; font: 16px Consolas, monospace; }
    main { width: min(720px, 100%); margin: auto; padding: 28px 18px 24px; }
    header { border-bottom: 1px solid var(--line); padding-bottom: 18px; }
    .eyebrow { color: var(--cyan); font-size: 12px; letter-spacing: 2px; }
    h1 { margin: 8px 0 4px; font: bold 30px Bahnschrift, sans-serif; letter-spacing: 1px; }
    .subtle { color: #78a5b5; margin: 0; font-size: 13px; }
    #transcript { min-height: 48vh; max-height: 58vh; overflow-y: auto; padding: 18px 0; }
    .message { border-left: 2px solid var(--line); margin: 10px 0; padding: 10px 14px; white-space: pre-wrap; line-height: 1.5; }
    .you { border-color: var(--amber); color: #ffe6a7; }
    .jarvis { border-color: var(--mint); color: var(--mint); }
    .speaker { display: block; color: #78a5b5; font-size: 11px; margin-bottom: 5px; }
    .controls { display: flex; gap: 8px; position: sticky; bottom: 0; background: rgba(7,18,31,.94); padding-top: 12px; }
    input { min-width: 0; flex: 1; background: #040b13; border: 1px solid var(--line); color: white; padding: 13px; font: inherit; border-radius: 0; }
    button { border: 1px solid var(--cyan); background: #123f56; color: var(--cyan); padding: 12px 14px; font: bold 13px Consolas, monospace; }
    button:active, button.listening { background: #1e7180; color: white; }
    #mic { min-width: 112px; }
    @media (max-width: 480px) { main { padding: 20px 14px; } h1 { font-size: 25px; } .controls { flex-wrap: wrap; } input { flex-basis: 100%; } #mic { flex: 1; } }
</style>
</head>
<body>
<main>
    <header><div class="eyebrow">REMOTE VOICE LINK // ONLINE</div><h1>DSC JARVIS LITE</h1><p class="subtle">Speak to the Jarvis instance running on your computer.</p></header>
    <section id="transcript" aria-live="polite"><div class="message jarvis"><span class="speaker">JARVIS</span>Voice channel open. Tap the mic and speak.</div></section>
    <form class="controls" id="chat-form"><input id="message" autocomplete="off" placeholder="Type a command..." aria-label="Command input"><button type="button" id="mic">MIC ON</button><button type="submit">SEND</button></form>
</main>
<script>
const transcript = document.getElementById('transcript');
const input = document.getElementById('message');
const mic = document.getElementById('mic');
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
function addMessage(speaker, text, kind) {
    const item = document.createElement('div'); item.className = 'message ' + kind;
    const label = document.createElement('span'); label.className = 'speaker'; label.textContent = speaker;
    item.append(label, document.createTextNode(text)); transcript.append(item); transcript.scrollTop = transcript.scrollHeight;
}
async function send(text) {
    text = text.trim(); if (!text) return;
    addMessage('YOU', text, 'you'); input.value = '';
    try {
        const result = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: text}) });
        const data = await result.json(); addMessage('JARVIS', data.response || data.error, 'jarvis');
    } catch (error) { addMessage('JARVIS', 'Connection lost. Check that the desktop app is running.', 'jarvis'); }
}
document.getElementById('chat-form').addEventListener('submit', event => { event.preventDefault(); send(input.value); });
if (Recognition) {
    const recognition = new Recognition(); recognition.lang = navigator.language || 'en-US'; recognition.interimResults = false;
    recognition.onstart = () => { mic.classList.add('listening'); mic.textContent = 'LISTENING...'; };
    recognition.onend = () => { mic.classList.remove('listening'); mic.textContent = 'MIC ON'; };
    recognition.onerror = () => addMessage('JARVIS', 'Microphone access failed. Allow microphone permission and try again.', 'jarvis');
    recognition.onresult = event => { input.value = event.results[0][0].transcript; send(input.value); };
    mic.addEventListener('click', () => recognition.start());
} else {
    mic.textContent = 'MIC N/A'; mic.title = 'Use Chrome or Edge on your phone for voice input';
    mic.addEventListener('click', () => addMessage('JARVIS', 'Voice input needs Chrome or Edge on your phone. You can still type commands.', 'jarvis'));
}
</script>
</body>
</html>"""


class VoiceChatHandler(BaseHTTPRequestHandler):
	server_version = "JarvisVoice/1.0"

	def _send_json(self, payload: dict[str, str], status: int = 200) -> None:
		body = json.dumps(payload).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.send_header("Access-Control-Allow-Origin", "*")
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self) -> None:
		if self.path != "/":
			self.send_error(404)
			return
		body = VOICE_CHAT_PAGE.encode("utf-8")
		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.end_headers()
		self.wfile.write(body)

	def do_POST(self) -> None:
		if self.path != "/api/chat":
			self._send_json({"error": "Not found"}, 404)
			return
		try:
			length = int(self.headers.get("Content-Length", "0"))
			payload = json.loads(self.rfile.read(length).decode("utf-8"))
			message = str(payload.get("message", "")).strip()[:500]
			if not message:
				self._send_json({"error": "Enter a command first."}, 400)
				return
			response = self.server.jarvis.handle_remote_chat(message)
			self._send_json({"response": response})
		except Exception:
			self._send_json({"error": "Jarvis could not process that command."}, 500)

	def log_message(self, format: str, *args) -> None:
		return


def start_voice_chat_server(jarvis: JarvisLite, port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("0.0.0.0", port), VoiceChatHandler)
    server.jarvis = jarvis
    threading.Thread(target=server.serve_forever, name="jarvis-voice-server", daemon=True).start()
    return server


def main() -> None:
    root = Tk()
    jarvis = JarvisLite(root)
    try:
        server = start_voice_chat_server(jarvis, VOICE_CHAT_PORT)
        jarvis.status.set(f"Voice link ready at http://<this-PC-IP>:{VOICE_CHAT_PORT}")
        root.protocol("WM_DELETE_WINDOW", lambda: (server.shutdown(), root.destroy()))
        print(f"Phone voice chat: http://<this-PC-IP>:{VOICE_CHAT_PORT}")
    except OSError as error:
        jarvis.status.set(f"Voice link unavailable on port {VOICE_CHAT_PORT}: {error}")
    root.mainloop()


if __name__ == "__main__":
    main()
