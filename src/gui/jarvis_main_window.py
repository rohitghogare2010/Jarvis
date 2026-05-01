"""
JARVIS OS - Main Window
Premium 3D holographic interface with glassmorphism effects.
"""

import sys
import os
import base64
import threading
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLineEdit, QLabel,
                             QStackedWidget, QSystemTrayIcon, QMenu, QFileDialog,
                             QComboBox, QCheckBox, QProgressBar, QSplitter,
                             QTabWidget, QScrollArea)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QBrush, QLinearGradient, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QRect
from PyQt6.QtCore import pyqtProperty

from ai.ollama_client import OllamaClient
from ai.image_gen import ImageGenerator
from ai.video_gen import VideoGenerator
from ai.character_engine import CharacterEngine, Character
from ai.jarvis_core import JarvisCore, get_jarvis_core
from ai.visual_discovery import VisualDiscovery, get_visual_discovery
from agents.coding_agent import CodingAgent, get_coding_agent
from agents.learning_engine import LearningEngine, get_learning_engine
from agents.project_builder import ProjectBuilder, get_project_builder
from audio.voice_io import VoiceIO
from utils.settings import Settings
from utils.os_control import OSControl
from utils.web_scraper import WebScraper
from utils.web_finder import WebFinder
from services.storage_cache import StorageCache, get_storage_cache
from services.knowledge_base import KnowledgeBase, get_knowledge_base


