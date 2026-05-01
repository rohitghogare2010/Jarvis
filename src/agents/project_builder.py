"""
Project Builder - Automated project generation with premium design
Creates fully functional projects, apps, webapps, desktop apps with 3D animation.
"""

import os
import json
import shutil
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ProjectType(Enum):
    """Types of projects that can be built"""
    WEBAPP = "webapp"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    FULLSTACK = "fullstack"


class Framework(Enum):
    """Supported frameworks"""
    # Web
    REACT = ("react", ProjectType.WEBAPP)
    VUE = ("vue", ProjectType.WEBAPP)
    ANGULAR = ("angular", ProjectType.WEBAPP)
    NEXTJS = ("nextjs", ProjectType.WEBAPP)
    SVELTE = ("svelte", ProjectType.WEBAPP)
    
    # Desktop
    ELECTRON = ("electron", ProjectType.DESKTOP)
    Tauri = ("tauri", ProjectType.DESKTOP)
    FLUTTER = ("flutter", ProjectType.DESKTOP)
    QT = ("qt", ProjectType.DESKTOP)
    
    # Backend
    DJANGO = ("django", ProjectType.FULLSTACK)
    FLASK = ("flask", ProjectType.WEBAPP)
    FASTAPI = ("fastapi", ProjectType.API)
    EXPRESS = ("express", ProjectType.WEBAPP)
    NESTJS = ("nestjs", ProjectType.API)
    SPRING = ("spring", ProjectType.FULLSTACK)
    
    # Database
    POSTGRESQL = ("postgresql", ProjectType.LIBRARY)
    MONGODB = ("mongodb", ProjectType.LIBRARY)
    REDIS = ("redis", ProjectType.LIBRARY)
    
    # Mobile
    REACT_NATIVE = ("react-native", ProjectType.MOBILE)
    FLUTTER_MOBILE = ("flutter-mobile", ProjectType.MOBILE)


@dataclass
class ProjectSpec:
    """Project specification"""
    name: str
    project_type: ProjectType
    framework: str
    description: str = ""
    features: List[str] = None
    has_auth: bool = False
    has_database: bool = False
    has_api: bool = False
    has_3d: bool = False
    has_ai: bool = False
    languages: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.languages is None:
            self.languages = ["en"]


