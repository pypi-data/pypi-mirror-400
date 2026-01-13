import os
import subprocess
import re
from collections import deque
from datetime import datetime
import psutil

class HardwareMonitor:
    def __init__(self):
        self.history_size = 60
        self.cpu_temp_history = deque(maxlen=self.history_size)
        self.cpu_usage_history = deque(maxlen=self.history_size)
        self.gpu_temp_history = deque(maxlen=self.history_size)
        self.gpu_usage_history = deque(maxlen=self.history_size)
        self.ram_usage_history = deque(maxlen=self.history_size)
        self.swap_usage_history = deque(maxlen=self.history_size)
        self.disk_temp_history = deque(maxlen=self.history_size)
        self.disk_usage_history = deque(maxlen=self.history_size)
        self.net_download_history = deque(maxlen=self.history_size)
        self.net_upload_history = deque(maxlen=self.history_size)
        self.timestamp_history = deque(maxlen=self.history_size)
        
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = datetime.now()
        
    def get_cpu_name(self):
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        return line.split(':')[1].strip()
        except Exception as e:
            print(f"Error reading CPU name: {e}")
        return "Unknown CPU"
    
    def get_cpu_temperature(self):
        try:
            # Use sensors command
            result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=2)
            output = result.stdout
            
            # CPU package temperature
            patterns = [
                r'Package id 0:\s+\+(\d+\.\d+)°C',
                r'Tdie:\s+\+(\d+\.\d+)°C',
                r'CPU:\s+\+(\d+\.\d+)°C',
                r'Core 0:\s+\+(\d+\.\d+)°C'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output)
                if match:
                    return float(match.group(1))
            
            # Use thermal_zone
            thermal_paths = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/thermal/thermal_zone1/temp'
            ]
            
            for path in thermal_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp = int(f.read().strip()) / 1000.0
                        if temp > 0 and temp < 150:
                            return temp
        except Exception as e:
            print(f"Error reading CPU temperature: {e}")
        
        return 0.0
    
    def get_cpu_usage(self):
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            print(f"Error reading CPU usage: {e}")
            return 0.0
    
    def get_gpu_name(self):
        try:
            # Try NVIDIA
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        try:
            # Try AMD via lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n'):
                if 'VGA compatible controller' in line or '3D controller' in line:
                    if 'AMD' in line or 'ATI' in line or 'Radeon' in line:
                        # Extract GPU name
                        parts = line.split(': ')
                        if len(parts) > 1:
                            return parts[1].strip()
        except:
            pass
        
        return None
    
    def get_gpu_temperature(self):
        try:
            # Try NVIDIA
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        
        try:
            # Try AMD via hwmon
            hwmon_paths = ['/sys/class/hwmon/hwmon0', '/sys/class/hwmon/hwmon1', '/sys/class/hwmon/hwmon2']
            for hwmon in hwmon_paths:
                name_path = os.path.join(hwmon, 'name')
                if os.path.exists(name_path):
                    with open(name_path, 'r') as f:
                        name = f.read().strip()
                        if 'amdgpu' in name.lower():
                            temp_path = os.path.join(hwmon, 'temp1_input')
                            if os.path.exists(temp_path):
                                with open(temp_path, 'r') as f:
                                    return int(f.read().strip()) / 1000.0
        except Exception as e:
            print(f"Error reading GPU temperature: {e}")
        
        return 0.0
    
    def get_gpu_usage(self):
        try:
            # Try NVIDIA
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        
        return 0.0
    
    def get_ram_info(self):
        try:
            # Try dmidecode for detailed RAM info
            result = subprocess.run(['dmidecode', '-t', 'memory'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                output = result.stdout
                
                # Split by Memory Device entries
                devices = output.split('Memory Device')
                installed_modules = []
                
                for device in devices[1:]:
                    # Check if module is installed
                    if 'No Module Installed' in device:
                        continue
                    
                    # Extract size
                    size_match = re.search(r'Size:\s+(\d+)\s+(GB|MB)', device)
                    if not size_match:
                        continue
                    
                    size_value = int(size_match.group(1))
                    size_unit = size_match.group(2)
                    
                    # Convert to GB if needed
                    if size_unit == 'MB':
                        size_value = size_value // 1024
                    
                    # Extract type
                    type_match = re.search(r'Type:\s+(DDR\d+)', device)
                    ram_type = type_match.group(1) if type_match else 'Unknown'
                    
                    # Extract rated speed
                    rated_speed_match = re.search(r'Speed:\s+(\d+)\s+MT/s', device)
                    rated_speed = rated_speed_match.group(1) if rated_speed_match else None
                    
                    # Extract configured/actual speed
                    configured_speed_match = re.search(r'Configured Memory Speed:\s+(\d+)\s+MT/s', device)
                    configured_speed = configured_speed_match.group(1) if configured_speed_match else None
                    
                    installed_modules.append({
                        'size': size_value,
                        'type': ram_type,
                        'rated_speed': rated_speed,
                        'configured_speed': configured_speed
                    })
                
                if installed_modules:
                    # Get the most common configuration
                    module_count = len(installed_modules)
                    module_size = installed_modules[0]['size']
                    ram_type = installed_modules[0]['type']
                    rated_speed = installed_modules[0]['rated_speed']
                    configured_speed = installed_modules[0]['configured_speed']
                    
                    # Format RAM string
                    if rated_speed and configured_speed and rated_speed != configured_speed:
                        return f"{module_count}x {module_size}GB {ram_type}-{rated_speed} ({configured_speed} MT/s)"
                    elif configured_speed:
                        return f"{module_count}x {module_size}GB {ram_type}-{configured_speed} MT/s"
                    elif rated_speed:
                        return f"{module_count}x {module_size}GB {ram_type}-{rated_speed} MT/s"
                    else:
                        return f"{module_count}x {module_size}GB {ram_type}"
        except:
            pass
        
        # Fallback to basic info
        try:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            return f"{total_ram_gb:.0f}GB RAM"
        except:
            return "RAM"
    
    def get_ram_usage(self):
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            print(f"Error reading RAM usage: {e}")
            return 0.0
    
    def get_swap_usage(self):
        try:
            return psutil.swap_memory().percent
        except Exception as e:
            print(f"Error reading Swap usage: {e}")
            return 0.0
    
    def get_disk_info(self):
        try:
            # Get disk name from lsblk
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,MODEL'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2 and ('nvme' in parts[0] or 'sd' in parts[0]):
                        model = ' '.join(parts[1:])
                        return model
        except:
            pass
        
        return "Disk"
    
    def get_disk_temperature(self):
        try:
            # Use sensors command
            result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=2)
            output = result.stdout
            
            # NVMe composite temperature
            patterns = [
                r'Composite:\s+\+(\d+\.\d+)°C',
                r'temp1:\s+\+(\d+\.\d+)°C'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output)
                if match:
                    return float(match.group(1))
            
            # Use hddtemp as fallback for SATA drives
            result = subprocess.run(['hddtemp', '/dev/sda'], capture_output=True, text=True, timeout=2)
            match = re.search(r'(\d+)°C', result.stdout)
            if match:
                return float(match.group(1))
        except Exception as e:
            print(f"Error reading disk temperature: {e}")
        
        return 0.0
    
    def get_disk_usage(self):
        try:
            return psutil.disk_usage('/').percent
        except Exception as e:
            print(f"Error reading disk usage: {e}")
            return 0.0
    
    def get_network_speed(self):
        try:
            current_net_io = psutil.net_io_counters()
            current_time = datetime.now()
            
            time_delta = (current_time - self.last_net_time).total_seconds()
            
            if time_delta > 0:
                download_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta / (1024 * 1024)
                upload_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta / (1024 * 1024)
                
                self.last_net_io = current_net_io
                self.last_net_time = current_time
                
                return download_speed, upload_speed
        except Exception as e:
            print(f"Error reading network speed: {e}")
        
        return 0.0, 0.0
    
    def update_all_metrics(self):
        self.timestamp_history.append(datetime.now())
        self.cpu_temp_history.append(self.get_cpu_temperature())
        self.cpu_usage_history.append(self.get_cpu_usage())
        self.gpu_temp_history.append(self.get_gpu_temperature())
        self.gpu_usage_history.append(self.get_gpu_usage())
        self.ram_usage_history.append(self.get_ram_usage())
        self.swap_usage_history.append(self.get_swap_usage())
        self.disk_temp_history.append(self.get_disk_temperature())
        self.disk_usage_history.append(self.get_disk_usage())
        
        download, upload = self.get_network_speed()
        self.net_download_history.append(download)
        self.net_upload_history.append(upload)