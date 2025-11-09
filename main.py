import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
import yaml
import time
import threading
import re
import os
import warnings
from opcua import Client, ua
from opcua.ua import utils
import logging
import pyttsx3
import queue
import collections

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# OPC UA server details
DEFAULT_OPC_UA_URL = "opc.tcp://desktop-j8ae1eh:61510/ABB.IoTGateway"
PROGRAM_POINT_NODE_ID = "ns=3;s=_isac/RAPID/T_ROB1/ProgramPointer"

# Updated Program Point Actions Mapping for different user levels
PROGRAM_POINT_ACTIONS = {
    # Main movements
    15: {
        "level1": "Moving to home position p10 to start operation",
        "level2": "Moving to home position p10",
        "level3": "Move to p10"
    },
    16: {
        "level1": "Waiting for shape selection on teach pendant",
        "level2": "Shape selection input required",
        "level3": "Select shape"
    },
    17: {
        "level1": "Press OK button to continue with selected shape",
        "level2": "Waiting for OK confirmation",
        "level3": "Wait OK"
    },

    # Shape selection and pickup movements
    22: {
        "level1": "Processing selected shape for pickup operation",
        "level2": "Evaluating shape selection for pickup",
        "level3": "Shape pickup start"
    },

    # Circle pickup sequence
    23: {
        "level1": "Moving to circle pickup position p20",
        "level2": "Moving to circle position p20 for pickup",
        "level3": "Circle pickup"
    },
    34: {
        "level1": "Moving down to pickup circle shape",
        "level2": "Approaching circle pickup position",
        "level3": "Pickup approach"
    },
    35: {
        "level1": "At exact pickup position for circle",
        "level2": "Precise positioning for circle pickup",
        "level3": "Pickup position"
    },
    36: {
        "level1": "Vacuum activated - picking up circle shape",
        "level2": "Vacuum gripper activated for circle",
        "level3": "Vacuum on"
    },
    37: {
        "level1": "Waiting for secure grip on circle shape",
        "level2": "Wait time for vacuum stabilization",
        "level3": "Grip wait"
    },
    38: {
        "level1": "Returning to safe height with circle shape",
        "level2": "Moving to safe height after circle pickup",
        "level3": "Safe height return"
    },

    # Star pickup sequence
    25: {
        "level1": "Moving to star pickup position p30",
        "level2": "Moving to star position p30 for pickup",
        "level3": "Star pickup"
    },
    39: {
        "level1": "Moving down to pickup star shape",
        "level2": "Approaching star pickup position",
        "level3": "Star approach"
    },
    40: {
        "level1": "At exact pickup position for star",
        "level2": "Precise positioning for star pickup",
        "level3": "Star position"
    },
    41: {
        "level1": "Vacuum activated - picking up star shape",
        "level2": "Vacuum gripper activated for star",
        "level3": "Vacuum on"
    },
    42: {
        "level1": "Waiting for secure grip on star shape",
        "level2": "Wait time for vacuum stabilization",
        "level3": "Grip wait"
    },
    43: {
        "level1": "Returning to safe height with star shape",
        "level2": "Moving to safe height after star pickup",
        "level3": "Safe height return"
    },

    # Hexagon pickup sequence
    27: {
        "level1": "Moving to hexagon pickup position p40",
        "level2": "Moving to hexagon position p40 for pickup",
        "level3": "Hexagon pickup"
    },
    44: {
        "level1": "Moving down to pickup hexagon shape",
        "level2": "Approaching hexagon pickup position",
        "level3": "Hexagon approach"
    },
    45: {
        "level1": "At exact pickup position for hexagon",
        "level2": "Precise positioning for hexagon pickup",
        "level3": "Hexagon position"
    },
    46: {
        "level1": "Vacuum activated - picking up hexagon shape",
        "level2": "Vacuum gripper activated for hexagon",
        "level3": "Vacuum on"
    },
    47: {
        "level1": "Waiting for secure grip on hexagon shape",
        "level2": "Wait time for vacuum stabilization",
        "level3": "Grip wait"
    },
    48: {
        "level1": "Returning to safe height with hexagon shape",
        "level2": "Moving to safe height after hexagon pickup",
        "level3": "Safe height return"
    },

    # Triangle pickup sequence
    29: {
        "level1": "Moving to triangle pickup position p50",
        "level2": "Moving to triangle position p50 for pickup",
        "level3": "Triangle pickup"
    },
    49: {
        "level1": "Moving down to pickup triangle shape",
        "level2": "Approaching triangle pickup position",
        "level3": "Triangle approach"
    },
    50: {
        "level1": "At exact pickup position for triangle",
        "level2": "Precise positioning for triangle pickup",
        "level3": "Triangle position"
    },
    51: {
        "level1": "Vacuum activated - picking up triangle shape",
        "level2": "Vacuum gripper activated for triangle",
        "level3": "Vacuum on"
    },
    52: {
        "level1": "Waiting for secure grip on triangle shape",
        "level2": "Wait time for vacuum stabilization",
        "level3": "Grip wait"
    },
    53: {
        "level1": "Returning to safe height with triangle shape",
        "level2": "Moving to safe height after triangle pickup",
        "level3": "Safe height return"
    },

    # Square pickup sequence
    31: {
        "level1": "Moving to square pickup position p60",
        "level2": "Moving to square position p60 for pickup",
        "level3": "Square pickup"
    },
    54: {
        "level1": "Moving down to pickup square shape",
        "level2": "Approaching square pickup position",
        "level3": "Square approach"
    },
    55: {
        "level1": "At exact pickup position for square",
        "level2": "Precise positioning for square pickup",
        "level3": "Square position"
    },
    56: {
        "level1": "Vacuum activated - picking up square shape",
        "level2": "Vacuum gripper activated for square",
        "level3": "Vacuum on"
    },
    57: {
        "level1": "Waiting for secure grip on square shape",
        "level2": "Wait time for vacuum stabilization",
        "level3": "Grip wait"
    },
    58: {
        "level1": "Returning to safe height with square shape",
        "level2": "Moving to safe height after square pickup",
        "level3": "Safe height return"
    },

    # Shape placing operations
    59: {
        "level1": "Starting placing operation for selected shape",
        "level2": "Beginning shape placement sequence",
        "level3": "Place start"
    },

    # Circle placing sequence
    60: {
        "level1": "Moving to circle placing position p20",
        "level2": "Moving to circle position p20 for placing",
        "level3": "Circle place"
    },
    61: {
        "level1": "Moving down to place circle shape",
        "level2": "Approaching circle placing position",
        "level3": "Place approach"
    },
    62: {
        "level1": "Vacuum deactivated - releasing circle shape",
        "level2": "Vacuum gripper deactivated for circle",
        "level3": "Vacuum off"
    },
    63: {
        "level1": "Waiting for shape release confirmation",
        "level2": "Wait time for object release",
        "level3": "Release wait"
    },

    # Star placing sequence
    64: {
        "level1": "Moving to star placing position p30",
        "level2": "Moving to star position p30 for placing",
        "level3": "Star place"
    },
    65: {
        "level1": "Moving down to place star shape",
        "level2": "Approaching star placing position",
        "level3": "Star place approach"
    },
    66: {
        "level1": "Vacuum deactivated - releasing star shape",
        "level2": "Vacuum gripper deactivated for star",
        "level3": "Vacuum off"
    },
    67: {
        "level1": "Waiting for shape release confirmation",
        "level2": "Wait time for object release",
        "level3": "Release wait"
    },
    68: {
        "level1": "Returning to safe height after placing star",
        "level2": "Moving to safe height after star placement",
        "level3": "Safe height return"
    },

    # Hexagon placing sequence
    69: {
        "level1": "Moving to hexagon placing position p40",
        "level2": "Moving to hexagon position p40 for placing",
        "level3": "Hexagon place"
    },
    70: {
        "level1": "Moving down to place hexagon shape",
        "level2": "Approaching hexagon placing position",
        "level3": "Hexagon place approach"
    },
    71: {
        "level1": "Vacuum deactivated - releasing hexagon shape",
        "level2": "Vacuum gripper deactivated for hexagon",
        "level3": "Vacuum off"
    },
    72: {
        "level1": "Waiting for shape release confirmation",
        "level2": "Wait time for object release",
        "level3": "Release wait"
    },
    73: {
        "level1": "Returning to safe height after placing hexagon",
        "level2": "Moving to safe height after hexagon placement",
        "level3": "Safe height return"
    },

    # Triangle placing sequence
    74: {
        "level1": "Moving to triangle placing position p50",
        "level2": "Moving to triangle position p50 for placing",
        "level3": "Triangle place"
    },
    75: {
        "level1": "Moving down to place triangle shape",
        "level2": "Approaching triangle placing position",
        "level3": "Triangle place approach"
    },
    76: {
        "level1": "Vacuum deactivated - releasing triangle shape",
        "level2": "Vacuum gripper deactivated for triangle",
        "level3": "Vacuum off"
    },
    77: {
        "level1": "Waiting for shape release confirmation",
        "level2": "Wait time for object release",
        "level3": "Release wait"
    },
    78: {
        "level1": "Returning to safe height after placing triangle",
        "level2": "Moving to safe height after triangle placement",
        "level3": "Safe height return"
    },

    # Square placing sequence
    79: {
        "level1": "Moving to square placing position p60",
        "level2": "Moving to square position p60 for placing",
        "level3": "Square place"
    },
    80: {
        "level1": "Moving down to place square shape",
        "level2": "Approaching square placing position",
        "level3": "Square place approach"
    },
    81: {
        "level1": "Vacuum deactivated - releasing square shape",
        "level2": "Vacuum gripper deactivated for square",
        "level3": "Vacuum off"
    },
    82: {
        "level1": "Waiting for shape release confirmation",
        "level2": "Wait time for object release",
        "level3": "Release wait"
    },
    83: {
        "level1": "Returning to safe height after placing square",
        "level2": "Moving to safe height after square placement",
        "level3": "Safe height return"
    },

    # Final operations
    84: {
        "level1": "Returning to home position p10 - operation completed",
        "level2": "Moving to home position p10",
        "level3": "Home return"
    },

    # End of program movements
    85: {
        "level1": "Moving to final position p30",
        "level2": "Moving to position p30",
        "level3": "Move to p30"
    },
    86: {
        "level1": "Moving to final position p40",
        "level2": "Moving to position p40",
        "level3": "Move to p40"
    },
    87: {
        "level1": "Moving to final position p50",
        "level2": "Moving to position p50",
        "level3": "Move to p50"
    },
    88: {
        "level1": "Moving to final position p60",
        "level2": "Moving to position p60",
        "level3": "Move to p60"
    },
    89: {
        "level1": "Moving to final position p70",
        "level2": "Moving to position p70",
        "level3": "Move to p70"
    }
}

