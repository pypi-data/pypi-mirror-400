import sys
import os
from PyQt5.QtWidgets import QApplication

from modules.main_window import HardwarePanelApp

def main():
    if os.geteuid() != 0:
        print("ERROR: Hardware Panel requires root privileges.")
        print("Please run with sudo:")
        print("  sudo hardware-panel")
        print("  or")
        print("  sudo hwpanel")
        sys.exit(1)
    
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