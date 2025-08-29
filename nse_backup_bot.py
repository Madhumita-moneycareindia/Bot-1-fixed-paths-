#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE DataSync Pro - Enhanced Member Backup Bot
Professional-grade NSE data synchronization with organized file structure
Version: 2.0 Professional Edition
"""

import os
import sys
import json
import time
import gzip
import sqlite3
import logging
import requests
import base64
import platform
import hashlib
import shutil
import urllib3  # Add direct import of urllib3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress SSL warnings - Fix the urllib3 attribute access issue
urllib3.disable_warnings(InsecureRequestWarning)

# Fix SQLite datetime deprecation warning for Python 3.12
from datetime import date
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_adapter(date, lambda val: val.isoformat())
sqlite3.register_converter("TIMESTAMP", lambda val: datetime.fromisoformat(val.decode()))
sqlite3.register_converter("DATE", lambda val: datetime.fromisoformat(val.decode()).date())

class NSEMemberBackupBot:
    """Enhanced NSE Member Backup Bot with professional file organization"""
    
    def __init__(self, member_code: str, login_id: str, password: str, 
                 secret_key: str, download_dir: Optional[str] = None):
        """Initialize the NSE backup bot"""
        self.member_code = member_code
        self.login_id = login_id
        self.password = password
        self.secret_key = secret_key
        
        # Set up download directory with professional structure
        if download_dir:
            self.base_download_dir = Path(download_dir)
        else:
            self.base_download_dir = Path.home() / 'Downloads' / 'NSE_DataSync_Pro'
        
        self.base_download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session and logging
        self.session_token = None
        self.session: Optional[requests.Session] = None  # Use Optional in type hint
        self.setup_logging()
        self.setup_session()
        
        # API endpoints
        self.base_url = "https://www.connect2nse.com/extranet-api"
        self.endpoints = {
            'login': f"{self.base_url}/login/2.0",
            'content_list': f"{self.base_url}/member/content/2.0",
            'file_download': f"{self.base_url}/member/file/download/2.0"
        }
        
        # Initialize database for tracking
        self.setup_database()
    
    def setup_logging(self):
        """Setup enhanced logging for the bot"""
        self.logger = logging.getLogger(f"{__name__}.{self.member_code}")
        
        if not self.logger.handlers:
            # Create logs directory
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Create log file
            log_file = log_dir / f"nse_bot_{self.member_code}_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Setup handler
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
            # Also add console handler for immediate feedback
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def setup_session(self):
        """Setup HTTP session with retry strategy"""
        # Initialize a new session
        self.session = requests.Session()
        
        # Configure session
        self.session.verify = False
        
        # Enhanced retry strategy (like working version)
        retry_strategy = Retry(
            total=5,  # Increased retries
            backoff_factor=2,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504, 408],  # Added 408
            read=3,  # Retry on read timeouts
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers
        self.session.headers.update({
            'User-Agent': 'NSE DataSync Pro/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def setup_database(self):
        """Setup database for download tracking - now uses consolidated database"""
        # Use the main consolidated database instead of separate file
        self.db_path = Path("nse_datasync_pro.db")
        
        # The consolidated database manager already creates the bot_file_downloads table
        # So we just need to verify connection and table exists
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Verify the table exists (created by EnhancedDatabaseManager)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bot_file_downloads'
            """)
            
            if not cursor.fetchone():
                # Fallback: create table if it doesn't exist (should not happen normally)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_file_downloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id TEXT,
                        file_name TEXT,
                        segment TEXT,
                        download_date DATE,
                        file_path TEXT,
                        file_size INTEGER,
                        checksum TEXT,
                        status TEXT DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_file_id ON bot_file_downloads(file_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_segment_date ON bot_file_downloads(segment, download_date)')
                conn.commit()
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt password using NSE's encryption method"""
        try:
            # Decode the base64 secret key
            key = base64.b64decode(self.secret_key)
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(password.encode('utf-8'))
            padded_data += padder.finalize()
            
            # Encrypt
            encrypted = encryptor.update(padded_data)
            encrypted += encryptor.finalize()
            
            # Return base64 encoded
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Password encryption failed: {e}")
            raise
    
    def login(self) -> bool:
        """Login to NSE extranet"""
        try:
            self.logger.info(f"Attempting login for member {self.member_code}")
            
            # Encrypt password
            encrypted_password = self.encrypt_password(self.password)
            
            # Login payload
            login_data = {
                "memberCode": self.member_code,
                "loginId": self.login_id,
                "password": encrypted_password
            }
            
            # Make sure session exists
            if self.session is None:
                self.setup_session()
                
            # Make sure session is initialized after setup
            if self.session is None:
                self.logger.error("Failed to initialize session")
                return False
                
            # Make login request
            response = self.session.post(
                self.endpoints['login'],
                json=login_data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for both 'code' and 'responseCode' fields (like working version)
                code = result.get('code') or result.get('responseCode')
                status = result.get('status')
                token = result.get('token')
                
                # Handle code as either string or list
                if (code == '601' or code == ['601']) and token:
                    self.session_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.session_token}'
                    })
                    
                    self.logger.info(f"NSE login successful for member: {self.member_code}")
                    return True
                elif status == 'success' and token:
                    # Alternative success check
                    self.session_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.session_token}'
                    })
                    
                    self.logger.info(f"NSE login successful for member: {self.member_code}")
                    return True
                else:
                    self.logger.error(f"Login failed: {result}")
                    return False
            else:
                self.logger.error(f"Login request failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login exception: {e}")
            return False
    
    def check_segment_access(self) -> Dict[str, bool]:
        """Check which segments the member has access to"""
        self.logger.info("Checking segment access permissions...")
        access_status = {}
        
        if not self.session_token:
            self.logger.error("Not logged in")
            return access_status
        
        # Ensure session is initialized before accessing it
        if self.session is None:
            self.setup_session()
            
        # Make sure session is initialized after setup
        if self.session is None:
            self.logger.error("Failed to initialize session")
            return access_status
            
        for segment in ['CM', 'FO', 'CD', 'CO', 'SLB']:
            try:
                # Try to list root path for each segment
                list_url = f"{self.endpoints['content_list']}?segment={segment}&folderPath=/"
                
                response = self.session.get(
                    list_url,
                    headers={
                        'Authorization': f'Bearer {self.session_token}',
                        'Accept': 'application/json'
                    },
                    timeout=30,
                    verify=False
                )
                
                if response.status_code == 200:
                    result = response.json()
                    code = result.get('code') or result.get('responseCode')
                    
                    # Check for specific error codes
                    if code == '720' or code == ['720']:
                        self.logger.warning(f"  ❌ {segment}: No access (Error 720)")
                        access_status[segment] = False
                    elif code == '704' or code == ['704']:
                        self.logger.warning(f"  ❌ {segment}: Not eligible (Error 704)")
                        access_status[segment] = False
                    elif code == '601' or code == ['601']:
                        self.logger.info(f"  ✅ {segment}: Access granted")
                        access_status[segment] = True
                    else:
                        self.logger.warning(f"  ⚠️  {segment}: Unknown status ({code})")
                        access_status[segment] = False
                else:
                    self.logger.warning(f"  ❌ {segment}: HTTP {response.status_code}")
                    access_status[segment] = False
                    
            except Exception as e:
                self.logger.error(f"  ❌ {segment}: Error - {e}")
                access_status[segment] = False
        
        # Summary
        accessible = [seg for seg, access in access_status.items() if access]
        if accessible:
            self.logger.info(f"\n✅ Accessible segments: {', '.join(accessible)}")
        else:
            self.logger.warning("\n⚠️  No segments are accessible with current credentials")
        
        return access_status
    
    def discover_folder_structure(self, segment: str) -> Optional[str]:
        """Discover the actual folder structure for a segment"""
        self.logger.info(f"Discovering folder structure for segment: {segment}")
        
        # Ensure session is initialized before accessing it
        if self.session is None:
            self.setup_session()
            
        # Make sure session is initialized after setup
        if self.session is None:
            self.logger.error("Failed to initialize session")
            return None
        
        # Start with root path
        try:
            list_url = f"{self.endpoints['content_list']}?segment={segment}&folderPath=/"
            
            response = self.session.get(
                list_url,
                headers={
                    'Authorization': f'Bearer {self.session_token}',
                    'Accept': 'application/json'
                },
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get('code') or result.get('responseCode')
                
                if code == '601' or code == ['601']:
                    items = result.get('data', [])
                    self.logger.info(f"Root folder contains {len(items)} items")
                    
                    # Look for Onlinebackup folder directly or member-specific folders
                    for item in items:
                        if isinstance(item, dict):
                            name = item.get('name', item.get('fileName', ''))
                            item_type = item.get('type', '')
                        else:
                            name = str(item)
                            item_type = 'unknown'
                        
                        self.logger.debug(f"Found item: {name} (type: {item_type})")
                        
                        # Check for Onlinebackup folder
                        if 'Onlinebackup' in name:
                            return f"/{name}"
                        
                        # Check for member-specific folder
                        if self.member_code in name:
                            # Check inside this folder for Onlinebackup
                            sub_path = self._check_subfolder(segment, f"/{name}")
                            if sub_path:
                                return sub_path
                    
                    # If no Onlinebackup found, just use root
                    self.logger.info("No Onlinebackup folder found, using root path")
                    return "/"
        except Exception as e:
            self.logger.error(f"Error discovering folder structure: {e}")
        
        return None
    
    def _check_subfolder(self, segment: str, parent_path: str) -> Optional[str]:
        """Check subfolders for Onlinebackup"""
        try:
            # Ensure session is initialized before accessing it
            if self.session is None:
                self.setup_session()
                
            # Make sure session is initialized after setup
            if self.session is None:
                self.logger.error("Failed to initialize session")
                return None
                
            list_url = f"{self.endpoints['content_list']}?segment={segment}&folderPath={parent_path}"
            
            response = self.session.get(
                list_url,
                headers={
                    'Authorization': f'Bearer {self.session_token}',
                    'Accept': 'application/json'
                },
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get('code') or result.get('responseCode')
                
                if code == '601' or code == ['601']:
                    items = result.get('data', [])
                    
                    for item in items:
                        if isinstance(item, dict):
                            name = item.get('name', item.get('fileName', ''))
                        else:
                            name = str(item)
                        
                        if 'Onlinebackup' in name:
                            return f"{parent_path}/{name}"
        except Exception:
            pass
        
        return None
    
    def get_file_list(self, segment: str) -> List[Dict]:
        """Get list of available files for a segment"""
        try:
            self.logger.info(f"Fetching file list for segment: {segment}")
            
            # Ensure session is initialized before accessing it
            if self.session is None:
                self.setup_session()
                
            # Make sure session is initialized after setup
            if self.session is None:
                self.logger.error("Failed to initialize session")
                return []
            
            # Try different folder paths in order of likelihood
            possible_paths = [
                "/Onlinebackup",  # Try this first (working bot uses this)
                "/",  # Root path
                f"/{self.member_code}/Onlinebackup",
                f"/{self.member_code}",
            ]
            
            # Add segment-specific paths
            if segment == 'FO':
                possible_paths.extend([
                    f"/faoftp/F{self.member_code}/Onlinebackup",
                    f"/faoftp/F{self.member_code}",
                    "/faoftp"
                ])
            elif segment == 'CM':
                possible_paths.extend([
                    f"/cmftp/{self.member_code}/Onlinebackup",
                    f"/cmftp/{self.member_code}",
                    "/cmftp"
                ])
            elif segment == 'SLB':
                possible_paths.extend([
                    f"/slbftp/S{self.member_code}/Onlinebackup",
                    f"/slbftp/S{self.member_code}",
                    "/slbftp"
                ])
            
            # Try each path until we find files
            for folder_path in possible_paths:
                self.logger.info(f"Trying path: {folder_path}")
                
                # Construct URL with query parameters
                list_url = f"{self.endpoints['content_list']}?segment={segment}&folderPath={folder_path}"
                
                response = self.session.get(
                    list_url,
                    headers={
                        'Authorization': f'Bearer {self.session_token}',
                        'Accept': 'application/json'
                    },
                    timeout=30,
                    verify=False
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    self.logger.debug(f"API Response for {segment} at {folder_path}: {result}")
                    
                    # Handle multiple response formats
                    code = result.get('code') or result.get('responseCode')
                    status = result.get('status')
                    
                    # Handle code as either string or list
                    if code == '601' or code == ['601'] or status == 'success':
                        files = result.get('data', [])
                        
                        self.logger.debug(f"Raw files data: {files}")
                        
                        # Process files
                        processed_files = []
                        for f in files:
                            if isinstance(f, dict):
                                # Check if it's a file (not a folder)
                                if f and f.get('type') != 'Folder':
                                    # Get filename from either 'fileName' or 'name'
                                    filename = f.get('fileName') or f.get('name', '')
                                    
                                    # Accept various file types
                                    if filename and (filename.endswith('.gz') or filename.endswith('.csv') or 
                                                   filename.endswith('.txt') or '.' in filename):
                                        # Create file object
                                        file_obj = {
                                            'name': filename,
                                            'fileName': filename,
                                            'id': filename,
                                            'fileSize': f.get('size', 0) or f.get('fileSize', 0),
                                            'lastModified': f.get('lastUpdated') or f.get('lastModified'),
                                            'folderPath': folder_path,
                                            'isFolder': False
                                        }
                                        processed_files.append(file_obj)
                            elif isinstance(f, str):
                                # If response is just filenames
                                if '.' in f:  # Any file with extension
                                    processed_files.append({
                                        'name': f,
                                        'fileName': f,
                                        'id': f,
                                        'folderPath': folder_path
                                    })
                        
                        if processed_files:
                            self.logger.info(f"Found {len(processed_files)} files for segment {segment} at path {folder_path}")
                            return processed_files
                        else:
                            self.logger.info(f"No files found at {folder_path}, trying next path...")
                            
                elif response.status_code == 404:
                    self.logger.debug(f"Path not found: {folder_path}")
                    continue
                else:
                    self.logger.debug(f"HTTP {response.status_code} for path: {folder_path}")
                    continue
            
            # If no files found in any path
            self.logger.error(f"No files found for segment {segment} in any of the tried paths")
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting file list for {segment}: {e}")
            return []
    
    
    def create_organized_directory(self, segment: str) -> Path:
        """Create base directory structure for segment"""
        # Just create the base segment directory
        # Individual files will be organized by date during download
        segment_dir = self.base_download_dir / segment
        segment_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Created base directory: {segment_dir}")
        return segment_dir
    
    def get_file_date_directory(self, segment: str, filename: str) -> Path:
        """Extract date from filename and create appropriate directory structure"""
        import re
        
        # Extract date from filename
        date_str = None
        
        # Pattern 1: Trade_NSE_XX_0_TM_06471_YYYYMMDD_X_0000.csv.gz
        pattern1 = r'Trade_NSE_\w+_\d+_TM_\d+_(\d{8})_'
        match1 = re.search(pattern1, filename)
        
        # Pattern 2: XX_ORD_LOG_DDMMYYYY_06471.CSV.gz
        pattern2 = r'_ORD_LOG_(\d{8})_'
        match2 = re.search(pattern2, filename)
        
        if match1:
            date_part = match1.group(1)
            # Format: YYYYMMDD
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
        elif match2:
            date_part = match2.group(1)
            # Format: DDMMYYYY
            day = date_part[:2]
            month = date_part[2:4]
            year = date_part[4:8]
        else:
            # If no date found, use current date
            now = datetime.now()
            year = str(now.year)
            month = f"{now.month:02d}"
            day = f"{now.day:02d}"
        
        # Convert month number to month name
        month_names = {
            '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
            '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
            '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
        }
        month_name = month_names.get(month, month)
        
        # Create the organized path: segment/year/month/day/
        organized_path = self.base_download_dir / segment / year / month_name / day
        organized_path.mkdir(parents=True, exist_ok=True)
        
        return organized_path
    
    def is_file_downloaded(self, file_id: str, segment: str) -> bool:
        """Check if file is already downloaded"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM bot_file_downloads 
                    WHERE file_id = ? AND segment = ?
                ''', (file_id, segment))
                
                return cursor.fetchone()[0] > 0
        except Exception as e:
            self.logger.error(f"Error checking file download status: {e}")
            return False
    
    def download_file(self, file_info: Dict, segment: str, base_dir: Path, folder_path: str) -> Dict:
        """Download a single file with enhanced error handling"""
        try:
            # Extract file information based on NSE API response structure
            file_name = file_info.get('fileName') or file_info.get('name', '')
            file_id = file_info.get('id', file_name)
            folder_path = file_info.get('folderPath', folder_path)
            
            if not file_name:
                self.logger.error("No valid filename found in file info")
                return {
                    'success': False,
                    'file_name': 'unknown',
                    'error': 'Invalid file info'
                }
            
            # Get the date-based directory for this file
            target_dir = self.get_file_date_directory(segment, file_name)
            
            # Check if already downloaded
            if self.is_file_downloaded(file_id, segment):
                self.logger.info(f"File {file_name} already downloaded previously")
                return {
                    'success': True,
                    'file_name': file_name,
                    'status': 'already_downloaded',
                    'size': 0
                }
            
            self.logger.info(f"Downloading {file_name} for segment {segment}")
            
            # Extract date from filename if present
            date_str = None
            import re
            
            # Try different date patterns
            # Pattern 1: DDMMYYYY
            date_match = re.search(r'(\d{8})', file_name)
            if date_match:
                date_part = date_match.group(1)
                # Check if it's DDMMYYYY format
                if int(date_part[:2]) <= 31 and int(date_part[2:4]) <= 12:
                    date_str = f"{date_part[:2]}-{date_part[2:4]}-{date_part[4:]}"
                # Check if it's YYYYMMDD format
                elif int(date_part[:4]) >= 2000:
                    date_str = f"{date_part[6:]}-{date_part[4:6]}-{date_part[:4]}"
            
            # Ensure session is initialized before accessing it
            if self.session is None:
                self.setup_session()
                
            # Make sure session is initialized after setup
            if self.session is None:
                self.logger.error("Failed to initialize session")
                return {
                    'success': False,
                    'file_name': file_name,
                    'error': 'Session initialization failed'
                }
            
            # Construct download URL with query parameters (like working version)
            download_url = f"{self.endpoints['file_download']}?segment={segment}&folderPath={folder_path}&filename={file_name}"
            
            # Add date if found
            if date_str:
                download_url += f"&date={date_str}"
            
            response = self.session.get(
                download_url,
                headers={
                    'Authorization': f'Bearer {self.session_token}',
                    'Accept': '*/*'  # Important: use */* like working bot
                },
                timeout=300,  # 5 minutes timeout for large files
                verify=False,
                stream=True
            )
            
            if response.status_code == 200:
                # Save file to segment directory
                temp_filename = f"{file_name}.tmp"
                temp_path = target_dir / temp_filename
                final_path = target_dir / file_name
                
                # Download to temp file first
                total_size = 0
                try:
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                total_size += len(chunk)
                    
                    # Verify and decompress if .gz
                    if file_name.endswith('.gz'):
                        try:
                            with gzip.open(temp_path, 'rb') as gz_file:
                                decompressed_content = gz_file.read()
                            
                            # Save decompressed file
                            decompressed_filename = file_name[:-3]
                            decompressed_path = target_dir / decompressed_filename
                            
                            with open(decompressed_path, 'wb') as f:
                                f.write(decompressed_content)
                            
                            self.logger.info(f"✅ Decompressed {file_name} -> {decompressed_filename}")
                            
                            # Remove temp .gz file after successful decompression
                            try:
                                temp_path.unlink()
                            except Exception:
                                pass
                                
                            # Use decompressed file for checksum
                            final_path = decompressed_path
                            
                        except Exception as e:
                            self.logger.warning(f"Could not decompress {file_name}: {e}")
                            # If decompression fails, rename temp to final
                            temp_path.rename(final_path)
                    else:
                        # Not a .gz file, just rename temp to final
                        temp_path.rename(final_path)
                    
                    # Calculate checksum
                    checksum = self.calculate_file_checksum(final_path)
                    
                    # Record download in database
                    self.record_download(file_id, file_name, segment, final_path, total_size, checksum)
                    
                    self.logger.info(f"Successfully downloaded {file_name} ({total_size:,} bytes)")
                    
                    return {
                        'success': True,
                        'file_name': file_name,
                        'file_path': str(final_path),
                        'size': total_size,
                        'checksum': checksum
                    }
                    
                except Exception as e:
                    # Clean up temp file on error
                    if temp_path.exists():
                        try:
                            temp_path.unlink()
                        except:
                            pass
                    raise e
            else:
                error_msg = f"Download failed: HTTP {response.status_code}"
                
                # Try to get error details from response
                try:
                    error_data = response.json()
                    code = error_data.get('code') or error_data.get('responseCode')
                    if code:
                        error_msg = f"API error code: {code}"
                    elif 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    pass
                
                self.logger.error(f"Failed to download {file_name}: {error_msg}")
                
                return {
                    'success': False,
                    'file_name': file_name,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"Download exception: {str(e)}"
            self.logger.error(f"Error downloading {file_info.get('name', 'unknown')}: {error_msg}")
            
            return {
                'success': False,
                'file_name': file_info.get('name', 'unknown'),
                'error': error_msg
            }
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def record_download(self, file_id: str, file_name: str, segment: str, 
                       file_path: Path, file_size: int, checksum: str):
        """Record successful download in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bot_file_downloads 
                    (file_id, file_name, segment, download_date, file_path, file_size, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (file_id, file_name, segment, datetime.now().date(), 
                      str(file_path), file_size, checksum))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording download: {e}")
    
    def download_segment_files(self, segment: str) -> Dict:
        """Download all files for a specific segment"""
        try:
            self.logger.info(f"Starting download for segment: {segment}")
            self.logger.info("=" * 50)
            self.logger.info(f"📂 Processing {segment} segment")
            self.logger.info("=" * 50)
            
            # Ensure we're logged in
            if not self.session_token:
                if not self.login():
                    return {
                        'success': False,
                        'error': 'Login failed',
                        'files_downloaded': 0,
                        'files_failed': 0
                    }
            
            # Create base directory for segment
            base_dir = self.create_organized_directory(segment)
            
            # Get file list
            files = self.get_file_list(segment)
            
            if not files:
                self.logger.warning(f"No files found in {segment}")
                return {
                    'success': False,
                    'error': 'No files found',
                    'files_downloaded': 0,
                    'files_failed': 0
                }
            
            self.logger.info(f"📋 Found {len(files)} files in {segment}")
            
            # Download files
            successful_downloads = 0
            failed_downloads = 0
            total_size = 0
            
            print(f"\n{'='*60}")
            print(f"📂 Processing {segment} segment")
            print(f"{'='*60}")
            print(f"📋 Found {len(files)} files in {segment}\n")
            
            for idx, file_info in enumerate(files, 1):
                # Print progress
                file_name = file_info.get('fileName') or file_info.get('name', 'unknown')
                print(f"[{idx}/{len(files)}] Processing: {file_name}")
                self.logger.info(f"\n[{idx}/{len(files)}] Processing: {file_name}")
                
                # Get folder path from file info
                folder_path = file_info.get('folderPath', '/Onlinebackup')
                
                # Download the file
                result = self.download_file(file_info, segment, base_dir, folder_path)
                
                if result['success']:
                    successful_downloads += 1
                    if result.get('status') != 'already_downloaded':
                        total_size += result.get('size', 0)
                        size_mb = result.get('size', 0) / (1024 * 1024)
                        print(f"✅ Downloaded {file_name} ({result.get('size', 0):,} bytes)")
                        self.logger.info(f"✅ Downloaded {file_name} ({result.get('size', 0):,} bytes / {size_mb:.2f} MB)")
                    else:
                        print(f"⏭️  Skipped {file_name} - already downloaded previously")
                        self.logger.info(f"⏭️  Skipped {file_name} - already downloaded previously")
                else:
                    failed_downloads += 1
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ Failed: {error_msg}")
                    self.logger.error(f"❌ Failed to download {file_name}: {error_msg}")
                
                # Small delay between downloads
                time.sleep(0.5)
            
            self.logger.info(f"\nSegment {segment} download completed:")
            self.logger.info(f"  ✅ Successful: {successful_downloads}")
            self.logger.info(f"  ❌ Failed: {failed_downloads}")
            self.logger.info(f"  💾 Total size: {total_size / (1024 * 1024):.2f} MB")
            
            print(f"\n{segment} Summary:")
            print(f"  ✅ Downloaded: {successful_downloads} files")
            print(f"  ❌ Failed: {failed_downloads} files")
            print(f"  💾 Total size: {total_size / (1024 * 1024):.2f} MB")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'files_downloaded': successful_downloads,
                'files_failed': failed_downloads,
                'total_size_mb': total_size / (1024 * 1024),
                'target_directory': str(base_dir)
            }
            
        except Exception as e:
            error_msg = f"Segment download error: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'files_downloaded': 0,
                'files_failed': 0
            }
    
    def download_all_segments(self, segments: Optional[List[str]] = None) -> Dict:
        """Download files for all specified segments"""
        if segments is None:
            segments = ['CM', 'FO', 'SLB']
        
        self.logger.info(f"Starting download for segments: {', '.join(segments)}")
        
        # Check segment access first
        access_status = self.check_segment_access()
        
        # Filter segments to only those with access
        accessible_segments = [seg for seg in segments if access_status.get(seg, False)]
        
        if not accessible_segments:
            self.logger.error("No accessible segments found")
            return {
                'success': False,
                'segments_completed': 0,
                'segments_failed': len(segments),
                'total_files_downloaded': 0,
                'total_files_failed': 0,
                'total_size_mb': 0,
                'segment_results': {seg: {'success': False, 'error': 'No access'} for seg in segments}
            }
        
        self.logger.info(f"Processing accessible segments: {', '.join(accessible_segments)}")
        
        overall_results = {
            'success': True,
            'segments_completed': 0,
            'segments_failed': 0,
            'total_files_downloaded': 0,
            'total_files_failed': 0,
            'total_size_mb': 0,
            'segment_results': {}
        }
        
        # Mark inaccessible segments as failed
        for segment in segments:
            if segment not in accessible_segments:
                overall_results['segments_failed'] += 1
                overall_results['segment_results'][segment] = {
                    'success': False,
                    'error': 'No access to segment'
                }
        
        # Process accessible segments
        for segment in accessible_segments:
            try:
                result = self.download_segment_files(segment)
                overall_results['segment_results'][segment] = result
                
                if result['success']:
                    overall_results['segments_completed'] += 1
                    overall_results['total_files_downloaded'] += result.get('files_downloaded', 0)
                    overall_results['total_files_failed'] += result.get('files_failed', 0)
                    overall_results['total_size_mb'] += result.get('total_size_mb', 0)
                else:
                    overall_results['segments_failed'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error processing segment {segment}: {e}")
                overall_results['segments_failed'] += 1
                overall_results['segment_results'][segment] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Overall success if at least one segment succeeded
        overall_results['success'] = overall_results['segments_completed'] > 0
        
        self.logger.info(f"Download completed: {overall_results['segments_completed']} segments successful, "
                        f"{overall_results['segments_failed']} failed, "
                        f"{overall_results['total_files_downloaded']} files downloaded")
        
        return overall_results
    
    def get_download_statistics(self, days: int = 30) -> Dict:
        """Get download statistics for the specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_files,
                        SUM(file_size) as total_size,
                        COUNT(DISTINCT segment) as segments_used,
                        COUNT(DISTINCT download_date) as days_active
                    FROM bot_file_downloads 
                    WHERE created_at >= ?
                ''', (cutoff_date,))
                
                overall_stats = cursor.fetchone()
                
                # Per-segment statistics
                cursor.execute('''
                    SELECT 
                        segment,
                        COUNT(*) as files,
                        SUM(file_size) as size
                    FROM bot_file_downloads 
                    WHERE created_at >= ?
                    GROUP BY segment
                ''', (cutoff_date,))
                
                segment_stats = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'total_files': overall_stats[0] or 0,
                    'total_size_mb': (overall_stats[1] or 0) / (1024 * 1024),
                    'segments_used': overall_stats[2] or 0,
                    'days_active': overall_stats[3] or 0,
                    'segment_breakdown': {
                        row[0]: {
                            'files': row[1],
                            'size_mb': row[2] / (1024 * 1024)
                        } for row in segment_stats
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}


def main():
    """Enhanced NSE bot with .env file support"""
    import argparse
    
    # Fix Unicode issues on Windows
    import sys
    import codecs
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    
    # Try to load .env file
    def load_env_file():
        """Load .env file using python-dotenv if available, or manual parsing"""
        # Get the directory where the script is located
        script_dir = Path(__file__).parent
        env_file = script_dir / '.env'
        
        if not env_file.exists():
            return
        
        try:
            # Try python-dotenv first
            from dotenv import load_dotenv
            load_dotenv(env_file)  # Pass the full path to load_dotenv
        except ImportError:
            # Fallback: manually parse .env file
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
    # Load environment variables
    load_env_file()
    
    # Get credentials from environment
    env_member_code = os.getenv('NSE_MEMBER_CODE')
    env_login_id = os.getenv('NSE_LOGIN_ID') 
    env_password = os.getenv('NSE_PASSWORD')
    env_secret_key = os.getenv('NSE_SECRET_KEY')
    env_download_dir = os.getenv('NSE_DOWNLOAD_DIR')
    
    # Create parser with optional arguments (since we have .env fallback)
    parser = argparse.ArgumentParser(
        description='NSE DataSync Pro - Enhanced Member Backup Bot',
        epilog='''
Credentials can be provided via:
1. .env file (recommended): NSE_MEMBER_CODE, NSE_LOGIN_ID, NSE_PASSWORD, NSE_SECRET_KEY
2. Command line arguments (override .env values)

Examples:
  python nse_backup_bot.py                           # Uses .env file
  python nse_backup_bot.py --member-code 12345       # Override member code from .env
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Make arguments optional since we have .env fallback
    parser.add_argument('--member-code', help='NSE Member Code (overrides .env)')
    parser.add_argument('--login-id', help='NSE Login ID (overrides .env)') 
    parser.add_argument('--password', help='NSE Password (overrides .env)')
    parser.add_argument('--secret-key', help='NSE Secret Key (overrides .env)')
    parser.add_argument('--download-dir', help='Download directory path (overrides .env)')
    parser.add_argument('--segments', default='CM,FO,SLB', help='Segments to download (comma-separated)')
    
    args = parser.parse_args()
    
    # Use command line args if provided, otherwise use environment variables
    member_code = args.member_code or env_member_code or ""  # Provide default empty string
    login_id = args.login_id or env_login_id or ""  # Provide default empty string
    password = args.password or env_password or ""  # Provide default empty string
    secret_key = args.secret_key or env_secret_key or ""  # Provide default empty string
    download_dir = args.download_dir or env_download_dir  # This can be None
    
    # Validate that we have all required credentials
    missing_creds = []
    if not member_code:
        missing_creds.append('member-code (NSE_MEMBER_CODE)')
    if not login_id:
        missing_creds.append('login-id (NSE_LOGIN_ID)')
    if not password:
        missing_creds.append('password (NSE_PASSWORD)')
    if not secret_key:
        missing_creds.append('secret-key (NSE_SECRET_KEY)')
    
    if missing_creds:
        print("[ERROR] Missing required credentials:")
        for cred in missing_creds:
            print(f"   - {cred}")
        print("\nPlease provide credentials via:")
        print("1. .env file with NSE_MEMBER_CODE, NSE_LOGIN_ID, NSE_PASSWORD, NSE_SECRET_KEY")
        print("2. Command line arguments --member-code --login-id --password --secret-key")
        print("\n[TIP] For GUI interface, run: python nse_datasync_gui.py")
        sys.exit(1)
    
    # Initialize bot with resolved credentials
    print("[INFO] Initializing NSE DataSync Pro...")
    print(f"[INFO] Member Code: {member_code}")
    print(f"[INFO] Login ID: {login_id}")
    print(f"[INFO] Download Dir: {download_dir or 'Default'}")
    
    bot = NSEMemberBackupBot(
        member_code=member_code,
        login_id=login_id,
        password=password,
        secret_key=secret_key,
        download_dir=download_dir
    )
    
    try:
        # Login
        print("[INFO] Connecting to NSE...")
        if not bot.login():
            print("[ERROR] Login failed!")
            sys.exit(1)
        
        print("[SUCCESS] Connected successfully!")
        
        # Download segments
        segments = [s.strip() for s in args.segments.split(',')]
        print(f"[INFO] Starting download for segments: {', '.join(segments)}")
        print(f"\n{'='*60}")
        print(f"NSE DataSync Pro - Member Backup")
        print(f"Member Code: {member_code}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Segments: {', '.join(segments)}")
        print(f"{'='*60}\n")
        
        results = bot.download_all_segments(segments)
        
        # Print results
        print(f"\n[RESULTS] Download Results:")
        print(f"  [SUCCESS] Segments completed: {results['segments_completed']}")
        print(f"  [FAILED] Segments failed: {results['segments_failed']}")
        print(f"  [FILES] Total files downloaded: {results['total_files_downloaded']}")
        print(f"  [SIZE] Total size: {results['total_size_mb']:.2f} MB")
        
        if results['segments_failed'] > 0:
            print(f"\n[WARNING] Failed segments:")
            for segment, result in results.get('segment_results', {}).items():
                if not result.get('success'):
                    print(f"     {segment}: {result.get('error', 'Unknown error')}")
        
        # Show statistics
        stats = bot.get_download_statistics(30)
        print(f"\n[STATS] 30-Day Statistics:")
        print(f"  [FILES] Total files: {stats.get('total_files', 0)}")
        print(f"  [SIZE] Total size: {stats.get('total_size_mb', 0):.2f} MB")
        print(f"  [DAYS] Active days: {stats.get('days_active', 0)}")
        
        print("\n[SUCCESS] Backup completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
