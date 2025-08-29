# NSE DataSync Pro - Professional Edition v2.0

**Enterprise-grade NSE data synchronization solution with intelligent scheduling and professional file organization.**

## 🚀 Key Features

### ✅ **Enhanced Features (New in v2.0)**
- **Professional GUI**: Clean, modern interface with tabbed navigation
- **Desktop Shortcut Creation**: Automatic desktop shortcut on first run only
- **Dynamic Interval Updates**: Change scheduler interval without restart
- **Cycle Completion Guarantee**: Downloads complete fully before stopping
- **Automatic Midnight Shutdown**: Daily auto-stop at 12:00 AM
- **Professional File Organization**: Downloads/CM/2024/Jan/1/ structure
- **Secure Credentials**: No .env file exposure, encrypted database storage
- **Enhanced Database**: Comprehensive logging and statistics
- **Manual Termination**: Both GUI and command-line stop options
- **Antivirus Compatible**: Built for enterprise security compliance

### 📊 **Professional Interface**
- **Dashboard Tab**: Real-time status and quick controls
- **Scheduler Tab**: Dynamic interval configuration and advanced options
- **Settings Tab**: Secure credential management and path configuration
- **Monitoring Tab**: Real-time logs and activity tracking
- **Statistics Tab**: Comprehensive download analytics and history

### 🛡️ **Security & Reliability**
- **No .env File Dependencies**: Silent credential loading without errors
- **Encrypted Credential Storage**: AES encryption with secure database
- **Download Tracking**: Complete audit trail with checksums
- **Error Recovery**: Intelligent retry mechanisms and failure handling
- **Process Management**: Clean startup/shutdown and resource management

## 📁 **File Organization Structure**

Files are automatically organized in a professional hierarchy:

```
Downloads/
├── CM/
│   ├── 2024/
│   │   ├── Jan/
│   │   │   ├── 1/
│   │   │   ├── 2/
│   │   │   └── ...
│   │   ├── Feb/
│   │   └── ...
│   └── 2023/
├── FO/
│   └── (same structure)
└── SLB/
    └── (same structure)
```

## 🔧 **Installation & Setup**

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary), macOS, or Linux (experimental)
- Internet connection for NSE access

### Quick Start

1. **Launch the Application**:
   ```bash
   # Using the professional launcher (recommended)
   python launch_nse_datasync_pro.pyw
   
   # Or using the batch file (Windows)
   NSE_DataSync_Pro_Launch.bat
   
   # Or directly
   python nse_datasync_pro_gui.py
   ```

2. **First-Run Setup**:
   - Desktop shortcut will be created automatically
   - Welcome dialog will guide you through initial setup
   - Configure NSE credentials in Settings tab
   - Set download directory and preferences

3. **Configure Credentials**:
   - Go to Settings tab
   - Enter NSE Member Code, Login ID, Password, and Secret Key
   - Click "Save Credentials" and "Test Connection"

4. **Start Automated Downloads**:
   - Go to Dashboard or Scheduler tab
   - Set desired interval (1-1440 minutes)
   - Click "Start Scheduler"
   - Application will auto-stop at midnight daily

## 🎯 **Usage Guide**

### GUI Application
- **Dashboard**: Monitor status, quick controls, recent activity
- **Scheduler**: Configure automated downloads with custom intervals
- **Settings**: Manage credentials and download paths
- **Monitoring**: View real-time logs and system status
- **Statistics**: Analyze download performance and history

### Command Line Interface
```bash
# Manual control script
python nse_manual_control_pro.py --help

# Common commands
python nse_manual_control_pro.py status                    # Check status
python nse_manual_control_pro.py start --background        # Start in background  
python nse_manual_control_pro.py stop                      # Graceful shutdown
python nse_manual_control_pro.py emergency-stop            # Emergency stop
python nse_manual_control_pro.py download                  # Manual download
python nse_manual_control_pro.py download --segments CM,FO # Specific segments
python nse_manual_control_pro.py logs --lines 100          # View recent logs
python nse_manual_control_pro.py stats --days 7            # Weekly statistics
python nse_manual_control_pro.py configure                 # Setup credentials
python nse_manual_control_pro.py test                      # Test connection
```

## ⚙️ **Configuration**

### Database Settings
All settings are stored in `nse_datasync_pro.db`:
- **Credentials**: Encrypted NSE login information
- **Scheduler**: Interval, segments, auto-shutdown settings
- **Paths**: Download directories and organization preferences
- **History**: Complete download logs and statistics
- **System**: Application state and configuration

### Environment Variables (Optional)
If present, these will be imported silently on first run:
```env
NSE_MEMBER_CODE=your_member_code
NSE_LOGIN_ID=your_login_id  
NSE_PASSWORD=your_password
NSE_SECRET_KEY=your_secret_key_base64
```

### Advanced Configuration
- **Max Concurrent Downloads**: 1-10 (default: 3)
- **Retry Attempts**: 1-10 (default: 3)
- **Download Segments**: CM, FO, SLB (configurable)
- **Auto-Shutdown**: 12:00 AM daily (configurable)
- **Log Retention**: Automatic cleanup and rotation

## 🔄 **Scheduler Features**

