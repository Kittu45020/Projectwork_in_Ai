import threading
import time
from datetime import datetime

try:
    from opcua import Client
    from opcua import ua
except ImportError:
    print("OPC UA library not installed. Install with: pip install opcua")
    Client = None


class ABBOPCUAConnector:
    def __init__(self, message_callback):
        self.message_callback = message_callback
        self.client = None
        self.is_connected = False
        self.is_monitoring = False
        self.subscription = None
        self.handles = {}

        # ABB Robot OPC UA Node IDs (standard addresses)
        self.node_ids = {
            # Robot Status
            'robot_ready': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.RobotReady',
            'robot_busy': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.RobotBusy',
            'robot_error': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.RobotError',

            # Current Position
            'current_x': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.ActualPosX',
            'current_y': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.ActualPosY',
            'current_z': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.ActualPosZ',

            # Target Position
            'target_x': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.TargetPosX',
            'target_y': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.TargetPosY',
            'target_z': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.TargetPosZ',

            # Movement Status
            'movement_type': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.MovementType',
            'movement_speed': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.Speed',

            # Program Control
            'current_program': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.CurrentProgram',
            'program_running': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.ProgramRunning',

            # Digital Outputs (Gripper, Tools)
            'gripper_status': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.GripperOpen',
            'tool_status': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.ToolActive',

            # Safety
            'emergency_stop': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.EmergencyStop',
            'safety_gates': 'ns=4;s=|var|CPX-E-CEC-M1-APPL.Application.GVL_Station.SafetyGateClosed'
        }

        # Movement type mappings
        self.movement_types = {
            0: "Idle",
            1: "Joint Move",
            2: "Linear Move",
            3: "Circular Move",
            4: "Absolute Move"
        }

    def connect(self, endpoint_url="opc.tcp://desktop-j8ae1eh:61510/ABB.IoTGateway"):
        """Connect to ABB Robot OPC UA server"""
        if Client is None:
            self.message_callback("error", "OPC UA library not available. Install with: pip install opcua")
            return False

        try:
            self.client = Client(endpoint_url)
            self.client.set_user("operator")
            self.client.set_password("password")
            self.client.connect()

            # Get root node
            root = self.client.get_root_node()
            self.message_callback("system", f"Connected to OPC UA server: {endpoint_url}")

            self.is_connected = True
            return True

        except Exception as e:
            self.message_callback("error", f"OPC UA connection failed: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from OPC UA server"""
        if self.client:
            self.stop_monitoring()
            self.client.disconnect()
            self.is_connected = False
            self.message_callback("system", "Disconnected from OPC UA server")

    def start_monitoring(self):
        """Start monitoring robot data in real-time"""
        if not self.is_connected:
            self.message_callback("error", "Not connected to OPC UA server")
            return False

        try:
            # Create subscription
            self.subscription = self.client.create_subscription(500, self)  # 500ms update interval

            # Subscribe to important nodes
            nodes_to_monitor = [
                'robot_busy', 'robot_ready', 'robot_error',
                'movement_type', 'movement_speed',
                'program_running', 'current_program',
                'gripper_status', 'tool_status',
                'emergency_stop'
            ]

            for node_name in nodes_to_monitor:
                node_id = self.node_ids.get(node_name)
                if node_id:
                    try:
                        node = self.client.get_node(node_id)
                        handle = self.subscription.subscribe_data_change(node)
                        self.handles[handle] = node_name
                    except Exception as e:
                        self.message_callback("warning", f"Could not subscribe to {node_name}: {e}")

            self.is_monitoring = True
            self.message_callback("system", "Started real-time OPC UA monitoring")

            # Start position polling thread
            threading.Thread(target=self._poll_positions, daemon=True).start()

            return True

        except Exception as e:
            self.message_callback("error", f"Monitoring start failed: {e}")
            return False

    def stop_monitoring(self):
        """Stop monitoring robot data"""
        if self.subscription:
            self.subscription.delete()
            self.subscription = None
        self.is_monitoring = False
        self.message_callback("system", "Stopped OPC UA monitoring")

    def datachange_notification(self, node, val, data):
        """Callback for OPC UA data changes"""
        try:
            node_id = str(node.nodeid)
            node_name = self._get_node_name_from_id(node_id)

            if node_name:
                self._handle_data_change(node_name, val)

        except Exception as e:
            self.message_callback("error", f"Data change handling error: {e}")

    def _get_node_name_from_id(self, node_id):
        """Get node name from node ID"""
        for name, nid in self.node_ids.items():
            if nid in node_id:
                return name
        return None

    def _handle_data_change(self, node_name, value):
        """Handle specific data changes"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if node_name == 'robot_busy' and value:
            self.message_callback("status", {"type": "robot_busy", "value": True})

        elif node_name == 'robot_ready' and value:
            self.message_callback("status", {"type": "robot_ready", "value": True})

        elif node_name == 'robot_error' and value:
            self.message_callback("error", {"type": "robot_error", "value": True})

        elif node_name == 'movement_type':
            movement_name = self.movement_types.get(value, "Unknown")
            self.message_callback("movement", {"type": "movement_type", "value": value, "name": movement_name})

        elif node_name == 'program_running' and value:
            self.message_callback("program", {"type": "program_started", "value": True})

        elif node_name == 'gripper_status':
            action = "opened" if value else "closed"
            self.message_callback("tool", {"type": "gripper", "action": action, "value": value})

        elif node_name == 'emergency_stop' and value:
            self.message_callback("safety", {"type": "emergency_stop", "value": True})

    def _poll_positions(self):
        """Poll position data continuously"""
        last_position = None

        while self.is_monitoring and self.is_connected:
            try:
                current_pos = self._read_current_position()

                # Check if position changed significantly
                if last_position and self._position_changed(last_position, current_pos):
                    self.message_callback("position", current_pos)

                last_position = current_pos
                time.sleep(0.5)  # Poll every 500ms

            except Exception as e:
                self.message_callback("error", f"Position polling error: {e}")
                time.sleep(2)

    def _read_current_position(self):
        """Read current robot position"""
        try:
            x = self._read_node('current_x')
            y = self._read_node('current_y')
            z = self._read_node('current_z')

            return {
                'x': x or 0.0,
                'y': y or 0.0,
                'z': z or 0.0,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}

    def _read_node(self, node_name):
        """Read value from specific node"""
        try:
            node_id = self.node_ids.get(node_name)
            if node_id:
                node = self.client.get_node(node_id)
                return node.get_value()
        except:
            return None

    def _position_changed(self, pos1, pos2, threshold=1.0):
        """Check if position changed significantly"""
        dx = abs(pos1['x'] - pos2['x'])
        dy = abs(pos1['y'] - pos2['y'])
        dz = abs(pos1['z'] - pos2['z'])

        return dx > threshold or dy > threshold or dz > threshold

    def get_robot_status(self):
        """Get comprehensive robot status"""
        if not self.is_connected:
            return None

        try:
            status = {
                'connected': self.is_connected,
                'ready': self._read_node('robot_ready'),
                'busy': self._read_node('robot_busy'),
                'error': self._read_node('robot_error'),
                'program_running': self._read_node('program_running'),
                'current_program': self._read_node('current_program'),
                'emergency_stop': self._read_node('emergency_stop'),
                'position': self._read_current_position(),
                'timestamp': datetime.now().isoformat()
            }
            return status
        except Exception as e:
            self.message_callback("error", f"Status read error: {e}")
            return None