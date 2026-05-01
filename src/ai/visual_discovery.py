"""
Visual AI Discovery System - Real-time visual detection and animated responses
Provides camera input processing, expression recognition, and visual feedback.
"""

import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import io
from PIL import Image
import threading
import time


class ExpressionType(Enum):
    """Facial expression types"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    EXCITED = "excited"
    FOCUSED = "focused"


class VisualResponseType(Enum):
    """Types of visual AI responses"""
    HOLOGRAPHIC = "holographic"
    ANIMATED = "animated"
    TEXT = "text"
    EMOJI = "emoji"
    PARTICLE = "particle"


@dataclass
class FaceData:
    """Data extracted from a detected face"""
    bbox: Tuple[int, int, int, int]
    landmarks: List[Tuple[int, int]]
    expression: ExpressionType
    confidence: float
    face_id: Optional[int] = None


@dataclass
class VisualFeedback:
    """Visual feedback data for AI response"""
    response_type: VisualResponseType
    content: any
    color: Tuple[int, int, int]
    animation_data: Optional[Dict] = None


class ExpressionRecognizer:
    """Recognizes facial expressions from camera input"""
    
    # Simple rule-based expression detection (can be replaced with ML model)
    EXPRESSION_INDICATORS = {
        ExpressionType.HAPPY: {'mouth_curve': 0.3, 'eye_squint': 0.2},
        ExpressionType.SAD: {'mouth_curve': -0.3, 'brow_inner': 0.1},
        ExpressionType.ANGRY: {'brow_inner': 0.2, 'mouth_curve': -0.1},
        ExpressionType.SURPRISED: {'eye_open': 0.3, 'mouth_open': 0.3},
        ExpressionType.CONFUSED: {'brow_inner': 0.1, 'head_tilt': 0.1},
        ExpressionType.EXCITED: {'eye_open': 0.2, 'mouth_curve': 0.4},
        ExpressionType.FOCUSED: {'brow_inner': 0.05, 'eye_open': 0.1},
        ExpressionType.NEUTRAL: {}
    }
    
    def __init__(self):
        self.last_expressions: List[ExpressionType] = []
        self.confidence_threshold = 0.6
    
    def detect_expression(self, face_data: FaceData) -> Tuple[ExpressionType, float]:
        """Detect expression from face data"""
        # Simple placeholder - in production, use a proper ML model
        # This is a simulation based on confidence
        if face_data.confidence > 0.8:
            expression = ExpressionType.INTERESTED
        elif face_data.confidence > 0.5:
            expression = ExpressionType.NEUTRAL
        else:
            expression = ExpressionType.NEUTRAL
        
        # Update rolling history
        self.last_expressions.append(expression)
        if len(self.last_expressions) > 5:
            self.last_expressions.pop(0)
        
        # Calculate confidence based on consistency
        if len(self.last_expressions) >= 3:
            consistency = self.last_expressions[-3:].count(expression) / 3
            confidence = consistency * 0.7 + face_data.confidence * 0.3
        else:
            confidence = face_data.confidence
        
        return expression, confidence
    
    def get_dominant_expression(self) -> ExpressionType:
        """Get the most common recent expression"""
        if not self.last_expressions:
            return ExpressionType.NEUTRAL
        return max(set(self.last_expressions), key=self.last_expressions.count)


class CameraHandler:
    """Handles camera capture and processing"""
    
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_active = False
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        self._frame_buffer: List[np.ndarray] = []
        self._max_buffer_size = 30
    
    def start(self) -> bool:
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.is_active = self.cap.isOpened()
            return self.is_active
        except Exception as e:
            print(f"Camera start error: {e}")
            return False
    
    def stop(self):
        """Stop camera capture"""
        if self.cap:
            self.cap.release()
            self.is_active = False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame from camera"""
        if not self.is_active or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            # Add to buffer
            self._frame_buffer.append(frame.copy())
            if len(self._frame_buffer) > self._max_buffer_size:
                self._frame_buffer.pop(0)
            return frame
        return None
    
    def get_face_detection_frame(self) -> Optional[np.ndarray]:
        """Get frame with face detection rectangles"""
        frame = self.read_frame()
        if frame is None:
            return None
        
        # Placeholder for face detection - use OpenCV Haar cascades or ML model
        # For now, return original frame
        return frame
    
    def encode_frame(self, frame: np.ndarray, format: str = 'jpg') -> bytes:
        """Encode frame to bytes"""
        if frame is None:
            return b''
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        if format == 'png':
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 9]
        
        _, buffer = cv2.imencode(f'.{format}', frame, encode_param)
        return buffer.tobytes()
    
    def get_base64_frame(self, format: str = 'jpg') -> str:
        """Get current frame as base64 string"""
        frame = self.read_frame()
        if frame is None:
            return ''
        
        bytes_data = self.encode_frame(frame, format)
        return base64.b64encode(bytes_data).decode('utf-8')
    
    def save_frame(self, frame: np.ndarray, filepath: str) -> bool:
        """Save frame to file"""
        try:
            cv2.imwrite(filepath, frame)
            return True
        except Exception as e:
            print(f"Save frame error: {e}")
            return False


