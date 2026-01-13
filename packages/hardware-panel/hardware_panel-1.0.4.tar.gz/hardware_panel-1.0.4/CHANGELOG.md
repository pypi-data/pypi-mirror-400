# Change Log

## [1.0.4] - 05-01-2026

### Changed
- Code cleanup
- Improved development environment
- Added Python cache files to .gitignore
- Updated screenshot to reflect current application state

## [1.0.3] - 04-01-2026

### Changed
- Memory graph now uses dual-axis display: RAM usage (left axis, green) and Swap usage (right axis, orange)
- Network graph now uses dual-axis display: Download speed (left axis, blue) and Upload speed (right axis, orange) and dynamically switches between KB/s and MB/s scales based on traffic speed
- Disabled zoom on all graphs to keep the time axis fixed at 60 seconds

## [1.0.2] - 04-01-2026

### Fixed
- Fixed screenshot display on PyPI page
- Fixed icons not appearing when installed via pip (system-wide installation)

## [1.0.1] - 04-01-2026

### Fixed
- Fixed icon loading when installed via pip

### Changed
- Updated installation instructions to require system-wide installation

### Added
- Added screenshot to README and PyPI page

## [1.0.0] - 04-01-2026

### Added
- Real-time hardware monitoring dashboard with intuitive interface
    - CPU monitoring: Temperature (Celsius) and Usage (%)
    - GPU monitoring: Temperature (Celsius) and Usage (%) with NVIDIA and AMD support
    - Memory monitoring: RAM Usage (%) and Swap Usage (%)
    - Disk monitoring: Temperature (Celsius) and Usage (%)
    - Network monitoring: Download and upload speeds (MB/s)
- Historical data tracking with interactive graphs displaying last 60 seconds of data
- Interactive crosshair for inspecting specific moments in time (timestamp display with hours, minutes, and seconds)
- Power profile management with three modes (Seamless switching without system restart):
    - Automatic Mode: Intelligent power management that adapts to workload
    - Power Saver: Optimized for battery life and low power consumption
    - Performance: Maximum performance for demanding tasks
- Multi-distribution Linux support (Fedora, Ubuntu, Debian, Arch Linux, and others)