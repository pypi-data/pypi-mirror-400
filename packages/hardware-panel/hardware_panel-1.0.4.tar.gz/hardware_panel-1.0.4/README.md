# Hardware Panel

## Overview

Hardware Panel is a powerful system monitoring and hardware control application for Linux. Built with Python and PyQt5, it provides real-time hardware monitoring and dynamic power profile management through an intuitive interface.

Compatible with all major Linux distributions including Fedora, Ubuntu, Debian, Arch Linux, and others.

![Hardware Panel Screenshot](https://raw.githubusercontent.com/martimmpr/linux-hardware-panel/main/screenshot.png)

## Features

### Real-Time Monitoring
- **CPU**: Temperature (Celsius) + Usage (%)
- **GPU**: Temperature (Celsius) + Usage (%)
- **Memory**: Usage (%) + Swap (%)
- **Disk**: Temperature (Celsius) + Usage (%)
- **Network**: Download (MB/s) + Upload (MB/s)

### Historical Data Tracking
- Real-time graphs displaying the last 60 seconds of data
- Interactive crosshair to inspect specific moments
- Precise timestamp display (hours, minutes, seconds)
- Instant value readout at any point on the timeline

### Power Profiles
- **Automatic Mode**: Intelligent power management that adapts to workload
- **Power Saver**: Optimized for battery life and low power consumption
- **Performance**: Maximum performance for demanding tasks

> Seamless switching between modes without system restart!

## Installation

### Quick Start

**1. Install system dependencies:**

```bash
# Fedora
sudo dnf install python3-pip lm_sensors kernel-tools

# Ubuntu/Debian
sudo apt install python3-pip lm-sensors linux-cpupower

# Arch Linux
sudo pacman -S python-pip lm_sensors cpupower
```

**2. Install Hardware Panel:**

```bash
sudo pip install hardware-panel
```

**3. Run the application:**

```bash
sudo hardware-panel
# or
sudo hwpanel
```

> **Note:** Root privileges are required for power profile management.

For detailed installation instructions and troubleshooting, see [INSTALL.md](INSTALL.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.