# Movement groups - lines that should trigger consolidated messages
# Movement groups - lines that should trigger consolidated messages
MOVEMENT_GROUPS = {
    # Pickup sequences (correct order matching RAPID CASE statements)
    "circle_pickup": [34, 35, 36, 37, 38],  # CASE 1: Circle
    "star_pickup": [39, 40, 41, 42, 43],  # CASE 2: Star
    "hexagon_pickup": [44, 45, 46, 47, 48],  # CASE 3: Hexagon
    "triangle_pickup": [49, 50, 51, 52, 53],  # CASE 4: Triangle
    "square_pickup": [54, 55, 56, 57, 58],  # CASE 5: Square

    # Place sequences (correct order matching RAPID CASE statements)
    "circle_place": [60, 61, 62, 63],  # CASE 1: Circle
    "star_place": [64, 65, 66, 67, 68],  # CASE 2: Star
    "hexagon_place": [69, 70, 71, 72, 73],  # CASE 3: Hexagon
    "triangle_place": [74, 75, 76, 77, 78],  # CASE 4: Triangle
    "square_place": [79, 80, 81, 82, 83],  # CASE 5: Square

    # Final movements
    "final_movements": [85, 86, 87, 88, 89]
}

# Lines that should be completely SILENT (no messages at all)
SILENT_LINES = {
    # These are typically internal program flow lines that don't need user notification
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100
}


