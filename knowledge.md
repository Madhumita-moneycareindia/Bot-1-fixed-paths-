# NSE_Datasync_Pro - Knowledge Base

## Quick Start Guide

### Running the Bot
1. **Desktop Icon**: Double-click `NSE_Bot_Direct.pyw`
2. **Batch File**: Run `SafeLauncher.bat`
3. **Direct**: `python nse_bot_gui_fixed.py`

### First Time Setup
1. Open GUI
2. Go to Configuration tab
3. Enter NSE credentials
4. Click "Save Configuration"
5. Click "Test Connection"

---

## Project Structure

```
NSE_ScriptMaster_Bot_2.0/
├── .env                        # Your credentials (DO NOT SHARE)
├── gui_config.json            # Settings
├── my_custom_backup.db        # Download history
├── downloads/                 # Downloaded files
└── NSE_ScriptMaster_Bot 2.0/
    ├── nse_bot_gui_fixed.py   # Main GUI
    ├── integrated_scheduler.py # Scheduler
    └── nse_member_backup_bot.py # Core bot
```

---

## Key Features

### ✅ Implemented Features
- **Continuous Scheduler**: Runs automatically at set intervals
- **Auto-Organization**: Files sorted by date/type
- **Midnight Auto-Stop**: Stops at 12:00 AM
- **Real-time Status**: Live countdown and progress
- **Error Recovery**: Continues despite failures
- **Multi-tab GUI**: Easy management interface

### 🔧 Recent Fixes
1. **Scheduler runs continuously** (not just once)
2. **No duplicate status messages**
3. **Status bar always shows current state**
4. **Enhanced login with retry logic**
5. **Removed auto-refresh feature**

---

## Configuration

### Environment Variables (.env)
```
NSE_MEMBER_CODE=your_member_code
NSE_LOGIN_ID=your_login_id
NSE_PASSWORD=your_password
NSE_SECRET_KEY=your_secret_key_base64
NSE_DOWNLOAD_DIR=path_to_downloads
```

### Scheduler Settings
- **Interval**: 1-1440 minutes
- **Auto-stop**: 12:00 AM (midnight)
- **Update interval**: Click "Update" button

---

## Common Operations

### Single Backup
1. Click "Run Backup Once"
2. Watch status bar for progress
3. Check downloads folder

### Scheduled Backup
1. Set interval (minutes)
2. Click "Start Scheduler"
3. Runs continuously until stopped
4. Auto-stops at midnight

### File Organization
1. Go to File Organization tab
2. Click "Preview Organization"
3. Click "Organize Files"

---

## Troubleshooting

### Login Issues
- **Check credentials**: Verify .env file
- **Test connection**: Use Test Connection button
- **Check logs**: Application Logs tab shows errors
- **Manual verify**: Try logging into NSE website

### Scheduler Not Running
- **Check credentials**: Must be saved first
- **Check logs**: Look for error messages
- **Restart GUI**: Close and reopen
- **Check status bar**: Shows current state

### Files Not Downloading
- **Check connection**: Internet working?
- **Check NSE site**: Is it accessible?
- **Check token**: May need fresh login
- **Check permissions**: Download folder writable?

---

## Technical Details

### Password Encryption
- **Method**: AES-256 ECB mode
- **Key**: Base64 encoded SECRET_KEY
- **Padding**: PKCS7 (128-bit)

### API Endpoints
- **Base**: `https://www.connect2nse.com/extranet-api`
- **Login**: `/login/2.0`
- **List**: `/member/content/2.0`
- **Download**: `/member/file/download/2.0`

### File Organization Structure
```
downloads/
├── 2024/
│   ├── 01_January/
│   │   ├── scripmaster/
│   │   ├── circulars/
│   │   └── others/
│   └── 02_February/
```

---

## Important Notes

⚠️ **Security**
- Never share your .env file
- Keep SECRET_KEY confidential
- Credentials are encrypted locally

📅 **Scheduling**
- Minimum interval: 1 minute
- Maximum interval: 1440 minutes (24 hours)
- Auto-stops at midnight for safety

📁 **Storage**
- Default download location: `downloads/`
- Database: `nse_bot.db`
- Logs: In GUI, not saved to file

🔄 **Updates**
- Scheduler uses IntegratedScheduler
- GUI imports fixed for continuous operation
- Enhanced error handling throughout

---

## Quick Commands

### Check Version
Look for "Fixed Version" in status bar

### View Statistics
1. Go to Statistics tab
2. Click "Refresh"

### Clear Logs
1. Go to Logs & Monitoring tab
2. Click "Clear Logs"

### Save Logs
1. Go to Logs & Monitoring tab
2. Click "Save Logs"
3. Choose location

---

## Contact & Support

For issues:
1. Check Application Logs first
2. Verify credentials are correct
3. Test NSE website manually
4. Check this knowledge base

---

*Last Updated: With all fixes including continuous scheduler, status updates, and midnight auto-stop*