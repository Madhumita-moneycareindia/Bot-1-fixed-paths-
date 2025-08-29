# NSE DataSync Pro - GUI Version

A professional GUI application for scheduling and managing NSE member-specific data downloads.

## Features

### ✅ Implemented Requirements

1. **Professional GUI Interface**
   - Clean, intuitive interface with tabbed layout
   - Real-time status updates
   - Progress tracking
   - History viewer

2. **Smart Directory Structure**
   - Files organized by: `Downloads/SEGMENT/YEAR/MONTH/DAY/`
   - Example: `Downloads/CM/2025/Jul/21/file.csv`

3. **Flexible Scheduling**
   - Adjustable execution intervals (15 minutes to 24 hours)
   - Dynamic schedule updates without restart
   - Next run time display

4. **Robust Process Management**
   - Graceful bot termination
   - Cycle completion guarantee
   - No interruption of running downloads

5. **Auto Shutdown**
   - Automatic shutdown at 12:00 AM daily
   - Can be enabled/disabled in settings

6. **Manual Control**
   - Command-line control script
   - Start/stop/status commands
   - Scheduled shutdown option

7. **Database Support**
   - SQLite database for configurations
   - Run history tracking
   - Settings persistence

8. **Silent Environment Handling**
   - .env file loaded internally
   - No user-facing environment options
   - Graceful error handling

9. **Professional Launch**
   - No console window on startup
   - Desktop shortcut creation (first run only)
   - Professional application icon

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows/macOS/Linux

### Setup Steps

1. **Install Dependencies**
   ```bash
   python setup_gui.py
   ```
   This will:
   - Install required packages
   - Create application icons
   - Set up directory structure
   - Initialize database

2. **Configure Credentials**
   - Ensure `.env` file exists with your NSE credentials
   - The GUI will read this automatically

## Usage

### Starting the GUI

#### Windows
- Double-click `NSE_DataSync_Pro.bat`
- Or double-click the desktop shortcut (created on first run)

#### macOS/Linux
```bash
python launch_nse_datasync.pyw
```

#### Command Line
```bash
python manual_control.py start-gui
```

### GUI Features

1. **Control Panel Tab**
   - Run Now: Execute bot immediately
   - Stop: Gracefully stop running bot
   - Schedule settings with interval adjustment

2. **Settings Tab**
   - Download path configuration
   - Segment selection (CM, FO, CD, SLB)
   - Auto shutdown toggle

3. **History Tab**
   - View recent runs
   - Check download statistics
   - Monitor errors

### Manual Control

The `manual_control.py` script provides command-line control:

```bash
# Show status
python manual_control.py status

# Stop running bot
python manual_control.py stop

# Force stop
python manual_control.py stop --force

# Run bot once
python manual_control.py run-once

# Schedule shutdown in 30 minutes
python manual_control.py shutdown 30
```

## Directory Structure

Downloaded files are organized as:
```
Downloads/
├── CM/
│   ├── 2025/
│   │   ├── Jan/
│   │   │   ├── 1/
│   │   │   │   └── CM_ORD_LOG_01012025_06471.CSV
│   │   │   ├── 2/
│   │   │   └── ...
│   │   ├── Feb/
│   │   └── ...
│   └── ...
├── FO/
│   └── [Same structure]
└── SLB/
    └── [Same structure]
```

## Configuration

### Database
- Location: `nse_datasync_config.db`
- Stores settings, schedules, and run history

### Logs
- Location: `logs/nse_datasync_gui_YYYYMMDD.log`
- Rotating daily logs

### Settings Persistence
All settings are saved in the database:
- Download path
- Schedule interval
- Enabled segments
- Auto shutdown preference

## Troubleshooting

### Bot Won't Start
1. Check credentials in `.env` file
2. Verify internet connection
3. Check logs for errors

### GUI Won't Launch
1. Ensure Python is installed
2. Run `python setup_gui.py` to reinstall dependencies
3. Check for error messages

### Files Not Downloading
1. Verify segment access permissions
2. Check download path permissions
3. Review logs for specific errors

## Security Notes

- Credentials are never exposed in GUI
- .env file is loaded silently
- All sensitive operations are logged
- Database stores only non-sensitive configuration

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: 512MB minimum
- **Storage**: 100MB for application + download space
- **Network**: Stable internet connection

## Antivirus Compatibility

The application is designed to be antivirus-friendly:
- No suspicious network behavior
- Standard Python libraries only
- Transparent logging
- No code obfuscation

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run `python manual_control.py status` for diagnostics
3. Review error messages in GUI status bar

## License

Proprietary - NSE DataSync Pro