class VisualAIDisplay:
    """Animated visual AI responses with holographic effects"""
    
    # Color schemes for different AI states
    STATE_COLORS = {
        'listening': (0, 255, 255),      # Cyan
        'thinking': (255, 200, 0),        # Gold
        'responding': (0, 255, 0),        # Green
        'error': (255, 0, 0),             # Red
        'learning': (138, 43, 226),        # Purple
        'idle': (100, 100, 100)           # Gray
    }
    
    def __init__(self):
        self.current_state = 'idle'
        self.animation_frame = 0
        self.particles: List[Dict] = []
        self.response_queue: List[VisualFeedback] = []
    
    def set_state(self, state: str):
        """Set AI state for visual feedback"""
        if state in self.STATE_COLORS:
            self.current_state = state
            self.animation_frame = 0
    
    def generate_holographic_effect(self, frame: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """Apply holographic effect to frame"""
        if frame is None:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a copy with holographic overlay
        h, w = frame.shape[:2]
        result = frame.copy()
        
        # Get color for current state
        color = self.STATE_COLORS.get(self.current_state, (0, 255, 255))
        
        # Add scan lines effect
        for y in range(0, h, 4):
            alpha = 0.1 * intensity * (0.5 + 0.5 * np.sin(y * 0.1 + self.animation_frame * 0.1))
            result[y:y+2, :] = cv2.addWeighted(result[y:y+2, :], 1-alpha, 
                                               np.full((2, w, 3), color, dtype=np.uint8), alpha)
        
        # Add corner brackets
        bracket_size = 30
        thickness = 2
        # Top-left
        cv2.line(result, (0, 0), (bracket_size, 0), color, thickness)
        cv2.line(result, (0, 0), (0, bracket_size), color, thickness)
        # Top-right
        cv2.line(result, (w-bracket_size, 0), (w, 0), color, thickness)
        cv2.line(result, (w, 0), (w, bracket_size), color, thickness)
        # Bottom-left
        cv2.line(result, (0, h-bracket_size), (0, h), color, thickness)
        cv2.line(result, (0, h), (bracket_size, h), color, thickness)
        # Bottom-right
        cv2.line(result, (w-bracket_size, h), (w, h), color, thickness)
        cv2.line(result, (w, h-bracket_size), (w, h), color, thickness)
        
        # Add glow effect in center
        center_x, center_y = w // 2, h // 2
        radius = int(50 * intensity)
        glow = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.circle(glow, (center_x, center_y), radius, color, -1)
        glow = cv2.GaussianBlur(glow, (0, 0), radius // 2)
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        mask = cv2.GaussianBlur(mask, (0, 0), radius // 3)
        mask = mask.astype(float) / 255.0
        
        for c in range(3):
            result[:, :, c] = np.clip(
                result[:, :, c] + glow[:, :, c] * mask * 0.3,
                0, 255
            ).astype(np.uint8)
        
        return result
    
    def generate_particle_effect(self, count: int = 50) -> np.ndarray:
        """Generate particle animation frame"""
        h, w = 400, 600
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        color = self.STATE_COLORS.get(self.current_state, (0, 255, 255))
        
        # Update and draw particles
        for i, particle in enumerate(self.particles):
            x = int(particle['x'])
            y = int(particle['y'])
            size = int(particle['size'])
            
            cv2.circle(frame, (x, y), size, color, -1)
            
            # Update position
            particle['y'] -= particle['vy']
            particle['x'] += particle['vx']
            particle['life'] -= 1
            
            # Respawn dead particles
            if particle['life'] <= 0:
                self.particles[i] = self._create_particle(w, h)
        
        return frame
    
    def _create_particle(self, width: int, height: int) -> Dict:
        """Create a new particle"""
        return {
            'x': np.random.randint(0, width),
            'y': np.random.randint(0, height),
            'vx': np.random.uniform(-1, 1),
            'vy': np.random.uniform(1, 3),
            'size': np.random.randint(2, 5),
            'life': np.random.randint(30, 100)
        }
    
    def init_particles(self, count: int = 50):
        """Initialize particle system"""
        w, h = 600, 400
        self.particles = [self._create_particle(w, h) for _ in range(count)]
    
    def generate_listening_animation(self) -> np.ndarray:
        """Generate listening state animation"""
        h, w = 400, 600
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        color = self.STATE_COLORS['listening']
        center_x, center_y = w // 2, h // 2
        
        # Animated rings
        for i in range(5):
            radius = 30 + i * 20 + (self.animation_frame % 20)
            alpha = max(0, 1 - (radius - 30) / 100)
            
            if alpha > 0:
                cv2.circle(frame, (center_x, center_y), radius, color, 1)
                ring = np.zeros((h, w, 3), dtype=np.uint8)
                cv2.circle(ring, (center_x, center_y), radius, color, 2)
                frame = cv2.addWeighted(frame, 1, ring, alpha * 0.3, 0)
        
        # Center indicator
        cv2.circle(frame, (center_x, center_y), 10, color, -1)
        
        return frame
    
    def generate_thinking_animation(self) -> np.ndarray:
        """Generate thinking state animation"""
        h, w = 400, 600
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        color = self.STATE_COLORS['thinking']
        center_x, center_y = w // 2, h // 2
        
        # Rotating segments
        num_segments = 8
        for i in range(num_segments):
            angle = (360 / num_segments) * i + self.animation_frame * 2
            end_angle = angle + 30
            
            pt1 = (
                int(center_x + 40 * np.cos(np.radians(angle))),
                int(center_y + 40 * np.sin(np.radians(angle)))
            )
            pt2 = (
                int(center_x + 40 * np.cos(np.radians(end_angle))),
                int(center_y + 40 * np.sin(np.radians(end_angle)))
            )
            cv2.line(frame, pt1, pt2, color, 3)
        
        cv2.circle(frame, (center_x, center_y), 5, color, -1)
        
        return frame
    
    def generate_responding_animation(self) -> np.ndarray:
        """Generate responding state animation"""
        h, w = 400, 600
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        color = self.STATE_COLORS['responding']
        center_x, center_y = w // 2, h // 2
        
        # Pulsing waves
        for i in range(3):
            radius = 30 + i * 30 + (self.animation_frame % 30)
            alpha = max(0, 1 - (radius - 30) / 90)
            cv2.circle(frame, (center_x, center_y), radius, color, 2)
        
        # Center dot
        cv2.circle(frame, (center_x, center_y), 8, color, -1)
        
        return frame


class VisualDiscovery:
    """
    Visual AI Discovery System - Main class
    Coordinates camera input, face detection, expression recognition,
    and visual AI responses with holographic effects.
    """
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/Jarvis-Cache")
        self.vision_dir = os.path.join(self.cache_dir, "vision")
        os.makedirs(self.vision_dir, exist_ok=True)
        
        # Initialize components
        self.camera = CameraHandler()
        self.expression_recognizer = ExpressionRecognizer()
        self.visual_display = VisualAIDisplay()
        
        # State management
        self.is_active = False
        self.current_session_frames: List[np.ndarray] = []
        self.detected_faces: List[FaceData] = []
        self.observation_history: List[Dict] = []
        
        # Settings
        self.detection_interval = 0.1  # seconds
        self.max_frames_in_memory = 100
        self.expression_sensitivity = 0.7
    
    def start_camera(self) -> bool:
        """Start camera for visual input"""
        success = self.camera.start()
        if success:
            self.is_active = True
            self.visual_display.set_state('listening')
            self.visual_display.init_particles(50)
        return success
    
    def stop_camera(self):
        """Stop camera capture"""
        self.camera.stop()
        self.is_active = False
        self.visual_display.set_state('idle')
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from camera"""
        return self.camera.read_frame()
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, any]:
        """Analyze a frame for faces and expressions"""
        if frame is None:
            return {'success': False, 'faces': []}
        
        # Placeholder for face detection
        # In production, use a proper face detection model like MTCNN, RetinaFace, or OpenCV DNN
        faces = []
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple face detection placeholder
        # This would be replaced with actual ML model inference
        face_data = FaceData(
            bbox=(100, 100, 300, 300),
            landmarks=[],
            expression=ExpressionType.NEUTRAL,
            confidence=0.85
        )
        
        # Detect expression
        expression, confidence = self.expression_recognizer.detect_expression(face_data)
        face_data.expression = expression
        face_data.confidence = confidence
        
        faces.append(face_data)
        self.detected_faces = faces
        
        return {
            'success': True,
            'faces': faces,
            'dominant_expression': self.expression_recognizer.get_dominant_expression().value,
            'frame_analyzed': True
        }
    
    def get_visual_response(self, text: str = "", mood: str = "neutral") -> VisualFeedback:
        """Generate visual feedback based on AI response"""
        state_map = {
            'happy': 'responding',
            'thinking': 'thinking',
            'listening': 'listening',
            'learning': 'learning',
            'error': 'error'
        }
        
        state = state_map.get(mood, 'responding')
        color = VisualAIDisplay.STATE_COLORS[state]
        
        return VisualFeedback(
            response_type=VisualResponseType.HOLOGRAPHIC,
            content=text,
            color=color,
            animation_data={'state': state}
        )
    
    def generate_display_frame(self, include_camera: bool = True) -> np.ndarray:
        """Generate the current display frame with effects"""
        if include_camera and self.is_active:
            camera_frame = self.camera.read_frame()
            if camera_frame is not None:
                return self.visual_display.generate_holographic_effect(camera_frame)
        
        # Generate animation based on state
        state = self.visual_display.current_state
        
        if state == 'listening':
            return self.visual_display.generate_listening_animation()
        elif state == 'thinking':
            return self.visual_display.generate_thinking_animation()
        elif state == 'responding':
            return self.visual_display.generate_responding_animation()
        else:
            return self.visual_display.generate_particle_effect()
    
    def save_session(self, session_name: str = None) -> str:
        """Save the current observation session"""
        if session_name is None:
            session_name = f"session_{int(time.time())}"
        
        session_dir = os.path.join(self.vision_dir, session_name)
        os.makedirs(session_dir, exist_ok=True)
        
        for i, frame in enumerate(self.current_session_frames):
            cv2.imwrite(os.path.join(session_dir, f"frame_{i:04d}.jpg"), frame)
        
        # Save observation metadata
        with open(os.path.join(session_dir, "metadata.json"), 'w') as f:
            json.dump({
                'session_name': session_name,
                'frame_count': len(self.current_session_frames),
                'faces_detected': len(self.detected_faces),
                'expressions': [f.expression.value for f in self.detected_faces]
            }, f, indent=2)
        
        return session_dir
    
    def get_observation_summary(self) -> Dict:
        """Get summary of visual observations"""
        return {
            'session_active': self.is_active,
            'frames_captured': len(self.current_session_frames),
            'faces_detected': len(self.detected_faces),
            'expressions_observed': [
                f.expression.value for f in self.detected_faces
            ],
            'dominant_expression': self.expression_recognizer.get_dominant_expression().value
        }
    
    def observe_and_learn(self, duration: int = 10) -> Dict:
        """Observe and learn from visual input for a duration"""
        self.visual_display.set_state('learning')
        start_time = time.time()
        observations = []
        
        while time.time() - start_time < duration and self.is_active:
            frame = self.capture_frame()
            if frame is not None:
                analysis = self.analyze_frame(frame)
                observations.append(analysis)
                self.current_session_frames.append(frame.copy())
                
                # Manage memory
                if len(self.current_session_frames) > self.max_frames_in_memory:
                    self.current_session_frames.pop(0)
        
        self.observation_history.append({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'observations': len(observations),
            'frames_saved': len(self.current_session_frames)
        })
        
        return {
            'observation_count': len(observations),
            'frames_saved': len(self.current_session_frames),
            'duration': time.time() - start_time
        }
    
    def update_animation(self):
        """Update animation frame counter"""
        self.visual_display.animation_frame += 1


# Import missing modules
import os
import json
from datetime import datetime


# Global instance
_visual_discovery = None

def get_visual_discovery(cache_dir: str = None) -> VisualDiscovery:
    """Get or create the global Visual Discovery instance"""
    global _visual_discovery
    if _visual_discovery is None:
        _visual_discovery = VisualDiscovery(cache_dir)
    return _visual_discovery