class TextToSpeechManager:
    """Manages text-to-speech functionality"""

    def __init__(self):
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speech_enabled = True
        self.rate = 150  # Default speech rate
        self.speech_callbacks = []  # Callbacks to notify when speech finishes
        self.initialize_engine()

    def initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            # Test if engine works
            voices = self.engine.getProperty('voices')
            print(f"Available voices: {len(voices)}")
            for i, voice in enumerate(voices):
                print(f"Voice {i}: {voice.name}")

            self.engine.setProperty('rate', self.rate)

            # Connect the callback for when speech finishes
            self.engine.connect('finished-utterance', self._on_speech_finished)

            print("TTS Engine initialized successfully")

        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def _on_speech_finished(self, name, completed):
        """Called when speech finishes"""
        print(f"TTS: Speech finished callback - completed: {completed}")
        if completed:
            # Notify all callbacks that speech is done
            for callback in self.speech_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in speech callback: {e}")
            self.speech_callbacks.clear()
        self.is_speaking = False

    def speak_text(self, text, callback=None):
        """Add text to speech queue with optional callback"""
        if not text or not text.strip():
            if callback:
                callback()  # Call immediately if no text
            return

        print(f"TTS: Speaking: {text}")

        if not self.engine:
            print("TTS: Engine not available")
            if callback:
                callback()
            return

        if not self.speech_enabled:
            print("TTS: Speech disabled")
            if callback:
                callback()
            return

        # Add callback if provided
        if callback:
            self.speech_callbacks.append(callback)

        self.speech_queue.put(text)
        print(f"TTS: Added to queue. Queue size: {self.speech_queue.qsize()}")

        if not self.is_speaking:
            self.process_speech_queue()

    def process_speech_queue(self):
        """Process the speech queue in a separate thread"""

        def _speak():
            self.is_speaking = True
            while not self.speech_queue.empty():
                try:
                    text = self.speech_queue.get_nowait()
                    # Clean the text for speech (remove timestamps, etc.)
                    clean_text = self.clean_text_for_speech(text)
                    if clean_text:
                        self.engine.say(clean_text)
                        self.engine.runAndWait()
                    self.speech_queue.task_done()
                except Exception as e:
                    print(f"Speech error: {e}")
                    break
            self.is_speaking = False

        if not self.is_speaking and self.engine:
            threading.Thread(target=_speak, daemon=True).start()

    def clean_text_for_speech(self, text):
        """Clean text for better speech output"""
        # Remove timestamps like [15:51:20]
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        # Remove OPC UA prefixes
        text = text.replace('OPC UA:', '')
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def toggle_speech(self, enabled=None):
        """Toggle speech on/off"""
        if enabled is None:
            self.speech_enabled = not self.speech_enabled
        else:
            self.speech_enabled = enabled
        return self.speech_enabled

    def set_speech_rate(self, rate):
        """Set speech rate"""
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)

    def stop_speech(self):
        """Stop current speech"""
        if self.engine:
            self.engine.stop()
        # Clear the queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                break
        self.is_speaking = False

    def is_speaking_now(self):
        """Check if currently speaking"""
        return self.is_speaking


# Global TTS Manager
tts_manager = TextToSpeechManager()


class MessageQueueManager:
    """Manages message queue with display of only 2 messages at a time"""

    def __init__(self, display_callback, speech_callback):
        self.message_queue = collections.deque()
        self.display_callback = display_callback
        self.speech_callback = speech_callback
        self.current_messages = []
        self.is_displaying = False
        self.waiting_for_speech = False

    def add_message(self, message):
        """Add message to queue"""
        self.message_queue.append(message)
        self.process_queue()

    def process_queue(self):
        """Process the message queue"""
        if not self.is_displaying and len(self.message_queue) >= 2:
            self.display_next_pair()

    def display_next_pair(self):
        """Display next 2 messages from queue"""
        if len(self.message_queue) < 2:
            return

        self.is_displaying = True
        self.current_messages = []

        # Get next 2 messages
        for _ in range(2):
            if self.message_queue:
                message = self.message_queue.popleft()
                self.current_messages.append(message)

        # Display the messages
        self.display_callback(self.current_messages)

        # Speak both messages together but wait for speech to finish
        speech_texts = []
        for message in self.current_messages:
            speech_texts.append(message)

        # Combine messages for speech
        combined_speech = " ".join(speech_texts)

        # Speak with callback - text stays until speech finishes
        self.speech_callback(combined_speech, self._on_speech_finished)

    def _on_speech_finished(self):
        """Called when speech finishes - NOW text stays until this is called"""
        print("MessageQueue: Speech finished completely, now clearing messages")
        # Add a small pause after speech finishes before showing next messages
        threading.Timer(1.0, self.clear_and_continue).start()

    def clear_and_continue(self):
        """Clear current display and continue with next messages"""
        self.current_messages = []
        self.is_displaying = False
        self.display_callback([])  # Clear display
        # Small delay before showing next messages
        threading.Timer(0.5, self.process_queue).start()  # Wait 0.5s then continue


