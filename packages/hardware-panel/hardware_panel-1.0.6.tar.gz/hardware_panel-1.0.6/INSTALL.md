# Installation Guide

## Prerequisites

### System Dependencies

These packages are required for hardware monitoring and power profile management:

#### Fedora
```bash
sudo dnf install python3 python3-pip lm_sensors kernel-tools
```

#### Ubuntu/Debian
```bash
sudo apt install python3 python3-pip lm-sensors linux-cpupower
```

#### Arch Linux
```bash
sudo pacman -S python python-pip lm_sensors cpupower
```

**What each package does:**
- `python3-pip` / `python-pip`: Python package manager
- `lm_sensors` / `lm-sensors`: Hardware temperature monitoring
- `kernel-tools` / `linux-cpupower` / `cpupower`: Power profile management

## Installation

### Option 1: Install from PyPI (Recommended)

Install the latest stable version directly from PyPI:

```bash
sudo pip install hardware-panel
```

This will automatically install Python dependencies (PyQt5, psutil, pyqtgraph) system-wide.

> **Note:** System-wide installation is required for `sudo` commands to work properly.

### Option 2: Install from Source

**A) Clone and install:**

```bash
# Clone the repository
git clone https://github.com/martimmpr/linux-hardware-panel.git
cd linux-hardware-panel

# Install system-wide
sudo pip install .
```

**B) Install in development mode (for contributors):**

```bash
# Install in editable mode (user installation)
pip install -e .

# Changes to source files will be reflected immediately
# Note: Run with full path: sudo ~/.local/bin/hardware-panel
```

**C) Install Python dependencies only:**

```bash
pip install -r requirements.txt
```

### Option 3: Run directly from source (without installing)

```bash
# Clone the repository
git clone https://github.com/martimmpr/linux-hardware-panel.git
cd linux-hardware-panel

# Install Python dependencies
pip install -r requirements.txt

# Run directly
sudo python3 hardware_panel.py
```

## GPU Support

### NVIDIA GPU
Install NVIDIA drivers and tools:
```bash
# Fedora
sudo dnf install nvidia-driver nvidia-settings

# Ubuntu
sudo apt install nvidia-driver-XXX nvidia-utils

# Arch
sudo pacman -S nvidia nvidia-utils
```

### AMD GPU
AMD GPU support is built-in through the `amdgpu` driver (already included in modern kernels).

## Permissions

Some features require root/sudo access:
- Power profile management

### Running with sudo
```bash
sudo hardware-panel
# or
sudo hwpanel
```

### Optional: Configure sudo without password

**Warning: This reduces system security. Only do this if you understand the risks.**

Create a sudoers file:
```bash
sudo visudo -f /etc/sudoers.d/hardware-panel
```

Add these lines:
```
# Allow user to run hardware-panel without password
your_username ALL=(ALL) NOPASSWD: /usr/local/bin/hardware-panel
your_username ALL=(ALL) NOPASSWD: /usr/bin/cpupower
```

Replace `your_username` with your actual username.

## Initialize Sensors

Before first run, initialize sensors:
```bash
sudo sensors-detect
```

Follow the prompts and accept the defaults.

## Troubleshooting

### "cpupower not found"
Install kernel-tools or linux-cpupower package for your distribution.

### No GPU detected
- Install appropriate GPU drivers (nvidia-smi for NVIDIA)
- For AMD, ensure amdgpu driver is loaded

### Graphs not displaying
- Ensure pyqtgraph is installed: `pip install pyqtgraph`
- Try reinstalling PyQt5: `pip install --force-reinstall PyQt5`

## Uninstall

```bash
sudo pip uninstall hardware-panel
```