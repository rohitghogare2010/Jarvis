import sys
import os
import base64
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLineEdit, QLabel, 
                             QStackedWidget, QSystemTrayIcon, QMenu, QFileDialog,
                             QComboBox, QCheckBox, QProgressBar)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ai.ollama_client import OllamaClient
from ai.image_gen import ImageGenerator
from ai.video_gen import VideoGenerator
from ai.character_engine import CharacterEngine, Character
from audio.voice_io import VoiceIO
from utils.settings import Settings
from utils.os_control import OSControl
from utils.web_scraper import WebScraper
from utils.web_finder import WebFinder

class AIWorker(QThread):
    response_received = pyqtSignal(str)
    
    def __init__(self, ollama, model, prompt, images=None):
        super().__init__()
        self.ollama = ollama
        self.model = model
        self.prompt = prompt
        self.images = images

    def run(self):
        response = self.ollama.generate_response(self.model, self.prompt, self.images)
        self.response_received.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.ollama = OllamaClient()
        self.os_control = OSControl()
        self.scraper = WebScraper()
        self.finder = WebFinder()
        self.char_engine = CharacterEngine(self.settings.get("cache_dir"))
        # These will be initialized on demand to save memory
        self.image_gen = None
        self.video_gen = None
        self.voice_io = None
        
        self.setWindowTitle("RS AI - Advanced AI Operating System")
        self.resize(1100, 800)
        
        self.init_ui()
        self.refresh_character_lists()
        self.init_tray()

    def refresh_character_lists(self):
        chars = self.char_engine.list_characters()
        self.img_char_select.clear()
        self.img_char_select.addItem("No Character")
        self.img_char_select.addItems(chars)
        
        self.vid_char_select.clear()
        self.vid_char_select.addItem("No Character")
        self.vid_char_select.addItems(chars)

    def create_character(self):
        name = self.char_name.text()
        age = int(self.char_age.text()) if self.char_age.text().isdigit() else 25
        gender = self.char_gender.currentText()
        char_type = self.char_type.currentText()
        desc = self.char_desc.toPlainText()
        
        if name:
            self.char_engine.create_character(name, age, gender, char_type, desc)
            self.chat_history.append(f"<b>System:</b> Character '{name}' created successfully.")
            self.refresh_character_lists()
            self.char_name.clear()
            self.char_age.clear()
            self.char_desc.clear()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(150)
        sidebar = QVBoxLayout(sidebar_widget)
        
        chat_btn = QPushButton("Chat")
        char_btn = QPushButton("Characters")
        image_btn = QPushButton("Image Gen")
        video_btn = QPushButton("Video Gen")
        finder_btn = QPushButton("Web Finder")
        os_btn = QPushButton("OS Control")
        settings_btn = QPushButton("Settings")
        
        sidebar.addWidget(chat_btn)
        sidebar.addWidget(char_btn)
        sidebar.addWidget(image_btn)
        sidebar.addWidget(video_btn)
        sidebar.addWidget(finder_btn)
        sidebar.addWidget(os_btn)
        sidebar.addStretch()
        sidebar.addWidget(settings_btn)
        
        layout.addWidget(sidebar_widget)
        
        # Main Content
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # 1. Chat Page
        self.chat_page = QWidget()
        chat_layout = QVBoxLayout(self.chat_page)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything or use /scrape [url]...")
        self.chat_input.returnPressed.connect(self.send_message)
        
        voice_btn = QPushButton("🎤")
        voice_btn.setFixedWidth(40)
        voice_btn.clicked.connect(self.record_voice)
        
        attach_btn = QPushButton("📎")
        attach_btn.setFixedWidth(40)
        attach_btn.clicked.connect(self.attach_image)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(voice_btn)
        input_layout.addWidget(attach_btn)
        input_layout.addWidget(send_btn)
        
        self.attached_image_path = None
        
        chat_layout.addWidget(self.chat_history)
        chat_layout.addLayout(input_layout)
        self.stack.addWidget(self.chat_page)
        
        # 1.5 Characters Page
        self.char_page = QWidget()
        char_layout = QVBoxLayout(self.char_page)
        self.char_name = QLineEdit()
        self.char_name.setPlaceholderText("Character Name")
        self.char_age = QLineEdit()
        self.char_age.setPlaceholderText("Age")
        self.char_gender = QComboBox()
        self.char_gender.addItems(["Male", "Female", "Other"])
        self.char_type = QComboBox()
        self.char_type.addItems(["Human", "Anime", "Supernatural"])
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("Detailed Appearance Description...")
        create_char_btn = QPushButton("Create Character")
        create_char_btn.clicked.connect(self.create_character)
        
        char_layout.addWidget(QLabel("Character Creation"))
        char_layout.addWidget(self.char_name)
        char_layout.addWidget(self.char_age)
        char_layout.addWidget(self.char_gender)
        char_layout.addWidget(self.char_type)
        char_layout.addWidget(self.char_desc)
        char_layout.addWidget(create_char_btn)
        char_layout.addStretch()
        self.stack.addWidget(self.char_page)
        
        # 2. Image Gen Page
        self.image_page = QWidget()
        image_layout = QVBoxLayout(self.image_page)
        self.image_prompt = QLineEdit()
        self.image_prompt.setPlaceholderText("Enter image prompt...")
        
        self.img_char_select = QComboBox()
        self.img_char_select.addItem("No Character")
        
        self.img_style_select = QComboBox()
        self.img_style_select.addItems(["Realistic", "Anime", "Supernatural", "Movie"])
        
        self.img_quality_select = QComboBox()
        self.img_quality_select.addItems(["8K", "16K"])
        
        self.gen_image_btn = QPushButton("Generate Professional Image")
        self.gen_image_btn.clicked.connect(self.generate_image)
        self.image_display = QLabel("Your image will appear here")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid gray;")
        
        image_layout.addWidget(QLabel("Professional Image Generation"))
        image_layout.addWidget(self.image_prompt)
        image_layout.addWidget(QLabel("Select Character:"))
        image_layout.addWidget(self.img_char_select)
        image_layout.addWidget(QLabel("Style:"))
        image_layout.addWidget(self.img_style_select)
        image_layout.addWidget(QLabel("Quality:"))
        image_layout.addWidget(self.img_quality_select)
        image_layout.addWidget(self.gen_image_btn)
        image_layout.addWidget(self.image_display, 1)
        self.stack.addWidget(self.image_page)
        
        # 3. Video Gen Page
        self.video_page = QWidget()
        video_layout = QVBoxLayout(self.video_page)
        self.video_prompt = QLineEdit()
        self.video_prompt.setPlaceholderText("Enter video prompt or movie idea...")
        
        self.vid_char_select = QComboBox()
        self.vid_char_select.addItem("No Character")
        
        self.gen_video_btn = QPushButton("Generate Supernatural Movie/Video")
        self.gen_video_btn.clicked.connect(self.generate_video)
        self.video_status = QLabel("Video generation status...")
        
        video_layout.addWidget(QLabel("Supernatural Movie/Video Generation"))
        video_layout.addWidget(self.video_prompt)
        video_layout.addWidget(QLabel("Main Character:"))
        video_layout.addWidget(self.vid_char_select)
        video_layout.addWidget(self.gen_video_btn)
        video_layout.addWidget(self.video_status, 1)
        self.stack.addWidget(self.video_page)
        
        # 3.5 Web Finder Page
        self.finder_page = QWidget()
        finder_layout = QVBoxLayout(self.finder_page)
        self.finder_input = QLineEdit()
        self.finder_input.setPlaceholderText("Search the precisely designed web finder...")
        self.finder_input.returnPressed.connect(self.run_search)
        search_btn = QPushButton("Precisely Search Web")
        search_btn.clicked.connect(self.run_search)
        self.finder_results = QTextEdit()
        self.finder_results.setReadOnly(True)
        
        finder_layout.addWidget(QLabel("Web Finder"))
        finder_layout.addWidget(self.finder_input)
        finder_layout.addWidget(search_btn)
        finder_layout.addWidget(self.finder_results)
        self.stack.addWidget(self.finder_page)
        
        # 4. OS Control Page
        self.os_page = QWidget()
        os_layout = QVBoxLayout(self.os_page)
        self.os_cmd_input = QLineEdit()
        self.os_cmd_input.setPlaceholderText("Enter system command...")
        run_cmd_btn = QPushButton("Run Command")
        run_cmd_btn.clicked.connect(self.run_os_command)
        self.os_output = QTextEdit()
        self.os_output.setReadOnly(True)
        
        os_layout.addWidget(QLabel("OS Control Center"))
        os_layout.addWidget(self.os_cmd_input)
        os_layout.addWidget(run_cmd_btn)
        os_layout.addWidget(self.os_output)
        self.stack.addWidget(self.os_page)
        
        # 5. Settings Page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout(self.settings_page)
        
        self.cache_dir_input = QLineEdit(self.settings.get("cache_dir"))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_cache_dir)
        
        self.autostart_cb = QCheckBox("Start with Windows")
        self.autostart_cb.setChecked(False) # Default
        self.autostart_cb.toggled.connect(self.os_control.set_autostart)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Punjabi", "Urdu"])
        self.lang_combo.setCurrentText(self.settings.get("language"))
        
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self.save_settings)
        
        settings_layout.addWidget(QLabel("Cache Directory (50GB storage recommended):"))
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.cache_dir_input)
        h_layout.addWidget(browse_btn)
        settings_layout.addLayout(h_layout)
        settings_layout.addWidget(self.autostart_cb)
        settings_layout.addWidget(QLabel("Preferred Language:"))
        settings_layout.addWidget(self.lang_combo)
        settings_layout.addStretch()
        settings_layout.addWidget(save_settings_btn)
        self.stack.addWidget(self.settings_page)
        
        # Sidebar Connections
        chat_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        char_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        image_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        video_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        finder_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        os_btn.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(6))

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("icon.png"))
        
        show_action = QAction("Show RS AI", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def attach_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.attached_image_path = file_path
            self.chat_history.append(f"<i>Attached image: {os.path.basename(file_path)}</i>")

    def send_message(self):
        prompt = self.chat_input.text()
        if not prompt and not self.attached_image_path:
            return
        
        self.chat_history.append(f"<b>You:</b> {prompt}")
        self.chat_input.clear()
        
        images = []
        if self.attached_image_path:
            with open(self.attached_image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                images.append(img_data)
            self.attached_image_path = None # Reset after sending

        if prompt.startswith("/scrape "):
            url = prompt.replace("/scrape ", "").strip()
            text = self.scraper.scrape_text(url)
            self.chat_history.append(f"<b>RS AI (Scraped Content):</b> {text[:1000]}...")
            return

        model = self.settings.get("ollama_model")
        # Use a vision model if an image is attached
        if images and model == "llama3": # Default might not support vision
            model = "llava" 
            
        self.worker = AIWorker(self.ollama, model, prompt, images)
        self.worker.response_received.connect(self.display_response)
        self.worker.start()

    def display_response(self, response):
        self.chat_history.append(f"<b>RS AI:</b> {response}")
        if self.settings.get("voice_enabled"):
            self.speak_response(response)

    def speak_response(self, text):
        if not self.voice_io:
            self.voice_io = VoiceIO(language=self.settings.get("language").lower())
        self.voice_io.speak(text)

    def record_voice(self):
        if not self.voice_io:
            self.voice_io = VoiceIO()
        audio_path = self.voice_io.record_audio()
        text, lang = self.voice_io.transcribe(audio_path)
        self.chat_input.setText(text)
        self.chat_history.append(f"<i>Detected language: {lang}</i>")

    def generate_image(self):
        prompt = self.image_prompt.text()
        if not prompt: return
        
        self.gen_image_btn.setEnabled(False)
        self.image_display.setText("Generating Professional 8K/16K image...")
        
        if not self.image_gen:
            self.image_gen = ImageGenerator(self.settings.get("cache_dir"))
            
        char_name = self.img_char_select.currentText()
        character = self.char_engine.get_character(char_name) if char_name != "No Character" else None
        style = self.img_style_select.currentText().lower()
        quality = self.img_quality_select.currentText()

        # In real app, run in thread
        image = self.image_gen.generate_professional(prompt, character=character, style=style, quality=quality)
        # For 16K we would do more tiling
        upscaled = self.image_gen.upscale_tiled(image, prompt)
        path = self.image_gen.save_image(upscaled, "gen_image_prof.png")
        
        pixmap = QPixmap(path)
        self.image_display.setPixmap(pixmap.scaled(self.image_display.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.gen_image_btn.setEnabled(True)

    def generate_video(self):
        prompt = self.video_prompt.text()
        if not prompt: return
        
        self.gen_video_btn.setEnabled(False)
        self.video_status.setText("Generating Supernatural Movie/Video...")
        
        if not self.video_gen:
            self.video_gen = VideoGenerator(self.settings.get("cache_dir"))
            
        char_name = self.vid_char_select.currentText()
        character = self.char_engine.get_character(char_name) if char_name != "No Character" else None

        # Placeholder for complex generation
        status = self.video_gen.generate_movie(prompt, characters=[character] if character else None)
        self.video_status.setText(status)
        self.gen_video_btn.setEnabled(True)

    def run_search(self):
        query = self.finder_input.text()
        if not query: return
        
        self.finder_results.setText(f"Searching for: {query}...")
        results = self.finder.search(query)
        
        if not results:
            self.finder_results.setText("No results found.")
            return
            
        display_text = ""
        for res in results:
            display_text += f"<b>{res['title']}</b><br>"
            display_text += f"<a href='{res['link']}'>{res['link']}</a><br>"
            display_text += f"{res['snippet']}<br><br>"
            
        self.finder_results.setHtml(display_text)

    def run_os_command(self):
        cmd = self.os_cmd_input.text()
        output = self.os_control.execute_command(cmd)
        self.os_output.append(f"> {cmd}\n{output}")

    def browse_cache_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if dir_path:
            self.cache_dir_input.setText(dir_path)

    def save_settings(self):
        self.settings.set("cache_dir", self.cache_dir_input.text())
        self.settings.set("language", self.lang_combo.currentText())
        # Ensure cache dir exists
        if not os.path.exists(self.cache_dir_input.text()):
            os.makedirs(self.cache_dir_input.text(), exist_ok=True)
        self.chat_history.append("<b>System:</b> Settings saved.")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