class OPCUASubscriptionHandler:
    """Handles incoming data change notifications from the OPC UA server."""

    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.last_point = None
        self.last_line_displayed = None
        self.processed_groups = set()  # Track which movement groups we've already processed

    def datachange_notification(self, node, val, data):
        try:
            print(f"Raw data received: {val}")  # Debug print
            print(f"Data type: {type(val)}")  # Debug print

            # Process the raw data
            data_source = None
            if isinstance(val, ua.ExtensionObject):
                # Attempt to decode the ExtensionObject
                try:
                    if hasattr(val, "Body") and val.Body is not None:
                        data_source = val.Body
                        self.gui_app.log_opcua_message(f"Decoded ExtensionObject Body: {data_source}")
                        print(f"ExtensionObject Body: {data_source}")  # Debug print
                    else:
                        decoded = utils.unpack_extension_object(val)
                        data_source = decoded
                        self.gui_app.log_opcua_message(f"Unpacked ExtensionObject: {decoded}")
                        print(f"Unpacked ExtensionObject: {decoded}")  # Debug print
                except Exception as e:
                    self.gui_app.log_opcua_message(f"Failed to unpack ExtensionObject: {e}", is_error=True)
                    print(f"ExtensionObject unpack error: {e}")  # Debug print
                    return
            elif hasattr(val, "Value"):
                data_source = val.Value
                print(f"Value attribute: {data_source}")  # Debug print
            else:
                data_source = val
                print(f"Direct value: {data_source}")  # Debug print

            current_point = None
            module_name = "---"
            routine_name = "---"

            # Extract program pointer data - try different attribute access patterns
            if hasattr(data_source, "Line"):
                current_point = data_source.Line
                module_name = getattr(data_source, "Module", "N/A")
                routine_name = getattr(data_source, "Routine", "N/A")
                print(
                    f"Attribute access - Line: {current_point}, Module: {module_name}, Routine: {routine_name}")  # Debug
            elif hasattr(data_source, "line"):
                current_point = data_source.line
                module_name = getattr(data_source, "module", "N/A")
                routine_name = getattr(data_source, "routine", "N/A")
                print(
                    f"Lowercase attribute access - Line: {current_point}, Module: {module_name}, Routine: {routine_name}")  # Debug
            elif isinstance(data_source, dict):
                current_point = data_source.get("Line") or data_source.get("line")
                module_name = data_source.get("Module", data_source.get("module", "N/A"))
                routine_name = data_source.get("Routine", data_source.get("routine", "N/A"))
                print(f"Dict access - Line: {current_point}, Module: {module_name}, Routine: {routine_name}")  # Debug
            else:
                # Try to inspect the object's attributes
                try:
                    attrs = dir(data_source)
                    print(f"Available attributes: {attrs}")  # Debug print
                    # Look for common attribute patterns
                    for attr in attrs:
                        if 'line' in attr.lower():
                            current_point = getattr(data_source, attr, None)
                            print(f"Found line attribute '{attr}': {current_point}")  # Debug
                        if 'module' in attr.lower():
                            module_name = getattr(data_source, attr, "N/A")
                            print(f"Found module attribute '{attr}': {module_name}")  # Debug
                        if 'routine' in attr.lower():
                            routine_name = getattr(data_source, attr, "N/A")
                            print(f"Found routine attribute '{attr}': {routine_name}")  # Debug
                except Exception as e:
                    print(f"Error inspecting object: {e}")  # Debug

            # Convert to integer if necessary
            if current_point is not None and not isinstance(current_point, int):
                try:
                    current_point = int(current_point)
                except Exception:
                    self.gui_app.log_opcua_message(f"Line number not convertible: {current_point}", is_error=True)
                    print(f"Line conversion failed: {current_point}")  # Debug
                    return

            # If we still don't have data, try string parsing
            if current_point is None and data_source is not None:
                data_str = str(data_source)
                print(f"Trying string parsing: {data_str}")  # Debug
                # Try to extract information from string representation
                if "Line" in data_str or "Module" in data_str or "Routine" in data_str:
                    # Simple string parsing as fallback
                    line_match = re.search(r'Line[=:]\s*(\d+)', data_str)
                    module_match = re.search(r'Module[=:]\s*([^,\s]+)', data_str)
                    routine_match = re.search(r'Routine[=:]\s*([^,\s]+)', data_str)

                    if line_match:
                        current_point = int(line_match.group(1))
                    if module_match:
                        module_name = module_match.group(1)
                    if routine_match:
                        routine_name = routine_match.group(1)

                    print(
                        f"String parsed - Line: {current_point}, Module: {module_name}, Routine: {routine_name}")  # Debug

            # Update GUI status
            self.gui_app.update_robot_status(module_name, routine_name, current_point or "---")

            # Only log if new line
            if current_point is not None and current_point != self.last_point:
                # Check if this line should be completely silent
                if current_point in SILENT_LINES:
                    print(f"Line {current_point} is in SILENT_LINES - skipping message")
                    self.last_point = current_point
                    return

                # Check if this line belongs to any movement group
                movement_message = self._get_movement_group_message(current_point)

                if movement_message:
                    # This is a grouped movement - send consolidated message
                    self.gui_app.log_opcua_message(f"{movement_message}")
                else:
                    # Individual line - use standard message only if it's defined in PROGRAM_POINT_ACTIONS
                    user_level = self.gui_app.user_level.lower()
                    action_info = PROGRAM_POINT_ACTIONS.get(current_point)

                    if action_info:
                        # Get message for current user level
                        message = action_info.get(user_level, f"Line {current_point}")
                        self.gui_app.log_opcua_message(f"{message}")
                    else:
                        # Skip completely for lines not in PROGRAM_POINT_ACTIONS
                        print(f"Line {current_point} not in PROGRAM_POINT_ACTIONS - skipping message")

                self.last_point = current_point
        except Exception as e:
            error_msg = f"Error in datachange_notification: {e}"
            self.gui_app.log_opcua_message(error_msg, is_error=True)
            print(error_msg)  # Debug print

    def _get_movement_group_message(self, current_point):
        """Check if current point belongs to a movement group and return consolidated message"""
        user_level = self.gui_app.user_level.lower()

        # Pickup sequences - CORRECTED ORDER
        pickup_groups = {
            "circle_pickup": ("Circle", "Executing circle pickup sequence"),
            "star_pickup": ("Star", "Executing star pickup sequence"),
            "hexagon_pickup": ("Hexagon", "Executing hexagon pickup sequence"),
            "triangle_pickup": ("Triangle", "Executing triangle pickup sequence"),
            "square_pickup": ("Square", "Executing square pickup sequence")
        }

        for group_name, (shape, message) in pickup_groups.items():
            if current_point in MOVEMENT_GROUPS[group_name]:
                if group_name not in self.processed_groups:
                    self.processed_groups.add(group_name)
                    if user_level == "level1":
                        return f"{message} - moving down, activating vacuum, and returning to safe height"
                    elif user_level == "level2":
                        return f"{shape} pickup: approach, vacuum on, safe return"
                    else:
                        return f"{shape} pickup"

        # Place sequences - CORRECTED ORDER
        place_groups = {
            "circle_place": ("Circle", "Executing circle placing sequence"),
            "star_place": ("Star", "Executing star placing sequence"),
            "hexagon_place": ("Hexagon", "Executing hexagon placing sequence"),
            "triangle_place": ("Triangle", "Executing triangle placing sequence"),
            "square_place": ("Square", "Executing square placing sequence")
        }

        for group_name, (shape, message) in place_groups.items():
            if current_point in MOVEMENT_GROUPS[group_name]:
                if group_name not in self.processed_groups:
                    self.processed_groups.add(group_name)
                    if user_level == "level1":
                        return f"{message} - moving down, releasing vacuum, and returning to safe height"
                    elif user_level == "level2":
                        return f"{shape} place: approach, vacuum off, safe return"
                    else:
                        return f"{shape} place"

        # Final movements
        if current_point in MOVEMENT_GROUPS["final_movements"]:
            if "final_movements" not in self.processed_groups:
                self.processed_groups.add("final_movements")
                if user_level == "level1":
                    return "Executing final position movements through p30 to p70"
                elif user_level == "level2":
                    return "Final movement sequence: positions p30-p70"
                else:
                    return "Final moves"

        return None

    def status_change_notification(self, status):
        status_msg = f"Subscription status changed: {status}"
        self.gui_app.log_opcua_message(status_msg)
        print(status_msg)  # Debug print


# ... (Rest of the code remains the same - ABBOPCUAConnector, UserLevelManager, LoginSystem, RobotSimulationWindow classes)

