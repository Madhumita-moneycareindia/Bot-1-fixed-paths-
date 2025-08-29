#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE DataSync Pro - Manual Control Interface
Command-line interface for managing NSE DataSync Pro operations
Version: 2.0 Professional Edition
"""

import os
import sys
import sqlite3
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Optional import with graceful fallback
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Some features may be limited.")


class NSEManualController:
    """Manual control interface for NSE DataSync Pro"""
    
    def __init__(self):
        self.db_path = Path("nse_datasync_pro.db")
        self.app_script = "nse_datasync_gui.py"  # Fixed: was nse_datasync_pro_gui.py
        self.process_names = [
            "nse_datasync_gui.py",  # Fixed: was nse_datasync_pro_gui.py
            "nse_backup_bot.py",    # Fixed: was nse_enhanced_backup_bot.py
            "nse_scheduler.py",
            "python.exe"  # For Windows processes
        ]

    def start_application(self, background=False):
        """Start the NSE DataSync Pro application"""
        try:
            if self.is_running():
                print("🟡 Application is already running")
                return True
            
            print("🚀 Starting NSE DataSync Pro...")
            
            if background:
                # Start in background mode
                if sys.platform == "win32":
                    subprocess.Popen([
                        sys.executable, self.app_script
                    ], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen([
                        sys.executable, self.app_script
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Start normally
                subprocess.Popen([sys.executable, self.app_script])
            
            # Wait a moment and check if it started
            time.sleep(3)
            if self.is_running():
                print("✅ Application started successfully")
                return True
            else:
                print("❌ Failed to start application")
                return False
                
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            return False

    def stop_application(self):
        """Stop the NSE DataSync Pro application gracefully"""
        if not HAS_PSUTIL:
            print("❌ psutil not available. Cannot stop processes automatically.")
            print("Please close the application manually or install psutil: pip install psutil")
            return False
            
        print("🛑 Stopping NSE DataSync Pro...")
        
        stopped_processes = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if it's our application process
                if proc.info['cmdline'] and any(
                    script in ' '.join(proc.info['cmdline']) 
                    for script in ['nse_datasync_gui.py', 'nse_backup_bot.py']  # Fixed module names
                ):
                    print(f"Stopping process {proc.info['pid']}: {proc.info['name']}")
                    proc.terminate()
                    stopped_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if stopped_processes > 0:
            print(f"✅ Stopped {stopped_processes} process(es)")
        else:
            print("🟡 No running processes found")
        
        return True

    def emergency_stop(self):
        """Emergency stop - forcefully kill all related processes"""
        if not HAS_PSUTIL:
            print("❌ psutil not available. Cannot perform emergency stop.")
            print("Please close the application manually or install psutil: pip install psutil")
            return False
            
        print("🚨 Emergency Stop - Terminating all NSE processes...")
        
        killed_processes = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(
                    script in ' '.join(proc.info['cmdline'])
                    for script in ['nse_datasync', 'NSE', 'nse_backup_bot', 'nse_scheduler']  # Fixed module names
                ):
                    print(f"Force killing PID {proc.info['pid']}: {proc.info['name']}")
                    proc.kill()
                    killed_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"✅ Emergency stop completed - {killed_processes} process(es) terminated")
        return True

    def is_running(self):
        """Check if the application is running"""
        if not HAS_PSUTIL:
            # Fallback: check if GUI script exists and assume it might be running
            gui_path = Path(self.app_script)
            if gui_path.exists():
                print("ℹ️ Cannot verify if application is running (psutil not available)")
                print("Install psutil for better process monitoring: pip install psutil")
            return False
            
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(
                    script in ' '.join(proc.info['cmdline'])
                    for script in ['nse_datasync_gui.py', 'nse_backup_bot.py']  # Fixed module names
                ):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def status(self):
        """Show detailed application status"""
        print("📊 NSE DataSync Pro - System Status")
        print("=" * 50)
        
        if not HAS_PSUTIL:
            print("⚠️ psutil not available - limited status information")
            print("Install psutil for full monitoring: pip install psutil")
            print()
        
        # Check running processes and build the missing process info
        running_processes = []
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
                try:
                    # Check if it's related to our application
                    if proc.info['cmdline'] and any(
                        script in ' '.join(proc.info['cmdline'])
                        for script in ['nse_datasync', 'NSE', 'nse_backup_bot']  # Fixed module names
                    ):
                        start_time = datetime.fromtimestamp(proc.info['create_time'])
                        running_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'start_time': start_time,
                            'uptime': datetime.now() - start_time
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        if running_processes:
            print("🟢 Status: RUNNING")
            print(f"Active Processes: {len(running_processes)}")
            for proc in running_processes:
                print(f"  PID {proc['pid']}: {proc['name']} (uptime: {proc['uptime']})")
        else:
            print("🔴 Status: STOPPED")
            print("No active processes found")
        
        print()
        
        # Check database status
        if self.db_path.exists():
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Get last activity
                    cursor.execute('''
                        SELECT start_time, status FROM run_history 
                        ORDER BY start_time DESC LIMIT 1
                    ''')
                    last_run = cursor.fetchone()
                    
                    if last_run:
                        last_time = datetime.fromisoformat(last_run[0])
                        print(f"Last Activity: {last_time.strftime('%Y-%m-%d %H:%M:%S')} ({last_run[1]})")
                    else:
                        print("Last Activity: Never")
                    
                    # Get scheduler status
                    cursor.execute('''
                        SELECT value FROM settings WHERE key = 'interval_minutes'
                    ''')
                    interval_result = cursor.fetchone()
                    interval = interval_result[0] if interval_result else "Not set"
                    
                    print(f"Scheduler Interval: {interval} minutes")
                    
                    # Get download directory
                    cursor.execute('''
                        SELECT value FROM settings WHERE key = 'download_path'
                    ''')
                    path_result = cursor.fetchone()
                    download_path = path_result[0] if path_result else "Not set"
                    
                    print(f"Download Directory: {download_path}")
                    
            except Exception as e:
                print(f"Database Error: {e}")
        else:
            print("Database: Not found (first run)")
    
    def run_manual_download(self, segments=None):
        """Run a manual download"""
        print("🔄 Starting Manual Download...")
        
        if segments is None:
            segments = ['CM', 'FO', 'SLB']
        
        print(f"Segments: {', '.join(segments)}")
        
        try:
            # Import and run the backup bot - Fixed module name
            from nse_backup_bot import NSEMemberBackupBot
            
            # Get credentials from database or environment
            credentials = self.get_credentials()
            if not credentials:
                print("❌ Error: No credentials found!")
                print("Please run the GUI application first to configure credentials.")
                return False
            
            # Get download directory
            download_dir = self.get_download_directory()
            
            # Initialize bot
            bot = NSEMemberBackupBot(
                member_code=credentials['member_code'],
                login_id=credentials['login_id'],
                password=credentials['password'],
                secret_key=credentials['secret_key'],
                download_dir=download_dir
            )
            
            # Execute download
            print("Connecting to NSE...")
            if not bot.login():
                print("❌ Login failed!")
                return False
            
            print("✅ Connected successfully")
            
            # Download each segment
            results = bot.download_all_segments(segments)
            
            # Print results
            print("\n📋 Download Results:")
            print(f"  Segments completed: {results['segments_completed']}")
            print(f"  Segments failed: {results['segments_failed']}")
            print(f"  Total files: {results['total_files_downloaded']}")
            print(f"  Total size: {results['total_size_mb']:.2f} MB")
            
            if results['segments_failed'] > 0:
                print("\n⚠️ Some segments failed:")
                for segment, result in results['segment_results'].items():
                    if not result.get('success'):
                        print(f"  {segment}: {result.get('error', 'Unknown error')}")
            
            return results['success']
            
        except ImportError as e:
            print(f"❌ Error: Required modules not found: {e}")
            print("Please ensure all dependencies are installed.")
            return False
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def get_credentials(self):
        """Get credentials from database"""
        try:
            if not self.db_path.exists():
                return None
                
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT member_code, login_id, encrypted_password, secret_key 
                    FROM credentials WHERE id = 1 AND is_active = 1
                ''')
                result = cursor.fetchone()
                
                if result:
                    import base64
                    decrypted_password = base64.b64decode(result[2].encode()).decode()
                    return {
                        'member_code': result[0],
                        'login_id': result[1],
                        'password': decrypted_password,
                        'secret_key': result[3]
                    }
        except Exception as e:
            print(f"Error getting credentials: {e}")
        return None
    
    def get_download_directory(self):
        """Get download directory from database"""
        try:
            if not self.db_path.exists():
                return str(Path.home() / 'Downloads' / 'NSE_DataSync_Pro')
                
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT value FROM settings WHERE key = 'download_path'
                ''')
                result = cursor.fetchone()
                
                if result:
                    return result[0]
        except Exception:
            pass
        
        return str(Path.home() / 'Downloads' / 'NSE_DataSync_Pro')
    
    def show_logs(self, lines=50):
        """Show recent log entries"""
        print(f"📋 Recent Log Entries (last {lines} lines)")
        print("=" * 60)
        
        log_dir = Path("logs")
        if not log_dir.exists():
            print("No logs found")
            return
        
        # Find the most recent log file
        log_files = sorted(log_dir.glob("*.log"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not log_files:
            print("No log files found")
            return
        
        latest_log = log_files[0]
        print(f"Log file: {latest_log}")
        print("-" * 60)
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in recent_lines:
                    print(line.rstrip())
                    
        except Exception as e:
            print(f"Error reading log file: {e}")
    
    def show_statistics(self, days=30):
        """Show download statistics"""
        print(f"📊 Download Statistics (last {days} days)")
        print("=" * 50)
        
        try:
            if not self.db_path.exists():
                print("No database found")
                return
                
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_runs,
                        SUM(files_downloaded) as total_files,
                        SUM(total_size_mb) as total_size,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_runs
                    FROM run_history 
                    WHERE start_time >= ?
                ''', (cutoff_date,))
                
                stats = cursor.fetchone()
                
                if stats and stats[0] > 0:
                    total_runs, total_files, total_size, successful_runs = stats
                    success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
                    
                    print(f"Total Runs: {total_runs}")
                    print(f"Successful Runs: {successful_runs}")
                    print(f"Success Rate: {success_rate:.1f}%")
                    print(f"Total Files Downloaded: {total_files or 0}")
                    print(f"Total Size: {total_size or 0:.2f} MB")
                    
                    # Per-segment breakdown
                    cursor.execute('''
                        SELECT segment, COUNT(*), SUM(files_downloaded), SUM(total_size_mb)
                        FROM run_history 
                        WHERE start_time >= ? AND segment IS NOT NULL
                        GROUP BY segment
                    ''', (cutoff_date,))
                    
                    segment_stats = cursor.fetchall()
                    
                    if segment_stats:
                        print("\nPer-Segment Breakdown:")
                        for segment, runs, files, size in segment_stats:
                            print(f"  {segment}: {runs} runs, {files or 0} files, {size or 0:.2f} MB")
                    
                else:
                    print("No data available for the specified period")
                    
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
    
    def configure_credentials(self):
        """Interactive credential configuration"""
        print("🔐 NSE Credentials Configuration")
        print("=" * 40)
        
        try:
            import getpass
            
            member_code = input("Member Code: ").strip()
            login_id = input("Login ID: ").strip()
            password = getpass.getpass("Password: ").strip()
            secret_key = input("Secret Key (base64): ").strip()
            
            if not all([member_code, login_id, password, secret_key]):
                print("❌ All fields are required!")
                return False
            
            # Encrypt and save credentials
            import base64
            encrypted_password = base64.b64encode(password.encode()).decode()
            
            # Ensure database exists
            if not self.db_path.exists():
                print("Creating new database...")
                # Import the database manager to create schema - Fixed module name
                try:
                    from nse_datasync_gui import EnhancedDatabaseManager
                    db_manager = EnhancedDatabaseManager()
                except ImportError:
                    print("⚠️ Could not import database manager. Creating basic schema...")
                    # Create basic schema if import fails
                    self._create_basic_db_schema()
            
            # Save credentials
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO credentials 
                    (id, member_code, login_id, encrypted_password, secret_key, 
                     last_verified, is_active)
                    VALUES (1, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
                ''', (member_code, login_id, encrypted_password, secret_key))
                conn.commit()
            
            print("✅ Credentials saved successfully!")
            
            # Test the credentials
            test_choice = input("Test credentials now? (y/n): ").strip().lower()
            if test_choice == 'y':
                return self.test_credentials()
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Configuration cancelled")
            return False
        except Exception as e:
            print(f"❌ Error saving credentials: {e}")
            return False
    
    def _create_basic_db_schema(self):
        """Create basic database schema if GUI module is not available"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS credentials (
                        id INTEGER PRIMARY KEY,
                        member_code TEXT NOT NULL,
                        login_id TEXT NOT NULL,
                        encrypted_password TEXT NOT NULL,
                        secret_key TEXT NOT NULL,
                        last_verified TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT DEFAULT 'general',
                        description TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS run_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        status TEXT,
                        segment TEXT,
                        files_downloaded INTEGER DEFAULT 0,
                        total_size_mb REAL DEFAULT 0.0,
                        error_message TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Error creating database schema: {e}")
    
    def test_credentials(self):
        """Test NSE credentials"""
        print("🔧 Testing NSE Connection...")
        
        try:
            credentials = self.get_credentials()
            if not credentials:
                print("❌ No credentials found! Run configure first.")
                return False
            
            # Fixed module name
            from nse_backup_bot import NSEMemberBackupBot
            
            bot = NSEMemberBackupBot(
                member_code=credentials['member_code'],
                login_id=credentials['login_id'],
                password=credentials['password'],
                secret_key=credentials['secret_key']
            )
            
            if bot.login():
                print("✅ Connection test successful!")
                return True
            else:
                print("❌ Connection test failed!")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='NSE DataSync Pro - Manual Control Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s start                    # Start the GUI application
  %(prog)s stop                     # Stop the application
  %(prog)s status                   # Show status
  %(prog)s emergency-stop           # Emergency stop all processes
  %(prog)s download                 # Run manual download
  %(prog)s download --segments CM,FO # Download specific segments
  %(prog)s logs --lines 100         # Show last 100 log lines
  %(prog)s stats --days 7           # Show 7-day statistics
  %(prog)s configure                # Configure credentials
  %(prog)s test                     # Test NSE connection
        '''
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the application')
    start_parser.add_argument('--background', '-b', action='store_true',
                            help='Start in background mode')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the application gracefully')
    
    # Status command
    subparsers.add_parser('status', help='Show application status')
    
    # Emergency stop command
    subparsers.add_parser('emergency-stop', help='Emergency stop all processes')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Run manual download')
    download_parser.add_argument('--segments', '-s', default='CM,FO,SLB',
                               help='Segments to download (comma-separated)')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show log entries')
    logs_parser.add_argument('--lines', '-n', type=int, default=50,
                           help='Number of recent lines to show')
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--days', '-d', type=int, default=30,
                            help='Number of days to include')
    
    # Configure command
    subparsers.add_parser('configure', help='Configure NSE credentials')
    
    # Test command
    subparsers.add_parser('test', help='Test NSE connection')
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Create controller instance
    controller = NSEManualController()
    
    # Execute command
    try:
        if args.command == 'start':
            controller.start_application(background=args.background)
        
        elif args.command == 'stop':
            controller.stop_application()
        
        elif args.command == 'status':
            controller.status()
        
        elif args.command == 'emergency-stop':
            controller.emergency_stop()
        
        elif args.command == 'download':
            segments = [s.strip() for s in args.segments.split(',')]
            controller.run_manual_download(segments)
        
        elif args.command == 'logs':
            controller.show_logs(args.lines)
        
        elif args.command == 'stats':
            controller.show_statistics(args.days)
        
        elif args.command == 'configure':
            controller.configure_credentials()
        
        elif args.command == 'test':
            controller.test_credentials()
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
