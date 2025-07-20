#!/usr/bin/env python3
"""
Database viewer for UF Backwash system
"""

import sqlite3
import json
from datetime import datetime

def view_database():
    """View database contents"""
    db_path = "uf_backwash.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 UF Backwash Database Viewer")
        print("=" * 50)
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # View prediction records
        print("📊 Prediction Records:")
        cursor.execute("SELECT COUNT(*) FROM prediction_records")
        count = cursor.fetchone()[0]
        print(f"  Total records: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT id, timestamp, turbidity, ph, temperature, 
                       flow_rate, inlet_pressure, fouling_status,
                       fouling_rate, efficiency, confidence_score
                FROM prediction_records 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            
            records = cursor.fetchall()
            for record in records:
                print(f"  ID: {record[0]}")
                print(f"  Time: {record[1]}")
                print(f"  Turbidity: {record[2]} NTU")
                print(f"  pH: {record[3]}")
                print(f"  Temperature: {record[4]}°C")
                print(f"  Flow Rate: {record[5]} GPM")
                print(f"  Inlet Pressure: {record[6]} PSIG")
                print(f"  Fouling Status: {record[7]}")
                print(f"  Fouling Rate: {record[8]:.3f}")
                print(f"  Efficiency: {record[9]:.1f}%")
                print(f"  Confidence: {record[10]:.2f}")
                print("  " + "-" * 30)
        
        # View system config
        print("\n⚙️ System Configuration:")
        cursor.execute("SELECT * FROM system_config")
        configs = cursor.fetchall()
        
        if configs:
            for config in configs:
                print(f"  Config: {config}")
        else:
            print("  No system configurations found")
        
        # View user sessions
        print("\n👤 User Sessions:")
        cursor.execute("SELECT COUNT(*) FROM user_sessions")
        session_count = cursor.fetchone()[0]
        print(f"  Total sessions: {session_count}")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database() 