import socket
from datetime import datetime, timezone
import time 
import re
from collections import OrderedDict
import pprint

from mintsXU4 import mintsSensorReader as mSR




defaultTaskID = "11"

class GaseraOneSensor:
    def __init__(self, host: str, defaultTaskID, port: int = 8888):
        self.host = host
        self.defualtTaskID = defaultTaskID
        self.startUpTime       = time.time()
        self.periodicCheckTime = time.time()    
        self.dailyCheckTime    = time.time()  
        self.port = port
        self.prevTimeStamp = datetime.now(timezone.utc)
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
            "2551-62-4" : "sulfurHexafluoride",
            "7732-18-5" : "water",
        }

    def connect(self, timeout=5):
        """Connects to the GASERA ONE sensor over TCP/IP with a timeout."""
        dateTime  = datetime.now(timezone.utc)

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)  # Set timeout for the connection
            self.socket.connect((self.host, self.port))
            print()
            print(f"Connected to GASERA ONE at {self.host}:{self.port}")
            print()
           
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                 ("hostIP"               ,str(self.host)),
                 ("ConnectionStatus"     ,0)
        	     ])
            mSR.sensorFinisher(dateTime,"GSR001CS",sensorDictionary)
            return True

        except socket.timeout:
            print(f"Connection timed out after {timeout} seconds.")
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                 ("hostIP"               ,str(self.host)),
                 ("ConnectionStatus"     ,1)
        	     ])            
            mSR.sensorFinisher(dateTime,"GSR001CS",sensorDictionary)
            return False
        
        except Exception as e:
            print(f"Error: {e}")
            sensorDictionary = OrderedDict([
                 ("dateTime"             ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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
    def request_status(self):
        """Request device status and parse the response."""
        command  = "ASTS"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)

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
                    ("dateTime"       ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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


    def request_active_errors(self):
        """Request device status and parse the response."""
        command  = "AERR"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)

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
                    ("dateTime"            ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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


    def request_task_list(self):
        """Request device status and parse the response."""
        command  = "ATSK"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"            ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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

    def request_measurement_status(self):
        """Request measurement status (AMST) and parse the response."""
        command  = "AMST"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"               ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"            ,int(error_status)),
                    ("measurementStatusCode"  ,int(self.measurement_status_code))
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                
                return True, f"Error Status: {error_status}, Measurement Status: {self.measurement_status}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_name(self):
        """Request device name and parse the response."""
        command  = "ANAM"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.device_name = parts[2] if len(parts) > 2 else ""
                sensorDictionary = OrderedDict([
                    ("dateTime"    ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus" ,int(error_status)),
                    ("gaseraName"  ,self.device_name)
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Device Name: {self.device_name}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_iteration_number(self):
        """Request current measurement iteration number and parse the response."""
        command  = "AITR"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.iteration_number = parts[2] if len(parts) > 2 else "-1"
                sensorDictionary = OrderedDict([
                    ("dateTime"        ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"     ,int(error_status)),
                    ("iterationNumber" ,int(self.iteration_number))
                    ])            
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Iteration Number: {self.iteration_number}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_network_settings(self):
        """Request current network settings and parse the response."""
        command  = "ANET"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"        ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"     ,int(error_status)),                    
                    ("useDHCP"         ,int(self.use_dhcp)),
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

    def request_datetime(self):
        """Request current device date and time."""
        command  = "ACLK"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.datetime = parts[2] if len(parts) > 2 else "Unknown"
                sensorDictionary = OrderedDict([
                    ("dateTime"        ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"     ,int(error_status)),                    
                    ("gaseraDateTime"  ,str(self.datetime)),
                    ])             
                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                return f"Error Status: {error_status}, Date/Time: {self.datetime}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"


    def request_multi_point_sampler_parameters(self):
        """Request multi-point sampler parameters."""
        command  = "AMPS"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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


    def request_system_parameters(self):
        """Request system parameters."""
        command  = "ASYP"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                sensorDictionary["dateTime"]  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
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



    def request_task_parameters(self):
        """Request measurement task parameters."""
        command  = "ATSP"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command, data=self.defualtTaskID)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status = parts[1]
                self.task_parameters = parts[2:] if len(parts) > 2 else []

                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"       ,int(error_status)),
                    ("taskID"            ,int(self.defualtTaskID)),
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

    def request_device_info(self):
        """Request device information and parse the response."""
        command  = "ADEV"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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
    def start_self_test(self):
        """Request device information and parse the response."""
        command  = "STST"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"       ,int(error_status)),                                                        
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)
                
                return f"Error Status: {error_status}, Self-Test Request Start Status: {'Success' if error_status == '0' else 'Error'}"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_self_test_result(self):
        """Request device information and parse the response."""
        command  = "ASTR"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
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
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
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


    def stop_measurement(self):
        """Request to stop the current measurement and parse the response."""
        command  = "STPM"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command)
        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                
                # Interpret the self-test state/result
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"       ,int(error_status)),                                                                          
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Stop Measurement Response: {parts[1]} (0=no errors, 1=error)"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def start_measurement(self):
        """Request to start a new measurement based on the specified task ID."""
        command  = "STAM"
        dateTime = datetime.now(timezone.utc)
        time.sleep(1)
        
        request_status = self.format_ak_request(command, data=self.defualtTaskID)

        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command:
                error_status          = parts[1]
                
                # Interpret the self-test state/result
                sensorDictionary = OrderedDict([
                    ("dateTime"          ,str(dateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))),
                    ("errorStatus"       ,int(error_status)),                                                                          
                    ])       

                mSR.sensorFinisher(dateTime,"GSR001"+command,sensorDictionary)

                return f"Start Measurement Response: {parts[1]} (0=no errors, 1=error)"
            else:
                return False, f"Invalid Command Output"
        else:
            False, f"Invalid Response"

    def request_last_measurement_results(self):
        """Request to retrieve the last measurement results (concentrations) and parse the response."""

        self.request_iteration_number()

        command  = "ACON"
        request_status = self.format_ak_request(command)

        self.socket.sendall(request_status)
        response_status = self.socket.recv(1024)
        valid, parts = self.clean_ak_response(response_status)
        if valid:
            if parts[0] == command and len(parts) == 17:
                error_status          = parts[1]
                timestamp             = parts[2]
                self.timeStamp    = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
                # Create an OrderedDict and add dateTime first
                sensorDictionary = OrderedDict()

                # Insert the current datetime as the first key
                sensorDictionary["dateTime"]    = str(self.timeStamp.strftime('%Y-%m-%d %H:%M:%S.%f'))
                sensorDictionary["errorStatus"] = int(error_status)

                self.measurements = []
                for i in range(2, len(parts), 3):
                    timestamp = parts[i]
                    cas       = parts[i + 1]
                    casGas    = self.cas_to_gas.get(parts[i + 1], "unknownCASNumber")
                    conc_ppm  = parts[i + 2]
                    self.measurements.append(f"Timestamp: {timestamp}, CAS: {cas}, gas: {casGas}, Concentration: {conc_ppm} ppm")
                    sensorDictionary[casGas]                           = float(conc_ppm)

                sensorDictionary["iterationNumber"]                = int(self.iteration_number)
                sensorDictionary["elapsedTime"]                    = int(time.time() - self.startUpTime)          
                sensorDictionary["elapsedTimeSinceDailyCheck"]     = int(time.time() - self.dailyCheckTime)       
                sensorDictionary["elapsedTimePeriodicCheck"]       = int(time.time() - self.periodicCheckTime)     


                if (self.timeStamp > self.prevTimeStamp):
                    print("New data available from the Gasera One")
                    mSR.sensorFinisher(self.timeStamp,"GSR001"+command,sensorDictionary)
                    self.prevTimeStamp = self.timeStamp
                else:
                    print("No new data available from the Gasera One")

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


    def startUpSequece(self):
        print("Running Start Up Sequence")
        time.sleep(10)
        print(self.stop_measurement())
        time.sleep(60)
        print(self.request_status())
                
        print(self.request_active_errors())
        # MAKE SURE TO MAKE STRING
        print(self.request_task_list())
        print(self.request_measurement_status())
        # MAKE SURE TO MAKE STRING
        print(self.request_name())
        print(self.request_iteration_number())
        # MAKE SURE TO MAKE STRING
        print(self.request_network_settings())
        # MAKE SURE TO MAKE STRING
        print(self.request_datetime())
        print(self.request_multi_point_sampler_parameters())
        print(self.request_system_parameters())
        # MAKE SURE TO MAKE STRING
        print(self.request_task_parameters())
        # MAKE SURE TO MAKE STRING
        print(self.request_device_info())
        print(self.start_self_test())
        time.sleep(120)
        print(self.request_self_test_result())
        time.sleep(60)
        print(self.start_measurement())
        time.sleep(120)

    #  May be not do this 
    def periodicCheck(self):
        self.periodicCheckTime  = time.time()       
        print("Running Periodic Checks")    
        print(self.request_measurement_status())
        print(self.request_network_settings())
        print(self.request_datetime())        


    def dailyCheck(self):
        self.dailyCheckTime = time.time()              
        print("Running Daily Self Checks")    
        time.sleep(10)
        print(self.stop_measurement())
        time.sleep(10)        
        print(self.start_self_test())
        time.sleep(120)
        print(self.request_self_test_result())
        time.sleep(60)        
        print(self.start_measurement())
        time.sleep(120)        