class PremiumButton(QPushButton):
    """Premium styled button with holographic glow effect"""
    
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hovered = False
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background gradient
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        if self.primary:
            gradient.setColorAt(0, QColor(0, 255, 255, 50))
            gradient.setColorAt(1, QColor(138, 43, 226, 50))
        else:
            gradient.setColorAt(0, QColor(100, 100, 120, 50))
            gradient.setColorAt(1, QColor(60, 60, 80, 50))
        
        # Draw rounded rectangle
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 255, 255, 100 if self.primary else 50), 2))
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 10, 10)
        
        # Draw text
        painter.setPen(Qt.GlobalColor.white)
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class GlassmorphismFrame(QWidget):
    """Widget with glassmorphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Glass background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 15))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRoundedRect(rect, 20, 20)
        
        # Inner glow
        inner_rect = rect.adjusted(1, 1, -1, -1)
        painter.setPen(QPen(QColor(0, 255, 255, 50), 1))
        painter.drawRoundedRect(inner_rect, 19, 19)


class AIWorker(QThread):
    """Background AI worker thread"""
    response_received = pyqtSignal(str)
    thinking_started = pyqtSignal()
    thinking_finished = pyqtSignal()
    
    def __init__(self, ollama, model, prompt, images=None):
        super().__init__()
        self.ollama = ollama
        self.model = model
        self.prompt = prompt
        self.images = images

    def run(self):
        self.thinking_started.emit()
        response = self.ollama.generate_response(self.model, self.prompt, self.images)
        self.thinking_finished.emit()
        self.response_received.emit(response)


class JARVISMainWindow(QMainWindow):
    """
    JARVIS OS Main Window
    Premium 3D holographic interface with all AI features.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize core systems
        self.settings = Settings()
        self.ollama = OllamaClient()
        self.os_control = OSControl()
        self.scraper = WebScraper()
        self.finder = WebFinder()
        self.char_engine = CharacterEngine(self.settings.get("cache_dir"))
        self.jarvis_core = get_jarvis_core(self.settings.get("cache_dir"))
        self.visual_discovery = get_visual_discovery(self.settings.get("cache_dir"))
        self.coding_agent = get_coding_agent()
        self.learning_engine = get_learning_engine()
        self.project_builder = get_project_builder()
        self.storage_cache = get_storage_cache(self.settings.get("cache_dir"))
        self.knowledge_base = get_knowledge_base(self.settings.get("cache_dir"))
        
        # Lazy-loaded components
        self.image_gen = None
        self.video_gen = None
        self.voice_io = None
        
        # UI State
        self.current_page = 0
        self.attached_image_path = None
        self.is_thinking = False
        
        # Window setup
        self.setWindowTitle("JARVIS OS - Advanced AI Operating System")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)
        self.animation_frame = 0
        
        self.init_ui()
        self.init_tray()
        self.refresh_character_lists()
    
    def update_animation(self):
        """Update animation frame for holographic effects"""
        self.animation_frame += 1
        if self.animation_frame > 360:
            self.animation_frame = 0
    
    def refresh_character_lists(self):
        """Refresh character selection lists"""
        chars = self.char_engine.list_characters()
        
        for combo in [self.img_char_select, self.vid_char_select]:
            current = combo.currentText() if combo.count() > 0 else ""
            combo.clear()
            combo.addItem("No Character")
            combo.addItems(chars)
            
            # Restore selection
            if current in chars:
                combo.setCurrentText(current)
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Premium Sidebar
        self.create_sidebar(main_layout)
        
        # Main Content Area
        self.create_main_content(main_layout)
    
    def create_sidebar(self, main_layout):
        """Create premium sidebar with glassmorphism"""
        sidebar = GlassmorphismFrame()
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(15)
        
        # Logo/Title
        logo_label = QLabel("JARVIS OS")
        logo_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI';
                qproperty-alignment: AlignCenter;
            }
        """)
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons
        nav_buttons = [
            ("💬 Chat", 0),
            ("👤 Characters", 1),
            ("🎨 Image Gen", 2),
            ("🎬 Video Gen", 3),
            ("🔍 Web Finder", 4),
            ("💻 Coding", 5),
            ("📚 Learning", 6),
            ("🏗️ Projects", 7),
            ("⚙️ OS Control", 8),
        ]
        
        self.nav_buttons = []
        for text, page in nav_buttons:
            btn = PremiumButton(text, primary=(page == 0))
            btn.clicked.connect(lambda checked, p=page: self.navigate_to(p))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Settings button at bottom
        settings_btn = PremiumButton("⚙️ Settings", primary=False)
        settings_btn.clicked.connect(lambda: self.navigate_to(9))
        sidebar_layout.addWidget(settings_btn)
        
        main_layout.addWidget(sidebar)
    
    def create_main_content(self, main_layout):
        """Create main content area with stacked pages"""
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stack for pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # Create all pages
        self.create_chat_page()
        self.create_characters_page()
        self.create_image_page()
        self.create_video_page()
        self.create_webfinder_page()
        self.create_coding_page()
        self.create_learning_page()
        self.create_projects_page()
        self.create_os_page()
        self.create_settings_page()
        
        main_layout.addWidget(content_container, 1)
    
    def create_chat_page(self):
        """Create AI Chat page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("🤖 Jarvis AI Assistant")
        header.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_history, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 14px;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input, 1)
        
        # Voice button
        voice_btn = QPushButton("🎤")
        voice_btn.setFixedSize(50, 50)
        voice_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 0.2);
                border: 1px solid rgba(0, 255, 255, 0.5);
                border-radius: 25px;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
            }
        """)
        voice_btn.clicked.connect(self.record_voice)
        input_layout.addWidget(voice_btn)
        
        # Attach button
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(50, 50)
        attach_btn.setStyleSheet("""
            QPushButton {
                background: rgba(138, 43, 226, 0.2);
                border: 1px solid rgba(138, 43, 226, 0.5);
                border-radius: 25px;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(138, 43, 226, 0.4);
            }
        """)
        attach_btn.clicked.connect(self.attach_image)
        input_layout.addWidget(attach_btn)
        
        # Send button
        send_btn = QPushButton("Send")
        send_btn.setFixedSize(80, 50)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ffff, stop:1 #8a2be2);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ffff, stop:1 #ff00ff);
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        self.stack.addWidget(page)
    
    def create_characters_page(self):
        """Create Characters management page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("👤 Character Engine")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QHBoxLayout()
        
        left_col = QVBoxLayout()
        self.char_name = QLineEdit()
        self.char_name.setPlaceholderText("Character Name")
        self.char_age = QLineEdit()
        self.char_age.setPlaceholderText("Age")
        
        left_col.addWidget(QLabel("Name:"))
        left_col.addWidget(self.char_name)
        left_col.addWidget(QLabel("Age:"))
        left_col.addWidget(self.char_age)
        
        right_col = QVBoxLayout()
        self.char_gender = QComboBox()
        self.char_gender.addItems(["Male", "Female", "Other"])
        self.char_type = QComboBox()
        self.char_type.addItems(["Human", "Anime", "Supernatural"])
        
        right_col.addWidget(QLabel("Gender:"))
        right_col.addWidget(self.char_gender)
        right_col.addWidget(QLabel("Type:"))
        right_col.addWidget(self.char_type)
        
        form_layout.addLayout(left_col)
        form_layout.addLayout(right_col)
        layout.addLayout(form_layout)
        
        # Description
        layout.addWidget(QLabel("Appearance Description:"))
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("Detailed appearance description...")
        self.char_desc.setMaximumHeight(100)
        layout.addWidget(self.char_desc)
        
        # Create button
        create_btn = PremiumButton("Create Character", primary=True)
        create_btn.clicked.connect(self.create_character)
        layout.addWidget(create_btn)
        
        # Character list
        layout.addWidget(QLabel("Saved Characters:"))
        self.char_list = QTextEdit()
        self.char_list.setReadOnly(True)
        self.char_list.setMaximumHeight(150)
        layout.addWidget(self.char_list, 1)
        
        self.stack.addWidget(page)
    
    def create_image_page(self):
        """Create Image Generation page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("🎨 Professional Image Generation")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Prompt input
        self.image_prompt = QLineEdit()
        self.image_prompt.setPlaceholderText("Enter your image prompt...")
        layout.addWidget(self.image_prompt)
        
        # Options row
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("Character:"))
        self.img_char_select = QComboBox()
        self.img_char_select.addItem("No Character")
        options_layout.addWidget(self.img_char_select)
        
        options_layout.addWidget(QLabel("Style:"))
        self.img_style_select = QComboBox()
        self.img_style_select.addItems(["Realistic", "Anime", "Supernatural", "Movie"])
        options_layout.addWidget(self.img_style_select)
        
        options_layout.addWidget(QLabel("Quality:"))
        self.img_quality_select = QComboBox()
        self.img_quality_select.addItems(["8K", "16K"])
        options_layout.addWidget(self.img_quality_select)
        
        layout.addLayout(options_layout)
        
        # Generate button
        self.gen_image_btn = PremiumButton("Generate Professional Image", primary=True)
        self.gen_image_btn.clicked.connect(self.generate_image)
        layout.addWidget(self.gen_image_btn)
        
        # Progress
        self.image_progress = QProgressBar()
        self.image_progress.setVisible(False)
        layout.addWidget(self.image_progress)
        
        # Display
        self.image_display = QLabel()
        self.image_display.setMinimumHeight(300)
        self.image_display.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 10px;
                qproperty-alignment: AlignCenter;
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.image_display.setText("Generated image will appear here")
        layout.addWidget(self.image_display, 1)
        
        self.stack.addWidget(page)
    
    def create_video_page(self):
        """Create Video Generation page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("🎬 Video/Movie Generation")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Prompt
        self.video_prompt = QLineEdit()
        self.video_prompt.setPlaceholderText("Enter movie/video idea or scene description...")
        layout.addWidget(self.video_prompt)
        
        # Character selection
        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Main Character:"))
        self.vid_char_select = QComboBox()
        self.vid_char_select.addItem("No Character")
        char_layout.addWidget(self.vid_char_select)
        char_layout.addStretch()
        layout.addLayout(char_layout)
        
        # Generate button
        self.gen_video_btn = PremiumButton("Generate Supernatural Movie/Video", primary=True)
        self.gen_video_btn.clicked.connect(self.generate_video)
        layout.addWidget(self.gen_video_btn)
        
        # Status
        self.video_status = QTextEdit()
        self.video_status.setReadOnly(True)
        self.video_status.setMaximumHeight(100)
        layout.addWidget(self.video_status)
        
        # Progress
        self.video_progress = QProgressBar()
        self.video_progress.setVisible(False)
        layout.addWidget(self.video_progress)
        
        # Status display
        self.video_display = QLabel()
        self.video_display.setMinimumHeight(200)
        self.video_display.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(138, 43, 226, 0.3);
                border-radius: 10px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.video_display.setText("Video status display")
        layout.addWidget(self.video_display, 1)
        
        self.stack.addWidget(page)
    
    def create_webfinder_page(self):
        """Create Web Finder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("🔍 Web Finder")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Search input
        search_layout = QHBoxLayout()
        self.finder_input = QLineEdit()
        self.finder_input.setPlaceholderText("Search the web...")
        self.finder_input.returnPressed.connect(self.run_search)
        search_layout.addWidget(self.finder_input, 1)
        
        search_btn = PremiumButton("Search", primary=True)
        search_btn.clicked.connect(self.run_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Results
        self.finder_results = QTextEdit()
        self.finder_results.setReadOnly(True)
        layout.addWidget(self.finder_results, 1)
        
        self.stack.addWidget(page)
    
    def create_coding_page(self):
        """Create Coding Agent page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("💻 Coding Agent")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Code input
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Enter code to analyze or execute...")
        self.code_input.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.7);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 10px;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.code_input, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        analyze_btn = PremiumButton("Analyze Code")
        analyze_btn.clicked.connect(self.analyze_code)
        actions_layout.addWidget(analyze_btn)
        
        execute_btn = PremiumButton("Execute")
        execute_btn.clicked.connect(self.execute_code)
        actions_layout.addWidget(execute_btn)
        
        create_project_btn = PremiumButton("Create Project")
        create_project_btn.clicked.connect(self.create_project)
        actions_layout.addWidget(create_project_btn)
        
        layout.addLayout(actions_layout)
        
        # Output
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.code_output.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.7);
                border: 1px solid rgba(138, 43, 226, 0.3);
                border-radius: 10px;
                color: white;
                font-family: 'Consolas', monospace;
            }
        """)
        layout.addWidget(self.code_output, 1)
        
        self.stack.addWidget(page)
    
    def create_learning_page(self):
        """Create Learning Engine page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("📚 Learning Engine")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Learn input
        learn_layout = QHBoxLayout()
        self.learn_input = QLineEdit()
        self.learn_input.setPlaceholderText("Enter topic to learn about...")
        learn_layout.addWidget(self.learn_input, 1)
        
        learn_btn = PremiumButton("Learn", primary=True)
        learn_btn.clicked.connect(self.learn_topic)
        learn_layout.addWidget(learn_btn)
        
        layout.addLayout(learn_layout)
        
        # Stats
        self.learning_stats = QTextEdit()
        self.learning_stats.setReadOnly(True)
        self.learning_stats.setMaximumHeight(100)
        layout.addWidget(self.learning_stats)
        
        # Recent learning
        self.learning_results = QTextEdit()
        self.learning_results.setReadOnly(True)
        layout.addWidget(self.learning_results, 1)
        
        self.stack.addWidget(page)
    
    def create_projects_page(self):
        """Create Project Builder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("🏗️ Project Builder")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Project name
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Project name...")
        layout.addWidget(self.project_name)
        
        # Framework selection
        framework_layout = QHBoxLayout()
        framework_layout.addWidget(QLabel("Framework:"))
        self.framework_select = QComboBox()
        self.framework_select.addItems([
            "React + Three.js", "Electron", "Next.js", 
            "Django", "FastAPI", "Flutter"
        ])
        framework_layout.addWidget(self.framework_select)
        framework_layout.addStretch()
        layout.addLayout(framework_layout)
        
        # Features
        features_layout = QHBoxLayout()
        self.has_3d_cb = QCheckBox("3D Animation")
        self.has_3d_cb.setChecked(True)
        self.has_ai_cb = QCheckBox("AI Integration")
        self.has_ai_cb.setChecked(True)
        features_layout.addWidget(self.has_3d_cb)
        features_layout.addWidget(self.has_ai_cb)
        features_layout.addStretch()
        layout.addLayout(features_layout)
        
        # Create button
        create_btn = PremiumButton("Create Premium Project", primary=True)
        create_btn.clicked.connect(self.build_project)
        layout.addWidget(create_btn)
        
        # Status
        self.project_status = QTextEdit()
        self.project_status.setReadOnly(True)
        layout.addWidget(self.project_status, 1)
        
        self.stack.addWidget(page)
    
    def create_os_page(self):
        """Create OS Control page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("⚙️ OS Control Center")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Command input
        cmd_layout = QHBoxLayout()
        self.os_cmd_input = QLineEdit()
        self.os_cmd_input.setPlaceholderText("Enter system command...")
        cmd_layout.addWidget(self.os_cmd_input, 1)
        
        run_btn = PremiumButton("Run")
        run_btn.clicked.connect(self.run_os_command)
        cmd_layout.addWidget(run_btn)
        
        layout.addLayout(cmd_layout)
        
        # Output
        self.os_output = QTextEdit()
        self.os_output.setReadOnly(True)
        layout.addWidget(self.os_output, 1)
        
        self.stack.addWidget(page)
    
    def create_settings_page(self):
        """Create Settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        header = QLabel("⚙️ Settings")
        header.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Cache directory
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("Cache Directory:"))
        self.cache_dir_input = QLineEdit(self.settings.get("cache_dir"))
        cache_layout.addWidget(self.cache_dir_input, 1)
        
        browse_btn = PremiumButton("Browse")
        browse_btn.clicked.connect(self.browse_cache_dir)
        cache_layout.addWidget(browse_btn)
        
        layout.addLayout(cache_layout)
        
        # Autostart
        self.autostart_cb = QCheckBox("Start with Windows")
        self.autostart_cb.toggled.connect(self.os_control.set_autostart)
        layout.addWidget(self.autostart_cb)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "English", "Hindi", "Marathi", "Tamil", 
            "Telugu", "Kannada", "Punjabi", "Urdu"
        ])
        self.lang_combo.setCurrentText(self.settings.get("language"))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Voice settings
        self.voice_cb = QCheckBox("Enable Voice Output")
        self.voice_cb.setChecked(self.settings.get("voice_enabled"))
        layout.addWidget(self.voice_cb)
        
        # Save button
        save_btn = PremiumButton("Save Settings", primary=True)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        # Storage info
        layout.addWidget(QLabel("Storage Statistics:"))
        self.storage_info = QTextEdit()
        self.storage_info.setReadOnly(True)
        layout.addWidget(self.storage_info, 1)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("JARVIS OS Ready")
        self.status_label.setStyleSheet("color: #00ff00;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self.stack.addWidget(page)
    
    def init_tray(self):
        """Initialize system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("JARVIS OS")
        
        show_action = QAction("Show JARVIS", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def navigate_to(self, page_index):
        """Navigate to a specific page"""
        self.stack.setCurrentIndex(page_index)
        
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("primary", i == page_index)
        
        # Update status
        self.status_label.setText(f"Current: {['Chat', 'Characters', 'Image Gen', 'Video Gen', 'Web Finder', 'Coding', 'Learning', 'Projects', 'OS Control', 'Settings'][page_index]}")
    
    # ============== Action Methods ==============
    
    def send_message(self):
        """Send chat message"""
        prompt = self.chat_input.text()
        if not prompt and not self.attached_image_path:
            return
        
        self.chat_history.append(f"<b style='color:#00ffff'>You:</b> {prompt}")
        self.chat_input.clear()
        
        images = []
        if self.attached_image_path:
            with open(self.attached_image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                images.append(img_data)
            self.chat_history.append(f"<i style='color:#888'>Attached: {os.path.basename(self.attached_image_path)}</i>")
            self.attached_image_path = None
        
        # Check for commands
        if prompt.startswith("/scrape "):
            url = prompt.replace("/scrape ", "").strip()
            text = self.scraper.scrape_text(url)
            self.chat_history.append(f"<b style='color:#ff00ff'>JARVIS:</b> {text[:2000]}...")
            return
        
        if prompt.startswith("/learn "):
            topic = prompt.replace("/learn ", "").strip()
            self.learn_topic(topic)
            return
        
        # Use AI
        model = self.settings.get("ollama_model")
        if images and model == "llama3":
            model = "llava"
        
        self.worker = AIWorker(self.ollama, model, prompt, images)
        self.worker.response_received.connect(self.display_response)
        self.worker.start()
    
    def display_response(self, response):
        """Display AI response"""
        self.chat_history.append(f"<b style='color:#ff00ff'>JARVIS:</b> {response}")
        
        if self.settings.get("voice_enabled"):
            self.speak_response(response)
    
    def speak_response(self, text):
        """Speak response using TTS"""
        if not self.voice_io:
            self.voice_io = VoiceIO(language=self.settings.get("language").lower())
        threading.Thread(target=self.voice_io.speak, args=(text[:500],)).start()
    
    def record_voice(self):
        """Record voice input"""
        try:
            if not self.voice_io:
                self.voice_io = VoiceIO()
            audio_path = self.voice_io.record_audio()
            text, lang = self.voice_io.transcribe(audio_path)
            self.chat_input.setText(text)
            self.chat_history.append(f"<i style='color:#888'>Detected ({lang}): {text}</i>")
        except Exception as e:
            self.chat_history.append(f"<i style='color:#ff0000'>Voice error: {e}</i>")
    
    def attach_image(self):
        """Attach an image to chat"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if file_path:
            self.attached_image_path = file_path
            self.chat_history.append(f"<i style='color:#888'>Attached: {os.path.basename(file_path)}</i>")
    
    def create_character(self):
        """Create a new character"""
        name = self.char_name.text()
        age = int(self.char_age.text()) if self.char_age.text().isdigit() else 25
        gender = self.char_gender.currentText()
        char_type = self.char_type.currentText()
        desc = self.char_desc.toPlainText()
        
        if name:
            self.char_engine.create_character(name, age, gender, char_type, desc)
            self.chat_history.append(f"<b style='color:#00ff00'>System:</b> Character '{name}' created!")
            self.refresh_character_lists()
            self.char_name.clear()
            self.char_age.clear()
            self.char_desc.clear()
    
    def generate_image(self):
        """Generate image"""
        prompt = self.image_prompt.text()
        if not prompt:
            return
        
        self.gen_image_btn.setEnabled(False)
        self.image_progress.setVisible(True)
        self.image_progress.setValue(0)
        
        def generate():
            if not self.image_gen:
                self.image_gen = ImageGenerator(self.settings.get("cache_dir"))
            
            char_name = self.img_char_select.currentText()
            character = self.char_engine.get_character(char_name) if char_name != "No Character" else None
            style = self.img_style_select.currentText().lower()
            quality = self.img_quality_select.currentText()
            
            image = self.image_gen.generate_professional(prompt, character=character, style=style, quality=quality)
            upscaled = self.image_gen.upscale_tiled(image, prompt)
            path = self.image_gen.save_image(upscaled, "jarvis_gen.png")
            
            QApplication.postEvent(self, ImageGeneratedEvent(path))
        
        threading.Thread(target=generate).start()
    
    def generate_video(self):
        """Generate video"""
        prompt = self.video_prompt.text()
        if not prompt:
            return
        
        self.gen_video_btn.setEnabled(False)
        self.video_status.setText("Generating video...")
        
        char_name = self.vid_char_select.currentText()
        character = self.char_engine.get_character(char_name) if char_name != "No Character" else None
        
        if not self.video_gen:
            self.video_gen = VideoGenerator(self.settings.get("cache_dir"))
        
        status = self.video_gen.generate_movie(prompt, characters=[character] if character else None)
        self.video_status.setText(status)
        self.gen_video_btn.setEnabled(True)
    
    def run_search(self):
        """Run web search"""
        query = self.finder_input.text()
        if not query:
            return
        
        self.finder_results.setText(f"Searching for: {query}...")
        
        def search():
            results = self.finder.search(query)
            
            if not results:
                QApplication.postEvent(self, SearchResultsEvent([]))
                return
            
            QApplication.postEvent(self, SearchResultsEvent(results))
        
        threading.Thread(target=search).start()
    
    def analyze_code(self):
        """Analyze code"""
        code = self.code_input.toPlainText()
        if not code:
            return
        
        result = self.coding_agent.analyze_code(code)
        output = f"Analysis Results:\n"
        output += f"- Language: {result['language']}\n"
        output += f"- Lines: {result['line_count']}\n"
        output += f"- Bugs found: {len(result['bugs'])}\n"
        
        if result['bugs']:
            output += "\nIssues:\n"
            for bug in result['bugs']:
                output += f"  - Line {bug['line']}: {bug['message']}\n"
        
        self.code_output.setText(output)
    
    def execute_code(self):
        """Execute code"""
        code = self.code_input.toPlainText()
        if not code:
            return
        
        from agents.coding_agent import Language
        result = self.coding_agent.execute_code(code, Language.PYTHON)
        
        output = f"Execution Result:\n"
        output += f"- Success: {result['success']}\n"
        output += f"- Output:\n{result['output']}\n"
        if result['error']:
            output += f"- Error:\n{result['error']}\n"
        
        self.code_output.setText(output)
    
    def create_project(self):
        """Open project builder"""
        self.navigate_to(7)
    
    def learn_topic(self, topic=None):
        """Learn about a topic"""
        if topic is None:
            topic = self.learn_input.text()
        if not topic:
            return
        
        def learn():
            result = self.learning_engine.search_and_learn(topic)
            
            output = f"Learning Results for: {topic}\n"
            output += f"- Sources found: {result['results_found']}\n"
            output += f"- Items learned: {result['learned']}\n"
            
            QApplication.postEvent(self, LearningResultsEvent(output))
        
        threading.Thread(target=learn).start()
    
    def build_project(self):
        """Build a project"""
        from agents.project_builder import ProjectSpec, ProjectType
        
        name = self.project_name.text()
        if not name:
            name = f"project_{int(time.time())}"
        
        framework = self.framework_select.currentText().split()[0].lower()
        
        spec = ProjectSpec(
            name=name,
            project_type=ProjectType.WEBAPP,
            framework=framework,
            has_3d=self.has_3d_cb.isChecked(),
            has_ai=self.has_ai_cb.isChecked()
        )
        
        result = self.project_builder.create_project(spec)
        
        output = f"Project '{name}' Creation Result:\n"
        output += f"- Success: {result['success']}\n"
        if result['success']:
            output += f"- Location: {result['project_dir']}\n"
            output += f"- Files created: {len(result['files_created'])}\n"
        else:
            output += f"- Error: {result['error']}\n"
        
        self.project_status.setText(output)
    
    def run_os_command(self):
        """Run OS command"""
        cmd = self.os_cmd_input.text()
        if not cmd:
            return
        
        output = self.os_control.execute_command(cmd)
        self.os_output.append(f"> {cmd}\n{output[:1000]}")
    
    def browse_cache_dir(self):
        """Browse for cache directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if dir_path:
            self.cache_dir_input.setText(dir_path)
    
    def save_settings(self):
        """Save settings"""
        self.settings.set("cache_dir", self.cache_dir_input.text())
        self.settings.set("language", self.lang_combo.currentText())
        self.settings.set("voice_enabled", self.voice_cb.isChecked())
        
        if not os.path.exists(self.cache_dir_input.text()):
            os.makedirs(self.cache_dir_input.text(), exist_ok=True)
        
        self.chat_history.append("<b style='color:#00ff00'>System:</b> Settings saved!")
        
        # Update storage info
        stats = self.storage_cache.get_stats()
        self.storage_info.setText(f"Cache: {stats['current_size_gb']:.2f}GB / {stats['max_size_gb']:.2f}GB ({stats['usage_percent']:.1f}%)\n")
        self.storage_info.append(f"Items: {stats['item_count']}\n")
        self.storage_info.append(f"Hit Rate: {stats['hit_rate']:.1%}")


class ImageGeneratedEvent(QEvent):
    """Custom event for image generation completion"""
    def __init__(self, path):
        super().__init__(QEvent.Type.User)
        self.path = path


class SearchResultsEvent(QEvent):
    """Custom event for search results"""
    def __init__(self, results):
        super().__init__(QEvent.Type.User + 1)
        self.results = results


class LearningResultsEvent(QEvent):
    """Custom event for learning results"""
    def __init__(self, output):
        super().__init__(QEvent.Type.User + 2)
        self.output = output


from PyQt6.QtCore import QEvent

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = JARVISMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