class ABBOPCUAConnector:
    """ABB OPC UA Connector using proper subscription model"""

    def __init__(self, message_callback):
        self.client = None
        self.subscription = None
        self.handler = None
        self.is_connected = False
        self.is_monitoring = False
        self.message_callback = message_callback

    def connect(self, url):
        """Connect to OPC UA server"""
        try:
            self.client = Client(url)
            self.client.application_uri = "urn:universitywest:ABB:PythonClient"

            self.log_message("Connecting to OPC UA server...")
            self.client.connect()

            # Load ABB type definitions for decoding ExtensionObjects
            self.client.load_type_definitions()

            self.is_connected = True
            self.log_message(" Successfully connected to ABB Robot OPC UA server")
            return True

        except Exception as e:
            self.log_message(f"❌ Connection failed: {e}", is_error=True)
            self.is_connected = False
            return False

    def disconnect(self):
        """Disconnect from OPC UA server"""
        try:
            self.stop_monitoring()

            if self.client:
                self.client.disconnect()
                self.client = None

            self.is_connected = False
            self.is_monitoring = False
            self.log_message(" Disconnected from OPC UA server")

        except Exception as e:
            self.log_message(f"Error during disconnect: {e}", is_error=True)

    def start_monitoring(self):
        """Start monitoring program pointer"""
        if not self.is_connected:
            self.log_message("Not connected to server", is_error=True)
            return False

        try:
            program_point_node = self.client.get_node(PROGRAM_POINT_NODE_ID)

            # Test reading the value first
            try:
                test_value = program_point_node.get_value()
                self.log_message(f"Test read value: {test_value}")
                print(f"Test read value type: {type(test_value)}")  # Debug
            except Exception as e:
                self.log_message(f"Test read failed: {e}", is_error=True)

            # Create subscription handler
            self.handler = OPCUASubscriptionHandler(self.gui_app)
            self.subscription = self.client.create_subscription(500, self.handler)
            self.subscription.subscribe_data_change(program_point_node)

            self.is_monitoring = True
            self.log_message("📡 Started monitoring program execution")
            return True

        except Exception as e:
            self.log_message(f"Failed to start monitoring: {e}", is_error=True)
            return False

    def stop_monitoring(self):
        """Stop monitoring"""
        try:
            if self.subscription:
                self.subscription.delete()
                self.subscription = None

            self.is_monitoring = False
            self.log_message("⏹️ Stopped program monitoring")

        except Exception as e:
            self.log_message(f"Error stopping monitoring: {e}", is_error=True)

    def get_robot_status(self):
        """Get current robot status"""
        if not self.is_connected:
            return None

        try:
            program_point_node = self.client.get_node(PROGRAM_POINT_NODE_ID)
            value = program_point_node.get_value()

            status_info = {
                'connected': True,
                'monitoring': self.is_monitoring,
                'program_point': str(value)
            }

            # Try to extract detailed info
            try:
                if hasattr(value, 'Line'):
                    status_info['line'] = value.Line
                if hasattr(value, 'Module'):
                    status_info['module'] = value.Module
                if hasattr(value, 'Routine'):
                    status_info['routine'] = value.Routine
            except:
                pass

            return status_info

        except Exception as e:
            self.log_message(f"Error getting robot status: {e}", is_error=True)
            return None

    def log_message(self, message, is_error=False):
        """Log message through callback"""
        if self.message_callback:
            category = "error" if is_error else "system"
            self.message_callback(category, message)


class UserLevelManager:
    """Manages user level configurations"""

    @staticmethod
    def get_numeric_level(user_level):
        """Convert user level string to numeric value"""
        level_map = {
            "level1": 1,
            "level2": 2,
            "level3": 3
        }
        return level_map.get(user_level.lower(), 1)

    @staticmethod
    def get_message_style(user_level):
        """Get description of message style for user level"""
        styles = {
            "level1": "",
            "level2": "",
            "level3": ""
        }
        return styles.get(user_level.lower(), "")


# Initialize user level manager
user_level_manager = UserLevelManager()


class LoginSystem:
    # Hardcoded users and their access levels
    HARDCODED_USERS = {
        "sai": {"password": "123", "name": "Sai", "user_level": "Level1"},
        "gayan": {"password": "456", "name": "Gayan", "user_level": "Level2"},
        "susmitha": {"password": "789", "name": "Susmitha", "user_level": "Level3"}
    }

    def __init__(self, root):
        self.root = root
        self.root.title("University West ABB Robot System")
        self.root.geometry("900x500")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)

        # Setup UI
        self.setup_ui()

        # Update status since DB connection is bypassed
        self.status_label.config(text="Database connection bypassed (Hardcoded Users)", fg='#f39c12')

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill='x', pady=(20, 10))

        title = tk.Label(header_frame, text="University West ABB Robot System", font=("Arial", 24, "bold"),
                         fg='#ecf0f1', bg='#2c3e50')
        title.pack()

        subtitle = tk.Label(header_frame, text="Select your access level and login", font=("Arial", 12),
                            fg='#bdc3c7', bg='#2c3e50')
        subtitle.pack(pady=(5, 15))

        # Main content frame
        main_frame = tk.Frame(self.root, bg='#34495e', padx=30, pady=30, relief='raised', bd=3)
        main_frame.pack(expand=True, fill='both', padx=40, pady=20)

        # Login form
        form_frame = tk.Frame(main_frame, bg='#34495e')
        form_frame.pack(pady=20)

        # User Level Selection (Dropdown)
        tk.Label(form_frame, text="User Level:", font=("Arial", 14),
                 fg='#ecf0f1', bg='#34495e').grid(row=0, column=0, sticky='w', pady=10, padx=10)

        self.user_level = tk.StringVar()
        self.user_level.set("Level1")

        level_dropdown = ttk.Combobox(form_frame, textvariable=self.user_level,
                                      font=("Arial", 12), width=22, state="readonly")
        level_dropdown['values'] = ('Level1', 'Level2', 'Level3')
        level_dropdown.grid(row=0, column=1, pady=10, padx=10)

        # User ID
        tk.Label(form_frame, text="User ID:", font=("Arial", 14),
                 fg='#ecf0f1', bg='#34495e').grid(row=1, column=0, sticky='w', pady=10, padx=10)

        self.entry_userid = tk.Entry(form_frame, font=("Arial", 14), width=25)
        self.entry_userid.grid(row=1, column=1, pady=10, padx=10)

        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 14),
                 fg='#ecf0f1', bg='#34495e').grid(row=2, column=0, sticky='w', pady=10, padx=10)

        self.entry_password = tk.Entry(form_frame, show="*", font=("Arial", 14), width=25)
        self.entry_password.grid(row=2, column=1, pady=10, padx=10)

        # Login button
        login_btn = tk.Button(form_frame, text="Login", command=self.login,
                              font=("Arial", 14, "bold"), bg='#3498db', fg='white',
                              width=12, height=1, relief='flat')
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Status frame
        status_frame = tk.Frame(main_frame, bg='#34495e')
        status_frame.pack(fill='x', pady=10)

        self.status_label = tk.Label(status_frame, text="Database connection bypassed (Hardcoded Users)",
                                     font=("Arial", 10), fg='#f39c12', bg='#34495e')
        self.status_label.pack()

        # Info frame
        info_frame = tk.Frame(main_frame, bg='#34495e')
        info_frame.pack(fill='x', pady=20)

        info_text = """Demo Login Credentials (Hardcoded):

Level 1 Users (Basic Access - ):
User ID: sai, Password: 123
• Real-time OPC UA connection
• Detailed robot operation messages  
• Line-by-line execution monitoring
• Text-to-Speech audio feedback

Level 2 Users (Moderate Access - ):
User ID: gayan, Password: 456

Level 3 Users (Admin Access - ):
User ID: susmitha, Password: 789

Select your access level from the dropdown menu"""

        info_label = tk.Label(info_frame, text=info_text, font=("Arial", 10),
                              fg='#bdc3c7', bg='#34495e', justify='left')
        info_label.pack()

    def login(self):
        user_level = self.user_level.get()
        userid = self.entry_userid.get().strip()
        password = self.entry_password.get().strip()

        if not userid or not password:
            messagebox.showerror("Input Error", "Please enter both User ID and Password")
            return

        # --- HARDCODED LOGIN LOGIC ---
        user_data = self.HARDCODED_USERS.get(userid.lower())

        if user_data:
            if user_data["password"] == password:
                # Check if user has the correct access level
                if user_data['user_level'] == user_level:
                    messagebox.showinfo("Login Success",
                                        f"Welcome {user_data['name']}!\nAccess Level: {user_data['user_level']}")

                    # Open different windows based on user level
                    self.open_demo_simulation(user_data['name'], user_data['user_level'])

                    self.entry_userid.delete(0, tk.END)
                    self.entry_password.delete(0, tk.END)
                else:
                    messagebox.showerror("Access Denied",
                                         f"Your account has {user_data['user_level']} access.\n"
                                         f"Please select {user_data['user_level']} from the dropdown.")
            else:
                messagebox.showerror("Login Failed", "Invalid User ID or Password")
        else:
            messagebox.showerror("Login Failed", "Invalid User ID or Password")

    def open_demo_simulation(self, username, user_level):
        """Open simulation window directly for the given user level"""
        window = RobotSimulationWindow(self.root, user_level, username)
        # Test speech after window opens
        window.window.after(1000, window.test_speech)


