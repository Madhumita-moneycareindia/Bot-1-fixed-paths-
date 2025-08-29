#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE DataSync Pro - Professional Launcher (Console-Free)
Keeps all features while eliminating console window completely
"""

import sys
import platform
import subprocess
import importlib.util
from pathlib import Path
import time
import os

# Application constants
APP_NAME = "NSE DataSync Pro"
APP_VERSION = "2.0 Professional Edition"

def hide_console():
    """Hide console window immediately on Windows"""
    if platform.system() == 'Windows':
        try:
            import ctypes
            # Hide console window completely
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

def show_error_dialog(title, message):
    """Show error in GUI dialog instead of console"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        # Create invisible root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # If tkinter fails, try basic system notification
        try:
            if platform.system() == 'Windows':
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, title, 0)
        except:
            pass

def show_info_dialog(title, message):
    """Show info in GUI dialog instead of console"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
    except:
        pass

def ensure_pil_available():
    """Ensure PIL is available, install if missing"""
    try:
        from PIL import Image
        return True
    except ImportError:
        try:
            # Try to install PIL/Pillow silently
            import subprocess
            import sys
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                from PIL import Image  # Test import after installation
                return True
        except:
            pass
        return False

def create_ico_from_png_robust():
    """Ultra-robust icon creation that works from double-click"""
    try:
        # Get absolute script directory
        script_dir = Path(__file__).parent.resolve()
        
        # Define absolute paths
        png_path = script_dir / 'assets' / 'icon.iconset' / 'icon_128x128@2x.png'
        ico_path = script_dir / 'assets' / 'nse_icon_hq.ico'
        debug_log = script_dir / 'icon_creation_debug.txt'
        
        # Create debug log
        debug_info = []
        debug_info.append(f"=== Icon Creation Debug ===")
        debug_info.append(f"Script dir: {script_dir}")
        debug_info.append(f"PNG path: {png_path}")
        debug_info.append(f"PNG exists: {png_path.exists()}")
        debug_info.append(f"ICO target: {ico_path}")
        
        # Check if PNG exists
        if not png_path.exists():
            debug_info.append(f"ERROR: PNG file missing!")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return False, "PNG file not found"
        
        # Ensure PIL is available
        debug_info.append("Checking PIL availability...")
        if not ensure_pil_available():
            debug_info.append("ERROR: PIL/Pillow not available and couldn't install")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return False, "PIL not available"
        
        debug_info.append("PIL available, proceeding with icon creation...")
        
        # Import PIL after ensuring it's available
        from PIL import Image
        
        # Open and process the image
        debug_info.append("Opening PNG image...")
        img = Image.open(png_path)
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        debug_info.append(f"Image mode: {img.mode}, size: {img.size}")
        
        # Create multiple sizes for the ICO file
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        debug_info.append(f"Creating ICO with sizes: {icon_sizes}")
        
        # Save as ICO
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        # Verify creation
        if ico_path.exists():
            file_size = ico_path.stat().st_size
            debug_info.append(f"SUCCESS: ICO created, size: {file_size} bytes")
            
            # Write success log
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            
            return True, f"Icon created successfully ({file_size} bytes)"
        else:
            debug_info.append("ERROR: ICO file was not created")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return False, "ICO file not created"
            
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        debug_info.append(f"ERROR: {error_msg}")
        
        try:
            import traceback
            debug_info.append(f"Traceback: {traceback.format_exc()}")
        except:
            pass
            
        try:
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
        except:
            pass
            
        return False, error_msg

def create_windows_shortcut_robust():
    """Ultra-robust shortcut creation"""
    try:
        script_dir = Path(__file__).parent.resolve()
        debug_log = script_dir / 'shortcut_creation_debug.txt'
        debug_info = []
        
        debug_info.append("=== Shortcut Creation Debug ===")
        
        # Step 1: Create the icon first
        debug_info.append("Step 1: Creating icon...")
        icon_success, icon_msg = create_ico_from_png_robust()
        debug_info.append(f"Icon creation: {icon_success} - {icon_msg}")
        
        # Step 2: Check pywin32 availability
        debug_info.append("Step 2: Checking pywin32...")
        try:
            import pythoncom
            import win32com.client
            from win32com.client import Dispatch
            debug_info.append("pywin32 available")
            pywin32_available = True
        except ImportError as e:
            debug_info.append(f"pywin32 not available: {e}")
            pywin32_available = False
        
        if not pywin32_available:
            debug_info.append("Cannot create .lnk shortcut without pywin32")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return False
        
        # Step 3: Create shortcut
        debug_info.append("Step 3: Creating shortcut...")
        
        desktop = Path.home() / 'Desktop'
        shortcut_path = desktop / f'{APP_NAME}.lnk'
        
        debug_info.append(f"Desktop: {desktop}")
        debug_info.append(f"Shortcut path: {shortcut_path}")
        debug_info.append(f"Shortcut exists: {shortcut_path.exists()}")
        
        if shortcut_path.exists():
            debug_info.append("Shortcut already exists, skipping creation")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return True
        
        # Create the shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Force use of virtual environment Python
        script_dir = Path(__file__).parent.resolve()
        venv_pythonw = script_dir / '.venv' / 'Scripts' / 'pythonw.exe'
        
        if venv_pythonw.exists():
            pythonw_path = str(venv_pythonw)
            debug_info.append(f"Using venv pythonw: {pythonw_path}")
        else:
            # Fallback to system Python
            import shutil
            pythonw_path = shutil.which('pythonw.exe') or shutil.which('pythonw')
            if not pythonw_path:
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
            debug_info.append(f"Using system pythonw: {pythonw_path}")
        
        # Set shortcut properties
        shortcut.Targetpath = pythonw_path
        shortcut.Arguments = f'"{Path(__file__).resolve()}"'
        shortcut.WorkingDirectory = str(script_dir)
        
        # Step 4: Set icon
        debug_info.append("Step 4: Setting icon...")
        
        # Try icons in priority order
        icon_files = ['nse_icon_hq.ico', 'favicon.ico', 'nse_icon.ico']
        icon_set = False
        
        for icon_file in icon_files:
            icon_path = script_dir / 'assets' / icon_file
            debug_info.append(f"Trying icon: {icon_file}")
            debug_info.append(f"Icon path: {icon_path}")
            debug_info.append(f"Icon exists: {icon_path.exists()}")
            
            if icon_path.exists():
                try:
                    shortcut.IconLocation = f"{str(icon_path.resolve())},0"
                    icon_set = True
                    debug_info.append(f"Icon set successfully: {icon_file}")
                    break
                except Exception as e:
                    debug_info.append(f"Failed to set icon {icon_file}: {e}")
                    continue
        
        if not icon_set:
            shortcut.IconLocation = f"{pythonw_path},0"
            debug_info.append("Using default Python icon")
        
        shortcut.Description = f'{APP_NAME} - Professional NSE Data Synchronization'
        shortcut.WindowStyle = 1
        
        # Save shortcut
        debug_info.append("Saving shortcut...")
        shortcut.save()
        
        # Verify shortcut was created
        if shortcut_path.exists():
            debug_info.append("SUCCESS: Shortcut created successfully")
            
            # Force icon cache refresh
            try:
                import ctypes
                ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
                debug_info.append("Icon cache refreshed")
            except Exception as e:
                debug_info.append(f"Icon cache refresh failed: {e}")
            
            # Write success log
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            
            return True
        else:
            debug_info.append("ERROR: Shortcut file was not created")
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
            return False
            
    except Exception as e:
        error_msg = f"Exception in shortcut creation: {str(e)}"
        debug_info.append(error_msg)
        
        try:
            import traceback
            debug_info.append(f"Traceback: {traceback.format_exc()}")
        except:
            pass
        
        try:
            with open(debug_log, 'w') as f:
                f.write('\n'.join(debug_info))
        except:
            pass
        
        return False

def create_macos_alias():
    """Create macOS desktop alias (silent)"""
    try:
        desktop = Path.home() / 'Desktop'
        app_path = Path(__file__).resolve()
        alias_name = f'{APP_NAME}'
        alias_path = desktop / alias_name
        
        if not alias_path.exists():
            script = f'''
tell application "Finder"
    make alias file to POSIX file "{app_path}" at desktop
    set name of result to "{alias_name}"
end tell
'''
            subprocess.run(['osascript', '-e', script], 
                         check=False, capture_output=True)
        return True
    except:
        return False

def create_linux_desktop_entry():
    """Create Linux desktop entry (silent)"""
    try:
        desktop = Path.home() / 'Desktop'
        entry_path = desktop / f'{APP_NAME.replace(" ", "_")}.desktop'
        
        if not entry_path.exists():
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment=Professional NSE Data Synchronization
Exec={sys.executable} "{Path(__file__).resolve()}"
Icon={Path(__file__).parent}/assets/nse_icon.png
Terminal=false
Categories=Office;Finance;
StartupNotify=true
"""
            entry_path.write_text(content)
            entry_path.chmod(0o755)
        return True
    except:
        return False

