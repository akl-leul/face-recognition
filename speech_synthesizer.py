import pyttsx3
import threading
import time

class SpeechSynthesizer:
    def __init__(self):
        self.engine = None
        self.last_spoken_name = None
        self.last_speak_time = 0
        self.speak_cooldown = 3.0  # seconds between same name calls
        self.init_speech_engine()
    
    def init_speech_engine(self):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties for better quality
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice (usually clearer)
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                
                # Set speech rate and volume
                self.engine.setProperty('rate', 150)  # Slightly slower for clarity
                self.engine.setProperty('volume', 0.9)  # Good volume
            
            print("✅ Speech synthesizer initialized")
        except Exception as e:
            print(f"❌ Error initializing speech: {e}")
            self.engine = None
    
    def speak_name(self, name, confidence=100.0):
        """Speak the recognized name only once"""
        if not self.engine:
            return
        
        current_time = time.time()
        
        # Check cooldown to prevent duplicate calls
        if (name == self.last_spoken_name and 
            current_time - self.last_speak_time < self.speak_cooldown):
            return
        
        # Update tracking
        self.last_spoken_name = name
        self.last_speak_time = current_time
        
        # Create speech message
        if confidence >= 95.0:
            message = f"Welcome {name}"
        elif confidence >= 85.0:
            message = f"I think you are {name}"
        else:
            message = f"Recognized {name}"
        
        # Speak directly (no threading to avoid conflicts)
        try:
            self.engine.say(message)
            self.engine.runAndWait()
            print(f"🔊 Spoke: {message}")
        except Exception as e:
            print(f"❌ Error speaking: {e}")
    
    def speak_custom_message(self, message):
        """Speak a custom message"""
        if not self.engine:
            return
        
        try:
            self.engine.say(message)
            self.engine.runAndWait()
            print(f"🔊 Spoke: {message}")
        except Exception as e:
            print(f"❌ Error speaking: {e}")
        
        # Add small delay to prevent conflicts
        time.sleep(0.5)
    
    def test_speech(self):
        """Test the speech synthesizer"""
        test_messages = [
            "Hello, I am ready for face recognition",
            "Testing speech synthesis",
            "Welcome to my face detection system, Welcome again,  to the system"
        ]
        
        for message in test_messages:
            self.speak_custom_message(message)
            time.sleep(2)

# Global speech synthesizer instance
speech_synthesizer = SpeechSynthesizer()

def speak_name_once(name, confidence=100.0):
    """Global function to speak name only once"""
    speech_synthesizer.speak_name(name, confidence)

def speak_message(message):
    """Global function to speak custom message"""
    speech_synthesizer.speak_custom_message(message)

if __name__ == "__main__":
    # Test speech synthesis
    speech_synthesizer.test_speech()
