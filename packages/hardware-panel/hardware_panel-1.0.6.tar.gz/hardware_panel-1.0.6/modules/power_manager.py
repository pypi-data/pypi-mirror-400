import subprocess
import re

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
            
            result = subprocess.run(['cpupower', 'frequency-set', '-g', governor], capture_output=True, text=True)
            
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