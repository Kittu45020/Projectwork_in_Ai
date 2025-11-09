import json
import random
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class ComprehensiveAIMessageGenerator:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.model_file = 'robot_message_model.joblib'
        self.comprehensive_data = self.generate_comprehensive_data()
        self.load_or_train_model()

    def generate_comprehensive_data(self):
        """Generate comprehensive training data on-the-fly"""
        print("Generating comprehensive training data for industrial robots...")

        # Expanded action categories for industrial scenarios
        base_actions = ['move', 'move_forward', 'move_backward', 'move_left', 'move_right', 'move_up', 'move_down',
                        'home']
        tool_actions = ['tool_change', 'tool_attach', 'tool_release', 'gripper_open', 'gripper_close']
        vision_actions = ['image_capture', 'object_detection', 'quality_inspection', 'barcode_scan']
        manufacturing_actions = ['welding', 'painting', 'assembly', 'drilling', 'cutting']
        abb_actions = ['joint_move', 'linear_move', 'circular_move', 'pick_place']
        safety_actions = ['emergency_stop', 'collision_detect', 'safety_check']

        all_actions = base_actions + tool_actions + vision_actions + manufacturing_actions + abb_actions + safety_actions

        training_data = []

        for action in all_actions:
            # Generate multiple variations for each level
            for level in [1, 2, 3]:
                variations = self.generate_action_variations(action, level, 3)
                training_data.extend(variations)

        print(f" Generated {len(training_data)} training examples for {len(all_actions)} industrial actions")
        return training_data

    def generate_action_variations(self, action, level, num_variations):
        """Generate multiple message variations"""
        variations = []

        for i in range(num_variations):
            if level == 1:
                message = self.generate_level1_message(action, i)
            elif level == 2:
                message = self.generate_level2_message(action, i)
            else:  # level 3
                message = self.generate_level3_message(action, i)

            variations.append({
                "input": f"{action} level{level}",
                "output": message
            })

        return variations

    def generate_level1_message(self, action, variation):
        """Generate Level 1: Detailed descriptive messages with context"""
        message_templates = {
            # Tool Operations
            'tool_change': [
                "Robot is changing tool, moving to tool holder position, securing new tool, and returning to work position safely",
                "Performing tool change operation: approaching tool station, exchanging end effector, and verifying tool connection",
                "Executing tool replacement sequence with alignment check and safety verification before continuing operation"
            ],
            'tool_attach': [
                "Robot is attaching tool, moving to tool position, connecting interface, and testing tool functionality",
                "Mounting end effector with precision alignment and verifying all connections are secure",
                "Installing tool with automatic calibration and performing functional test before operation"
            ],
            'tool_release': [
                "Robot is releasing current tool, moving to storage position, and safely detaching end effector",
                "Removing tool with controlled motion and storing it in designated location for next use",
                "Detaching end effector with safety checks and returning to home position after tool release"
            ],

            # Movement Operations
            'move_forward': [
                "Robot is moving forward along X-axis, maintaining safe speed, and monitoring for obstacles",
                "Executing forward motion with continuous path monitoring and collision avoidance systems active",
                "Moving in forward direction with smooth acceleration and position feedback control"
            ],
            'move_backward': [
                "Robot is moving backward to previous position, checking rear area, and maintaining safe clearance",
                "Reversing motion with rear collision detection enabled and controlled deceleration profile",
                "Moving backward along programmed path with safety zone monitoring"
            ],
            'move_left': [
                "Robot is moving left along Y-axis, adjusting position, and maintaining workspace boundaries",
                "Executing leftward motion with side clearance verification and continuous position tracking",
                "Moving to the left with coordinated axis movement and workspace limit monitoring"
            ],
            'move_right': [
                "Robot is moving right to target position, following smooth trajectory, and avoiding obstacles",
                "Performing rightward motion with path optimization and real-time obstacle detection",
                "Moving right with precision control and maintaining safe distance from equipment"
            ],
            'move_up': [
                "Robot is moving upward along Z-axis, lifting payload, and maintaining stable elevation",
                "Executing upward motion with load compensation and height limit monitoring",
                "Rising vertically with smooth acceleration and top position safety checks"
            ],
            'move_down': [
                "Robot is moving downward to lower position, controlled descent, and accurate placement",
                "Lowering with precision control and monitoring for ground clearance",
                "Moving downward with gradual speed reduction and target position verification"
            ],
            'home': [
                "Robot is returning to home position, following safe path, and preparing for next operation",
                "Moving to home position with optimized trajectory and system reset procedure",
                "Returning to reference position with all axes coordinated and safety checks completed"
            ],

            # Manufacturing Operations
            'welding': [
                "Robot is performing welding operation, maintaining arc stability, and monitoring weld quality",
                "Executing weld sequence with parameter control and real-time quality inspection",
                "Welding with precise path following and continuous process monitoring"
            ],
            'painting': [
                "Robot is painting surface, maintaining consistent spray pattern, and ensuring complete coverage",
                "Performing paint application with flow control and surface quality verification",
                "Spray painting with optimized path and coating thickness monitoring"
            ],
            'assembly': [
                "Robot is assembling components, precise part placement, and verifying correct fitment",
                "Executing assembly sequence with force control and component alignment checks",
                "Performing mechanical assembly with insertion verification and quality assurance"
            ],

            # Vision Operations
            'image_capture': [
                "Robot is capturing images for inspection, adjusting lighting, and processing visual data",
                "Taking high-resolution images with camera system and analyzing for quality control",
                "Performing vision inspection with multiple angle capture and defect detection"
            ],
            'quality_inspection': [
                "Robot is conducting quality check, comparing measurements, and recording inspection results",
                "Executing quality inspection routine with sensor fusion and tolerance verification",
                "Performing comprehensive quality assessment with multiple test criteria"
            ],

            # Safety Operations
            'emergency_stop': [
                "EMERGENCY STOP ACTIVATED: Robot is immediately stopping all motion, applying brakes, and entering safe state",
                "Safety emergency triggered: All systems halted with controlled deceleration and safety protocols engaged",
                "Emergency stop executed: Motion terminated, power reduced, and safety monitoring active"
            ],
            'collision_detect': [
                "Collision detection active: Robot is monitoring workspace, reducing speed in tight areas, and avoiding obstacles",
                "Collision avoidance system engaged: Scanning environment and adjusting path for safety",
                "Proximity monitoring: Robot is maintaining safe distances and preparing for emergency stop if needed"
            ],

            # Default movement patterns
            'move': [
                "Robot is moving to target position with coordinated axis control and continuous path monitoring",
                "Executing movement sequence with smooth trajectory planning and obstacle avoidance",
                "Performing precise positioning with real-time feedback and safety system monitoring"
            ],
            'connect': [
                "Robot system is establishing connection with external controller and verifying communication protocols",
                "Initializing communication interface and performing handshake with control system",
                "Establishing secure connection with robot controller and verifying data exchange"
            ]
        }

        # Default templates for unknown actions
        default_templates = [
            f"Robot is performing {action.replace('_', ' ')} operation with full monitoring and safety systems active",
            f"Executing {action.replace('_', ' ')} sequence with complete system oversight and quality checks",
            f"Performing {action.replace('_', ' ')} procedure with real-time monitoring and safety verification"
        ]

        templates = message_templates.get(action, default_templates)
        return templates[variation % len(templates)]

    def generate_level2_message(self, action, variation):
        """Generate Level 2: Simple operational messages"""
        message_templates = {
            'tool_change': [
                "Robot is changing tool",
                "Performing tool change",
                "Exchanging end effector"
            ],
            'tool_attach': [
                "Attaching tool",
                "Mounting end effector",
                "Installing tool"
            ],
            'tool_release': [
                "Releasing tool",
                "Removing end effector",
                "Detaching tool"
            ],
            'move_forward': [
                "Moving forward",
                "Going forward",
                "Advancing"
            ],
            'move_backward': [
                "Moving backward",
                "Going back",
                "Reversing"
            ],
            'move_left': [
                "Moving left",
                "Going left",
                "Left motion"
            ],
            'move_right': [
                "Moving right",
                "Going right",
                "Right motion"
            ],
            'move_up': [
                "Moving up",
                "Going up",
                "Rising"
            ],
            'move_down': [
                "Moving down",
                "Going down",
                "Lowering"
            ],
            'home': [
                "Going home",
                "Returning to home",
                "Home position"
            ],
            'welding': [
                "Performing welding",
                "Welding operation",
                "Arc welding"
            ],
            'painting': [
                "Spray painting",
                "Painting surface",
                "Coating application"
            ],
            'assembly': [
                "Assembling parts",
                "Component assembly",
                "Mechanical assembly"
            ],
            'image_capture': [
                "Taking pictures",
                "Image capture",
                "Vision inspection"
            ],
            'quality_inspection': [
                "Quality check",
                "Inspecting quality",
                "Quality verification"
            ],
            'emergency_stop': [
                "Emergency stop",
                "Safety stop",
                "Emergency halt"
            ],
            'collision_detect': [
                "Collision monitoring",
                "Obstacle detection",
                "Safety scanning"
            ],
            'move': [
                "Moving to position",
                "Executing movement",
                "Positioning robot"
            ],
            'connect': [
                "Connecting to system",
                "Establishing connection",
                "Initializing link"
            ]
        }

        default_templates = [
            f"Performing {action.replace('_', ' ')}",
            f"Executing {action.replace('_', ' ')}",
            f"Running {action.replace('_', ' ')}"
        ]

        templates = message_templates.get(action, default_templates)
        return templates[variation % len(templates)]

    def generate_level3_message(self, action, variation):
        """Generate Level 3: Very brief status messages"""
        short_forms = {
            'tool_change': "Changing tool",
            'tool_attach': "Attaching tool",
            'tool_release': "Releasing tool",
            'move_forward': "Forward",
            'move_backward': "Backward",
            'move_left': "Left",
            'move_right': "Right",
            'move_up': "Up",
            'move_down': "Down",
            'home': "Home",
            'welding': "Welding",
            'painting': "Painting",
            'assembly': "Assembly",
            'image_capture': "Image capture",
            'quality_inspection': "Quality check",
            'emergency_stop': "E-stop",
            'collision_detect': "Collision check",
            'gripper_open': "Grip open",
            'gripper_close': "Grip close",
            'joint_move': "Joint move",
            'linear_move': "Linear move",
            'circular_move': "Circular move",
            'pick_place': "Pick place",
            'object_detection': "Object detect",
            'barcode_scan': "Scanning",
            'safety_check': "Safety check",
            'move': "Moving",
            'connect': "Connecting"
        }

        return short_forms.get(action, action.replace('_', ' '))

    def load_or_train_model(self):
        """Load existing model or train a new one with comprehensive data"""
        try:
            if os.path.exists(self.model_file):
                self.model = joblib.load(self.model_file)
                self.is_trained = True
                print("AI Model loaded successfully!")
            else:
                print("Model file not found. Training new AI model...")
                self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}. Training new model...")
            self.train_model()

    def train_model(self):
        """Train the AI model with comprehensive data"""
        try:
            inputs = [item['input'] for item in self.comprehensive_data]
            outputs = [item['output'] for item in self.comprehensive_data]

            # Create and train model
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])

            self.model.fit(inputs, outputs)
            self.is_trained = True

            # Save the model
            joblib.dump(self.model, self.model_file)
            print(f"AI Model trained with {len(self.comprehensive_data)} industrial examples!")
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False

    def generate_message(self, action, user_level, step_details=None):
        """Generate AI message based on action and user level"""
        # Ensure user_level is integer (convert from string if needed)
        try:
            if isinstance(user_level, str):
                # Convert "Level1" to 1, "Level2" to 2, etc.
                user_level = int(user_level.replace('Level', ''))
        except:
            user_level = 1  # Default to level 1

        # Use direct generation instead of ML model for reliability
        return self.direct_message_generation(action, user_level, step_details)

    def direct_message_generation(self, action, user_level, step_details=None):
        """Direct message generation without ML model for reliability"""
        action_lower = action.lower()

        # Map actions to categories
        if any(word in action_lower for word in
               ['move', 'position', 'motion', 'forward', 'backward', 'left', 'right', 'up', 'down']):
            category = 'movement'
        elif any(word in action_lower for word in ['tool', 'gripper', 'attach', 'release', 'change']):
            category = 'tool'
        elif any(word in action_lower for word in ['image', 'vision', 'camera', 'detect', 'inspect', 'scan']):
            category = 'vision'
        elif any(word in action_lower for word in ['weld', 'paint', 'glue', 'screw', 'drill', 'cut', 'assemble']):
            category = 'manufacturing'
        elif any(word in action_lower for word in ['pick', 'place', 'pallet', 'conveyor', 'load', 'unload']):
            category = 'material_handling'
        elif any(word in action_lower for word in ['stop', 'emergency', 'safety', 'collision', 'error']):
            category = 'safety'
        elif any(word in action_lower for word in ['home', 'reset', 'initialize']):
            category = 'system'
        elif any(word in action_lower for word in ['connect', 'link', 'establish']):
            category = 'connection'
        else:
            category = 'general'

        # Generate messages based on category and user level
        messages = {
            'movement': {
                1: [
                    f"Robot is moving to target position with coordinated axis control and continuous path monitoring",
                    f"Executing movement sequence with smooth trajectory planning and obstacle avoidance",
                    f"Performing precise positioning with real-time feedback and safety system monitoring"
                ],
                2: [
                    f"Moving to target position",
                    f"Executing movement sequence",
                    f"Positioning robot arm"
                ],
                3: [
                    f"Moving",
                    f"Positioning",
                    f"Motion"
                ]
            },
            'tool': {
                1: [
                    f"Robot is operating tool system with interface control and status verification",
                    f"Executing tool operation with precision control and safety monitoring",
                    f"Performing tool manipulation with force feedback and alignment checks"
                ],
                2: [
                    f"Tool operation in progress",
                    f"Operating end effector",
                    f"Tool manipulation"
                ],
                3: [
                    f"Tool ops",
                    f"End effector",
                    f"Tool control"
                ]
            },
            'vision': {
                1: [
                    f"Robot is performing vision system operation with camera adjustment and image processing",
                    f"Executing vision inspection with lighting control and defect detection algorithms",
                    f"Performing optical measurement with calibration checks and quality validation"
                ],
                2: [
                    f"Vision system operation",
                    f"Performing image capture",
                    f"Vision inspection"
                ],
                3: [
                    f"Vision ops",
                    f"Image capture",
                    f"Inspection"
                ]
            },
            'safety': {
                1: [
                    f"Robot is executing safety procedure with system monitoring and protection protocols",
                    f"Performing safety check with comprehensive system scan and risk assessment",
                    f"Executing safety routine with emergency system verification and hazard prevention"
                ],
                2: [
                    f"Safety operation",
                    f"Performing safety check",
                    f"Safety monitoring"
                ],
                3: [
                    f"Safety",
                    f"Safety check",
                    f"Secure"
                ]
            },
            'connection': {
                1: [
                    f"Robot system is establishing secure connection with external controller and verifying communication protocols",
                    f"Initializing communication interface and performing handshake with control system",
                    f"Establishing secure connection with robot controller and verifying data exchange"
                ],
                2: [
                    f"Connecting to system",
                    f"Establishing connection",
                    f"Initializing link"
                ],
                3: [
                    f"Connecting",
                    f"Link",
                    f"Connect"
                ]
            },
            'general': {
                1: [
                    f"Robot is performing {action.replace('_', ' ')} operation with system monitoring and safety protocols",
                    f"Executing {action.replace('_', ' ')} procedure with real-time monitoring and quality checks",
                    f"Performing {action.replace('_', ' ')} operation with complete system oversight"
                ],
                2: [
                    f"Performing {action.replace('_', ' ')}",
                    f"Executing {action.replace('_', ' ')}",
                    f"Running {action.replace('_', ' ')}"
                ],
                3: [
                    f"{action.replace('_', ' ')}",
                    f"Operation",
                    f"Task"
                ]
            }
        }

        # Get category messages or default to general
        category_messages = messages.get(category, messages['general'])
        level_messages = category_messages.get(user_level, category_messages[1])

        # Select random message from available options
        message = random.choice(level_messages)

        # Add target information if available for level 1 and 2
        if step_details and 'target' in step_details and step_details['target']:
            if user_level == 1:
                message = f"{message} towards {step_details['target']}"
            elif user_level == 2:
                message = f"{message} to {step_details['target']}"
            # Level 3 remains very brief

        return message

    def generate_opcua_message(self, program_point, user_level):
        """Generate messages for OPC UA real-time program execution"""
        # Convert user_level to integer if needed
        if isinstance(user_level, str):
            user_level = int(user_level.replace('Level', ''))

        action_description = PROGRAM_POINT_ACTIONS.get(program_point, f"Executing program line {program_point}")

        if user_level == 1:
            return f"Robot is {action_description.lower()}"
        elif user_level == 2:
            # Extract the main action from the description
            main_action = action_description.split(':')[-1] if ':' in action_description else action_description
            return f"Executing: {main_action.strip()}"
        else:  # level 3
            # Very brief - just the key action
            if 'Executing' in action_description:
                return action_description.split('Executing')[-1].strip("' ").split(' ')[0]
            else:
                return action_description.split(' ')[0] if action_description else "Operating"


# Global instance
ai_generator = ComprehensiveAIMessageGenerator()

# Define PROGRAM_POINT_ACTIONS here for the OPC UA message generation
PROGRAM_POINT_ACTIONS = {
    15: "Moving to initial safe/home position",
    16: "Pausing for user input on Teach Pendant",
    17: "Waiting for external signal confirmation",
    18: "Starting pick-and-place operation",
    19: "Exiting main procedure",
    22: "Checking selected shape type",
    23: "Processing triangle shape",
    25: "Processing hexagon shape",
    27: "Processing circle shape",
    29: "Processing square shape",
    31: "Processing star shape",
    34: "Approaching pickup position",
    35: "Moving to exact pickup point",
    36: "Activating vacuum gripper",
    41: "Deactivating vacuum gripper",
    44: "Returning to home position",
    45: "Completing pickup procedure"
}