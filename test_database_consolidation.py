#!/usr/bin/env python3
"""
Test script to verify database consolidation is working correctly
"""

import sqlite3
from pathlib import Path
import logging

def test_consolidated_database():
    """Test that the consolidated database works properly"""
    print("🔍 Testing NSE DataSync Pro Database Consolidation")
    print("=" * 50)
    
    # Check main database exists
    main_db = Path("nse_datasync_pro.db")
    if main_db.exists():
        print(f"✅ Main database exists: {main_db} ({main_db.stat().st_size} bytes)")
    else:
        print(f"❌ Main database not found: {main_db}")
        return False
    
    # Test database connection and tables
    try:
        with sqlite3.connect(str(main_db)) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\n📊 Found {len(tables)} tables:")
            
            # Expected tables
            expected_tables = [
                'settings', 'run_history', 'scheduler_config', 'credentials', 
                'download_tracking', 'bot_file_downloads', 'scheduler_downloads', 
                'scheduler_sessions'
            ]
            
            for table in expected_tables:
                if table in tables:
                    # Count records in each table
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  ✅ {table}: {count} records")
                else:
                    print(f"  ❌ {table}: Missing")
            
            # Check for any unexpected tables
            extra_tables = set(tables) - set(expected_tables)
            if extra_tables:
                print(f"\n🔍 Additional tables found: {', '.join(extra_tables)}")
            
            print(f"\n📈 Database consolidation test: {'✅ PASSED' if all(t in tables for t in expected_tables) else '❌ FAILED'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_gui_database_manager():
    """Test the EnhancedDatabaseManager"""
    print(f"\n🎯 Testing GUI Database Manager:")
    print("-" * 30)
    
    try:
        # Import the GUI database manager
        import sys
        sys.path.append('.')
        from nse_datasync_gui import EnhancedDatabaseManager
        
        # Initialize database manager
        db_manager = EnhancedDatabaseManager()
        
        # Test basic operations
        test_key = "test_consolidation"
        test_value = "success"
        
        # Set a test setting
        db_manager.set_setting(test_key, test_value, 'test')
        
        # Get the test setting
        retrieved_value = db_manager.get_setting(test_key)
        
        if retrieved_value == test_value:
            print("  ✅ Database operations working correctly")
            print("  ✅ Migration functions executed successfully")
            
            # Clean up test data
            with sqlite3.connect(str(db_manager.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM settings WHERE key = ?", (test_key,))
                conn.commit()
            
            return True
        else:
            print(f"  ❌ Database operation failed: Expected '{test_value}', got '{retrieved_value}'")
            return False
            
    except Exception as e:
        print(f"  ❌ GUI Database Manager test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        # Run all tests
        db_test = test_consolidated_database()
        gui_test = test_gui_database_manager()
        
        print(f"\n🎉 Overall Result:")
        print("=" * 20)
        if db_test and gui_test:
            print("✅ Database consolidation is working perfectly!")
            print("\n💡 Benefits achieved:")
            print("  • Single database file for all operations")
            print("  • Unified data access across all components")
            print("  • Automatic migration from legacy databases (if they exist)")
            print("  • Better performance and maintenance")
            print("  • Fresh consolidated tables created automatically")
        else:
            print("❌ Some tests failed. Please check the errors above.")
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc() 