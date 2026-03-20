![Logo](https://raw.githubusercontent.com/BassMastaCod/DaemonCrafter/refs/heads/master/logo.png)

A cross-platform Python library for managing system services and daemons with a unified interface.

## Overview

DaemonCrafter simplifies the process of creating, managing, and controlling system services across different operating systems. It automatically detects your platform and uses the appropriate service management backend:

- **Linux**: systemd
- **Windows**: Service Control Manager (SCM)

## Features

- 🔄 **Cross-platform compatibility** - Works seamlessly on Linux and Windows
- 🚀 **Easy service installation** - Install any Python script or executable as a system service
- 🎛️ **Complete lifecycle management** - Install, uninstall, start, stop, enable, disable services
- 📊 **Log management** - Retrieve and monitor service logs
- 🔧 **Automatic backend selection** - No need to worry about platform-specific implementations
- 🐍 **Python 3.8+ support** - Compatible with modern Python versions

## Installation

```bash
pip install DaemonCrafter
```

## Quick Start

```python
from pathlib import Path
from daemoncrafter import DaemonCrafter

# Create a daemon manager for your application
daemon = DaemonCrafter(
  name="my-app-service",
  executable=Path("/path/to/your/application")
)

# Install the service
daemon.install()

# Enable auto-start at boot
daemon.enable()

# Start the service
daemon.start()

# Check if it's running
if daemon.is_running():
  print("Service is running!")

# View recent logs
logs = daemon.get_logs(lines=20)
for log_line in logs:
  print(log_line)
```

## API Reference

### DaemonCrafter Class

#### Constructor
```python
DaemonCrafter(name: str, executable: Path, backend: Optional[type[DaemonProvider]] = None)
```

- `name`: The name of the service
- `executable`: Path to the executable or script
- `backend`: Optional custom backend provider (auto-detected if not specified)

#### Methods

| Method | Description |
|--------|-------------|
| `install()` | Install the application as a system service |
| `uninstall()` | Remove the service (keeps application files) |
| `start()` | Start the service |
| `stop()` | Stop the service |
| `restart()` | Restart the service |
| `enable()` | Enable auto-start at boot |
| `disable()` | Disable auto-start at boot |
| `is_installed()` | Check if service is installed |
| `is_running()` | Check if service is currently running |
| `is_enabled()` | Check if service is enabled for auto-start |
| `get_logs(lines, since, until)` | Retrieve service logs |

## Advanced Usage

### Custom Backend

```python
from daemoncrafter import DaemonCrafter
from daemoncrafter.linux import SystemdProvider

# Force use of systemd even on other platforms
daemon = DaemonCrafter(
  name="my-service",
  executable=Path("/usr/local/bin/myapp"),
  backend=SystemdProvider
)
```

### Log Management

```python
# Get last 100 lines
logs = daemon.get_logs(lines=100)

# Get logs from specific time period
logs = daemon.get_logs(since="2024-01-01", until="2024-01-02")
```

## Platform Support

### Linux
- Uses systemd for service management
- Requires systemd-enabled distribution
- Services installed in `/etc/systemd/system/`

### Windows
- Uses Windows Service Control Manager (SCM)
- Includes winsw.exe for service wrapper functionality
- Services registered in Windows Services

### Mac
- Not yet supported (PRs welcome!)

## Requirements

- Python 3.8 or higher
- `str-case-util` dependency
- Platform-specific requirements:
  - Linux: systemd
  - Windows: Administrative privileges for service installation
