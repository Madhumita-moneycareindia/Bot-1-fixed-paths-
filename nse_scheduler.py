#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE Backup Scheduler - Complete Integrated Version
All components included in a single file to resolve import issues
Enhanced scheduler with automatic file organization and professional features
Version: 2.0 Professional Edition
"""

import os
import sys
import time
import json
import sqlite3
import logging
import requests
import base64
import gzip
import threading
import schedule
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

# =============================================================================
# CONFIGURATION CLASS
# =============================================================================

class Config:
    """Configuration management for NSE scheduler"""
    
    # Environment variables with defaults
    MEMBER_CODE = os.getenv('NSE_MEMBER_CODE', '').strip()
    LOGIN_ID = os.getenv('NSE_LOGIN_ID', '').strip()
    PASSWORD = os.getenv('NSE_PASSWORD', '').strip()
    SECRET_KEY = os.getenv('NSE_SECRET_KEY', '').strip()
    
    # Paths
    DOWNLOAD_DIR = os.getenv('NSE_DOWNLOAD_DIR', str(Path.home() / 'Downloads' / 'NSE_DataSync'))
    DB_PATH = os.getenv('NSE_DB_PATH', 'nse_datasync_pro.db')  # Changed to use consolidated database
    LOG_DIR = Path('logs')
    
    # NSE API Configuration
    NSE_BASE_URL = "https://www.connect2nse.com/extranet-api"
    NSE_LOGIN_URL = f"{NSE_BASE_URL}/login/2.0"
    NSE_CONTENT_URL = f"{NSE_BASE_URL}/member/content/2.0"
    NSE_DOWNLOAD_URL = f"{NSE_BASE_URL}/member/file/download/2.0"
    
    # Default segments
    SEGMENTS = ['CM', 'FO', 'SLB']
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        missing = []
        
        if not cls.MEMBER_CODE:
            missing.append('NSE_MEMBER_CODE')
        if not cls.LOGIN_ID:
            missing.append('NSE_LOGIN_ID') 
        if not cls.PASSWORD:
            missing.append('NSE_PASSWORD')
        if not cls.SECRET_KEY:
            missing.append('NSE_SECRET_KEY')
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Create directories
        Path(cls.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        
        return True

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"nse_scheduler_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

# =============================================================================
# DATABASE MANAGER
# =============================================================================

class DatabaseManager:
    """Enhanced database management for NSE scheduler"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database schema - now uses consolidated database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verify consolidated tables exist (created by EnhancedDatabaseManager)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='scheduler_downloads'
            """)
            
            if not cursor.fetchone():
                # Fallback: create tables if they don't exist (should not happen normally)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scheduler_downloads (
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
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scheduler_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        status TEXT,
                        files_downloaded INTEGER DEFAULT 0,
                        files_failed INTEGER DEFAULT 0,
                        segments TEXT,
                        error_message TEXT
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduler_file_id ON scheduler_downloads(file_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduler_segment_date ON scheduler_downloads(segment, download_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON scheduler_sessions(session_id)')
                
                conn.commit()
    
    def log_session(self, session_data: Dict):
        """Log a backup session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO scheduler_sessions 
                    (session_id, start_time, end_time, status, files_downloaded, files_failed, segments, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_data.get('session_id'),
                    session_data.get('start_time'),
                    session_data.get('end_time'),
                    session_data.get('status'),
                    session_data.get('files_downloaded', 0),
                    session_data.get('files_failed', 0),
                    session_data.get('segments', ''),
                    session_data.get('error_message', '')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging session: {e}")
    
    def log_download(self, file_data: Dict):
        """Log a file download"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scheduler_downloads 
                    (file_id, file_name, segment, download_date, file_path, file_size, checksum, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_data.get('file_id'),
                    file_data.get('file_name'),
                    file_data.get('segment'),
                    file_data.get('download_date', datetime.now().date()),
                    file_data.get('file_path'),
                    file_data.get('file_size', 0),
                    file_data.get('checksum', ''),
                    file_data.get('status', 'completed')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging download: {e}")
    
    def get_statistics(self, days: int = 30) -> Dict:
        """Get download statistics for the specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_downloads,
                        SUM(file_size) as total_size,
                        COUNT(DISTINCT segment) as segments_count
                    FROM scheduler_downloads 
                    WHERE created_at >= ?
                ''', (cutoff_date,))
                
                overall = cursor.fetchone()
                
                # Per-segment statistics
                cursor.execute('''
                    SELECT segment, COUNT(*), SUM(file_size)
                    FROM scheduler_downloads 
                    WHERE created_at >= ?
                    GROUP BY segment
                ''', (cutoff_date,))
                
                segments = dict(cursor.fetchall())
                
                return {
                    'total_downloads': overall[0] or 0,
                    'total_size_mb': (overall[1] or 0) / (1024 * 1024),
                    'segments_count': overall[2] or 0,
                    'segments': segments
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

# =============================================================================
# NSE FILE ORGANIZER  
# =============================================================================

class NSEFileOrganizer:
    """Professional file organization for NSE downloads"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or Config.DOWNLOAD_DIR)
        self.db_manager = DatabaseManager()
    
    def create_organized_structure(self, segment: str, date: Optional[datetime] = None) -> Path:
        """Create organized directory structure: Downloads/CM/2024/Jan/1/"""
        if date is None:
            date = datetime.now()
        
        year = date.strftime('%Y')
        month = date.strftime('%b')  # Jan, Feb, Mar, etc.
        day = str(date.day)
        
        organized_path = self.base_dir / segment / year / month / day
        organized_path.mkdir(parents=True, exist_ok=True)
        
        return organized_path
    
    def organize_files(self, dry_run: bool = False) -> Dict:
        """Organize downloaded files into proper structure"""
        stats = {
            'organized_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'segments': {}
        }
        
        try:
            logger.info(f"Starting file organization (dry_run: {dry_run})")
            
            # Find all files in base directory that need organization
            for file_path in self.base_dir.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip already organized files
                if self._is_already_organized(file_path):
                    stats['skipped_files'] += 1
                    continue
                
                # Determine segment from filename or path
                segment = self._determine_segment(file_path)
                if not segment:
                    continue
                
                # Create target path
                target_dir = self.create_organized_structure(segment)
                target_path = target_dir / file_path.name
                
                try:
                    if not dry_run:
                        if target_path.exists():
                            # File already exists, skip or rename
                            counter = 1
                            base_name = file_path.stem
                            extension = file_path.suffix
                            while target_path.exists():
                                new_name = f"{base_name}_{counter}{extension}"
                                target_path = target_dir / new_name
                                counter += 1
                        
                        # Move file
                        shutil.move(str(file_path), str(target_path))
                        
                        # Log organization
                        self._log_organization(file_path, target_path, segment)
                    
                    stats['organized_files'] += 1
                    
                    # Update segment stats
                    if segment not in stats['segments']:
                        stats['segments'][segment] = 0
                    stats['segments'][segment] += 1
                    
                    logger.info(f"Organized: {file_path.name} -> {segment}")
                    
                except Exception as e:
                    logger.error(f"Error organizing {file_path}: {e}")
                    stats['error_files'] += 1
            
            logger.info(f"Organization complete: {stats['organized_files']} files organized, "
                       f"{stats['skipped_files']} skipped, {stats['error_files']} errors")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in file organization: {e}")
            return stats
    
    def _is_already_organized(self, file_path: Path) -> bool:
        """Check if file is already in organized structure"""
        # Check if path follows CM/YYYY/MMM/DD/ pattern
        parts = file_path.parts
        
        # Need at least 5 parts: base, segment, year, month, day, filename
        if len(parts) < 5:
            return False
        
        try:
            segment_part = parts[-5]  # CM, FO, SLB
            year_part = parts[-4]     # 2024
            month_part = parts[-3]    # Jan, Feb, etc.
            day_part = parts[-2]      # 1, 2, etc.
            
            # Validate structure
            if segment_part not in Config.SEGMENTS:
                return False
            
            # Check year format
            if not year_part.isdigit() or len(year_part) != 4:
                return False
            
            # Check day format
            if not day_part.isdigit():
                return False
            
            return True
            
        except (IndexError, ValueError):
            return False
    
    def _determine_segment(self, file_path: Path) -> Optional[str]:
        """Determine NSE segment from filename or path"""
        file_name = file_path.name.upper()
        path_str = str(file_path).upper()
        
        # Check filename patterns
        if 'CM' in file_name or 'CASH' in file_name:
            return 'CM'
        elif 'FO' in file_name or 'FUTURE' in file_name or 'OPTION' in file_name:
            return 'FO'
        elif 'SLB' in file_name:
            return 'SLB'
        
        # Check path patterns
        for segment in Config.SEGMENTS:
            if segment in path_str:
                return segment
        
        # Default fallback based on common patterns
        if any(pattern in file_name for pattern in ['EQ', 'EQUITY', 'STOCK']):
            return 'CM'
        elif any(pattern in file_name for pattern in ['DERIV', 'FUT', 'OPT']):
            return 'FO'
        
        logger.warning(f"Could not determine segment for: {file_path}")
        return None
    
    def _log_organization(self, original_path: Path, organized_path: Path, segment: str):
        """Log file organization to database"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_organization 
                    (original_path, organized_path, segment, organization_date)
                    VALUES (?, ?, ?, ?)
                ''', (str(original_path), str(organized_path), segment, datetime.now().date()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging organization: {e}")
    
    def get_file_statistics(self) -> Dict:
        """Get file organization statistics"""
        stats = {
            'total_files': 0,
            'segments': {}
        }
        
        try:
            for segment in Config.SEGMENTS:
                segment_dir = self.base_dir / segment
                if segment_dir.exists():
                    file_count = len(list(segment_dir.rglob('*')))
                    stats['segments'][segment] = {
                        'total_files': file_count,
                        'path': str(segment_dir)
                    }
                    stats['total_files'] += file_count
                else:
                    stats['segments'][segment] = {
                        'total_files': 0,
                        'path': str(segment_dir)
                    }
            
        except Exception as e:
            logger.error(f"Error getting file statistics: {e}")  
        
        return stats

# =============================================================================
# NSE MEMBER BACKUP BOT
# =============================================================================

class NSEMemberBackupBot:
    """Enhanced NSE Member Backup Bot with professional features"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.member_code = Config.MEMBER_CODE
        self.login_id = Config.LOGIN_ID
        self.password = Config.PASSWORD
        self.secret_key = Config.SECRET_KEY
        
        # Session attributes will be set in setup_session()
        self.session: requests.Session 
        self.session_token: Optional[str] = None
        self.db_manager = db_manager or DatabaseManager()
        
        self.setup_session()
    
    def setup_session(self):
        """Setup HTTP session with retry strategy"""
        # Initialize session
        self.session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
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
            logger.error(f"Password encryption failed: {e}")
            raise
    
    def login(self) -> bool:
        """Login to NSE extranet"""
        try:
            logger.info(f"Attempting login for member {self.member_code}")
            
            # Encrypt password
            encrypted_password = self.encrypt_password(self.password)
            
            # Login payload
            login_data = {
                "memberCode": self.member_code,
                "userId": self.login_id,
                "password": encrypted_password
            }
            
            # Make sure session exists
            if self.session is None:
                self.setup_session()
                
            # Make login request
            response = self.session.post(
                Config.NSE_LOGIN_URL,
                json=login_data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('status') == 'success':
                    self.session_token = response_data.get('token')
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.session_token}'
                    })
                    
                    logger.info("NSE login successful")
                    return True
                else:
                    error_msg = response_data.get('message', 'Unknown login error')
                    logger.error(f"Login failed: {error_msg}")
                    return False
            else:
                logger.error(f"Login request failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return False
    
    def get_file_list(self, segment: str) -> List[Dict]:
        """Get list of available files for a segment"""
        try:
            logger.info(f"Fetching file list for segment: {segment}")
            
            params = {
                'segment': segment,
                'type': 'onlinebackup'
            }
            
            # Make sure session exists
            if not hasattr(self, 'session') or self.session is None:
                self.setup_session()
                
            response = self.session.get(
                Config.NSE_CONTENT_URL,
                params=params,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    files = data.get('files', [])
                    logger.info(f"Found {len(files)} files for segment {segment}")
                    return files
                else:
                    logger.error(f"File list error: {data.get('message')}")
                    return []
            else:
                logger.error(f"File list request failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting file list for {segment}: {e}")
            return []
    
    def download_file(self, file_info: Dict, segment: str) -> Dict:
        """Download a single file"""
        try:
            file_id = file_info.get('id')
            file_name = file_info.get('name', f"file_{file_id}")
            
            logger.info(f"Downloading {file_name} for segment {segment}")
            
            # Create segment directory
            segment_dir = Path(Config.DOWNLOAD_DIR) / segment
            segment_dir.mkdir(parents=True, exist_ok=True)
            
            # Download request
            download_data = {
                'fileId': file_id,
                'segment': segment
            }
            
            # Make sure session exists
            if not hasattr(self, 'session') or self.session is None:
                self.setup_session()
                
            response = self.session.post(
                Config.NSE_DOWNLOAD_URL,
                json=download_data,
                timeout=300,
                verify=False,
                stream=True
            )
            
            if response.status_code == 200:
                file_path = segment_dir / file_name
                total_size = 0
                
                # Download with progress
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                
                # Calculate checksum
                checksum = self.calculate_checksum(file_path)
                
                # Log download
                self.db_manager.log_download({
                    'file_id': file_id,
                    'file_name': file_name,
                    'segment': segment,
                    'file_path': str(file_path),
                    'file_size': total_size,
                    'checksum': checksum
                })
                
                logger.info(f"Successfully downloaded {file_name} ({total_size} bytes)")
                
                return {
                    'success': True,
                    'file_name': file_name,
                    'file_path': str(file_path),
                    'size': total_size
                }
            else:
                error_msg = f"Download failed: HTTP {response.status_code}"
                logger.error(f"Failed to download {file_name}: {error_msg}")
                
                return {
                    'success': False,
                    'file_name': file_name,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"Download exception: {str(e)}"
            logger.error(f"Error downloading {file_info.get('name', 'unknown')}: {error_msg}")
            
            return {
                'success': False,
                'file_name': file_info.get('name', 'unknown'),
                'error': error_msg
            }
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def download_segment(self, segment: str) -> Dict:
        """Download all files for a segment"""
        try:
            logger.info(f"Starting download for segment: {segment}")
            
            # Get file list
            files = self.get_file_list(segment)
            
            if not files:
                return {
                    'success': False,
                    'segment': segment,
                    'files_downloaded': 0,
                    'files_failed': 0,
                    'error': 'No files found'
                }
            
            # Download files
            successful_downloads = 0
            failed_downloads = 0
            
            for file_info in files:
                result = self.download_file(file_info, segment)
                
                if result['success']:
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                
                # Small delay between downloads
                time.sleep(0.5)
            
            logger.info(f"Segment {segment} download completed: {successful_downloads} successful, {failed_downloads} failed")
            
            return {
                'success': True,
                'segment': segment,
                'files_downloaded': successful_downloads,
                'files_failed': failed_downloads
            }
            
        except Exception as e:
            error_msg = f"Segment download error: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'segment': segment,
                'files_downloaded': 0,
                'files_failed': 0,
                'error': error_msg
            }
    
    def run_backup(self) -> Dict:
        """Run complete backup for all segments"""
        session_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        session_data = {
            'session_id': session_id,
            'start_time': start_time,
            'status': 'running',
            'segments': ','.join(Config.SEGMENTS)
        }
        
        try:
            logger.info(f"Starting backup session: {session_id}")
            
            # Login to NSE
            if not self.login():
                session_data.update({
                    'end_time': datetime.now(),
                    'status': 'failed',
                    'error_message': 'Login failed'
                })
                self.db_manager.log_session(session_data)
                return {'success': False, 'error': 'Login failed'}
            
            # Download all segments
            total_downloaded = 0
            total_failed = 0
            segment_results = {}
            
            for segment in Config.SEGMENTS:
                result = self.download_segment(segment)
                segment_results[segment] = result
                
                total_downloaded += result.get('files_downloaded', 0)
                total_failed += result.get('files_failed', 0)
                
                # Log individual segment result
                logger.info(f"Segment {segment}: {result.get('files_downloaded', 0)} downloaded, {result.get('files_failed', 0)} failed")
            
            # Update session data
            session_data.update({
                'end_time': datetime.now(),
                'status': 'completed',
                'files_downloaded': total_downloaded,
                'files_failed': total_failed
            })
            
            self.db_manager.log_session(session_data)
            
            logger.info(f"Backup session completed: {total_downloaded} files downloaded, {total_failed} failed")
            
            return {
                'success': True,
                'session_id': session_id,
                'files_downloaded': total_downloaded,
                'files_failed': total_failed,
                'segment_results': segment_results
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Backup session failed: {error_msg}")
            
            session_data.update({
                'end_time': datetime.now(),
                'status': 'error',
                'error_message': error_msg
            })
            
            self.db_manager.log_session(session_data)
            
            return {'success': False, 'error': error_msg}

# =============================================================================
# ENHANCED SCHEDULER
# =============================================================================

class EnhancedBackupScheduler:
    """Professional NSE backup scheduler with automatic organization"""
    
    def __init__(self):
        self.running = False
        self.stop_event = threading.Event()
        self.db_manager = DatabaseManager()
        self.organizer = NSEFileOrganizer()
        
        # Validate configuration
        try:
            Config.validate()
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def run_backup_job(self) -> Dict:
        """Run complete backup job with organization"""
        try:
            logger.info("Starting backup job...")
            
            # Run the backup
            bot = NSEMemberBackupBot(self.db_manager)
            backup_result = bot.run_backup()
            
            if backup_result['success']:
                # Organize downloaded files
                logger.info("Organizing downloaded files...")
                org_stats = self.organizer.organize_files(dry_run=False)
                
                logger.info(f"Organization complete: {org_stats['organized_files']} files organized")
                
                backup_result['organization_stats'] = org_stats
                
            return backup_result
            
        except Exception as e:
            error_msg = f"Error in backup job: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def run_scheduled(self, interval_minutes: int = 30):
        """Run scheduled backups"""
        self.running = True
        logger.info(f"Starting enhanced scheduler with {interval_minutes} minute intervals")
        logger.info("Press Ctrl+C to stop scheduler gracefully")
        
        next_run = datetime.now()
        
        try:
            while self.running and not self.stop_event.is_set():
                current_time = datetime.now()
                
                # Check if it's time to run
                if current_time >= next_run:
                    logger.info(f"Running scheduled backup at {current_time.strftime('%H:%M:%S')}")
                    
                    result = self.run_backup_job()
                    
                    if result['success']:
                        logger.info("Scheduled backup completed successfully")
                        files_downloaded = result.get('files_downloaded', 0)
                        files_organized = result.get('organization_stats', {}).get('organized_files', 0)
                        logger.info(f"Downloaded: {files_downloaded} files, Organized: {files_organized} files")
                    else:
                        logger.error(f"Scheduled backup failed: {result.get('error', 'Unknown error')}")
                    
                    # Schedule next run
                    next_run = current_time + timedelta(minutes=interval_minutes)
                    logger.info(f"Next backup scheduled for: {next_run.strftime('%H:%M:%S')}")
                
                # Check for midnight shutdown
                if current_time.hour == 0 and current_time.minute == 0:
                    logger.info("Midnight auto-shutdown triggered")
                    break
                
                # Sleep for 1 second and check stop event
                if self.stop_event.wait(1):
                    break
                    
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
        finally:
            self.running = False
            logger.info("Enhanced scheduler stopped")
    
    def stop(self):
        """Stop the scheduler gracefully"""
        logger.info("Stopping scheduler...")
        self.running = False
        self.stop_event.set()
    
    def show_status(self):
        """Show comprehensive scheduler status"""
        try:
            print("\n" + "="*60)
            print("NSE DATASYNC PRO - ENHANCED SCHEDULER STATUS")
            print("="*60)
            print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Scheduler running: {'Yes' if self.running else 'No'}")
            
            # Configuration info
            print(f"\nConfiguration:")
            print(f"  Member Code: {Config.MEMBER_CODE}")
            print(f"  Download Dir: {Config.DOWNLOAD_DIR}")
            print(f"  Database: {Config.DB_PATH}")
            print(f"  Segments: {', '.join(Config.SEGMENTS)}")
            
            # Database statistics
            stats = self.db_manager.get_statistics()
            print(f"\nRecent Statistics (30 days):")
            print(f"  Total Downloads: {stats.get('total_downloads', 0)}")
            print(f"  Total Size: {stats.get('total_size_mb', 0):.2f} MB")
            print(f"  Active Segments: {stats.get('segments_count', 0)}")
            
            # File organization stats
            file_stats = self.organizer.get_file_statistics()
            print(f"\nFile Organization:")
            print(f"  Total Organized Files: {file_stats['total_files']}")
            
            for segment, segment_stats in file_stats["segments"].items():
                if segment_stats["total_files"] > 0:
                    print(f"  {segment}: {segment_stats['total_files']} files")
            
        except Exception as e:
            print(f"Error getting status: {e}")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function with comprehensive scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NSE DataSync Pro - Enhanced Scheduler v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interval 60           # Run every 60 minutes
  %(prog)s --once                  # Run backup once and exit
  %(prog)s --status                # Show status and statistics
  %(prog)s --organize-only         # Only organize existing files
  %(prog)s --test                  # Test NSE connection
        """
    )
    
    parser.add_argument("--interval", type=int, default=30,
                        help="Backup interval in minutes (default: 30)")
    parser.add_argument("--once", action="store_true",
                        help="Run backup once and exit")
    parser.add_argument("--status", action="store_true",
                        help="Show comprehensive status and exit")
    parser.add_argument("--organize-only", action="store_true",
                        help="Only organize existing files, don't run backup")
    parser.add_argument("--test", action="store_true",
                        help="Test NSE connection and exit")
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        Config.validate()
        
        # Create enhanced scheduler
        scheduler = EnhancedBackupScheduler()
        
        if args.status:
            scheduler.show_status()
            return
        
        if args.test:
            logger.info("Testing NSE connection...")
            bot = NSEMemberBackupBot(scheduler.db_manager)
            if bot.login():
                print("✅ NSE connection successful!")
            else:
                print("❌ NSE connection failed!")
            return
        
        if args.organize_only:
            logger.info("Organizing existing files only...")
            stats = scheduler.organizer.organize_files(dry_run=False)
            logger.info(f"Organization complete: {stats['organized_files']} files organized")
            return
        
        if args.once:
            logger.info("Running backup once with auto-organization...")
            result = scheduler.run_backup_job()
            if result['success']:
                files_downloaded = result.get('files_downloaded', 0)
                files_organized = result.get('organization_stats', {}).get('organized_files', 0)
                logger.info(f"Backup completed successfully: {files_downloaded} downloaded, {files_organized} organized")
            else:
                logger.error(f"Backup failed: {result.get('error', 'Unknown error')}")
            return
        
        # Run scheduled backups
        logger.info(f"Starting scheduled backups every {args.interval} minutes...")
        logger.info("Features: Auto-organization, Midnight shutdown, Professional logging")
        
        try:
            scheduler.run_scheduled(args.interval)
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        finally:
            scheduler.stop()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