class TemplateEngine:
    """Manages project templates"""
    
    def __init__(self):
        self.templates = {}
        self._init_templates()
    
    def _init_templates(self):
        """Initialize project templates"""
        self.templates = {
            'react_3d_modern': self._react_3d_template(),
            'electron_premium': self._electron_template(),
            'nextjs_saas': self._nextjs_template(),
            'django_fullstack': self._django_template(),
            'fastapi_modern': self._fastapi_template(),
            'flutter_desktop': self._flutter_template(),
        }
    
    def _react_3d_template(self) -> Dict[str, str]:
        """React with Three.js 3D template"""
        return {
            'package.json': json.dumps({
                "name": "{{project_name}}",
                "version": "1.0.0",
                "private": True,
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "three": "^0.160.0",
                    "@react-three/fiber": "^8.15.0",
                    "@react-three/drei": "^9.92.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^4.2.0",
                    "vite": "^5.0.0",
                    "tailwindcss": "^3.4.0",
                    "autoprefixer": "^10.4.16",
                    "postcss": "^8.4.32"
                }
            }, indent=2),
            
            'src/App.jsx': '''import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Stars } from '@react-three/drei';
import HolographicCube from './components/HolographicCube';
import PremiumLayout from './components/PremiumLayout';
import AIDashboard from './components/AIDashboard';

function App() {
  return (
    <PremiumLayout>
      <Suspense fallback={<LoadingSpinner />}>
        <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
          <HolographicCube />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
          <Environment preset="city" />
        </Canvas>
        <AIDashboard />
      </Suspense>
    </PremiumLayout>
  );
}

export default App;
''',
            'src/components/PremiumLayout.jsx': '''import React from 'react';
import Glassmorphism from './Glassmorphism';
import PremiumButton from './PremiumButton';
import './premium.css';

const PremiumLayout = ({ children }) => {
  return (
    <div className="premium-container">
      <Glassmorphism>
        <nav className="premium-nav">
          <div className="logo">JARVIS OS</div>
          <div className="nav-links">
            <PremiumButton label="Dashboard" />
            <PremiumButton label="AI Tools" />
            <PremiumButton label="Settings" primary />
          </div>
        </nav>
        <main className="premium-main">
          {children}
        </main>
        <footer className="premium-footer">
          <p>Powered by Advanced AI</p>
        </footer>
      </Glassmorphism>
    </div>
  );
};

export default PremiumLayout;
''',
            'src/components/HolographicCube.jsx': '''import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const HolographicCube = () => {
  const mesh = useRef();
  const edges = useRef();
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    mesh.current.rotation.x = t * 0.2;
    mesh.current.rotation.y = t * 0.3;
    
    // Holographic glow effect
    const scale = 1 + Math.sin(t * 2) * 0.05;
    mesh.current.scale.set(scale, scale, scale);
  });

  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const edgesGeometry = new THREE.EdgesGeometry(geometry);

  return (
    <group>
      <mesh ref={mesh}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color="#00ffff"
          transparent
          opacity={0.3}
          metalness={1}
          roughness={0}
        />
      </mesh>
      <lineSegments ref={edges}>
        <edgesGeometry attach="geometry" args={[1, 1, 1]} />
        <lineBasicMaterial attach="material" color="#00ffff" linewidth={2} />
      </lineSegments>
    </group>
  );
};

export default HolographicCube;
''',
            'src/components/Glassmorphism.jsx': '''import React from 'react';

const Glassmorphism = ({ children }) => {
  return (
    <div className="glassmorphism-container">
      {children}
      <style jsx>{`
        .glassmorphism-container {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 20px;
          box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 0 80px rgba(255, 255, 255, 0.05);
        }
      `}</style>
    </div>
  );
};

export default Glassmorphism;
''',
            'src/components/PremiumButton.jsx': '''import React from 'react';

const PremiumButton = ({ label, onClick, primary = false }) => {
  return (
    <button 
      className={`premium-button ${primary ? 'primary' : ''}`}
      onClick={onClick}
    >
      <span className="button-glow" />
      <span className="button-text">{label}</span>
      <style jsx>{`
        .premium-button {
          position: relative;
          padding: 12px 24px;
          background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(138, 43, 226, 0.2));
          border: 1px solid rgba(0, 255, 255, 0.3);
          border-radius: 10px;
          color: white;
          font-weight: 600;
          cursor: pointer;
          overflow: hidden;
          transition: all 0.3s ease;
        }
        .premium-button:hover {
          background: linear-gradient(135deg, rgba(0, 255, 255, 0.4), rgba(138, 43, 226, 0.4));
          box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
          transform: translateY(-2px);
        }
        .primary {
          background: linear-gradient(135deg, #00ffff, #8a2be2);
        }
        .button-glow {
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transition: left 0.5s;
        }
        .premium-button:hover .button-glow {
          left: 100%;
        }
      `}</style>
    </button>
  );
};

export default PremiumButton;
''',
            'src/components/AIDashboard.jsx': '''import React, { useState } from 'react';
import VoiceInput from './VoiceInput';
import ChatInterface from './ChatInterface';

const AIDashboard = () => {
  const [activeTab, setActiveTab] = useState('chat');
  
  return (
    <div className="ai-dashboard">
      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          AI Chat
        </button>
        <button 
          className={activeTab === 'image' ? 'active' : ''}
          onClick={() => setActiveTab('image')}
        >
          Image Gen
        </button>
        <button 
          className={activeTab === 'video' ? 'active' : ''}
          onClick={() => setActiveTab('video')}
        >
          Video Gen
        </button>
      </div>
      
      {activeTab === 'chat' && <ChatInterface />}
      {activeTab === 'image' && <ImageGenerator />}
      {activeTab === 'video' && <VideoGenerator />}
      
      <VoiceInput />
    </div>
  );
};

export default AIDashboard;
''',
            'src/premium.css': '''@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Rajdhani', sans-serif;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: white;
  min-height: 100vh;
  overflow-x: hidden;
}

.premium-container {
  width: 100vw;
  height: 100vh;
  position: relative;
}

.premium-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.logo {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(90deg, #00ffff, #8a2be2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
}

.nav-links {
  display: flex;
  gap: 20px;
}

.premium-main {
  padding: 40px;
  height: calc(100vh - 160px);
}

.canvas-container {
  width: 100%;
  height: 100%;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 0 50px rgba(0, 255, 255, 0.2);
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); }
  50% { box-shadow: 0 0 40px rgba(0, 255, 255, 0.8); }
}
''',
            'vite.config.js': '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000
  }
});
''',
            'tailwind.config.js': '''module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#00ffff',
        secondary: '#8a2be2',
      },
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        rajdhani: ['Rajdhani', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
''',
            'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JARVIS OS - Premium AI Interface</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
''',
            'README.md': '''# {{project_name}} - Premium 3D AI Interface

## Features
- 🎨 Premium 3D holographic design
- 🤖 AI-powered interactions
- 🌟 Glassmorphism UI
- ⚡ Lightning fast performance

## Getting Started
```bash
npm install
npm run dev
```

## Tech Stack
- React 18 with Vite
- Three.js for 3D graphics
- @react-three/fiber for React integration
- TailwindCSS for styling
'''
        }
    
    def _electron_template(self) -> Dict[str, str]:
        """Electron desktop app template"""
        return {
            'package.json': json.dumps({
                "name": "{{project_name}}",
                "version": "1.0.0",
                "main": "main.js",
                "scripts": {
                    "start": "electron .",
                    "dev": "concurrently \"npm run dev:vite\" \"npm run dev:electron\"",
                    "build": "vite build && electron-builder"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "devDependencies": {
                    "electron": "^28.0.0",
                    "electron-builder": "^24.9.0",
                    "vite": "^5.0.0",
                    "@vitejs/plugin-react": "^4.2.0"
                }
            }, indent=2),
            'main.js': '''const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: false,
    transparent: true,
    backgroundColor: '#00000000'
  });

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
  }
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
''',
            'preload.js': '''const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close')
});
'''
        }
    
    def _nextjs_template(self) -> Dict[str, str]:
        """Next.js SaaS template"""
        return {
            'package.json': json.dumps({
                "name": "{{project_name}}",
                "version": "1.0.0",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "next": "^14.0.0",
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "three": "^0.160.0",
                    "@react-three/fiber": "^8.15.0",
                    "lucide-react": "^0.294.0"
                }
            }, indent=2)
        }
    
    def _django_template(self) -> Dict[str, str]:
        """Django fullstack template"""
        return {
            'requirements.txt': '''Django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.3
psycopg2-binary>=2.9
python-dotenv>=1.0
channels>=4.0
redis>=5.0
''',
            'manage.py': '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
''',
            'config/__init__.py': '',
            'config/settings.py': '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
''',
            'api/models.py': '''from django.db import models

class AIConversation(models.Model):
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
''',
            'api/views.py': '''from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        # AI processing logic here
        return JsonResponse({
            'response': f'AI response to: {message}',
            'status': 'success'
        })
    return JsonResponse({'error': 'Invalid method'}, status=400)
'''
        }
    
    def _fastapi_template(self) -> Dict[str, str]:
        """FastAPI template"""
        return {
            'main.py': '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="JARVIS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ImageRequest(BaseModel):
    prompt: str
    style: str = "realistic"
    quality: str = "8k"

@app.get("/")
def read_root():
    return {"message": "JARVIS API is running", "version": "1.0.0"}

@app.post("/chat")
async def chat(request: ChatRequest):
    return {
        "response": f"AI processing: {request.message}",
        "session_id": request.session_id
    }

@app.post("/image")
async def generate_image(request: ImageRequest):
    return {
        "image_url": "/generated_images/sample.png",
        "prompt": request.prompt,
        "style": request.style
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            'requirements.txt': '''fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
aiofiles>=23.2.0
torch>=2.0.0
diffusers>=0.25.0
'''
        }
    
    def _flutter_template(self) -> Dict[str, str]:
        """Flutter desktop template"""
        return {
            'pubspec.yaml': '''name: {{project_name}}
description: Premium AI Desktop Application
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.6
  three_dart: ^0.0.16
  window_manager: ^0.3.7

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
''',
            'lib/main.dart': '''import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();
  
  WindowOptions windowOptions = WindowOptions(
    size: Size(1400, 900),
    center: true,
    backgroundColor: Colors.transparent,
    skipTaskbar: false,
    titleBarStyle: TitleBarStyle.hidden,
  );
  
  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(JarvisApp());
}

class JarvisApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JARVIS OS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Color(0xFF0A0A1A),
        primaryColor: Color(0xFF00FFFF),
      ),
      home: HomePage(),
    );
  }
}
'''
        }
    
    def get_template(self, name: str) -> Dict[str, str]:
        """Get a template by name"""
        return self.templates.get(name, {})
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.templates.keys())