def check_dependencies():
    """Check if required dependencies are installed (silent)"""
    required_packages = [
        ('tkinter', 'tkinter'),
        ('requests', 'requests'), 
        ('cryptography', 'cryptography'),
        ('PIL', 'Pillow'),
        ('pystray', 'pystray'),
        ('schedule', 'schedule')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            if import_name == 'tkinter':
                import tkinter
            elif import_name == 'PIL':
                import PIL
            else:
                __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages (with GUI progress)"""
    if not packages:
        return True
        
    try:
        # Show installation dialog
        show_info_dialog("Installing Dependencies", 
                        f"Installing required packages: {', '.join(packages)}\n\nThis may take a moment...")
        
        for package in packages:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                show_error_dialog("Installation Failed", 
                                f"Failed to install {package}:\n{result.stderr}")
                return False
        
        show_info_dialog("Installation Complete", 
                        "All required packages have been installed successfully!")
        return True
    except Exception as e:
        show_error_dialog("Installation Error", f"Error installing packages: {str(e)}")
        return False

def refresh_icon_cache():
    """Force Windows to refresh icon cache"""
    try:
        import ctypes
        from ctypes import wintypes
        
        # Refresh icon cache
        SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
        SHChangeNotify(0x08000000, 0x0000, None, None)  # SHCNE_ASSOCCHANGED
    except:
        pass

def fix_existing_shortcut_icon():
    """Fix the icon of existing shortcut"""
    try:
        script_dir = Path(__file__).parent.resolve()
        desktop = Path.home() / 'Desktop'
        shortcut_path = desktop / f'{APP_NAME}.lnk'
        
        if not shortcut_path.exists():
            return False
            
        # Check if we have pywin32
        try:
            import win32com.client
            from win32com.client import Dispatch
        except ImportError:
            return False
        
        # Open existing shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Fix the icon
        icon_path = script_dir / 'assets' / 'nse_icon_hq.ico'
        if icon_path.exists():
            shortcut.IconLocation = f"{str(icon_path.resolve())},0"
            shortcut.save()
            
            # Force icon refresh
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            
            return True
            
    except Exception as e:
        return False

def main():
    """Main launcher function with single execution lock"""
    # Hide console immediately
    hide_console()
    
    # Prevent multiple simultaneous executions
    script_dir = Path(__file__).parent.resolve()
    lock_file = script_dir / 'launcher.lock'
    
    try:
        # Check if already running
        if lock_file.exists():
            # Check if lock is stale (older than 30 seconds)
            lock_age = time.time() - lock_file.stat().st_mtime
            if lock_age < 30:
                return  # Another instance is running
            else:
                lock_file.unlink()  # Remove stale lock
        
        # Create lock file
        lock_file.write_text(str(os.getpid()))
        
        try:
            # Check and install dependencies with GUI feedback
            missing = check_dependencies()
            if missing:
                if not install_missing_packages(missing):
                    return
            
            # Create desktop shortcut ONLY if it doesn't exist
            if platform.system() == 'Windows':
                desktop = Path.home() / 'Desktop'
                shortcut_path = desktop / f'{APP_NAME}.lnk'
                
                # Only create if shortcut doesn't exist
                if not shortcut_path.exists():
                    create_windows_shortcut_robust()
                else:
                    # Shortcut exists, just launch the app
                    pass
            
            # Launch GUI
            from nse_datasync_gui import NSEDataSyncProGUI
            app = NSEDataSyncProGUI()
            app.run()
            
        finally:
            # Remove lock file
            if lock_file.exists():
                lock_file.unlink()
            
    except Exception as e:
        # Remove lock file on error
        if lock_file.exists():
            lock_file.unlink()
        show_error_dialog("Startup Error", f"Error starting {APP_NAME}:\n{str(e)}")

if __name__ == "__main__":
    main()