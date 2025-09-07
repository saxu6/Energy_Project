#!/usr/bin/env python3
"""
Energy Consumption Analyzer - System Startup Script
Provides easy access to run the ML engine or full system
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print the system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        Energy Consumption Analyzer - ML System               ║
    ║                                                              ║
    ║        Advanced Anomaly Detection & Analysis                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    from config import REQUIRED_PACKAGES
    
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("📦 Install missing packages with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_data_files():
    """Check if data files exist"""
    print("\n📁 Checking data files...")
    
    from config import DATA_DIR
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        return False
    
    # Check for at least one month of data
    months = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name not in ['venv', '__pycache__', 'models']]
    
    if not months:
        print("❌ No data directories found")
        return False
    
    print(f"✅ Found {len(months)} data directories: {[m.name for m in months]}")
    return True

def run_ml_engine():
    """Run the ML engine directly"""
    print("\n🤖 Starting ML Engine...")
    print("=" * 50)
    
    try:
        # Import and run the ML engine
        from backend.ml_engine import main
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  ML Engine stopped by user")
    except Exception as e:
        print(f"\n❌ Error running ML Engine: {e}")

def run_full_system():
    """Run the full system with API and frontend"""
    print("\n🚀 Starting Full System (API + Frontend)...")
    print("=" * 50)
    
    try:
        # Start the API server
        print("🌐 Starting API server...")
        api_process = subprocess.Popen([
            sys.executable, 'server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            from config import API_URL
            response = requests.get(f'{API_URL}/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ API server is running!")
            else:
                print("❌ API server failed to start properly")
                return
        except:
            print("❌ API server failed to start")
            return
        
        # Open browser
        print("🌍 Opening browser...")
        from config import API_URL
        webbrowser.open(API_URL)
        
        print("\n🎉 System is running!")
        print(f"📊 Frontend: {API_URL}")
        print(f"🔌 API: {API_URL}/api")
        print("\n⏹️  Press Ctrl+C to stop the system")
        
        # Keep the system running
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping system...")
            api_process.terminate()
            api_process.wait()
            print("✅ System stopped")
            
    except Exception as e:
        print(f"\n❌ Error starting full system: {e}")

def show_menu():
    """Show the main menu"""
    print("\n" + "=" * 50)
    print("🎯 Choose an option:")
    print("=" * 50)
    print("1. 🤖 Run ML Engine (Command Line)")
    print("2. 🚀 Run Full System (API + Frontend)")
    print("3. 📊 Test ML Engine")
    print("4. 🔧 Check System Status")
    print("5. 📖 View Documentation")
    print("6. 🚪 Exit")
    print("=" * 50)

def test_ml_engine():
    """Test the ML engine with sample data"""
    print("\n🧪 Testing ML Engine...")
    
    try:
        from backend.ml_engine import EnergyConsumptionAnalyzer
        
        analyzer = EnergyConsumptionAnalyzer()
        
        # Test with sample data
        print("📊 Testing with sample data...")
        
        # Create sample data
        import pandas as pd
        import numpy as np
        
        sample_data = []
        for room in range(1, 16):
            energy_usage = np.random.uniform(2.0, 5.0, 12)  # 12 time intervals
            total_energy = np.sum(energy_usage)
            
            row = {'Day': 1, 'Room No': room, 'Total Energy (kWh)': total_energy}
            for i, usage in enumerate(energy_usage):
                time_interval = f"{i*2:02d}-{(i+1)*2:02d}"
                row[time_interval] = usage
            
            sample_data.append(row)
        
        df = pd.DataFrame(sample_data)
        
        # Test feature engineering
        print("🔧 Testing feature engineering...")
        df = analyzer.engineer_features(df)
        print(f"✅ Added {len(analyzer.feature_columns)} features")
        
        # Test anomaly detection
        print("🚨 Testing anomaly detection...")
        df = analyzer.detect_anomalies_advanced(df)
        anomalies = df[df['final_anomaly'] == 1]
        print(f"✅ Detected {len(anomalies)} anomalies")
        
        # Test insights generation
        print("💡 Testing insights generation...")
        insights = analyzer.generate_insights(df)
        print(f"✅ Generated insights with {len(insights['recommendations'])} recommendations")
        
        print("\n🎉 ML Engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ ML Engine test failed: {e}")

def check_system_status():
    """Check the overall system status"""
    print("\n🔍 System Status Check")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check data files
    data_ok = check_data_files()
    
    # Check if API can start
    print("\n🌐 Checking API availability...")
    try:
        import requests
        from config import API_URL
        response = requests.get(f'{API_URL}/api/health', timeout=2)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding")
    except:
        print("❌ API server is not running")
    
    print("\n" + "=" * 50)
    if deps_ok and data_ok:
        print("✅ System is ready to run!")
    else:
        print("⚠️  System has issues that need to be resolved")

def show_documentation():
    """Show documentation links"""
    print("\n📖 Documentation")
    print("=" * 50)
    print("📄 README.md - Complete project documentation")
    print("🔧 requirements.txt - Python dependencies")
    print("🤖 optimized_ml_engine.py - ML engine source code")
    print("🌐 frontend/ - Frontend application files")
    print("🔌 api_bridge.py - API server source code")
    print("\n💡 Quick Start:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Run full system: python start_system.py")
    print("   3. Choose option 2 for API + Frontend")
    print("   4. Open browser to http://localhost:8000")

def main():
    """Main function"""
    print_banner()
    
    # Check system status first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    if not check_data_files():
        print("\n❌ Please ensure data files are available")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\n🎯 Enter your choice (1-6): ").strip()
            
            if choice == '1':
                run_ml_engine()
            elif choice == '2':
                run_full_system()
            elif choice == '3':
                test_ml_engine()
            elif choice == '4':
                check_system_status()
            elif choice == '5':
                show_documentation()
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
