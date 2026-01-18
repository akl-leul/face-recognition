from speech_synthesizer import speak_name_once, speak_message
import time

print("Testing speech synthesis...")

# Test speech synthesis
speak_message("Testing speech synthesis")
time.sleep(2)

speak_name_once("John Doe", 95.0)
time.sleep(2)

speak_name_once("Jane Smith", 85.0)

print("Speech test completed!")