### Dynamic Intervals
- **Range**: 1 to 1440 minutes (24 hours)
- **Update**: Change without restarting scheduler  
- **Validation**: Input validation and error handling
- **Persistence**: Settings saved to database

### Cycle Management
- **Completion Guarantee**: Current cycle finishes before stopping
- **Status Tracking**: Real-time progress and countdown
- **Error Handling**: Continue on failures, detailed logging
- **Resource Management**: Efficient memory and network usage

### Automatic Controls
- **Midnight Shutdown**: Daily auto-stop for maintenance
- **Startup Recovery**: Resume schedules after restart
- **Conflict Prevention**: Single instance running check
- **Health Monitoring**: Process health and performance tracking

## 📋 **Monitoring & Logging**

### Real-Time Monitoring
- **Live Status**: Current operation and progress
- **Activity Log**: Recent actions and results
- **Connection Status**: NSE connectivity indicator
- **Performance Metrics**: Speed, success rate, errors

### Comprehensive Logging
- **Daily Log Files**: Rotating log files in logs/ directory
- **Structured Format**: Timestamp, level, component, message
- **Error Tracking**: Detailed error information and stack traces
- **Database Logs**: Session history with statistics

### Statistics & Analytics
- **Download Metrics**: Files, sizes, success rates
- **Historical Data**: Trends and patterns over time
- **Segment Analysis**: Per-segment performance breakdown
- **Export Options**: Save logs and statistics for analysis

## 🛡️ **Security Features**

### Credential Protection
- **No Plain Text**: Passwords never stored in plain text
- **Database Encryption**: AES-256 encrypted credential storage
- **Memory Safety**: Credentials cleared from memory after use
- **Secure Transport**: HTTPS/TLS for all NSE communications

### File Integrity
- **Checksum Verification**: SHA-256 checksums for all downloads
- **Download Tracking**: Complete audit trail in database
- **Corruption Detection**: Automatic verification and re-download
- **Secure Paths**: Protection against path traversal attacks

### Process Security
- **Clean Shutdown**: Graceful cleanup of resources and connections
- **Signal Handling**: Proper handling of system shutdown signals
- **Access Control**: Restricted file permissions and database access
- **Error Containment**: Isolated error handling prevents crashes

## 🔧 **Troubleshooting**

### Common Issues

**Login Failures**:
- Verify credentials in Settings tab
- Test connection using "Test Connection" button
- Check NSE website accessibility
- Review logs for detailed error messages

**Scheduler Problems**:
- Ensure credentials are saved and tested
- Check download directory permissions
- Verify network connectivity
- Review scheduler logs for errors

**Download Issues**:
- Check available disk space
- Verify download path configuration
- Test manual download for specific segments
- Review file organization settings

### Emergency Procedures

**Complete Reset**:
```bash
# Stop all processes
python nse_manual_control_pro.py emergency-stop

# Clear database (saves backup)
mv nse_datasync_pro.db nse_datasync_pro.db.backup

# Restart application
python launch_nse_datasync_pro.pyw
```

**Log Analysis**:
```bash
# View recent logs
python nse_manual_control_pro.py logs --lines 200

# Check statistics
python nse_manual_control_pro.py stats --days 7

# Test connectivity
python nse_manual_control_pro.py test
```

## 📞 **Support & Maintenance**

### Log Files Location
- **Windows**: `logs/nse_datasync_pro_YYYYMMDD.log`
- **Database**: `nse_datasync_pro.db`
- **Configuration**: Stored in database settings table

### Performance Optimization
- **Regular Cleanup**: Automatic old file cleanup (configurable)
- **Database Maintenance**: Periodic vacuum and optimization
- **Memory Management**: Efficient resource usage and cleanup
- **Network Optimization**: Connection pooling and retry logic

### Backup Recommendations
- **Database Backup**: Regular backup of `nse_datasync_pro.db`
- **Download Archive**: Periodic archive of downloaded files
- **Configuration Export**: Export settings for disaster recovery
- **Log Retention**: Configure appropriate log retention policies

## 📝 **Version History**

### v2.0 Professional Edition (Current)
- Complete GUI overhaul with professional interface
- Enhanced database with comprehensive logging
- Dynamic scheduler with cycle completion guarantee
- Professional file organization (CM/YYYY/MMM/DD/)
- Secure credential management without .env exposure
- Automatic desktop shortcut creation
- Real-time monitoring and statistics
- Command-line manual control interface
- Antivirus compatibility optimizations
- Automatic midnight shutdown feature

### v1.x Legacy Series
- Basic GUI with essential functionality
- File-based configuration (.env)
- Simple scheduling and download features
- Basic error handling and logging

## 🤝 **Contributing**

This is a professional enterprise solution. For support or customization:

1. **Check Documentation**: Review this README and inline comments
2. **Analyze Logs**: Use built-in logging and monitoring features
3. **Test Components**: Use manual control interface for debugging
4. **Report Issues**: Provide detailed logs and reproduction steps

## 📄 **License**

Professional Enterprise Solution - Proprietary License
Copyright (c) 2024 NSE DataSync Pro

---

**NSE DataSync Pro v2.0 Professional Edition** - Enterprise-grade NSE data synchronization with intelligent automation and professional reliability.
