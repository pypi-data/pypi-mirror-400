import sys
import os
import subprocess
import re
from collections import deque
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox, QScrollArea, QToolTip
from PyQt5.QtCore import QTimer, Qt, QEvent, QSize
from PyQt5.QtGui import QPalette, QColor, QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer
import pyqtgraph as pg
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
            return psutil.cpu_percent(interval = 0.1)
        except Exception as e:
            print(f"Error reading CPU usage: {e}")
            return 0.0
    
    def get_gpu_name(self):
        try:
            # Try NVIDIA
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=  True, text = True, timeout = 2)

            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        try:
            # Try AMD via lspci
            result = subprocess.run(['lspci'], capture_output=  True, text = True, timeout = 2)

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
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], capture_output = True, text = True, timeout = 2)

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
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output = True, text = True, timeout = 2)

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
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,MODEL'], capture_output = True, text = True, timeout =2 )

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
            result = subprocess.run(['sensors'], capture_output = True, text = True, timeout = 2)
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
            result = subprocess.run(['hddtemp', '/dev/sda'], capture_output = True, text = True, timeout = 2)
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

class PowerManager:
    def __init__(self):
        self.current_mode = "Power Saver"
        self.auto_mode_enabled = True
        self.available_governors = self._get_available_governors()
    
    def _get_available_governors(self):
        try:
            result = subprocess.run(['cpupower', 'frequency-info', '-g'], capture_output = True, text = True)

            if result.returncode == 0:
                # Extract governors from output
                match = re.search(r'available cpufreq governors: (.+)', result.stdout)

                if match:
                    return match.group(1).strip().split()
        except Exception as e:
            print(f"Error getting available governors: {e}")
        
        return ['powersave', 'performance']  # Default fallback
    
    def set_power_profile(self, mode):
        try:
            if mode == "Automatic":
                self.auto_mode_enabled = True
                return True
            
            # Determine governor based on mode
            if mode == "Power Saver":
                governor = "powersave"
            elif mode == "Performance":
                governor = "performance"
            else:
                return False
            
            result = subprocess.run(['cpupower', 'frequency-set', '-g', governor], capture_output = True, text = True)
            
            if result.returncode == 0:
                self.current_mode = mode
                self.auto_mode_enabled = False

                return True
            else:
                # Only print actual errors from stderr
                if result.stderr and result.stderr.strip():
                    print(f"Error setting power profile: {result.stderr.strip()}")
                return False
                
        except FileNotFoundError:
            raise FileNotFoundError("cpupower not found. Please install kernel-tools or linux-cpupower.")
        except PermissionError:
            raise PermissionError("Permission denied. Please run with sudo.")
        except Exception as e:
            print(f"Error setting power profile: {e}")
            return False
    
    def auto_switch_profile(self, cpu_usage, cpu_temp):
        if not self.auto_mode_enabled:
            return
        
        try:
            # Switch between Power Saver and Performance based on load
            if cpu_usage > 50 or cpu_temp > 70:
                target_mode = "Performance"
            else:
                target_mode = "Power Saver"
            
            if target_mode != self.current_mode:
                self.set_power_profile(target_mode)
                # Don't disable auto mode when auto-switching
                self.auto_mode_enabled = True
        except Exception as e:
            print(f"Error in auto switch: {e}")

class HardwarePanelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.hardware_monitor = HardwareMonitor()
        self.power_manager = PowerManager()
        
        # Get hardware info once
        self.cpu_name = self.hardware_monitor.get_cpu_name()
        self.gpu_name = self.hardware_monitor.get_gpu_name()
        self.ram_info = self.hardware_monitor.get_ram_info()
        self.disk_info = self.hardware_monitor.get_disk_info()
        
        self.init_ui()
        
        # Setup update timer (1 second)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)
        
        # Initial update
        self.update_data()
    
    def init_ui(self):
        self.setWindowTitle("Hardware Panel")
        
        # Set window size
        window_width = 1000
        window_height = 600
        self.resize(window_width, window_height)
        self.setMinimumSize(window_width, window_height)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)
        
        # Apply dark theme
        self.set_dark_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top section: Current values (left) and Power profile (right)
        top_layout = QHBoxLayout()
        self.create_current_values_section(top_layout)
        self.create_power_profile_section(top_layout)
        main_layout.addLayout(top_layout, 0)  # No stretch - fixed size
        
        # Graphs section
        self.create_graphs_section(main_layout)
    
    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        self.setStyleSheet("""
            QToolTip {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #51CF66;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
    
    def create_current_values_section(self, parent_layout):
        """Create current values section with icons"""

        values_widget = QWidget()
        values_layout = QVBoxLayout(values_widget)
        values_layout.setSpacing(8)
        values_layout.setContentsMargins(5, 5, 5, 5)
        
        icon_locations = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons'),  # Development mode
            '/usr/share/hardware-panel/icons',
            '/usr/local/share/hardware-panel/icons',
        ]
        icon_dir = next((path for path in icon_locations if os.path.exists(path)), '')
        
        def create_icon(icon_name):
            icon_label = QLabel()
            icon_path = os.path.join(icon_dir, icon_name)
            if os.path.exists(icon_path):
                pixmap = QPixmap(24, 24)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer = QSvgRenderer(icon_path)
                renderer.render(painter)
                painter.end()
                
                image = pixmap.toImage()
                for x in range(image.width()):
                    for y in range(image.height()):
                        pixel = image.pixelColor(x, y)
                        if pixel.alpha() > 0:
                            image.setPixelColor(x, y, QColor(255, 255, 255, pixel.alpha()))
                
                icon_label.setPixmap(QPixmap.fromImage(image))
            return icon_label
        
        def create_info_row(icon_name):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            
            icon = create_icon(icon_name)
            layout.addWidget(icon)
            
            label = QLabel()
            label.setTextFormat(Qt.RichText)
            label.setStyleSheet("color: #FFFFFF; font-size: 13px;")
            layout.addWidget(label)
            layout.addStretch()
            
            return container, label
        
        # Grid for CPU, GPU, RAM, Disk (1 column x 4 rows)
        hardware_grid = QGridLayout()
        hardware_grid.setSpacing(8)
        hardware_grid.setContentsMargins(0, 0, 0, 0)
        
        # CPU
        cpu_container, self.cpu_info_label = create_info_row('cpu.svg')
        hardware_grid.addWidget(cpu_container, 0, 0)
        
        # GPU
        gpu_container, self.gpu_info_label = create_info_row('gpu.svg')
        hardware_grid.addWidget(gpu_container, 1, 0)
        
        # RAM
        ram_container, self.ram_info_label = create_info_row('ram.svg')
        hardware_grid.addWidget(ram_container, 2, 0)
        
        # Disk
        disk_container, self.disk_info_label = create_info_row('disk.svg')
        hardware_grid.addWidget(disk_container, 3, 0)
        
        values_layout.addLayout(hardware_grid)
        
        # Grid for Network (2 columns x 1 row)
        network_grid = QGridLayout()
        network_grid.setContentsMargins(0, 0, 0, 0)
        network_grid.setSpacing(5)
        
        # Network Download
        net_down_container, self.net_download_info_label = create_info_row('download.svg')
        network_grid.addWidget(net_down_container, 0, 0)
        
        # Network Upload
        net_up_container, self.net_upload_info_label = create_info_row('upload.svg')
        network_grid.addWidget(net_up_container, 0, 1)
        
        values_layout.addLayout(network_grid)
        values_layout.addStretch()
        
        parent_layout.addWidget(values_widget, 1)
    
    def create_graphs_section(self, parent_layout):
        """Create graphs section with grid layout"""

        # First row: CPU and GPU
        first_row = QHBoxLayout()
        first_row.setSpacing(10)
        
        # Configure pyqtgraph
        pg.setConfigOptions(antialias=True)
        
        # CPU Graph (Temperature + Usage)
        self.cpu_graph = pg.PlotWidget(title="CPU")
        self.cpu_graph.setBackground('#1a1a1a')
        self.cpu_graph.setMouseEnabled(x=False, y=False)
        self.cpu_graph.hideButtons()
        self.cpu_graph.setMenuEnabled(False)
        self.cpu_graph.setLabel('left', 'Temperature (°C)', color='#FF6B6B')
        self.cpu_graph.setLabel('right', 'Usage (%)', color='#51CF66')
        self.cpu_graph.setLabel('bottom', 'Time (seconds)')
        self.cpu_graph.setXRange(0, 60, padding=0)
        self.cpu_graph.setYRange(0, 100, padding=0)
        self.cpu_graph.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.cpu_graph.getAxis('right').setStyle(showValues=True, autoExpandTextSpace=False)
        self.cpu_graph.showAxis('right')
        self.cpu_graph.getViewBox().setLimits(xMin=0, xMax=60, yMin=0, yMax=100)
        self.cpu_graph.getViewBox().setAutoVisible(y=False)
        
        # CPU crosshair
        self.cpu_vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.cpu_hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.cpu_vline.setVisible(False)
        self.cpu_hline.setVisible(False)
        self.cpu_graph.addItem(self.cpu_vline, ignoreBounds=True)
        self.cpu_graph.addItem(self.cpu_hline, ignoreBounds=True)
        self.cpu_label = pg.TextItem(anchor=(0, 1))
        self.cpu_label.setVisible(False)
        self.cpu_graph.addItem(self.cpu_label)
        
        # Dual axis for CPU
        self.cpu_temp_curve = self.cpu_graph.plot(pen=pg.mkPen(color='#FF6B6B', width=2))
        
        # Second Y-axis for CPU usage
        self.cpu_usage_viewbox = pg.ViewBox()
        self.cpu_graph.scene().addItem(self.cpu_usage_viewbox)
        self.cpu_graph.getAxis('right').linkToView(self.cpu_usage_viewbox)
        self.cpu_usage_viewbox.setXLink(self.cpu_graph)
        self.cpu_usage_viewbox.setMouseEnabled(x=False, y=False)
        self.cpu_usage_viewbox.setYRange(0, 100, padding=0)
        self.cpu_usage_viewbox.setLimits(yMin=0, yMax=100)
        self.cpu_usage_curve = pg.PlotCurveItem(pen=pg.mkPen(color='#51CF66', width=2))
        self.cpu_usage_viewbox.addItem(self.cpu_usage_curve)
        
        # Connect mouse move event for CPU
        self.cpu_proxy = pg.SignalProxy(self.cpu_graph.scene().sigMouseMoved, rateLimit=60, slot=lambda evt: self.mouseMoved(evt, 'cpu'))
        self.cpu_graph.installEventFilter(self)
        self.cpu_graph.setMouseTracking(True)
        
        # GPU Graph (Temperature + Usage)
        self.gpu_graph = pg.PlotWidget(title="GPU")
        self.gpu_graph.setBackground('#1a1a1a')
        self.gpu_graph.setMouseEnabled(x=False, y=False)
        self.gpu_graph.hideButtons()
        self.gpu_graph.setMenuEnabled(False)
        self.gpu_graph.setLabel('left', 'Temperature (°C)', color='#FF6B6B')
        self.gpu_graph.setLabel('right', 'Usage (%)', color='#51CF66')
        self.gpu_graph.setLabel('bottom', 'Time (seconds)')
        self.gpu_graph.setXRange(0, 60, padding=0)
        self.gpu_graph.setYRange(0, 100, padding=0)
        self.gpu_graph.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.gpu_graph.getAxis('right').setStyle(showValues=True, autoExpandTextSpace=False)
        self.gpu_graph.showAxis('right')
        self.gpu_graph.getViewBox().setLimits(xMin=0, xMax=60, yMin=0, yMax=100)
        self.gpu_graph.getViewBox().setAutoVisible(y=False)
        
        # GPU crosshair
        self.gpu_vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.gpu_hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.gpu_vline.setVisible(False)
        self.gpu_hline.setVisible(False)
        self.gpu_graph.addItem(self.gpu_vline, ignoreBounds=True)
        self.gpu_graph.addItem(self.gpu_hline, ignoreBounds=True)
        self.gpu_label = pg.TextItem(anchor=(0, 1))
        self.gpu_label.setVisible(False)
        self.gpu_graph.addItem(self.gpu_label)
        
        # Dual axis for GPU
        self.gpu_temp_curve = self.gpu_graph.plot(pen=pg.mkPen(color='#FF6B6B', width=2))
        
        # Second Y-axis for GPU usage
        self.gpu_usage_viewbox = pg.ViewBox()
        self.gpu_graph.scene().addItem(self.gpu_usage_viewbox)
        self.gpu_graph.getAxis('right').linkToView(self.gpu_usage_viewbox)
        self.gpu_usage_viewbox.setXLink(self.gpu_graph)
        self.gpu_usage_viewbox.setMouseEnabled(x=False, y=False)
        self.gpu_usage_viewbox.setYRange(0, 100, padding=0)
        self.gpu_usage_viewbox.setLimits(yMin=0, yMax=100)
        self.gpu_usage_curve = pg.PlotCurveItem(pen=pg.mkPen(color='#51CF66', width=2))
        self.gpu_usage_viewbox.addItem(self.gpu_usage_curve)
        
        # Connect mouse move event for GPU
        self.gpu_proxy = pg.SignalProxy(self.gpu_graph.scene().sigMouseMoved, rateLimit=60, slot=lambda evt: self.mouseMoved(evt, 'gpu'))
        self.gpu_graph.installEventFilter(self)
        self.gpu_graph.setMouseTracking(True)
        
        # Add CPU and GPU to first row
        first_row.addWidget(self.cpu_graph)
        first_row.addWidget(self.gpu_graph)
        parent_layout.addLayout(first_row, 1)  # Equal stretch factor
        
        # Second row: RAM, Disk, and Network
        second_row = QHBoxLayout()
        second_row.setSpacing(10)
        
        # RAM Graph (RAM Usage + Swap Usage)
        self.ram_graph = pg.PlotWidget(title="Memory")
        self.ram_graph.setBackground('#1a1a1a')
        self.ram_graph.setMouseEnabled(x=False, y=False)
        self.ram_graph.hideButtons()
        self.ram_graph.setMenuEnabled(False)
        self.ram_graph.setLabel('left', 'RAM Usage (%)', color='#51CF66')
        self.ram_graph.setLabel('right', 'Swap Usage (%)', color='#FFA94D')
        self.ram_graph.setLabel('bottom', 'Time (seconds)')
        self.ram_graph.setXRange(0, 60, padding=0)
        self.ram_graph.setYRange(0, 100, padding=0)
        self.ram_graph.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.ram_graph.getAxis('right').setStyle(showValues=True, autoExpandTextSpace=False)
        self.ram_graph.showAxis('right')
        self.ram_graph.getViewBox().setLimits(xMin=0, xMax=60, yMin=0, yMax=100)
        self.ram_graph.getViewBox().setAutoVisible(y=False)
        
        # RAM crosshair
        self.ram_vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.ram_hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.ram_vline.setVisible(False)
        self.ram_hline.setVisible(False)
        self.ram_graph.addItem(self.ram_vline, ignoreBounds=True)
        self.ram_graph.addItem(self.ram_hline, ignoreBounds=True)
        self.ram_label = pg.TextItem(anchor=(0, 1))
        self.ram_label.setVisible(False)
        self.ram_graph.addItem(self.ram_label)
        
        # Dual axis for RAM
        self.ram_usage_curve = self.ram_graph.plot(pen=pg.mkPen(color='#51CF66', width=2))
        
        # Second Y-axis for Swap usage
        self.swap_usage_viewbox = pg.ViewBox()
        self.ram_graph.scene().addItem(self.swap_usage_viewbox)
        self.ram_graph.getAxis('right').linkToView(self.swap_usage_viewbox)
        self.swap_usage_viewbox.setXLink(self.ram_graph)
        self.swap_usage_viewbox.setMouseEnabled(x=False, y=False)
        self.swap_usage_viewbox.setYRange(0, 100, padding=0)
        self.swap_usage_viewbox.setLimits(yMin=0, yMax=100)
        self.swap_usage_curve = pg.PlotCurveItem(pen=pg.mkPen(color='#FFA94D', width=2))
        self.swap_usage_viewbox.addItem(self.swap_usage_curve)
        
        # Connect mouse move event for RAM
        self.ram_proxy = pg.SignalProxy(self.ram_graph.scene().sigMouseMoved, rateLimit=60, slot=lambda evt: self.mouseMoved(evt, 'ram'))
        self.ram_graph.installEventFilter(self)
        self.ram_graph.setMouseTracking(True)
        
        # Disk Graph (Temperature + Usage)
        self.disk_graph = pg.PlotWidget(title="Disk")
        self.disk_graph.setBackground('#1a1a1a')
        self.disk_graph.setMouseEnabled(x=False, y=False)
        self.disk_graph.hideButtons()
        self.disk_graph.setMenuEnabled(False)
        self.disk_graph.setLabel('left', 'Temperature (°C)', color='#FF6B6B')
        self.disk_graph.setLabel('right', 'Usage (%)', color='#51CF66')
        self.disk_graph.setLabel('bottom', 'Time (seconds)')
        self.disk_graph.setXRange(0, 60, padding=0)
        self.disk_graph.setYRange(0, 100, padding=0)
        self.disk_graph.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.disk_graph.getAxis('right').setStyle(showValues=True, autoExpandTextSpace=False)
        self.disk_graph.showAxis('right')
        self.disk_graph.getViewBox().setLimits(xMin=0, xMax=60, yMin=0, yMax=100)
        self.disk_graph.getViewBox().setAutoVisible(y=False)
        
        # Disk crosshair
        self.disk_vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.disk_hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.disk_vline.setVisible(False)
        self.disk_hline.setVisible(False)
        self.disk_graph.addItem(self.disk_vline, ignoreBounds=True)
        self.disk_graph.addItem(self.disk_hline, ignoreBounds=True)
        self.disk_label = pg.TextItem(anchor=(0, 1))
        self.disk_label.setVisible(False)
        self.disk_graph.addItem(self.disk_label)
        
        # Dual axis for Disk
        self.disk_temp_curve = self.disk_graph.plot(pen=pg.mkPen(color='#FF6B6B', width=2))
        
        # Second Y-axis for Disk usage
        self.disk_usage_viewbox = pg.ViewBox()
        self.disk_graph.scene().addItem(self.disk_usage_viewbox)
        self.disk_graph.getAxis('right').linkToView(self.disk_usage_viewbox)
        self.disk_usage_viewbox.setXLink(self.disk_graph)
        self.disk_usage_viewbox.setMouseEnabled(x=False, y=False)
        self.disk_usage_viewbox.setYRange(0, 100, padding=0)
        self.disk_usage_viewbox.setLimits(yMin=0, yMax=100)
        self.disk_usage_curve = pg.PlotCurveItem(pen=pg.mkPen(color='#51CF66', width=2))
        self.disk_usage_viewbox.addItem(self.disk_usage_curve)
        
        # Connect mouse move event for Disk
        self.disk_proxy = pg.SignalProxy(self.disk_graph.scene().sigMouseMoved, rateLimit=60, slot=lambda evt: self.mouseMoved(evt, 'disk'))
        self.disk_graph.installEventFilter(self)
        self.disk_graph.setMouseTracking(True)
        
        # Network Graph (Download + Upload)
        self.net_graph = pg.PlotWidget(title="Network")
        self.net_graph.setBackground('#1a1a1a')
        self.net_graph.setMouseEnabled(x=False, y=False)
        self.net_graph.hideButtons()
        self.net_graph.setMenuEnabled(False)
        self.net_graph.setLabel('left', 'Download (MB/s)', color='#339AF0')
        self.net_graph.setLabel('right', 'Upload (MB/s)', color='#FFA94D')
        self.net_graph.setLabel('bottom', 'Time (seconds)')
        self.net_graph.setXRange(0, 60, padding=0)
        self.net_graph.getAxis('left').setStyle(autoExpandTextSpace=False)
        self.net_graph.getAxis('right').setStyle(showValues=True, autoExpandTextSpace=False)
        self.net_graph.showAxis('right')
        self.net_graph.getViewBox().setLimits(xMin=0, xMax=60, yMin=0)
        self.net_graph.getViewBox().setAutoVisible(y=True)
        
        # Network crosshair
        self.net_vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.net_hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#ADB5BD', width=1, style=Qt.DashLine))
        self.net_vline.setVisible(False)
        self.net_hline.setVisible(False)
        self.net_graph.addItem(self.net_vline, ignoreBounds=True)
        self.net_graph.addItem(self.net_hline, ignoreBounds=True)
        self.net_label = pg.TextItem(anchor=(0, 1))
        self.net_label.setVisible(False)
        self.net_graph.addItem(self.net_label)
        
        # Dual axis for Network
        self.net_download_curve = self.net_graph.plot(pen=pg.mkPen(color='#339AF0', width=2))
        
        # Second Y-axis for Upload
        self.net_upload_viewbox = pg.ViewBox()
        self.net_graph.scene().addItem(self.net_upload_viewbox)
        self.net_graph.getAxis('right').linkToView(self.net_upload_viewbox)
        self.net_upload_viewbox.setXLink(self.net_graph)
        self.net_upload_viewbox.setMouseEnabled(x=False, y=False)
        self.net_upload_viewbox.setLimits(yMin=0)
        self.net_upload_viewbox.setAutoVisible(y=True)
        self.net_upload_curve = pg.PlotCurveItem(pen=pg.mkPen(color='#FFA94D', width=2))
        self.net_upload_viewbox.addItem(self.net_upload_curve)
        
        # Connect mouse move event for Network
        self.net_proxy = pg.SignalProxy(self.net_graph.scene().sigMouseMoved, rateLimit=60, slot=lambda evt: self.mouseMoved(evt, 'net'))
        self.net_graph.installEventFilter(self)
        self.net_graph.setMouseTracking(True)
        
        # Add RAM, Disk, and Network to second row
        second_row.addWidget(self.ram_graph)
        second_row.addWidget(self.disk_graph)
        second_row.addWidget(self.net_graph)
        parent_layout.addLayout(second_row, 1)  # Equal stretch factor
        
        # Update viewbox geometry for dual-axis graphs
        def updateCPUViews():
            self.cpu_usage_viewbox.setGeometry(self.cpu_graph.getViewBox().sceneBoundingRect())
            self.cpu_usage_viewbox.linkedViewChanged(self.cpu_graph.getViewBox(), self.cpu_usage_viewbox.XAxis)
        
        def updateGPUViews():
            self.gpu_usage_viewbox.setGeometry(self.gpu_graph.getViewBox().sceneBoundingRect())
            self.gpu_usage_viewbox.linkedViewChanged(self.gpu_graph.getViewBox(), self.gpu_usage_viewbox.XAxis)
        
        def updateDiskViews():
            self.disk_usage_viewbox.setGeometry(self.disk_graph.getViewBox().sceneBoundingRect())
            self.disk_usage_viewbox.linkedViewChanged(self.disk_graph.getViewBox(), self.disk_usage_viewbox.XAxis)
        
        def updateRAMViews():
            self.swap_usage_viewbox.setGeometry(self.ram_graph.getViewBox().sceneBoundingRect())
            self.swap_usage_viewbox.linkedViewChanged(self.ram_graph.getViewBox(), self.swap_usage_viewbox.XAxis)
        
        def updateNetViews():
            self.net_upload_viewbox.setGeometry(self.net_graph.getViewBox().sceneBoundingRect())
            self.net_upload_viewbox.linkedViewChanged(self.net_graph.getViewBox(), self.net_upload_viewbox.XAxis)
        
        updateCPUViews()
        updateGPUViews()
        updateDiskViews()
        updateRAMViews()
        updateNetViews()

        self.cpu_graph.getViewBox().sigResized.connect(updateCPUViews)
        self.gpu_graph.getViewBox().sigResized.connect(updateGPUViews)
        self.disk_graph.getViewBox().sigResized.connect(updateDiskViews)
        self.ram_graph.getViewBox().sigResized.connect(updateRAMViews)
        self.net_graph.getViewBox().sigResized.connect(updateNetViews)
    
    def create_power_profile_section(self, parent_layout):
        power_widget = QWidget()
        power_layout = QVBoxLayout(power_widget)
        power_layout.setSpacing(8)
        power_layout.setContentsMargins(5, 5, 5, 5)
        
        title_layout = QHBoxLayout()
        title_label = QLabel("Power Profile")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        title_layout.addWidget(title_label)
        
        icon_locations = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons'),  # Development mode
            '/usr/share/hardware-panel/icons',
            '/usr/local/share/hardware-panel/icons',
        ]
        icon_dir = next((path for path in icon_locations if os.path.exists(path)), '')
        
        help_btn = QPushButton()
        help_icon_path = os.path.join(icon_dir, 'help.svg')
        if os.path.exists(help_icon_path):
            pixmap = QPixmap(20, 20)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer = QSvgRenderer(help_icon_path)
            renderer.render(painter)
            painter.end()
            
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    pixel = image.pixelColor(x, y)

                    if pixel.alpha() > 0:
                        image.setPixelColor(x, y, QColor(255, 255, 255, pixel.alpha()))
            
            help_btn.setIcon(QIcon(QPixmap.fromImage(image)))
            help_btn.setIconSize(QSize(20, 20))

        help_btn.setFlat(True)
        help_btn.setFixedSize(26, 26)
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.setStyleSheet("QPushButton { border: none; background: transparent; padding: 2px; }")
        help_btn.setFocusPolicy(Qt.NoFocus)
        help_tooltip = (
            "<div style='line-height: 1.4;'>"
            "<p style='margin: 0 0 4px 0;'><b style='color: #51CF66;'>Automatic Mode:</b> Intelligently switches between profiles:</p>"
            "<p style='margin: 0 0 2px 0; padding-left: 12px;'>• CPU usage &lt; 50% and temp &lt; 70°C → Power Saver</p>"
            "<p style='margin: 0 0 8px 0; padding-left: 12px;'>• CPU usage ≥ 50% or temp ≥ 70°C → Performance</p>"
            "<p style='margin: 0 0 6px 0;'><b style='color: #51CF66;'>Power Saver:</b> Low power consumption with dynamic frequency</p>"
            "<p style='margin: 0;'><b style='color: #FF6B6B;'>Performance:</b> Maximum performance at all times</p>"
            "</div>"
        )
        help_btn.setToolTip(help_tooltip)
        help_btn.setToolTipDuration(0)
        help_btn.installEventFilter(self)
        self.help_btn = help_btn
        title_layout.addWidget(help_btn)
        title_layout.addStretch()
        power_layout.addLayout(title_layout)
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        self.auto_btn = QPushButton("Automatic Mode")
        self.auto_btn.setMinimumHeight(35)
        self.auto_btn.clicked.connect(lambda: self.set_power_mode("Automatic"))
        button_layout.addWidget(self.auto_btn)
        
        self.power_saver_btn = QPushButton("Power Saver")
        self.power_saver_btn.setMinimumHeight(35)
        self.power_saver_btn.clicked.connect(lambda: self.set_power_mode("Power Saver"))
        button_layout.addWidget(self.power_saver_btn)
        
        self.performance_btn = QPushButton("Performance")
        self.performance_btn.setMinimumHeight(35)
        self.performance_btn.clicked.connect(lambda: self.set_power_mode("Performance"))
        button_layout.addWidget(self.performance_btn)
        
        power_layout.addLayout(button_layout)
        power_layout.addStretch()
        
        parent_layout.addWidget(power_widget, 1)
        
        self.update_power_button_styles()
    
    def eventFilter(self, obj, event):
        if hasattr(self, 'help_btn') and obj == self.help_btn:
            if event.type() == QEvent.Enter:
                # Show tooltip immediately on hover
                QToolTip.showText(self.help_btn.mapToGlobal(self.help_btn.rect().bottomLeft()), self.help_btn.toolTip(), self.help_btn)

                return True
            elif event.type() == QEvent.Leave:
                QToolTip.hideText()
                return True
        
        # Hide graph crosshairs on Leave event
        if event.type() == QEvent.Leave:
            if obj == self.cpu_graph:
                self.cpu_vline.setVisible(False)
                self.cpu_hline.setVisible(False)
                self.cpu_label.setVisible(False)

                return True
            elif obj == self.gpu_graph:
                self.gpu_vline.setVisible(False)
                self.gpu_hline.setVisible(False)
                self.gpu_label.setVisible(False)

                return True
            elif obj == self.ram_graph:
                self.ram_vline.setVisible(False)
                self.ram_hline.setVisible(False)
                self.ram_label.setVisible(False)

                return True
            elif obj == self.disk_graph:
                self.disk_vline.setVisible(False)
                self.disk_hline.setVisible(False)
                self.disk_label.setVisible(False)

                return True
            elif obj == self.net_graph:
                self.net_vline.setVisible(False)
                self.net_hline.setVisible(False)
                self.net_label.setVisible(False)

                return True
            
        return super().eventFilter(obj, event)
    
    def hideAllCrosshairs(self):
        self.cpu_vline.setVisible(False)
        self.cpu_hline.setVisible(False)
        self.cpu_label.setVisible(False)
        self.gpu_vline.setVisible(False)
        self.gpu_hline.setVisible(False)
        self.gpu_label.setVisible(False)
        self.ram_vline.setVisible(False)
        self.ram_hline.setVisible(False)
        self.ram_label.setVisible(False)
        self.disk_vline.setVisible(False)
        self.disk_hline.setVisible(False)
        self.disk_label.setVisible(False)
        self.net_vline.setVisible(False)
        self.net_hline.setVisible(False)
        self.net_label.setVisible(False)
    
    def mouseMoved(self, evt, graph_type):
        pos = evt[0]
        
        if graph_type == 'cpu':
            if self.cpu_graph.sceneBoundingRect().contains(pos):
                mousePoint = self.cpu_graph.getViewBox().mapSceneToView(pos)
                index = int(mousePoint.x())

                if 0 <= index < len(self.hardware_monitor.cpu_temp_history):
                    self.cpu_vline.setVisible(True)
                    self.cpu_hline.setVisible(True)
                    self.cpu_label.setVisible(True)
                    self.cpu_vline.setPos(mousePoint.x())
                    self.cpu_hline.setPos(mousePoint.y())
                    timestamp = self.hardware_monitor.timestamp_history[index].strftime('%H:%M:%S') if index < len(self.hardware_monitor.timestamp_history) else 'N/A'
                    temp = self.hardware_monitor.cpu_temp_history[index]
                    usage = self.hardware_monitor.cpu_usage_history[index]
                    self.cpu_label.setText(f"Time: {timestamp}\nTemp: {temp:.1f}°C\nUsage: {usage:.1f}%")
                    self.cpu_label.setPos(mousePoint.x(), mousePoint.y())
            else:
                self.cpu_vline.setVisible(False)
                self.cpu_hline.setVisible(False)
                self.cpu_label.setVisible(False)
        
        elif graph_type == 'gpu':
            if self.gpu_graph.sceneBoundingRect().contains(pos):
                mousePoint = self.gpu_graph.getViewBox().mapSceneToView(pos)
                index = int(mousePoint.x())

                if 0 <= index < len(self.hardware_monitor.gpu_temp_history):
                    self.gpu_vline.setVisible(True)
                    self.gpu_hline.setVisible(True)
                    self.gpu_label.setVisible(True)
                    self.gpu_vline.setPos(mousePoint.x())
                    self.gpu_hline.setPos(mousePoint.y())
                    timestamp = self.hardware_monitor.timestamp_history[index].strftime('%H:%M:%S') if index < len(self.hardware_monitor.timestamp_history) else 'N/A'
                    temp = self.hardware_monitor.gpu_temp_history[index]
                    usage = self.hardware_monitor.gpu_usage_history[index]
                    self.gpu_label.setText(f"Time: {timestamp}\nTemp: {temp:.1f}°C\nUsage: {usage:.1f}%")
                    self.gpu_label.setPos(mousePoint.x(), mousePoint.y())
            else:
                self.gpu_vline.setVisible(False)
                self.gpu_hline.setVisible(False)
                self.gpu_label.setVisible(False)
        
        elif graph_type == 'ram':
            if self.ram_graph.sceneBoundingRect().contains(pos):
                mousePoint = self.ram_graph.getViewBox().mapSceneToView(pos)
                index = int(mousePoint.x())

                if 0 <= index < len(self.hardware_monitor.ram_usage_history):
                    self.ram_vline.setVisible(True)
                    self.ram_hline.setVisible(True)
                    self.ram_label.setVisible(True)
                    self.ram_vline.setPos(mousePoint.x())
                    self.ram_hline.setPos(mousePoint.y())
                    timestamp = self.hardware_monitor.timestamp_history[index].strftime('%H:%M:%S') if index < len(self.hardware_monitor.timestamp_history) else 'N/A'
                    ram = self.hardware_monitor.ram_usage_history[index]
                    swap = self.hardware_monitor.swap_usage_history[index]
                    self.ram_label.setText(f"Time: {timestamp}\nRAM: {ram:.1f}%\nSwap: {swap:.1f}%")
                    self.ram_label.setPos(mousePoint.x(), mousePoint.y())
            else:
                self.ram_vline.setVisible(False)
                self.ram_hline.setVisible(False)
                self.ram_label.setVisible(False)
        
        elif graph_type == 'disk':
            if self.disk_graph.sceneBoundingRect().contains(pos):
                mousePoint = self.disk_graph.getViewBox().mapSceneToView(pos)
                index = int(mousePoint.x())

                if 0 <= index < len(self.hardware_monitor.disk_temp_history):
                    self.disk_vline.setVisible(True)
                    self.disk_hline.setVisible(True)
                    self.disk_label.setVisible(True)
                    self.disk_vline.setPos(mousePoint.x())
                    self.disk_hline.setPos(mousePoint.y())
                    timestamp = self.hardware_monitor.timestamp_history[index].strftime('%H:%M:%S') if index < len(self.hardware_monitor.timestamp_history) else 'N/A'
                    temp = self.hardware_monitor.disk_temp_history[index]
                    usage = self.hardware_monitor.disk_usage_history[index]
                    self.disk_label.setText(f"Time: {timestamp}\nTemp: {temp:.1f}°C\nUsage: {usage:.1f}%")
                    self.disk_label.setPos(mousePoint.x(), mousePoint.y())
            else:
                self.disk_vline.setVisible(False)
                self.disk_hline.setVisible(False)
                self.disk_label.setVisible(False)
        
        elif graph_type == 'net':
            if self.net_graph.sceneBoundingRect().contains(pos):
                mousePoint = self.net_graph.getViewBox().mapSceneToView(pos)
                index = int(mousePoint.x())

                if 0 <= index < len(self.hardware_monitor.net_download_history):
                    self.net_vline.setVisible(True)
                    self.net_hline.setVisible(True)
                    self.net_label.setVisible(True)
                    self.net_vline.setPos(mousePoint.x())
                    self.net_hline.setPos(mousePoint.y())
                    timestamp = self.hardware_monitor.timestamp_history[index].strftime('%H:%M:%S') if index < len(self.hardware_monitor.timestamp_history) else 'N/A'
                    download = self.hardware_monitor.net_download_history[index]
                    upload = self.hardware_monitor.net_upload_history[index]
                    
                    # Format with appropriate unit based on value
                    if download < 1:
                        download_str = f"{download * 1024:.2f} KB/s"
                    else:
                        download_str = f"{download:.2f} MB/s"
                    
                    if upload < 1:
                        upload_str = f"{upload * 1024:.2f} KB/s"
                    else:
                        upload_str = f"{upload:.2f} MB/s"
                    
                    self.net_label.setText(f"Time: {timestamp}\nDownload: {download_str}\nUpload: {upload_str}")
                    self.net_label.setPos(mousePoint.x(), mousePoint.y())
            else:
                self.net_vline.setVisible(False)
                self.net_hline.setVisible(False)
                self.net_label.setVisible(False)
    
    def update_power_button_styles(self):
        """Update power button styles based on current mode"""

        inactive_style = "font-size: 13px; padding: 8px; background-color: #353535; color: #FFFFFF;"
        active_green_style = "font-size: 13px; padding: 8px; background-color: #51CF66; color: #000000; font-weight: bold;"
        active_red_style = "font-size: 13px; padding: 8px; background-color: #FF6B6B; color: #000000; font-weight: bold;"
        
        # Get current actual mode
        current_mode = self.power_manager.current_mode
        
        if self.power_manager.auto_mode_enabled:
            # Automatic mode - current profile in parentheses
            self.auto_btn.setText(f"Automatic Mode ({current_mode})")

            # Green for Power Saver
            if current_mode == "Power Saver":
                self.auto_btn.setStyleSheet(active_green_style)
            else:  # Red for Performance
                self.auto_btn.setStyleSheet(active_red_style)
            self.power_saver_btn.setStyleSheet(inactive_style)
            self.performance_btn.setStyleSheet(inactive_style)
        elif current_mode == "Power Saver":
            self.auto_btn.setText("Automatic Mode")
            self.auto_btn.setStyleSheet(inactive_style)
            self.power_saver_btn.setStyleSheet(active_green_style)
            self.performance_btn.setStyleSheet(inactive_style)
        elif current_mode == "Performance":
            self.auto_btn.setText("Automatic Mode")
            self.auto_btn.setStyleSheet(inactive_style)
            self.power_saver_btn.setStyleSheet(inactive_style)
            self.performance_btn.setStyleSheet(active_red_style)
    
    def get_temp_color(self, temp):
        if temp < 60:
            return '#51CF66'
        elif temp < 75:
            return '#FFA94D'
        else:
            return '#FF6B6B'
    
    def get_usage_color(self, usage):
        if usage < 50:
            return '#51CF66'
        elif usage < 80:
            return '#FFA94D'
        else:
            return '#FF6B6B'
        
    def get_disk_usage_color(self, usage):
        if usage < 50:
            return '#51CF66'
        elif usage < 75:
            return '#FFA94D'
        else:
            return '#FF6B6B'
    
    def set_power_mode(self, mode):
        try:
            if self.power_manager.set_power_profile(mode):
                self.update_power_button_styles()
                QMessageBox.information(self, "Success", f"Power mode set to: {mode}")
            else:
                QMessageBox.warning(self, "Warning", f"Failed to set power mode to: {mode}")
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))
        except PermissionError as e:
            QMessageBox.warning(self, "Permission Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set power mode: {e}")
    
    def update_data(self):
        # Update hardware monitor
        self.hardware_monitor.update_all_metrics()
        
        # Get latest values
        cpu_temp = self.hardware_monitor.cpu_temp_history[-1] if self.hardware_monitor.cpu_temp_history else 0
        cpu_usage = self.hardware_monitor.cpu_usage_history[-1] if self.hardware_monitor.cpu_usage_history else 0
        gpu_temp = self.hardware_monitor.gpu_temp_history[-1] if self.hardware_monitor.gpu_temp_history else 0
        gpu_usage = self.hardware_monitor.gpu_usage_history[-1] if self.hardware_monitor.gpu_usage_history else 0
        ram_usage = self.hardware_monitor.ram_usage_history[-1] if self.hardware_monitor.ram_usage_history else 0
        swap_usage = self.hardware_monitor.swap_usage_history[-1] if self.hardware_monitor.swap_usage_history else 0
        disk_temp = self.hardware_monitor.disk_temp_history[-1] if self.hardware_monitor.disk_temp_history else 0
        disk_usage = self.hardware_monitor.disk_usage_history[-1] if self.hardware_monitor.disk_usage_history else 0
        net_download = self.hardware_monitor.net_download_history[-1] if self.hardware_monitor.net_download_history else 0
        net_upload = self.hardware_monitor.net_upload_history[-1] if self.hardware_monitor.net_upload_history else 0
        
        # Update labels with detailed format
        cpu_temp_color = self.get_temp_color(cpu_temp)
        cpu_usage_color = self.get_usage_color(cpu_usage)
        gpu_temp_color = self.get_temp_color(gpu_temp)
        gpu_usage_color = self.get_usage_color(gpu_usage)
        ram_usage_color = self.get_usage_color(ram_usage)
        swap_usage_color = self.get_usage_color(swap_usage)
        disk_temp_color = self.get_temp_color(disk_temp)
        disk_usage_color = self.get_disk_usage_color(disk_usage)
        
        # CPU: Name + (Temp Cº, Usage%)
        self.cpu_info_label.setText(
            f"<span style='color:#FFFFFF; font-weight: 600;'>{self.cpu_name}</span> "
            f"(<span style='color:{cpu_temp_color}; font-weight: bold;'>{cpu_temp:.1f}°C</span> / "
            f"<span style='color:{cpu_usage_color}; font-weight: bold;'>{cpu_usage:.1f}%</span>)"
        )
        
        # GPU: Name + (Temp Cº, Usage%)
        if self.gpu_name:
            self.gpu_info_label.setText(
                f"<span style='color:#FFFFFF; font-weight: 600;'>{self.gpu_name}</span> "
                f"(<span style='color:{gpu_temp_color}; font-weight: bold;'>{gpu_temp:.1f}°C</span> / "
                f"<span style='color:{gpu_usage_color}; font-weight: bold;'>{gpu_usage:.1f}%</span>)"
            )
        else:
            self.gpu_info_label.setText("<span style='color:#868E96;'>No GPU detected</span>")
        
        # RAM: Info + (Usage% / Swap%)
        self.ram_info_label.setText(
            f"<span style='color:#FFFFFF; font-weight: 600;'>{self.ram_info}</span> "
            f"(<span style='color:{ram_usage_color}; font-weight: bold;'>{ram_usage:.1f}%</span> / "
            f"<span style='color:{swap_usage_color}; font-weight: bold;'>{swap_usage:.1f}%</span>)"
        )
        
        # Disk: Name + (Used/Total GB, Temp Cº, Usage%)
        disk_total = psutil.disk_usage('/').total / (1024**3)
        disk_used = psutil.disk_usage('/').used / (1024**3)
        self.disk_info_label.setText(
            f"<span style='color:#FFFFFF; font-weight: 600;'>{self.disk_info}</span> "
            f"(<span style='color:{disk_usage_color}; font-weight: bold;'>{disk_used:.0f}/{disk_total:.0f}GB</span>, "
            f"<span style='color:{disk_temp_color}; font-weight: bold;'>{disk_temp:.1f}°C</span>, "
            f"<span style='color:{disk_usage_color}; font-weight: bold;'>{disk_usage:.1f}%</span>)"
        )
        
        # Network: Download + Upload (dynamic MB/s or KB/s)
        max_net_speed = max(net_download, net_upload)
        if max_net_speed < 1:
            # Use KB/s
            download_kb = net_download * 1024
            upload_kb = net_upload * 1024
            self.net_download_info_label.setText(f"<span style='color:#339AF0; font-weight: bold;'>{download_kb:.2f} KB/s</span>")
            self.net_upload_info_label.setText(f"<span style='color:#FFA94D; font-weight: bold;'>{upload_kb:.2f} KB/s</span>")
        else:
            # Use MB/s
            self.net_download_info_label.setText(f"<span style='color:#339AF0; font-weight: bold;'>{net_download:.2f} MB/s</span>")
            self.net_upload_info_label.setText(f"<span style='color:#FFA94D; font-weight: bold;'>{net_upload:.2f} MB/s</span>")
        
        # Update graphs - CPU
        self.cpu_temp_curve.setData(list(self.hardware_monitor.cpu_temp_history))
        self.cpu_usage_curve.setData(list(range(len(self.hardware_monitor.cpu_usage_history))), list(self.hardware_monitor.cpu_usage_history))
        
        # Update GPU graph
        self.gpu_temp_curve.setData(list(self.hardware_monitor.gpu_temp_history))
        self.gpu_usage_curve.setData(list(range(len(self.hardware_monitor.gpu_usage_history))), list(self.hardware_monitor.gpu_usage_history))
        
        # Update RAM graph
        self.ram_usage_curve.setData(list(self.hardware_monitor.ram_usage_history))
        self.swap_usage_curve.setData(list(range(len(self.hardware_monitor.swap_usage_history))), list(self.hardware_monitor.swap_usage_history))
        
        # Update Disk graph
        self.disk_temp_curve.setData(list(self.hardware_monitor.disk_temp_history))
        self.disk_usage_curve.setData(list(range(len(self.hardware_monitor.disk_usage_history))), list(self.hardware_monitor.disk_usage_history))
        
        # Update Network graph with dynamic scale
        if self.hardware_monitor.net_download_history or self.hardware_monitor.net_upload_history:
            max_download = max(self.hardware_monitor.net_download_history) if self.hardware_monitor.net_download_history else 0
            max_upload = max(self.hardware_monitor.net_upload_history) if self.hardware_monitor.net_upload_history else 0
            max_speed = max(max_download, max_upload)
            
            # KB/s if max speed is less than 1 MB/s, otherwise use MB/s
            if max_speed < 1:
                # Convert to KB/s
                download_data = [d * 1024 for d in self.hardware_monitor.net_download_history]
                upload_data = [u * 1024 for u in self.hardware_monitor.net_upload_history]
                max_speed_download = max(download_data) if download_data else 1
                max_speed_upload = max(upload_data) if upload_data else 1
                
                self.net_download_curve.setData(download_data)
                self.net_upload_curve.setData(list(range(len(upload_data))), upload_data)
                
                self.net_graph.setLabel('left', 'Download (KB/s)', color='#339AF0')
                self.net_graph.setLabel('right', 'Upload (KB/s)', color='#FFA94D')
                self.net_graph.setYRange(0, max_speed_download * 1.1, padding=0)
                self.net_upload_viewbox.setYRange(0, max_speed_upload * 1.1, padding=0)
            else:
                # Use MB/s
                self.net_download_curve.setData(list(self.hardware_monitor.net_download_history))
                self.net_upload_curve.setData(list(range(len(self.hardware_monitor.net_upload_history))), list(self.hardware_monitor.net_upload_history))
                
                max_speed_download = max(max_download, 1)
                max_speed_upload = max(max_upload, 1)
                
                self.net_graph.setLabel('left', 'Download (MB/s)', color='#339AF0')
                self.net_graph.setLabel('right', 'Upload (MB/s)', color='#FFA94D')
                self.net_graph.setYRange(0, max_speed_download * 1.1, padding=0)
                self.net_upload_viewbox.setYRange(0, max_speed_upload * 1.1, padding=0)
        
        # Auto power management
        self.power_manager.auto_switch_profile(cpu_usage, cpu_temp)
        
        # Update power profile button styles
        self.update_power_button_styles()


def main():
    # Check if running with proper permissions
    if os.geteuid() != 0:
        print("ERROR: Hardware Panel requires root privileges.")
        print("Please run with sudo:")
        print("  sudo hardware-panel")
        print("  or")
        print("  sudo hwpanel")
        sys.exit(1)
    
    # Check if installed correctly
    icon_locations = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons'),  # Development mode
        '/usr/local/share/hardware-panel/icons',
        '/usr/share/hardware-panel/icons',
    ]
    icons_found = any(os.path.exists(path) and os.listdir(path) for path in icon_locations)
    
    if not icons_found:
        print("ERROR: Hardware Panel is not installed correctly.")
        print()
        print("Please install with sudo:")
        print("  pip uninstall hardware-panel")
        print("  sudo pip install hardware-panel")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = HardwarePanelApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()