class ProjectBuilder:
    """
    Main Project Builder - Creates fully functional projects
    with premium design, 3D animations, and AI integration.
    """
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or tempfile.mkdtemp()
        self.template_engine = TemplateEngine()
        self.generated_projects: Dict[str, Dict] = {}
    
    def create_project(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Create a new project from specification"""
        result = {
            'success': False,
            'project_dir': '',
            'files_created': [],
            'error': ''
        }
        
        try:
            # Create project directory
            project_dir = os.path.join(self.workspace_dir, spec.name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Select template based on framework
            template_name = self._select_template(spec)
            template = self.template_engine.get_template(template_name)
            
            if not template:
                result['error'] = f"Template not found: {template_name}"
                return result
            
            # Generate files from template
            for file_path, content in template.items():
                # Replace placeholders
                content = content.replace('{{project_name}}', spec.name)
                content = content.replace('{{description}}', spec.description)
                
                # Create file
                full_path = os.path.join(project_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                result['files_created'].append(file_path)
            
            # Create project metadata
            self._create_metadata(project_dir, spec)
            
            result['success'] = True
            result['project_dir'] = project_dir
            self.generated_projects[spec.name] = result
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _select_template(self, spec: ProjectType) -> str:
        """Select appropriate template based on spec"""
        if spec.framework == 'react' and spec.has_3d:
            return 'react_3d_modern'
        elif spec.framework == 'electron':
            return 'electron_premium'
        elif spec.framework == 'nextjs':
            return 'nextjs_saas'
        elif spec.framework == 'django':
            return 'django_fullstack'
        elif spec.framework == 'fastapi':
            return 'fastapi_modern'
        elif spec.framework == 'flutter':
            return 'flutter_desktop'
        else:
            return 'react_3d_modern'  # Default
    
    def _create_metadata(self, project_dir: str, spec: ProjectSpec):
        """Create project metadata file"""
        metadata = {
            'name': spec.name,
            'version': '1.0.0',
            'created': datetime.now().isoformat(),
            'spec': {
                'project_type': spec.project_type.value,
                'framework': spec.framework,
                'description': spec.description,
                'features': spec.features,
                'has_auth': spec.has_auth,
                'has_database': spec.has_database,
                'has_3d': spec.has_3d,
                'has_ai': spec.has_ai
            }
        }
        
        with open(os.path.join(project_dir, 'jarvis-project.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def create_webapp(self, name: str, framework: str = 'react', 
                      has_3d: bool = True) -> Dict[str, Any]:
        """Quick create a webapp"""
        spec = ProjectSpec(
            name=name,
            project_type=ProjectType.WEBAPP,
            framework=framework,
            has_3d=has_3d,
            features=['ai-chat', 'image-gen']
        )
        return self.create_project(spec)
    
    def create_desktop_app(self, name: str, framework: str = 'electron') -> Dict[str, Any]:
        """Quick create a desktop app"""
        spec = ProjectSpec(
            name=name,
            project_type=ProjectType.DESKTOP,
            framework=framework,
            features=['window-controls', 'system-tray']
        )
        return self.create_project(spec)
    
    def create_api(self, name: str, framework: str = 'fastapi',
                   has_ai: bool = True) -> Dict[str, Any]:
        """Quick create an API"""
        spec = ProjectSpec(
            name=name,
            project_type=ProjectType.API,
            framework=framework,
            has_ai=has_ai,
            features=['rest-endpoints', 'websocket']
        )
        return self.create_project(spec)
    
    def get_generated_projects(self) -> List[str]:
        """Get list of generated projects"""
        return list(self.generated_projects.keys())
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Get workspace status"""
        projects = []
        for root, dirs, files in os.walk(self.workspace_dir):
            if 'jarvis-project.json' in files:
                with open(os.path.join(root, 'jarvis-project.json')) as f:
                    projects.append(json.load(f))
        
        return {
            'workspace_dir': self.workspace_dir,
            'projects_count': len(projects),
            'projects': projects
        }


# Global instance
_project_builder = None

def get_project_builder(workspace_dir: str = None) -> ProjectBuilder:
    """Get or create the global Project Builder instance"""
    global _project_builder
    if _project_builder is None:
        _project_builder = ProjectBuilder(workspace_dir)
    return _project_builder
