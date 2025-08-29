# NSE DataSync Pro - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Launch Application
**Choose your preferred method:**

**Option A: Professional Launcher (Recommended)**
```bash
python launch_nse_datasync_pro.pyw
```

**Option B: Windows Batch File**
```bash
NSE_DataSync_Pro_Launch.bat
```

**Option C: Direct Launch**
```bash
python nse_datasync_pro_gui.py
```

### Step 2: First-Time Setup (Automatic)
- ✅ Desktop shortcut created automatically
- ✅ Welcome dialog appears
- ✅ Professional interface opens

### Step 3: Configure NSE Credentials
1. Go to **Settings** tab
2. Enter your NSE details:
   - **Member Code**: Your NSE member code
   - **Login ID**: Your NSE login ID
   - **Password**: Your NSE password
   - **Secret Key**: Your base64 secret key
3. Click **"Save Credentials"**
4. Click **"Test Connection"** to verify

### Step 4: Set Download Preferences
1. In **Settings** tab:
   - **Download Directory**: Choose where files will be saved
   - **Segments**: Select CM, FO, SLB (or specific ones)
2. Click **"Save Configuration"**

### Step 5: Start Automated Downloads
1. Go to **Dashboard** or **Scheduler** tab
2. Set **Download Interval**: 1-1440 minutes (default: 60)
3. Click **"Start Scheduler"**
4. ✅ **Done!** Downloads will run automatically

---

## 📊 Professional Interface Overview

### 🏠 Dashboard Tab
- **Current Status**: Real-time system status
- **Quick Controls**: Start/stop scheduler, manual download
- **Recent Activity**: Latest download results

### ⏰ Scheduler Tab  
- **Interval Configuration**: Set download frequency
- **Segment Selection**: Choose CM, FO, SLB segments
- **Advanced Options**: Concurrent downloads, retry settings
- **Dynamic Updates**: Change settings without restart

### ⚙️ Settings Tab
- **NSE Credentials**: Secure login configuration
- **Download Configuration**: Paths and organization
- **Test Connection**: Verify NSE connectivity

### 📋 Monitoring Tab
- **Real-time Logs**: Live activity monitoring
- **Log Controls**: Clear, save, refresh logs
- **Auto-scroll**: Follow activity in real-time

### 📈 Statistics Tab
- **Performance Overview**: Success rates and metrics
- **Download History**: Complete download records
- **Analytics**: Trends and patterns

---

## 🗂️ File Organization (Automatic)

Your downloads are automatically organized as:

```
Downloads/
├── CM/
│   ├── 2024/
│   │   ├── Jan/
│   │   │   ├── 1/    ← Today's files
│   │   │   ├── 2/
│   │   │   └── ...
│   │   ├── Feb/
│   │   └── ...
├── FO/
│   └── (same structure)
└── SLB/
    └── (same structure)
```

---

## ⚡ Quick Commands

### GUI Quick Actions
- **⚡ Quick Download**: Download now (header button)
- **⏸️ Emergency Stop**: Stop all operations immediately
- **▶️ Start Scheduler**: Begin automated downloads
- **⏹️ Stop Scheduler**: Stop automated downloads gracefully

### Command Line (Advanced)
```bash
# Show status
python nse_manual_control_pro.py status

# Manual download
python nse_manual_control_pro.py download

# Start application in background
python nse_manual_control_pro.py start --background

# View recent logs
python nse_manual_control_pro.py logs

# Emergency stop
python nse_manual_control_pro.py emergency-stop
```

---

## 🛡️ Key Security Features

- **🔐 Encrypted Credentials**: No plain-text passwords
- **📊 Database Storage**: Secure configuration management
- **🚫 No .env Dependencies**: Silent environment handling
- **✅ Antivirus Compatible**: Enterprise security compliant
- **🔒 Checksum Verification**: File integrity protection

---

## 📅 Automated Features

### ⏰ Smart Scheduling
- **Continuous Operation**: Runs every X minutes
- **Cycle Completion**: Always finishes current download
- **Dynamic Updates**: Change interval without restart
- **Midnight Auto-Stop**: Daily shutdown at 12:00 AM

### 🔄 Error Handling
- **Automatic Retry**: Failed downloads retry automatically  
- **Graceful Recovery**: Continue despite individual failures
- **Detailed Logging**: Complete audit trail
- **Real-time Status**: Always know what's happening

---

## ❓ Quick Troubleshooting

### ❌ Can't Connect to NSE
1. Check credentials in Settings → Test Connection
2. Verify internet connectivity
3. Try NSE website manually
4. Check logs in Monitoring tab

### ❌ Scheduler Not Starting
1. Save credentials first in Settings tab
2. Test connection successfully
3. Set valid interval (1-1440 minutes)
4. Check logs for error messages

### ❌ Files Not Downloading
1. Verify download directory permissions
2. Check available disk space
3. Test manual download first
4. Review error logs in Monitoring

### 🆘 Emergency Reset
```bash
# Stop everything
python nse_manual_control_pro.py emergency-stop

# Restart fresh
python launch_nse_datasync_pro.pyw
```

---

## 🎯 Pro Tips

### 🚀 Performance
- **Optimal Interval**: 30-60 minutes for most use cases
- **Concurrent Downloads**: 3-5 for best performance
- **Disk Space**: Monitor available space regularly
- **Network**: Stable internet connection recommended

### 📊 Monitoring
- **Dashboard**: Check status regularly
- **Statistics**: Review weekly performance
- **Logs**: Monitor for any issues
- **Database**: Backup `nse_datasync_pro.db` periodically

### 🔧 Maintenance
- **Auto-Cleanup**: Old files cleaned automatically
- **Log Rotation**: Daily log files for easy management  
- **Database Vacuum**: Periodic optimization
- **Updates**: Check for new versions regularly

---

## 🎉 You're All Set!

**Congratulations!** NSE DataSync Pro is now running professionally:

✅ **Desktop shortcut created**  
✅ **Credentials configured securely**  
✅ **Automated downloads scheduled**  
✅ **Professional file organization active**  
✅ **Real-time monitoring enabled**  
✅ **Enterprise security features active**  

**Your NSE data will now be synchronized automatically with professional reliability!**

---

**Need More Help?**
- 📖 **Full Documentation**: See `README_Professional.md`
- 📋 **Monitoring**: Check Monitoring tab for real-time status
- 📊 **Statistics**: Review performance in Statistics tab
- 🔧 **Manual Control**: Use `nse_manual_control_pro.py` for advanced operations

**NSE DataSync Pro v2.0 Professional Edition** - Your enterprise-grade NSE data synchronization solution.