class RobotSimulationWindow:
    def __init__(self, parent, user_level="Level1", username=""):
        self.parent = parent
        self.user_level = user_level
        self.username = username
        self.user_numeric_level = user_level_manager.get_numeric_level(user_level)
        self.last_line_displayed = None
        self.gui_app = self  # Add this reference for OPCUA handler

        # Initialize message queue manager
        self.message_queue_manager = MessageQueueManager(
            display_callback=self.display_messages,
            speech_callback=tts_manager.speak_text
        )

        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"ABB Robot Real-Time Monitor - {user_level} User: {username}")
        self.window.geometry("1200x750")
        self.window.configure(bg='#2c3e50')
        self.window.resizable(True, True)

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Initialize OPC UA connector
        self.opcua_connector = ABBOPCUAConnector(self.handle_opcua_message)
        self.opcua_connector.gui_app = self  # Set reference for connector

        # Setup UI
        self.setup_ui()

        # Center the window
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def setup_ui(self):
        """Setup the main user interface"""
        # Header
        header_frame = tk.Frame(self.window, bg='#3498db')
        header_frame.pack(fill='x', pady=(0, 10))

        title = tk.Label(header_frame, text=f" ABB Robot Real-Time Monitor - {self.user_level}",
                         font=("Arial", 18, "bold"), fg='white', bg='#3498db')
        title.pack(pady=10)

        user_info = tk.Label(header_frame,
                             text=f"User: {self.username} | Level: {self.user_level} - {user_level_manager.get_message_style(self.user_level)}",
                             font=("Arial", 10), fg='#ecf0f1', bg='#3498db')
        user_info.pack(pady=(0, 10))

        # OPC UA Connection Frame
        self.setup_opcua_interface()

        # Main content frame - AI Messages on top (full width)
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # AI Messages frame - Full width at the top
        ai_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        ai_frame.pack(fill='x', pady=(0, 10))  # Full width, bottom margin

        # Setup AI messages display (full width)
        self.setup_ai_messages_display(ai_frame)

        # Real-time execution frame - Centered at bottom
        execution_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        execution_frame.pack(fill='x', pady=(0, 5))  # Reduced bottom margin

        # Setup real-time execution display
        self.setup_realtime_execution_display(execution_frame)

        # Program Status Display - Single line toolbar at very bottom
        status_toolbar = tk.Frame(main_frame, bg='#2c3e50', relief='sunken', bd=1)
        status_toolbar.pack(fill='x', pady=(5, 0))

        # Create program status display in the toolbar
        self.create_program_status_display(status_toolbar)

        # Add welcome messages to queue
        # self.message_queue_manager.add_message(f" Welcome {self.username}! Ready to monitor ABB robot in real-time.")
        # self.message_queue_manager.add_message(f" OPC UA connection will show real robot movements line by line")

    def setup_opcua_interface(self):
        """Setup OPC UA connection interface"""
        opcua_frame = tk.Frame(self.window, bg='#34495e', relief='raised', bd=2)
        opcua_frame.pack(fill='x', padx=20, pady=10)

        # OPC UA Controls
        control_frame = tk.Frame(opcua_frame, bg='#34495e')
        control_frame.pack(fill='x', pady=5)

        tk.Label(control_frame, text="ABB Robot OPC UA Monitor:",
                 font=("Arial", 11, "bold"), fg='#ecf0f1', bg='#34495e').pack(side='left')

        # Connection URL
        url_frame = tk.Frame(control_frame, bg='#34495e')
        url_frame.pack(side='left', padx=10)

        tk.Label(url_frame, text="Server URL:", font=("Arial", 9),
                 fg='#ecf0f1', bg='#34495e').pack(side='left')

        self.opcua_url = tk.Entry(url_frame, width=35, font=("Arial", 9))
        self.opcua_url.insert(0, DEFAULT_OPC_UA_URL)
        self.opcua_url.pack(side='left', padx=5)

        # Connection buttons
        self.connect_btn = tk.Button(
            control_frame,
            text="Connect to Robot",
            command=self.connect_opcua,
            font=("Arial", 10),
            bg='#27ae60',
            fg='white',
            relief='flat',
            padx=15
        )
        self.connect_btn.pack(side='left', padx=5)

        self.monitor_btn = tk.Button(
            control_frame,
            text="Start Monitoring",
            command=self.toggle_opcua_monitoring,
            font=("Arial", 10),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=15,
            state=tk.DISABLED
        )
        self.monitor_btn.pack(side='left', padx=5)

        self.status_btn = tk.Button(
            control_frame,
            text="Get Status",
            command=self.get_robot_status,
            font=("Arial", 10),
            bg='#9b59b6',
            fg='white',
            relief='flat',
            padx=15,
            state=tk.DISABLED
        )
        self.status_btn.pack(side='left', padx=5)

        # Connection status indicator
        status_indicator_frame = tk.Frame(control_frame, bg='#34495e')
        status_indicator_frame.pack(side='right', padx=10)

        tk.Label(status_indicator_frame, text="Connection:", font=("Arial", 9),
                 fg='#ecf0f1', bg='#34495e').pack(side='left')

        self.connection_indicator = tk.Label(
            status_indicator_frame,
            text="●",
            font=("Arial", 16),
            fg='#e74c3c',  # Red for disconnected
            bg='#34495e'
        )
        self.connection_indicator.pack(side='left', padx=5)

        self.opcua_status = tk.Label(
            status_indicator_frame,
            text="Disconnected",
            font=("Arial", 9),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.opcua_status.pack(side='left')

    def create_program_status_display(self, parent):
        """Create program status display as single line toolbar"""
        # Main container for status items
        status_container = tk.Frame(parent, bg='#34495e')
        status_container.pack(fill='x', padx=10, pady=8)

        # Title label
        tk.Label(status_container, text="Program Status:",
                 font=("Arial", 10, "bold"), fg='#ecf0f1', bg='#34495e'
                 ).pack(side='left', padx=(0, 15))

        # Module Display
        module_frame = tk.Frame(status_container, bg='#34495e')
        module_frame.pack(side='left', padx=15)

        tk.Label(module_frame, text="Module:", font=("Arial", 9),
                 fg='#bdc3c7', bg='#34495e').pack(side='left')
        self.module_label = tk.Label(module_frame, text="---",
                                     font=("Arial", 9, "bold"), fg='#3498db', bg='#34495e')
        self.module_label.pack(side='left', padx=(5, 0))

        # Separator
        tk.Label(status_container, text="|", font=("Arial", 9),
                 fg='#7f8c8d', bg='#34495e').pack(side='left', padx=15)

        # Routine Display
        routine_frame = tk.Frame(status_container, bg='#34495e')
        routine_frame.pack(side='left', padx=15)

        tk.Label(routine_frame, text="Routine:", font=("Arial", 9),
                 fg='#bdc3c7', bg='#34495e').pack(side='left')
        self.routine_label = tk.Label(routine_frame, text="---",
                                      font=("Arial", 9, "bold"), fg='#27ae60', bg='#34495e')
        self.routine_label.pack(side='left', padx=(5, 0))

        # Separator
        tk.Label(status_container, text="|", font=("Arial", 9),
                 fg='#7f8c8d', bg='#34495e').pack(side='left', padx=15)

        # Line Number Display
        line_frame = tk.Frame(status_container, bg='#34495e')
        line_frame.pack(side='left', padx=15)

        tk.Label(line_frame, text="Line:", font=("Arial", 9),
                 fg='#bdc3c7', bg='#34495e').pack(side='left')
        self.line_label = tk.Label(line_frame, text="---",
                                   font=("Arial", 9, "bold"), fg='#e74c3c', bg='#34495e')
        self.line_label.pack(side='left', padx=(5, 0))

    def setup_realtime_execution_display(self, parent):
        """Setup the real-time execution display"""
        # Status frame
        status_frame = tk.Frame(parent, bg='#34495e')
        status_frame.pack(fill='x', pady=5, padx=10)

        self.sim_status_label = tk.Label(status_frame, text="Ready to monitor real robot execution...",
                                         font=("Arial", 12, "bold"), fg='#ecf0f1', bg='#34495e')
        self.sim_status_label.pack()

        # Real-time execution display area
        display_frame = tk.Frame(parent, bg='#34495e')
        display_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Text area for real-time execution details - Centered
        tk.Label(display_frame, text="Real-Time Robot Execution:", font=("Arial", 11, "bold"),
                 fg='#ecf0f1', bg='#34495e').pack(anchor='center')

        self.execution_text = scrolledtext.ScrolledText(display_frame, height=8, width=60,
                                                        font=("Courier New", 9), bg='#ecf0f1',
                                                        fg='#2c3e50')
        self.execution_text.pack(expand=True, fill='both', padx=5, pady=5)
        self.execution_text.config(state=tk.DISABLED)

        # Configure tags for execution text
        self.execution_text.tag_configure("execution_time", foreground="#7f8c8d")

    def setup_ai_messages_display(self, parent):
        """Setup the AI messages display area"""
        # Header for AI messages with audio controls
        ai_header_frame = tk.Frame(parent, bg='#2980b9')
        ai_header_frame.pack(fill='x', pady=(0, 5))

        # Left side: Title
        title_frame = tk.Frame(ai_header_frame, bg='#2980b9')
        title_frame.pack(side='left', fill='x', expand=True)

        ai_title = tk.Label(title_frame, text="- ROBOT COMMUNICATION - ",
                            font=("Arial", 14, "bold"), fg='white', bg='#2980b9')
        ai_title.pack(pady=8)

        # Right side: Audio controls
        audio_frame = tk.Frame(ai_header_frame, bg='#2980b9')

        audio_frame.pack(side='right', padx=10)

        # Audio icon and controls - using simple text symbols
        self.audio_icon = tk.Label(audio_frame, text="[SPK]", font=("Arial", 10, "bold"),
                                   bg='#2980b9', fg='#27ae60', cursor="hand2")
        self.audio_icon.pack(side='left', padx=5)
        self.audio_icon.bind("<Button-1>", self.toggle_speech)

        self.audio_btn = tk.Button(audio_frame, text="Speech: ON",
                                   command=self.toggle_speech,
                                   font=("Arial", 8), bg='#27ae60', fg='white',
                                   relief='flat', padx=8, pady=2)
        self.audio_btn.pack(side='left', padx=5)

        # User level info
        level_info = tk.Label(ai_header_frame,
                              text=f"Message Level: {self.user_level} ({user_level_manager.get_message_style(self.user_level)})",
                              font=("Arial", 10), fg='#ecf0f1', bg='#2980b9')
        level_info.pack(pady=(0, 8))

        # AI Messages display - Special frame for 2 messages only
        messages_frame = tk.Frame(parent, bg='#2c3e50', height=150)  # Fixed height
        messages_frame.pack(fill='x', padx=10, pady=10)
        messages_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Create a dedicated text widget for displaying only 2 messages
        self.ai_message_display = tk.Text(messages_frame, height=4, width=80,
                                          font=("Arial", 14, "bold"),  # Increased font size
                                          bg='#2c3e50', fg='white',
                                          wrap=tk.WORD, relief='flat')

        # Configure tags for different message levels with larger fonts
        self.ai_message_display.tag_configure("level1", foreground="#3498db", font=("Arial", 14, "bold"))
        self.ai_message_display.tag_configure("level2", foreground="#27ae60", font=("Arial", 14, "bold"))
        self.ai_message_display.tag_configure("level3", foreground="#e74c3c", font=("Arial", 14, "bold"))

        self.ai_message_display.pack(expand=True, fill='both', padx=5, pady=5)
        self.ai_message_display.config(state=tk.DISABLED)

        # Queue status label
        self.queue_status = tk.Label(parent, text="Messages in queue: 0",
                                     font=("Arial", 10), fg='#bdc3c7', bg='#34495e')
        self.queue_status.pack(pady=(0, 10))

    def display_messages(self, messages):
        """Display 2 messages at a time or clear the display"""
        self.ai_message_display.config(state=tk.NORMAL)
        self.ai_message_display.delete(1.0, tk.END)

        if messages:
            for i, message in enumerate(messages):
                tag = f"level{self.user_numeric_level}"
                self.ai_message_display.insert(tk.END, f"{message}\n\n", tag)

        self.ai_message_display.config(state=tk.DISABLED)

        # Update queue status
        queue_size = len(self.message_queue_manager.message_queue)
        self.queue_status.config(text=f"Messages in queue: {queue_size}")

    def toggle_speech(self, event=None):
        """Toggle text-to-speech on/off"""
        speech_enabled = tts_manager.toggle_speech()
        if speech_enabled:
            self.audio_icon.config(text="[SPK]", fg='#27ae60')
            self.audio_btn.config(text="Speech: ON", bg='#27ae60')
            self.add_ai_message("Text-to-speech enabled")
        else:
            self.audio_icon.config(text="[SPK]", fg='#e74c3c')
            self.audio_btn.config(text="Speech: OFF", bg='#e74c3c')
            tts_manager.stop_speech()
            self.add_ai_message("Text-to-speech disabled")

    def clean_unicode_chars(self, text):
        """Placeholder for robust cleaning logic"""
        if not isinstance(text, str):
            return str(text)
        return text.encode('ascii', 'ignore').decode('ascii')

    def add_ai_message(self, message):
        """Add an AI-generated message to the queue"""
        safe_message = self.clean_unicode_chars(message)
        self.message_queue_manager.add_message(safe_message)

    def add_execution_message(self, message):
        """Add execution message to real-time display"""
        safe_message = self.clean_unicode_chars(message)

        self.execution_text.config(state=tk.NORMAL)

        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.execution_text.insert(tk.END, f"[{timestamp}] ", "execution_time")

        self.execution_text.insert(tk.END, f"{safe_message}\n")
        self.execution_text.see(tk.END)
        self.execution_text.config(state=tk.DISABLED)

    def connect_opcua(self):
        """Connect to ABB Robot OPC UA server"""
        url = self.opcua_url.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter OPC UA server URL")
            return

        self.opcua_status.config(text="Connecting...", fg='#f39c12')
        self.connection_indicator.config(fg='#f39c12')  # Yellow for connecting
        self.connect_btn.config(state=tk.DISABLED)

        # Connect in separate thread
        threading.Thread(target=self._connect_async, args=(url,), daemon=True).start()

    def _connect_async(self, url):
        """Connect to OPC UA asynchronously"""
        success = self.opcua_connector.connect(url)

        # Update UI in main thread
        self.window.after(0, self._update_connection_status, success)

    def _update_connection_status(self, success):
        """Update connection status in UI"""
        if success:
            self.opcua_status.config(text="Connected", fg='#27ae60')
            self.connection_indicator.config(fg='#27ae60')  # Green for connected
            self.monitor_btn.config(state=tk.NORMAL)
            self.status_btn.config(state=tk.NORMAL)
            self.connect_btn.config(text="Disconnect", bg='#e74c3c', command=self.disconnect_opcua)
            self.add_ai_message("Successfully connected to ABB Robot via OPC UA")
            self.add_execution_message("OPC UA Connection Established - Ready to monitor robot execution")
            self.sim_status_label.config(text="Connected to robot - Ready for real-time monitoring")
        else:
            self.opcua_status.config(text="Connection failed", fg='#e74c3c')
            self.connection_indicator.config(fg='#e74c3c')  # Red for failed
            self.connect_btn.config(state=tk.NORMAL)
            self.add_ai_message("Failed to connect to ABB Robot")

    def disconnect_opcua(self):
        """Disconnect from OPC UA server"""
        self.opcua_connector.disconnect()
        self.opcua_status.config(text="Disconnected", fg='#e74c3c')
        self.connection_indicator.config(fg='#e74c3c')  # Red for disconnected
        self.connect_btn.config(text="Connect to Robot", bg='#27ae60', command=self.connect_opcua)
        self.monitor_btn.config(state=tk.DISABLED, text="Start Monitoring", bg='#3498db')
        self.status_btn.config(state=tk.DISABLED)
        self.add_ai_message(" Disconnected from ABB Robot")
        self.add_execution_message("OPC UA Connection Closed")
        self.sim_status_label.config(text="Disconnected from robot")

        # Reset program status display
        self.update_robot_status("---", "---", "---")

    def toggle_opcua_monitoring(self):
        """Start/stop OPC UA monitoring"""
        if not self.opcua_connector.is_monitoring:
            success = self.opcua_connector.start_monitoring()
            if success:
                self.monitor_btn.config(text="Stop Monitoring", bg='#e74c3c')
                self.add_ai_message("Started real-time monitoring of ABB Robot")
                self.add_execution_message("Real-time monitoring STARTED - Watching program execution")
                self.sim_status_label.config(text="Monitoring robot execution in real-time")
        else:
            self.opcua_connector.stop_monitoring()
            self.monitor_btn.config(text="Start Monitoring", bg='#3498db')
            self.add_ai_message("️ Stopped robot monitoring")
            self.add_execution_message("Real-time monitoring STOPPED")
            self.sim_status_label.config(text="Monitoring stopped - Robot connected")

    def get_robot_status(self):
        """Get and display current robot status"""
        status = self.opcua_connector.get_robot_status()
        if status:
            self.add_ai_message(f" Robot Status: Connected={status['connected']}, Monitoring={status['monitoring']}")
            if 'line' in status:
                self.add_ai_message(
                    f" Current Line: {status.get('line', 'N/A')}, Module: {status.get('module', 'N/A')}, Routine: {status.get('routine', 'N/A')}")

    def handle_opcua_message(self, category, data):
        """Handle messages from OPC UA connector"""
        if category == "system":
            self.add_ai_message(f" {data}")
        elif category == "error":
            self.add_ai_message(f" {data}")

    def log_opcua_message(self, message, is_error=False):
        """Log OPC UA messages"""
        if is_error:
            self.add_ai_message(f"{message}")
            self.add_execution_message(f"ERROR: {message}")
        else:
            # Remove OPC UA prefix and send clean message
            clean_message = message.replace('OPC UA:', '').strip()
            self.add_ai_message(clean_message)
            self.add_execution_message(f"INFO: {clean_message}")

    def update_robot_status(self, module, routine, line):
        """Update robot program status in UI"""
        self.window.after(0, self._update_status_display, module, routine, line)

    def _update_status_display(self, module, routine, line):
        """Update status display in main thread"""
        self.module_label.config(text=module)
        self.routine_label.config(text=routine)
        self.line_label.config(text=str(line))

        # Also add to execution display
        if line != "---" and line != self.last_line_displayed:
            self.add_execution_message(f"Program Pointer: Module={module}, Routine={routine}, Line={line}")
            self.last_line_displayed = line

    def test_speech(self):
        """Test speech functionality"""
        tts_manager.test_speech()


# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginSystem(root)
    root.mainloop()