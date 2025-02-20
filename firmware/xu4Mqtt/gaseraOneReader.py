import socket
from datetime import datetime
import time 
import re

class GaseraOneSensor:
    def __init__(self, host: str, port: int = 8888):
        self.host = host
        self.port = port
        self.status_map = {
            "0": "Device initializing",
            "1": "Initialization error",
            "2": "Device idle state",
            "3": "Device self-test in progress",
            "4": "Malfunction",
            "5": "Measurement in progress",
            "6": "Calibration in progress",
            "7": "Canceling measurement",
            "8": "Laserscan in progress"
        }
        self.measurement_status_map = {
            "0": "None (device is idle)",
            "1": "Gas exchange in progress",
            "2": "Sample integration (measurement) in progress",
            "3": "Sample analysis in progress",
            "4": "Laser tuning in progress"
        }
    
    def format_ak_request(self, command: str, channel: str = "0", data: str = "") -> bytes:
        """Formats an AK request according to the specified protocol."""
        stx = b'\x02'
        etx = b'\x03'
        blank = b' '
        formatted_command = f"{command} K{channel} {data}".encode()
        return stx + blank + formatted_command + etx
    
    def parse_ak_response(self, response: bytes) -> str:
        """Parses the AK response and extracts relevant information."""
        if response.startswith(b'\x02') and response.endswith(b'\x03'):
            response_str = response[1:-1].decode()
            parts = re.findall(r'([^\s"]+|\"[^\"]*\")', response_str)

            if parts[0] == "AMST":
                error_status = parts[1]
                measurement_status_code = parts[2] if len(parts) > 2 else "Unknown"
                measurement_status = self.measurement_status_map.get(measurement_status_code, "Unknown measurement status")
                return f"Error Status: {error_status}, Measurement Status: {measurement_status}"
        
        return "Invalid response format"
    
    def connect(self):
        """Connects to the GASERA ONE sensor over TCP/IP."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to GASERA ONE at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error: {e}")
            return None

    def disconnect(self):
        """Disconnects the connection to the sensor."""
        if hasattr(self, 'socket'):
            self.socket.close()
            print("Disconnected from GASERA ONE")
    
    def request_measurement_status(self):
        """Request measurement status (AMST) and parse the response."""
        request_status = self.format_ak_request("AMST")
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        return self.parse_ak_response(response_status)
    
    def get_measurement_status(self):
        """Retrieves the measurement status."""
        return self.request_measurement_status()



if __name__ == "__main__":
    # Create an instance of the sensor
    sensor = GaseraOneSensor("192.168.20.112")
    
    # Connect to the sensor
    sensor.connect()
    
    # Get the device status, active errors, task list, last measurement results, and stop measurement
    print(f"Device Status: {sensor.get_device_status()}")
    print(f"Active Errors: {sensor.get_active_errors()}")
    print(f"Task List:\n{sensor.get_task_list()}")
    print(f"Measurement Status: {sensor.get_measurement_status()}")
    # time.sleep(60)
    # print(f"Stop Measurement: {sensor.stop_measurement()}")
    # time.sleep(60)
    # task_id = "11"  # Example task ID
    # print(f"Start Measurement Response: {sensor.request_start_measurement(task_id)}")
    # time.sleep(60)
    
    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(60)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(60)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(60)

    
    time.sleep(1)
    # print(f"Stop Measurement: {sensor.stop_measurement()}")
    
    # Disconnect when done
    sensor.disconnect()

