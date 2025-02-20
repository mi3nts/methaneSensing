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

            if parts[0] == "ATSK":
                if parts[1] == "1":
                    return "Error: Unable to retrieve task list"
                elif parts[1] == "0" and len(parts) > 2:
                    tasks = []
                    for i in range(2, len(parts), 2):
                        task_id = parts[i]
                        task_name = parts[i + 1].strip('"')
                        tasks.append(f"Task ID: {task_id}, Task Name: {task_name}")
                    return "\n".join(tasks)
            elif parts[0] == "ASTS":
                error_status = parts[1]
                device_status_code = parts[2] if len(parts) > 2 else "Unknown"
                device_status = self.status_map.get(device_status_code, "Unknown status")
                return f"Error Status: {error_status}, Device Status: {device_status}"
            elif parts[0] == "AERR":
                if parts[1] == "0":
                    errors = parts[2:] if len(parts) > 2 else ["No active errors"]
                    return f"Active Errors: {', '.join(errors)}"
                elif parts[1] == "1":
                    return "Request error when fetching active errors"
            elif parts[0] == "STAM":
                return f"Start Measurement Response: {parts[1]} (0=no errors, 1=error)"
            elif parts[0] == "STPM":
                return f"Stop Measurement Response: {parts[1]} (0=no errors, 1=error)"
            elif parts[0] == "ACON":
                if parts[1] == "1":
                    return "Error retrieving last measurement results"
                else:
                    measurements = []
                    for i in range(2, len(parts), 3):
                        timestamp = parts[i]
                        cas = parts[i + 1]
                        conc_ppm = parts[i + 2]
                        measurements.append(f"Timestamp: {timestamp}, CAS: {cas}, Concentration: {conc_ppm} ppm")
                    return "\n".join(measurements)

            elif parts[0] == "AMST":
                error_status = parts[1]
                measurement_status_code = parts[2] if len(parts) > 2 else "Unknown"
                measurement_status = self.measurement_status_map.get(measurement_status_code, "Unknown measurement status")
                return f"Error Status: {error_status}, Measurement Status: {measurement_status}"
        
            
            elif parts[0] == "ANAM":
                error_status = parts[1]
                device_name = parts[2] if len(parts) > 2 else ""
                return f"Error Status: {error_status}, Device Name: {device_name}"
        

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

    def request_device_status(self):
        """Request device status and parse the response."""
        request_status = self.format_ak_request("ASTS")
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        return self.parse_ak_response(response_status)

    def request_active_errors(self):
        """Request active errors and parse the response."""
        request_errors = self.format_ak_request("AERR")
        self.socket.sendall(request_errors)
        response_errors = self.socket.recv(1024)
        return self.parse_ak_response(response_errors)

    def request_task_list(self):
        """Request task list and parse the response."""
        request_tasks = self.format_ak_request("ATSK")
        self.socket.sendall(request_tasks)
        response_tasks = self.socket.recv(1024)
        return self.parse_ak_response(response_tasks)
        
    def request_start_measurement(self, task_id: str):
        """Request to start a new measurement based on the specified task ID."""
        request_start = self.format_ak_request("STAM", data=task_id)
        self.socket.sendall(request_start)
        response_start = self.socket.recv(1024)
        return self.parse_ak_response(response_start)

    def request_stop_measurement(self):
        """Request to stop the current measurement and parse the response."""
        request_stop = self.format_ak_request("STPM")
        self.socket.sendall(request_stop)
        response_stop = self.socket.recv(1024)
        return self.parse_ak_response(response_stop)

    def request_last_measurement_results(self):
        """Request to retrieve the last measurement results (concentrations) and parse the response."""
        request_results = self.format_ak_request("ACON")
        self.socket.sendall(request_results)
        response_results = self.socket.recv(1024)
        return self.parse_ak_response(response_results)

    def request_measurement_status(self):
        """Request measurement status (AMST) and parse the response."""
        request_status = self.format_ak_request("AMST")
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        return self.parse_ak_response(response_status)

    def request_device_name(self):
        """Request device name and parse the response."""
        request_name = self.format_ak_request("ANAM")
        self.socket.sendall(request_name)
        response_name = self.socket.recv(1024)
        return self.parse_ak_response(response_name)

    def get_device_status(self):
        """Retrieves the device status."""
        return self.request_device_status()

    def get_active_errors(self):
        """Retrieves the active errors."""
        return self.request_active_errors()

    def get_task_list(self):
        """Retrieves the task list."""
        return self.request_task_list()

    def stop_measurement(self):
        """Stops the current measurement."""
        return self.request_stop_measurement()

    def get_last_measurement_results(self):
        """Retrieves the last measurement results (concentrations)."""
        return self.request_last_measurement_results()


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
    print(f"Device Name: {sensor.request_device_name()}")    
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

