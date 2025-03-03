import socket
from datetime import datetime, timezone
import time 
import re
from collections import OrderedDict
import pprint

from mintsXU4 import mintsSensorReader as mSR

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
    
        self.cas_to_gas = {
            "74-82-8"   : "methane",
            "124-38-9"  : "carbonDioxide",
            "10024-97-2": "nitrousOxide",
            "7782-44-7" : "oxygen",
            "7783-06-4" : "hydrogenSulfide",
            "7664-41-7" : "ammonia",
            "1333-74-0" : "hydrogen",
            "10102-43-9": "nitrogenDioxide",
            "7440-37-1" : "argon",
            "7782-50-5" : "chlorine",
            "630-08-0"  : "carbonMonoxide",
            "2551-62-4" : "sulfurHexafluoride"
        }

    def connect(self, timeout=5):
        """Connects to the GASERA ONE sensor over TCP/IP with a timeout."""
        dateTime  = datetime.now()
        try:
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)  # Set timeout for the connection
            self.socket.connect((self.host, self.port))
            print(f"Connected to GASERA ONE at {self.host}:{self.port}")
            # Publish 
           
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime)),
                 ("hostIP"               ,str(self.host)),
                 ("ConnectionStatus"     ,0)
        	     ])
            mSR.sensorFinisher(dateTime,"GSR001CS",sensorDictionary)
            return True

        except socket.timeout:
            print(f"Connection timed out after {timeout} seconds.")
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime)),
                 ("hostIP"               ,str(self.host)),
                 ("ConnectionStatus"     ,1)
        	     ])            
            mSR.sensorFinisher(dateTime,"GSR001CS",sensorDictionary)
            return False
        
        except Exception as e:
            print(f"Error: {e}")
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime)),
                 ("hostIP"               ,str(self.host)),
                 ("ConnectionStatus"     ,2)
        	     ])            
            mSR.sensorFinisher(dateTime,"GSR001CS",sensorDictionary)
            return False            

    def format_ak_request(self, command: str, channel: str = "0", data: str = "") -> bytes:
        """Formats an AK request according to the specified protocol."""
        stx = b'\x02'
        etx = b'\x03'
        blank = b' '
        formatted_command = f"{command} K{channel} {data}".encode()
        return stx + blank + formatted_command + etx
    
    def clean_ak_response(self, response: bytes) -> str:
        """Parses the AK response and extracts relevant information."""
        if response.startswith(b'\x02') and response.endswith(b'\x03'):
            # print(response)
            response_str = response[1:-1].decode()
            parts = re.findall(r'([^\s"]+|\"[^\"]*\")', response_str)
            return True, parts;
        else: 
            return False, None;

    #  
    def request_gasera_status(self):
        """Request device status and parse the response."""
        command  = "ASTS"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.device_status_code = parts[2] if len(parts) > 2 else "-1"
                device_status = self.status_map.get(self.device_status_code, "Unknown status")

                sensorDictionary = OrderedDict([
                    ("dateTime"       ,str(dateTime)),
                    ("errorStatus"    ,int(error_status)),
                    ("deviceStatus"   ,int(self.device_status_code))
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001ASTS",sensorDictionary)
                # print(sensorDictionary)
                return True, f"Error Status: {error_status}, Device Status: {device_status}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def request_gasera_active_errors(self):
        """Request device status and parse the response."""
        command  = "AERR"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.errors  = parts[2:]
                errors0 = parts[2] if len(parts) > 2 else "0"
                errors1 = parts[3] if len(parts) > 3 else "0"
                errors2 = parts[4] if len(parts) > 4 else "0"
                errors3 = parts[5] if len(parts) > 5 else "0"
                errors4 = parts[6] if len(parts) > 6 else "0"

                sensorDictionary = OrderedDict([
                    ("dateTime"            ,str(dateTime)),
                    ("errorStatus"         ,int(error_status)),
                    ("activeError0"        ,int(errors0)),
                    ("activeError1"        ,int(errors1)),
                    ("activeError2"        ,int(errors2)),
                    ("activeError3"        ,int(errors3)),
                    ("activeError4"        ,int(errors4)),                                                            
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return True, f"Active Errors: {', '.join(parts[2:])}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def request_gasera_task_list(self):
        """Request device status and parse the response."""
        command  = "ATSK"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.errors = parts[2:] if len(parts) > 2 else []

                self.tasks = []
                self.task_ids   = []
                self.task_names = []
                
                for i in range(2, len(parts), 2):
                    task_id = parts[i]
                    task_name = parts[i + 1].strip('"')
                    self.task_ids.append(task_id)
                    self.task_names.append(task_name)
                    self.tasks.append(f"Task ID: {task_id}, Task Name: {task_name}")

                taskID0 = self.task_ids[0] if len(self.task_ids) > 0 else -1
                taskID1 = self.task_ids[1] if len(self.task_ids) > 1 else -1
                taskID2 = self.task_ids[2] if len(self.task_ids) > 2 else -1
                taskID3 = self.task_ids[3] if len(self.task_ids) > 3 else -1
                taskID4 = self.task_ids[4] if len(self.task_ids) > 4 else -1

                taskName0 = self.task_names[0] if len(self.task_names) > 0 else "NT"
                taskName1 = self.task_names[1] if len(self.task_names) > 1 else "NT"
                taskName2 = self.task_names[2] if len(self.task_names) > 2 else "NT"
                taskName3 = self.task_names[3] if len(self.task_names) > 3 else "NT"
                taskName4 = self.task_names[4] if len(self.task_names) > 4 else "NT"

                sensorDictionary = OrderedDict([
                    ("dateTime"            ,str(dateTime)),
                    ("errorStatus"         ,int(error_status)),
                    ("taskID0"             ,taskID0),       
                    ("taskName0"           ,taskName0),          
                    ("taskID0"             ,taskID0),       
                    ("taskName0"           ,taskName0),          
                    ("taskID1"             ,taskID1),       
                    ("taskName1"           ,taskName1),          
                    ("taskID2"             ,taskID2),       
                    ("taskName2"           ,taskName2),          
                    ("taskID3"             ,taskID3),       
                    ("taskName3"           ,taskName3),          
                    ("taskID4"             ,taskID4),       
                    ("taskName4"           ,taskName4),                                                                                                                         
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return True, "\n".join(self.tasks).replace('\n'," || ")
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_measurement_status(self):
        """Request measurement status (AMST) and parse the response."""
        command  = "AMST"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.measurement_status_code = parts[2] if len(parts) > 2 else "-1"
                self.measurement_status = \
                    self.measurement_status_map.get(\
                    self.measurement_status_code,\
                    "Unknown measurement status")
                
                sensorDictionary = OrderedDict([
                    ("dateTime"               ,str(dateTime)),
                    ("errorStatus"            ,int(error_status)),
                    ("measurementStatusCode"  ,int(self.measurement_status_code))
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                
                return True, f"Error Status: {error_status}, Measurement Status: {self.measurement_status}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_name(self):
        """Request device name and parse the response."""
        command  = "ANAM"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.device_name = parts[2] if len(parts) > 2 else ""
                sensorDictionary = OrderedDict([
                    ("dateTime"    ,str(dateTime)),
                    ("errorStatus" ,int(error_status)),
                    ("gaseraName"  ,self.device_name)
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Device Name: {self.device_name}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_iteration_number(self):
        """Request current measurement iteration number and parse the response."""
        command  = "AITR"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.iteration_number = parts[2] if len(parts) > 2 else "-1"
                sensorDictionary = OrderedDict([
                    ("dateTime"        ,str(dateTime)),
                    ("errorStatus"     ,int(error_status)),
                    ("iterationNumber" ,int(self.iteration_number))
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Iteration Number: {self.iteration_number}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_network_settings(self):
        """Request current network settings and parse the response."""
        command  = "ANET"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.use_dhcp = parts[2]
                self.ip_address = parts[3]
                self.netmask = parts[4]
                self.gateway = parts[5]
                sensorDictionary = OrderedDict([
                    ("dateTime"        ,str(dateTime)),
                    ("errorStatus"     ,int(error_status)),                    
                    ("useDHCP"         ,self.use_dhcp),
                    ("ip"              ,str(self.ip_address)),
                    ("netmask"         ,str(self.netmask)),
                    ("gateway"         ,str(self.gateway)),
                    ])            

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}," + ",".join(
                        f"{label}: {value}" for label, value in {
                            "Use DHCP": self.use_dhcp,
                            "IP Address": self.ip_address,
                            "Netmask": self.netmask,
                            "Gateway": self.gateway
                        }.items()
                    )
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_datetime(self):
        """Request current device date and time."""
        command  = "ACLK"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.gasera_datetime = parts[2] if len(parts) > 2 else "Unknown"
                sensorDictionary = OrderedDict([
                    ("dateTime"        ,str(dateTime)),
                    ("errorStatus"     ,int(error_status)),                    
                    ("gaseraDateTime"  ,str(self.gasera_datetime)),
                    ])             
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Date/Time: {self.gasera_datetime}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def request_gasera_multi_point_sampler_parameters(self):
        """Request multi-point sampler parameters."""
        command  = "AMPS"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.parameters = parts[2:]
                parameters0 = parts[2] if len(parts) > 2 else "NP"
                parameters1 = parts[3] if len(parts) > 3 else "NP"
                parameters2 = parts[4] if len(parts) > 4 else "NP"
                parameters3 = parts[5] if len(parts) > 5 else "NP"
                parameters4 = parts[6] if len(parts) > 6 else "NP"

                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),
                    ("parameter0"        ,parameters0),
                    ("parameter1"        ,parameters1),
                    ("parameter2"        ,parameters2),
                    ("parameter3"        ,parameters3),
                    ("parameter4"        ,parameters4),                                                            
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Error Status: {error_status}, parameters: {self.parameters}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def request_gasera_system_parameters(self):
        """Request system parameters."""
        command  = "ASYP"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        time.sleep(.1)
        response_status = self.socket.recv(4096)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                parameters = [param for param in parts[2:] if param != b'NULL'] if len(parts) > 2 else []
                self.system_parameters = [','.join([item for item in string.split(',') if item != 'NULL']) for string in parameters]
       
                # Create an OrderedDict and add dateTime first
                sensorDictionary = OrderedDict()

                # Insert the current datetime as the first key
                sensorDictionary["dateTime"]  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sensorDictionary["errorStatus"] =  int(error_status)
                # Convert list items into key-value pairs
                for item in self.system_parameters:
                    key, value = item.split(",")
                    try:
                        value = int(value)
                    except ValueError:
                        value = float(value)
                    sensorDictionary[str(key)] = value
 
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Error Status: {error_status}, System Parameters: {self.system_parameters}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"



    def request_gasera_task_parameters(self,task_id):
        """Request measurement task parameters."""
        command  = "ATSP"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command, data=task_id)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.task_parameters = parts[2:] if len(parts) > 2 else []

                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),
                    ("taskID"            ,task_id),
                    ("casNumbers"        ,str(self.task_parameters[0]).replace(",","_")),
                    ("targetPressure"    ,int(self.task_parameters[1])),
                    ("flushTimeBypass"   ,int(self.task_parameters[2])),
                    ("flushTimeCell"     ,int(self.task_parameters[3])),
                    ("cellFlushCycles"   ,int(self.task_parameters[4])),                                                            
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Error Status: {error_status}, Parameters: {self.task_parameters}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_device_info(self):
        """Request device information and parse the response."""
        command  = "ADEV"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                self.manufacturer     = parts[2].strip('"')
                self.serial_number    = parts[3].strip('"')
                self.device_name      = parts[4].strip('"') 
                self.firmware_version = parts[5].strip('"') 

                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),
                    ("manufacturer"      ,self.manufacturer),
                    ("serialNumber"      ,int(self.serial_number)),
                    ("deviceName"        ,self.device_name),
                    ("firmwareVersion"   ,int(self.firmware_version)),                                                          
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                
                return f"Error Status: {error_status}, Manufacturer: {self.manufacturer}, Serial Number: {self.serial_number}, Device Name: {self.device_name}, Firmware Version: {self.firmware_version}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    # """Request to start the device self-test routine."""
    # request_test = self.format_ak_request("STST")
    def start_gasera_self_test(self):
        """Request device information and parse the response."""
        command  = "STST"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),                                                        
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                
                return f"Error Status: {error_status}, Self-Test Request Start Status: {'Success' if error_status == '0' else 'Error'}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_self_test_result(self):
        """Request device information and parse the response."""
        command  = "ASTR"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                self.self_test_result = parts[2]
                
                # Interpret the self-test state/result
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),      
                    ("selfTestResult"    ,int(self.self_test_result)),                                                                            
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                if error_status == "0":
                    if self.self_test_result == "-2":
                        return False,"Self-test result: N/A (test not started)"
                    elif self.self_test_result == "-1":
                        return False,"Self-test in progress"
                    elif self.self_test_result == "0":
                        return False,"Self-test failed"
                    elif self.self_test_result == "1":
                        return True,"Self-test completed successfully"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def stop_gasera_measurement(self):
        """Request to stop the current measurement and parse the response."""
        command  = "STPM"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                
                # Interpret the self-test state/result
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),                                                                          
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Stop Measurement Response: {parts[1]} (0=no errors, 1=error)"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def start_gasera_measurement(self,task_id: str):
        """Request to start a new measurement based on the specified task ID."""
        command  = "STAM"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command, data=task_id)

        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                
                # Interpret the self-test state/result
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime)),
                    ("errorStatus"       ,int(error_status)),                                                                          
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Start Measurement Response: {parts[1]} (0=no errors, 1=error)"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_gasera_last_measurement_results(self):
        """Request to retrieve the last measurement results (concentrations) and parse the response."""

        command  = "ACON"
        dateTime = datetime.now()
        request_status = self.format_ak_request(command)

        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            print(len(parts))
            print(parts)
            if parts[0] == command and len(parts) == 17:
                error_status          = parts[1]
                timestamp             = parts[2]

                # Create an OrderedDict and add dateTime first
                sensorDictionary = OrderedDict()

                # Insert the current datetime as the first key
                sensorDictionary["dateTime"]    = str(datetime.fromtimestamp(int(timestamp), tz=timezone.utc))
                sensorDictionary["errorStatus"] = int(error_status)

                self.measurements = []
                for i in range(2, len(parts), 3):
                    timestamp = parts[i]
                    cas       = parts[i + 1]
                    casGas    = self.cas_to_gas.get(parts[i + 1], "unknownCASNumber")
                    conc_ppm  = parts[i + 2]
                    self.measurements.append(f"Timestamp: {timestamp}, CAS: {cas}, gas: {casGas}, Concentration: {conc_ppm} ppm")
                    sensorDictionary[casGas] =  float(conc_ppm)

                print(sensorDictionary)
                # mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return "\n".join(self.measurements)
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def disconnect(self):
        """Disconnects the connection to the sensor."""
        if hasattr(self, 'socket'):
            self.socket.close()
            print("Disconnected from GASERA ONE")


if __name__ == "__main__":
    print("==========================================")
    print("================== MINTS =================")
    print("------------------------------------------")
    # Create an instance of the sensor
    sensor = GaseraOneSensor("192.168.20.112")
    
    # Connect to the sensor
    sensor.connect()
    # Connected to GASERA ONE at 192.168.20.112:8888

    time.sleep(20)
    print(f"Stop Measurement: {sensor.stop_measurement()}")
    time.sleep(5)
    print(sensor.stop_gasera_measurement())

    # Get the device status, active errors, task list, last measurement results, and stop measurement
    # Device Status: Error Status: 0, Device Status: Device idle state
    print(f"Device Status: {sensor.get_device_status()}")
    print(sensor.request_gasera_status())


    print(f"Active Errors: {sensor.get_active_errors()}")
    print(sensor.request_gasera_active_errors())
    # Active Errors: Active Errors: 8002, 8004

    # MAKE SURE TO MAKE STRING
    print(f"Task List:\n{sensor.get_task_list()}")
    print(sensor.request_gasera_task_list())
    # Task List:
    # Task ID: 7,  Task Name: Calibration task
    # Task ID: 11, Task Name: DEFAULT
    # Task ID: 12, Task Name: FLUSH

    print(f"Measurement Status: {sensor.get_measurement_status()}")
    print(sensor.request_gasera_measurement_status())
    # Measurement Status: Error Status: 0, Measurement Status: None (device is idle)
    

    # MAKE SURE TO MAKE STRING
    print(f"Device Name: {sensor.request_device_name()}")    
    print(sensor.request_gasera_name())
    # Device Name: Error Status: 0, Device Name: mints-gasera-one

    print(f"Iteration Number: {sensor.request_iteration_number()}")
    print(sensor.request_gasera_iteration_number())
    # Iteration Number: Error Status: 0, Iteration Number: 0
  
    # MAKE SURE TO MAKE STRING
    print(f"Network Settings: {sensor.request_network_settings()}")
    print(sensor.request_gasera_network_settings())
    # Network Settings: Error Status: 0, Use DHCP: 1, IP Address: 192.168.20.112, Netmask: 255.255.255.0, Gateway: 192.168.20.1

    # MAKE SURE TO MAKE STRING
    print(f"Device Date/Time: {sensor.request_device_datetime()}")
    print(sensor.request_gasera_datetime())
    # Device Date/Time: Error Status: 0, Date/Time: 2025-02-26T17:02:51

    print(f"Multi-Point Sampler Parameters: {sensor.request_multi_point_sampler()}")
    print(sensor.request_gasera_multi_point_sampler_parameters())
    # Multi-Point Sampler Parameters: Error Status: 2, Multi-Point Sampler Parameters: []
   
    print(f"System Parameters: {sensor.request_system_parameters()}")
    print(sensor.request_gasera_system_parameters())
    # System Parameters: Error Status: 0, System Parameters: ['TargetPressure,850', 'FlushTimeBypass,1', 'NFlushBypass,1', 'FlushTimeCell,1', 'NFlushCell,6', 'GasInput,0', 'ContinuousPumping,0', 'GasExForEachChannel,0', 'CalibIterations,10', 'DeviceType,3', 'LoggingEnabled,1', 'ChannelGroupWaveNStepSize,0', 'SamplingMode,0', 'PumpRate,6.5', 'MovingAvgInterval,0', 'PPMRangeMin0,0', 'PPMRangeMax0,0', 'PPMRangeMin1,0', 'PPMRangeMax1,0', 'CompensationCompId,3', 'LaserTuneStartOffset1,0', 'LaserTuneStartOffset2,0', 'NumberOfLasers,1', 'AllowNegResults,0', 'ModbusSlaveId,0', 'DisableScanTuning,0', 'RemoteMaintenance,0', 'RemoteMaintenanceVisible,0', 'UsageTimeMeasure,8260', 'UsageTimeIdle,11190', 'STDVComponentIdCh0,0', 'STDVComponentIdCh1,0', 'PPMRangeMin2,0', 'PPMRangeMax2,0', 'STDVComponentIdCh2,0', 'PPMRangeMin3,0', 'PPMRangeMax3,0', 'STDVComponentIdCh3,0', 'PPMRangeMin4,0', 'PPMRangeMax4,0', 'STDVComponentIdCh4,0', 'PPMRangeMin5,0', 'PPMRangeMax5,0', 'STDVComponentIdCh5,0', 'PPMRangeMin6,0', 'PPMRangeMax6,0', 'STDVComponentIdCh6,0', 'PPMRangeMin7,0', 'PPMRangeMax7,0', 'STDVComponentIdCh7,0', 'PPMRangeMin8,0', 'PPMRangeMax8,0', 'STDVComponentIdCh8,0', 'PPMRangeMin9,0', 'PPMRangeMax9,0', 'STDVComponentIdCh9,0', 'PPMRangeMin10,0', 'PPMRangeMax10,0', 'STDVComponentIdCh10,0', 'PPMRangeMin11,0', 'PPMRangeMax11,0', 'STDVComponentIdCh11,0', 'PPMRangeMin12,0', 'PPMRangeMax12,0', 'STDVComponentIdCh12,0', 'STDVMPSInletCh0,0', 'STDVMPSInletCh1,0', 'STDVMPSInletCh2,0', 'STDVMPSInletCh3,0', 'STDVMPSInletCh4,0', 'STDVMPSInletCh5,0', 'STDVMPSInletCh6,0', 'STDVMPSInletCh7,0', 'STDVMPSInletCh8,0', 'STDVMPSInletCh9,0', 'STDVMPSInletCh10,0', 'STDVMPSInletCh11,0', 'STDVMPSInletCh12,0', 'BGCompensationInterval,1', 'InternalTimeout,0', 'ExternalTimeout,0', 'IntervalEnabled,0', 'y-AxisMin,0', 'y-AxisMax,0.1', 'y-AxisAutoscaleOn,1']


    # MAKE SURE TO MAKE STRING
    print(f"Measurement Task Parameters: {sensor.request_task_parameters('11')}")
    print(sensor.request_gasera_task_parameters('11'))
    # Measurement Task Parameters: Error Status: 0, Parameters: ['74-82-8,124-38-9,7732-18-5,630-08-0,10024-97-2', '850', '1', '1', '6']
    
    # MAKE SURE TO MAKE STRING
    print(f"Device Info: {sensor.request_device_info()}")
    print(sensor.request_gasera_device_info())
    # Device Info: Error Status: 0, Manufacturer: "Gasera Ltd", Serial Number: "030109", Device Name: "MINTS-GASERA-ONE", Firmware Version: "010304"
    
    # Cant do two togeather
    # print(f"Self-Test Status: {sensor.start_self_test()}")
    print(sensor.start_gasera_self_test())
    # Self-Test Status: Error Status: 0, Self-Test Request Status: Success

    time.sleep(120)

    print(f"Device Self-Test Result: {sensor.get_device_self_test_result()}")
    print(sensor.request_gasera_self_test_result())
    # Device Self-Test Result: Self-test completed successfully
    
    print(f"Stop Measurement: {sensor.stop_measurement()}")
    time.sleep(5)
    print(sensor.stop_gasera_measurement())
    # Stop Measurement: Stop Measurement Response: 0 (0=no errors, 1=error)
    
    time.sleep(60)

    task_id = "11"  # The Default Task ID
    # print(f"Start Measurement Response: {sensor.request_start_measurement(task_id)}")
    print(sensor.start_gasera_measurement(task_id))

    time.sleep(120)

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    
    time.sleep(10)

    print(sensor.request_gasera_last_measurement_results())

    time.sleep(10)

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)    

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)   
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)    

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)

    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)
    
    print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    time.sleep(10)    



    # Start Measurement Response: Start Measurement Response: 0 (0=no errors, 1=error)
    
    # Last Measurement Results:
    # Timestamp: 1740589731, CAS: 74-82-8, Concentration: 0.919465 ppm
    # Timestamp: 1740589731, CAS: 124-38-9, Concentration: 536.757 ppm
    # Timestamp: 1740589731, CAS: 7732-18-5, Concentration: 14351.4 ppm
    # Timestamp: 1740589731, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589731, CAS: 10024-97-2, Concentration: 0.382638 ppm
    # Last Measurement Results:
    # Timestamp: 1740589731, CAS: 74-82-8, Concentration: 0.919465 ppm
    # Timestamp: 1740589731, CAS: 124-38-9, Concentration: 536.757 ppm
    # Timestamp: 1740589731, CAS: 7732-18-5, Concentration: 14351.4 ppm
    # Timestamp: 1740589731, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589731, CAS: 10024-97-2, Concentration: 0.382638 ppm
    # Last Measurement Results:
    # Timestamp: 1740589812, CAS: 74-82-8, Concentration: 0.840892 ppm
    # Timestamp: 1740589812, CAS: 124-38-9, Concentration: 538.124 ppm
    # Timestamp: 1740589812, CAS: 7732-18-5, Concentration: 14258.2 ppm
    # Timestamp: 1740589812, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589812, CAS: 10024-97-2, Concentration: 0.356376 ppm
    # Last Measurement Results:
    # Timestamp: 1740589812, CAS: 74-82-8, Concentration: 0.840892 ppm
    # Timestamp: 1740589812, CAS: 124-38-9, Concentration: 538.124 ppm
    # Timestamp: 1740589812, CAS: 7732-18-5, Concentration: 14258.2 ppm
    # Timestamp: 1740589812, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589812, CAS: 10024-97-2, Concentration: 0.356376 ppm
    # Last Measurement Results:
    # Timestamp: 1740589812, CAS: 74-82-8, Concentration: 0.840892 ppm
    # Timestamp: 1740589812, CAS: 124-38-9, Concentration: 538.124 ppm
    # Timestamp: 1740589812, CAS: 7732-18-5, Concentration: 14258.2 ppm
    # Timestamp: 1740589812, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589812, CAS: 10024-97-2, Concentration: 0.356376 ppm
    # Last Measurement Results:
    # Timestamp: 1740589894, CAS: 74-82-8, Concentration: 0.97967 ppm
    # Timestamp: 1740589894, CAS: 124-38-9, Concentration: 539.85 ppm
    # Timestamp: 1740589894, CAS: 7732-18-5, Concentration: 14186.4 ppm
    # Timestamp: 1740589894, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589894, CAS: 10024-97-2, Concentration: 0.348337 ppm
    # Last Measurement Results:
    # Timestamp: 1740589894, CAS: 74-82-8, Concentration: 0.97967 ppm
    # Timestamp: 1740589894, CAS: 124-38-9, Concentration: 539.85 ppm
    # Timestamp: 1740589894, CAS: 7732-18-5, Concentration: 14186.4 ppm
    # Timestamp: 1740589894, CAS: 630-08-0, Concentration: 0 ppm
    # Timestamp: 1740589894, CAS: 10024-97-2, Concentration: 0.348337 ppm
    # Stop Measurement: Stop Measurement Response: 0 (0=no errors, 1=error)
    # Disconnected from GASERA ON

    # print(f"Device Self-Test Result: {sensor.get_device_self_test_result()}")
    # time.sleep(120)
    # print(f"Stop Measurement: {sensor.stop_measurement()}")
    # time.sleep(120)

    # time.sleep(120)
    
    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)
    
    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(30)

    # print(f"Last Measurement Results:\n{sensor.get_last_measurement_results()}")
    # time.sleep(1)

    time.sleep(5)
    print(sensor.stop_gasera_measurement())
    
    # Disconnect when done
    sensor.disconnect()

    print("==========================================")
    print("=============== MINTS DONE ===============")
    print("------------------------------------------")